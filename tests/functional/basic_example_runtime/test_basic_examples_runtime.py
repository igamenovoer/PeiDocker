from __future__ import annotations

from pathlib import Path
import time
from typing import Any

import pytest
import yaml

from .helpers import (
    REPO_ROOT,
    TMP_ROOT,
    ExampleScenario,
    ProxySettings,
    RuntimeProject,
    SSHUser,
    assert_contains,
    detect_proxy_settings,
    host_has_gpu_runtime,
    read_tcp_banner,
)


pytestmark = pytest.mark.basic_example_runtime


DEV_USER = SSHUser("dev", "123456")
DEVELOPER_USER = SSHUser("developer", "dev123")
SCIENTIST_USER = SSHUser("scientist", "science123")
ALICE_USER = SSHUser("alice", "alice123")
BOB_USER = SSHUser("bob", "bob123")


def _set_fixed_outputs(config: dict[str, Any], runtime: RuntimeProject) -> None:
    config["stage_1"]["image"]["output"] = f"{runtime.project_name}:stage-1"
    if "stage_2" in config:
        config["stage_2"]["image"]["output"] = f"{runtime.project_name}:stage-2"
    config["stage_1"]["ssh"]["host_port"] = runtime.ports.ssh


def _fixed_config_adapter(config: dict[str, Any], runtime: RuntimeProject) -> None:
    _set_fixed_outputs(config, runtime)


def _env_variables_adapter(config: dict[str, Any], runtime: RuntimeProject) -> None:
    del config
    del runtime


def _env_passthrough_adapter(config: dict[str, Any], runtime: RuntimeProject) -> None:
    del config
    del runtime


def _host_mount_adapter(config: dict[str, Any], runtime: RuntimeProject) -> None:
    _set_fixed_outputs(config, runtime)


def _port_mapping_adapter(config: dict[str, Any], runtime: RuntimeProject) -> None:
    _set_fixed_outputs(config, runtime)
    stage_1 = config["stage_1"]
    stage_2 = config["stage_2"]
    stage_1["ports"] = [f"{runtime.ports.tensorboard}:6006"]
    stage_2["ports"] = [
        f"{runtime.ports.web}:80",
        f"{runtime.ports.app_range_start}-{runtime.ports.app_range_end}:3000-3002",
    ]


def _proxy_adapter(config: dict[str, Any], runtime: RuntimeProject) -> None:
    _set_fixed_outputs(config, runtime)
    if runtime.proxy_settings is None:
        raise AssertionError("Proxy scenario requires detected proxy settings")
    config["stage_1"]["proxy"]["address"] = runtime.proxy_settings.host
    config["stage_1"]["proxy"]["port"] = runtime.proxy_settings.port
    config["stage_1"]["proxy"]["use_https"] = runtime.proxy_settings.scheme == "https"


def _fixed_configure_env(runtime: RuntimeProject) -> dict[str, str]:
    return {}


def _fixed_compose_env(runtime: RuntimeProject) -> dict[str, str]:
    return {}


def _host_mount_configure_env(runtime: RuntimeProject) -> dict[str, str]:
    return {"HOST_WORKSPACE": str(runtime.host_workspace_dir)}


def _env_variables_configure_env(runtime: RuntimeProject) -> dict[str, str]:
    return {
        "PROJECT_NAME": runtime.project_name,
        "SSH_HOST_PORT": str(runtime.ports.ssh),
        "APP_MODE": "prod",
        "CASE_NAME": "env-vars-runtime",
        "APT_REPO_SOURCE": "tuna",
    }


def _env_passthrough_configure_env(runtime: RuntimeProject) -> dict[str, str]:
    return {
        "PROJECT_NAME": runtime.project_name,
        "SSH_HOST_PORT": str(runtime.ports.ssh),
        "APT_REPO_SOURCE": "tuna",
    }


def _env_passthrough_compose_env(runtime: RuntimeProject) -> dict[str, str]:
    return {
        "TAG": "ci",
        "WEB_HOST_PORT": str(runtime.ports.web),
    }


