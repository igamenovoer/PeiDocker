from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import shlex
import shutil
import socket
import subprocess
import sys
import time
from typing import Any, Callable
from urllib.parse import urlparse

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES_ROOT = REPO_ROOT / "src" / "pei_docker" / "examples" / "basic"
TMP_ROOT = REPO_ROOT / "tmp" / "basic-example-runtime-e2e"


def _sanitize(value: str) -> str:
    safe = []
    for char in value:
        if char.isalnum() or char in {"-", "_", "."}:
            safe.append(char)
        else:
            safe.append("-")
    return "".join(safe).strip("-") or "item"


def allocate_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return int(sock.getsockname()[1])


def allocate_consecutive_ports(count: int) -> tuple[int, int]:
    if count <= 0:
        raise ValueError("count must be positive")

    for start in range(30000, 60000 - count):
        sockets: list[socket.socket] = []
        try:
            for offset in range(count):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("127.0.0.1", start + offset))
                sockets.append(sock)
            return start, start + count - 1
        except OSError:
            for sock in sockets:
                sock.close()
        finally:
            for sock in sockets:
                sock.close()

    raise RuntimeError(f"Could not find {count} consecutive free ports")


def deep_merge_env(base: dict[str, str], extra: dict[str, str] | None) -> dict[str, str]:
    merged = dict(base)
    if extra:
        merged.update(extra)
    return merged


@dataclass(frozen=True)
class SSHUser:
    username: str
    password: str


@dataclass(frozen=True)
class ProxySettings:
    scheme: str
    host: str
    port: int


@dataclass
class ScenarioPorts:
    ssh: int
    web: int | None = None
    tensorboard: int | None = None
    app_range_start: int | None = None
    app_range_end: int | None = None


@dataclass(frozen=True)
class ExampleScenario:
    name: str
    users: tuple[SSHUser, ...]
    config_adapter: Callable[[dict[str, Any], "RuntimeProject"], None]
    assert_runtime: Callable[["RuntimeProject"], None]
    configure_env_builder: Callable[["RuntimeProject"], dict[str, str]]
    compose_env_builder: Callable[["RuntimeProject"], dict[str, str]]
    requires_proxy: bool = False
    requires_gpu: bool = False

    @property
    def example_dir(self) -> Path:
        return EXAMPLES_ROOT / self.name