def _read_compose(project: RuntimeProject) -> dict[str, Any]:
    compose_path = project.project_dir / "docker-compose.yml"
    return yaml.safe_load(compose_path.read_text(encoding="utf-8"))


def _assert_minimal_ssh(runtime: RuntimeProject) -> None:
    output = runtime.ssh(DEV_USER, "minimal-ssh-whoami", "whoami && printf '%s' \"$HOME\"")
    assert_contains(output, "dev")
    assert_contains(output, "/home/dev")


def _assert_host_mount(runtime: RuntimeProject) -> None:
    host_file = runtime.host_workspace_dir / "from-host.txt"
    host_file.write_text("from-host", encoding="utf-8")
    container_read = runtime.ssh(
        DEV_USER,
        "host-mount-read-host-file",
        "cat /soft/workspace/from-host.txt",
    )
    assert container_read == "from-host"

    runtime.ssh(
        DEV_USER,
        "host-mount-write-container-file",
        "printf 'from-container' >/soft/workspace/from-container.txt",
    )
    assert (runtime.host_workspace_dir / "from-container.txt").read_text(encoding="utf-8") == (
        "from-container"
    )


def _assert_docker_volume(runtime: RuntimeProject) -> None:
    runtime.ssh(
        DEV_USER,
        "docker-volume-write-file",
        "printf 'persistent-data' >/soft/workspace/persist.txt",
    )
    runtime.down(remove_volumes=False)
    runtime.up()
    runtime.wait_for_all_users()
    persisted = runtime.ssh(
        DEV_USER,
        "docker-volume-read-file",
        "cat /soft/workspace/persist.txt",
    )
    assert persisted == "persistent-data"


def _assert_custom_script(runtime: RuntimeProject) -> None:
    content = runtime.ssh(
        DEV_USER,
        "custom-script-artifact",
        "cat /tmp/peidocker-custom-script.txt",
    )
    assert content == "hello-from-custom-script"


def _assert_env_variables(runtime: RuntimeProject) -> None:
    compose = _read_compose(runtime)
    environment = compose["services"]["stage-2"]["environment"]
    assert environment["APP_MODE"] == "prod"
    assert environment["CASE_NAME"] == "env-vars-runtime"

    output = runtime.docker_exec(
        "env-variables-runtime-env",
        "printenv",
        "APP_MODE",
        "CASE_NAME",
        "RESOLVED_AT",
    )
    assert output.splitlines() == ["prod", "env-vars-runtime", "configure-time"]


def _assert_env_passthrough(runtime: RuntimeProject) -> None:
    compose_text = (runtime.project_dir / "docker-compose.yml").read_text(encoding="utf-8")
    assert "${TAG:-dev}" in compose_text
    assert "${WEB_HOST_PORT:-18080}" in compose_text

    output = runtime.docker_exec(
        "env-passthrough-runtime-env",
        "printenv",
        "RUNTIME_TAG",
        "HOST_WEB_PORT",
        "CONFIG_MODE",
    )
    assert output.splitlines() == ["ci", str(runtime.ports.web), "compose-time"]


def _assert_port_mapping(runtime: RuntimeProject) -> None:
    for container_port in (80, 3000, 3001, 3002, 6006):
        runtime.start_temp_sshd_listener(container_port)
    time.sleep(2)

    port_expectations = {
        runtime.ports.web: "SSH-",
        runtime.ports.app_range_start: "SSH-",
        runtime.ports.app_range_start + 1: "SSH-",
        runtime.ports.app_range_end: "SSH-",
        runtime.ports.tensorboard: "SSH-",
    }
    for host_port, banner_prefix in port_expectations.items():
        banner = read_tcp_banner(host_port)
        assert banner.startswith(banner_prefix), (host_port, banner)


def _assert_apt_mirrors(runtime: RuntimeProject) -> None:
    output = runtime.ssh(
        DEV_USER,
        "apt-mirror-config",
        "grep -R \"mirrors.tuna.tsinghua.edu.cn\" /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null",
    )
    assert_contains(output, "mirrors.tuna.tsinghua.edu.cn")


def _assert_pixi_environment(runtime: RuntimeProject) -> None:
    version = runtime.ssh(DEVELOPER_USER, "pixi-version", "pixi --version")
    assert_contains(version, "pixi")
    global_list = runtime.ssh(DEVELOPER_USER, "pixi-global-list", "pixi global list")
    for package_name in ("scipy", "click", "attrs", "omegaconf", "rich", "networkx"):
        assert_contains(global_list, package_name)


def _assert_conda_environment(runtime: RuntimeProject) -> None:
    output = runtime.ssh(
        SCIENTIST_USER,
        "conda-login-session",
        "printf '%s|%s|%s' \"$(command -v conda)\" \"$(conda info --base)\" \"$(python -c 'import sys; print(sys.executable)')\"",
    )
    parts = output.split("|")
    assert "conda" in parts[0]
    assert parts[1].endswith("/soft/app/miniconda3") or parts[1].endswith(
        "/hard/image/app/miniconda3"
    )
    assert "miniconda3" in parts[2]


def _assert_proxy_setup(runtime: RuntimeProject) -> None:
    compose_text = (runtime.project_dir / "docker-compose.yml").read_text(encoding="utf-8")
    assert_contains(compose_text, "host.docker.internal")
    assert_contains(compose_text, str(runtime.proxy_settings.port if runtime.proxy_settings else ""))

    output = runtime.ssh(
        DEV_USER,
        "proxy-runtime-cleanup",
        "env | grep -Ei '^(http|https|all)_proxy=' || true",
    )
    assert output == ""

    proxy_file_check = runtime.ssh(
        DEV_USER,
        "proxy-apt-cleanup",
        "if [ -f /etc/apt/apt.conf.d/proxy.conf ]; then echo present; else echo absent; fi",
    )
    assert proxy_file_check == "absent"


def _assert_gpu_container(runtime: RuntimeProject) -> None:
    env_output = runtime.docker_exec(
        "gpu-runtime-env",
        "printenv",
        "NVIDIA_VISIBLE_DEVICES",
        "NVIDIA_DRIVER_CAPABILITIES",
    )
    assert env_output.splitlines() == ["all", "compute,utility"]

    if runtime.host_has_gpu_runtime:
        gpu_output = runtime.ssh(DEV_USER, "gpu-runtime-nvidia-smi", "nvidia-smi -L")
        assert_contains(gpu_output, "GPU")


def _assert_multi_user_ssh(runtime: RuntimeProject) -> None:
    assert runtime.ssh(ALICE_USER, "alice-login", "whoami") == "alice"
    assert runtime.ssh(BOB_USER, "bob-login", "whoami") == "bob"

    authorized_keys = runtime.ssh(
        BOB_USER,
        "bob-authorized-keys",
        "cat ~/.ssh/authorized_keys",
    )
    packaged_key = (
        REPO_ROOT
        / "src"
        / "pei_docker"
        / "project_files"
        / "installation"
        / "stage-1"
        / "system"
        / "ssh"
        / "keys"
        / "example-pubkey.pub"
    ).read_text(encoding="utf-8").strip()
    assert_contains(authorized_keys, packaged_key)