@dataclass
class RuntimeProject:
    scenario: ExampleScenario
    artifact_root: Path
    run_id: str
    proxy_settings: ProxySettings | None
    host_has_gpu_runtime: bool
    ports: ScenarioPorts = field(init=False)
    project_name: str = field(init=False)
    compose_project_name: str = field(init=False)
    artifact_dir: Path = field(init=False)
    project_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    host_workspace_dir: Path = field(init=False)
    configure_env: dict[str, str] = field(default_factory=dict)
    compose_env: dict[str, str] = field(default_factory=dict)
    _log_counter: int = field(default=0, init=False)
    _resolved_images: list[str] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.project_name = f"pei-basic-{self.scenario.name}-{self.run_id}"
        self.compose_project_name = _sanitize(self.project_name)
        self.artifact_dir = self.artifact_root / self.scenario.name
        self.project_dir = self.artifact_dir / "project"
        self.logs_dir = self.artifact_dir / "logs"
        self.host_workspace_dir = self.artifact_dir / "host-workspace"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.host_workspace_dir.mkdir(parents=True, exist_ok=True)
        self.ports = self._allocate_ports()

    def _allocate_ports(self) -> ScenarioPorts:
        ssh_port = allocate_free_port()
        if self.scenario.name == "port-mapping":
            app_start, app_end = allocate_consecutive_ports(3)
            return ScenarioPorts(
                ssh=ssh_port,
                web=allocate_free_port(),
                tensorboard=allocate_free_port(),
                app_range_start=app_start,
                app_range_end=app_end,
            )
        if self.scenario.name == "env-passthrough":
            return ScenarioPorts(ssh=ssh_port, web=allocate_free_port())
        return ScenarioPorts(ssh=ssh_port)

    def example_dir(self) -> Path:
        return self.scenario.example_dir

    def run(
        self,
        label: str,
        cmd: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        self._log_counter += 1
        log_path = self.logs_dir / f"{self._log_counter:02d}-{_sanitize(label)}.log"
        merged_env = deep_merge_env(os.environ, env)
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=merged_env,
            capture_output=True,
            text=True,
            check=False,
        )
        transcript = "\n".join(
            [
                f"$ {' '.join(shlex.quote(part) for part in cmd)}",
                f"cwd={cwd or Path.cwd()}",
                f"returncode={result.returncode}",
                "",
                "[stdout]",
                result.stdout,
                "",
                "[stderr]",
                result.stderr,
                "",
            ]
        )
        log_path.write_text(transcript, encoding="utf-8")
        if check and result.returncode != 0:
            raise AssertionError(
                f"Command failed for {self.scenario.name}: {cmd!r}. See {log_path}"
            )
        return result

    def docker_compose(
        self,
        label: str,
        *args: str,
        env: dict[str, str] | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        cmd = ["docker", "compose", "-p", self.compose_project_name, *args]
        return self.run(
            label,
            cmd,
            cwd=self.project_dir,
            env=deep_merge_env(self.compose_env, env),
            check=check,
        )

    def prepare(self) -> None:
        if self.scenario.requires_proxy and self.proxy_settings is None:
            raise RuntimeError("Proxy-sensitive scenario requires detected proxy settings")

        self.run(
            "create-project",
            [sys.executable, "-m", "pei_docker.pei", "create", "-p", str(self.project_dir)],
        )
        self._overlay_example()
        self._adapt_user_config()
        self.configure_env = self.scenario.configure_env_builder(self)
        self.compose_env = self.scenario.compose_env_builder(self)
        self.run(
            "configure-project",
            [sys.executable, "-m", "pei_docker.pei", "configure", "-p", str(self.project_dir)],
            env=self.configure_env,
        )
        self._resolved_images = self._resolve_images()

    def build(self) -> None:
        self.docker_compose("compose-build-stage1", "build", "stage-1")
        self.docker_compose("compose-build-stage2", "build", "stage-2")

    def up(self) -> None:
        self.docker_compose("compose-up-stage2", "up", "-d", "stage-2")

    def down(self, remove_volumes: bool = True) -> None:
        args = ["down", "--remove-orphans"]
        if remove_volumes:
            args.append("-v")
        self.docker_compose("compose-down", *args, check=False)

    def teardown(self) -> None:
        self.docker_compose("compose-ps", "ps", check=False)
        self.docker_compose("compose-logs", "logs", "--no-color", check=False)
        self.down(remove_volumes=True)
        for image in self._resolved_images:
            self.run("remove-image-" + image, ["docker", "image", "rm", "-f", image], check=False)

    def wait_for_ssh(self, user: SSHUser, timeout_seconds: int = 90) -> None:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            probe = subprocess.run(
                [
                    "sshpass",
                    "-p",
                    user.password,
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-o",
                    "LogLevel=ERROR",
                    "-o",
                    "ConnectTimeout=2",
                    "-p",
                    str(self.ports.ssh),
                    f"{user.username}@127.0.0.1",
                    "bash -lic 'echo ready'",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if probe.returncode == 0 and "ready" in probe.stdout:
                return
            time.sleep(2)
        raise AssertionError(
            f"SSH did not become ready for user {user.username} on port {self.ports.ssh}"
        )

    def wait_for_all_users(self) -> None:
        for user in self.scenario.users:
            self.wait_for_ssh(user)

    def ssh(self, user: SSHUser, label: str, command: str, *, check: bool = True) -> str:
        wrapped = f"bash -ic {shlex.quote(command)}"
        result = self.run(
            label,
            [
                "sshpass",
                "-p",
                user.password,
                "ssh",
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-o",
                "LogLevel=ERROR",
                "-o",
                "ConnectTimeout=5",
                "-p",
                str(self.ports.ssh),
                f"{user.username}@127.0.0.1",
                wrapped,
            ],
            check=check,
        )
        return normalize_command_output(result.stdout)

    def docker_exec(self, label: str, *command: str, check: bool = True) -> str:
        result = self.docker_compose(
            label,
            "exec",
            "-T",
            "stage-2",
            *command,
            check=check,
        )
        return normalize_command_output(result.stdout)

    def docker_exec_detached(self, label: str, *command: str) -> None:
        self.docker_compose(label, "exec", "-d", "stage-2", *command)

    def start_temp_sshd_listener(self, container_port: int) -> None:
        self.docker_exec_detached(
            f"start-sshd-{container_port}",
            "/usr/sbin/sshd",
            "-D",
            "-o",
            "PermitRootLogin=yes",
            "-o",
            "PasswordAuthentication=yes",
            "-o",
            "ListenAddress=0.0.0.0",
            "-o",
            f"PidFile=/tmp/sshd-{container_port}.pid",
            "-p",
            str(container_port),
        )

    def _overlay_example(self) -> None:
        for item in self.example_dir().iterdir():
            dst = self.project_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst)

    def _adapt_user_config(self) -> None:
        user_config_path = self.project_dir / "user_config.yml"
        config = yaml.safe_load(user_config_path.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise AssertionError("Expected dictionary-shaped user_config.yml")
        self.scenario.config_adapter(config, self)
        user_config_path.write_text(
            yaml.safe_dump(config, sort_keys=False),
            encoding="utf-8",
        )

    def _resolve_images(self) -> list[str]:
        result = self.docker_compose("compose-config-images", "config", "--images")
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def detect_proxy_settings(env: dict[str, str] | None = None) -> ProxySettings | None:
    search_env = env or dict(os.environ)
    candidates = [
        search_env.get("HTTP_PROXY"),
        search_env.get("http_proxy"),
        search_env.get("HTTPS_PROXY"),
        search_env.get("https_proxy"),
        search_env.get("ALL_PROXY"),
        search_env.get("all_proxy"),
    ]
    for value in candidates:
        if not value:
            continue
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or not parsed.port:
            continue
        host = parsed.hostname
        if host in {"127.0.0.1", "localhost"}:
            host = "host.docker.internal"
        return ProxySettings(scheme=parsed.scheme, host=host, port=parsed.port)
    return None


def host_has_gpu_runtime() -> bool:
    if shutil.which("nvidia-smi") is None:
        return False
    result = subprocess.run(
        ["nvidia-smi"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def read_tcp_banner(port: int, timeout_seconds: float = 10.0) -> str:
    deadline = time.time() + timeout_seconds
    last_error: OSError | None = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=2) as sock:
                sock.settimeout(2)
                data = sock.recv(128)
                return data.decode("utf-8", errors="replace")
        except OSError as exc:
            last_error = exc
            time.sleep(1)
    raise AssertionError(f"Could not connect to host port {port}: {last_error}")


def assert_contains(text: str, needle: str, message: str | None = None) -> None:
    if needle not in text:
        raise AssertionError(message or f"Expected {needle!r} in output: {text!r}")


def normalize_command_output(text: str) -> str:
    ignored_lines = {
        'To run a command as administrator (user "root"), use "sudo <command>".',
        'See "man sudo_root" for details.',
    }
    lines = [line for line in text.splitlines() if line not in ignored_lines]

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines)