SCENARIOS = [
    ExampleScenario(
        name="minimal-ssh",
        users=(DEV_USER,),
        config_adapter=_fixed_config_adapter,
        assert_runtime=_assert_minimal_ssh,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
    ExampleScenario(
        name="host-mount",
        users=(DEV_USER,),
        config_adapter=_host_mount_adapter,
        assert_runtime=_assert_host_mount,
        configure_env_builder=_host_mount_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
    ExampleScenario(
        name="docker-volume",
        users=(DEV_USER,),
        config_adapter=_fixed_config_adapter,
        assert_runtime=_assert_docker_volume,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
    ExampleScenario(
        name="custom-script",
        users=(DEV_USER,),
        config_adapter=_fixed_config_adapter,
        assert_runtime=_assert_custom_script,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
    ExampleScenario(
        name="env-variables",
        users=(DEV_USER,),
        config_adapter=_env_variables_adapter,
        assert_runtime=_assert_env_variables,
        configure_env_builder=_env_variables_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
    ExampleScenario(
        name="env-passthrough",
        users=(DEV_USER,),
        config_adapter=_env_passthrough_adapter,
        assert_runtime=_assert_env_passthrough,
        configure_env_builder=_env_passthrough_configure_env,
        compose_env_builder=_env_passthrough_compose_env,
    ),
    ExampleScenario(
        name="port-mapping",
        users=(DEV_USER,),
        config_adapter=_port_mapping_adapter,
        assert_runtime=_assert_port_mapping,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
    ExampleScenario(
        name="apt-mirrors",
        users=(DEV_USER,),
        config_adapter=_fixed_config_adapter,
        assert_runtime=_assert_apt_mirrors,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
    ExampleScenario(
        name="pixi-environment",
        users=(DEVELOPER_USER,),
        config_adapter=_fixed_config_adapter,
        assert_runtime=_assert_pixi_environment,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
    ExampleScenario(
        name="conda-environment",
        users=(SCIENTIST_USER,),
        config_adapter=_fixed_config_adapter,
        assert_runtime=_assert_conda_environment,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
    ExampleScenario(
        name="proxy-setup",
        users=(DEV_USER,),
        config_adapter=_proxy_adapter,
        assert_runtime=_assert_proxy_setup,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
        requires_proxy=True,
    ),
    ExampleScenario(
        name="gpu-container",
        users=(DEV_USER,),
        config_adapter=_fixed_config_adapter,
        assert_runtime=_assert_gpu_container,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
        requires_gpu=True,
    ),
    ExampleScenario(
        name="multi-user-ssh",
        users=(ALICE_USER, BOB_USER),
        config_adapter=_fixed_config_adapter,
        assert_runtime=_assert_multi_user_ssh,
        configure_env_builder=_fixed_configure_env,
        compose_env_builder=_fixed_compose_env,
    ),
]


@pytest.fixture(scope="session")
def basic_example_artifact_root() -> Path:
    run_id = time.strftime("run-%Y%m%d-%H%M%S")
    path = TMP_ROOT / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture(scope="session")
def detected_proxy_settings() -> ProxySettings | None:
    return detect_proxy_settings()


@pytest.fixture(scope="session")
def gpu_runtime_available() -> bool:
    return host_has_gpu_runtime()


@pytest.fixture
def runtime_project(
    request: pytest.FixtureRequest,
    basic_example_artifact_root: Path,
    detected_proxy_settings: ProxySettings | None,
    gpu_runtime_available: bool,
) -> RuntimeProject:
    scenario = request.param
    if scenario.requires_proxy and detected_proxy_settings is None:
        pytest.skip("No HTTP/HTTPS proxy environment detected for proxy-sensitive scenario")
    if scenario.requires_gpu and not gpu_runtime_available:
        pytest.skip("GPU runtime not available on host")

    runtime = RuntimeProject(
        scenario=scenario,
        artifact_root=basic_example_artifact_root,
        run_id=f"{int(time.time())}-{scenario.name}",
        proxy_settings=detected_proxy_settings,
        host_has_gpu_runtime=gpu_runtime_available,
    )
    runtime.prepare()
    runtime.build()
    runtime.up()
    runtime.wait_for_all_users()

    try:
        yield runtime
    finally:
        runtime.teardown()


@pytest.mark.parametrize("runtime_project", SCENARIOS, ids=lambda scenario: scenario.name, indirect=True)
def test_basic_example_runtime(runtime_project: RuntimeProject) -> None:
    runtime_project.scenario.assert_runtime(runtime_project)
