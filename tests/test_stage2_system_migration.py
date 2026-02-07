"""
Regression tests for the "stage-2 system -> stage-1 canonical" migration.

These tests focus on invariants that should remain stable over time:
- canonical installer implementations live under `installation/stage-1/system/**`
- `installation/stage-2/system/**` scripts are compatibility wrappers
- non-shell assets (e.g., OpenGL JSON/YAML, LiteLLM proxy) are canonical in stage-1
- wrappers are source-safe and forward arguments verbatim
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import omegaconf as oc
import pytest

from pei_docker.config_processor import PeiConfigProcessor

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALLATION_ROOT = REPO_ROOT / "src" / "pei_docker" / "project_files" / "installation"
STAGE1_SYSTEM = INSTALLATION_ROOT / "stage-1" / "system"
STAGE2_SYSTEM = INSTALLATION_ROOT / "stage-2" / "system"


def _load_compose_template() -> oc.DictConfig:
    import pei_docker

    pkg_root = Path(pei_docker.__file__).resolve().parent
    template_path = pkg_root / "templates" / "base-image-gen.yml"
    cfg = oc.OmegaConf.load(str(template_path))
    assert isinstance(cfg, oc.DictConfig)
    return cfg


def test_stage1_contains_migrated_system_tools() -> None:
    assert (STAGE1_SYSTEM / "bun").is_dir()
    assert (STAGE1_SYSTEM / "claude-code").is_dir()
    assert (STAGE1_SYSTEM / "codex-cli").is_dir()
    assert (STAGE1_SYSTEM / "litellm").is_dir()
    assert (STAGE1_SYSTEM / "magnum").is_dir()
    assert (STAGE1_SYSTEM / "nodejs").is_dir()
    assert (STAGE1_SYSTEM / "opencv").is_dir()
    assert (STAGE1_SYSTEM / "opengl").is_dir()
    assert (STAGE1_SYSTEM / "set-locale.sh").is_file()


def test_stage2_contains_wrapper_paths() -> None:
    assert (STAGE2_SYSTEM / "bun" / "install-bun.sh").is_file()
    assert (STAGE2_SYSTEM / "claude-code" / "install-claude-code.sh").is_file()
    assert (STAGE2_SYSTEM / "codex-cli" / "install-codex-cli.sh").is_file()
    assert (STAGE2_SYSTEM / "litellm" / "install-litellm.sh").is_file()
    assert (STAGE2_SYSTEM / "magnum" / "install-magnum-gl.sh").is_file()
    assert (STAGE2_SYSTEM / "nodejs" / "install-nvm.sh").is_file()
    assert (STAGE2_SYSTEM / "opencv" / "install-opencv-cpu.sh").is_file()
    assert (STAGE2_SYSTEM / "opengl" / "setup-opengl-win32.sh").is_file()
    assert (STAGE2_SYSTEM / "set-locale.sh").is_file()


def test_assets_are_canonical_in_stage1_only() -> None:
    # LiteLLM: proxy asset is stage-1 canonical.
    assert (STAGE1_SYSTEM / "litellm" / "proxy.py").is_file()
    assert not (STAGE2_SYSTEM / "litellm" / "proxy.py").exists()

    # OpenGL: JSON/YAML assets are stage-1 canonical.
    assert (STAGE1_SYSTEM / "opengl" / "10_nvidia.json").is_file()
    assert (STAGE1_SYSTEM / "opengl" / "docker-compose-win32.yml").is_file()
    assert not (STAGE2_SYSTEM / "opengl" / "10_nvidia.json").exists()
    assert not (STAGE2_SYSTEM / "opengl" / "docker-compose-win32.yml").exists()


def _extract_stage1_script_relative_path(wrapper_text: str) -> str:
    match = re.search(r"\$PEI_STAGE_DIR_1/system/([^\"]+)", wrapper_text)
    assert match is not None, "Could not extract stage-1 script path from wrapper"
    return match.group(1)


@pytest.mark.parametrize(
    "wrapper_relpath",
    [
        "bun/install-bun.sh",
        "claude-code/install-claude-code.sh",
        "codex-cli/install-codex-cli.sh",
        "litellm/install-litellm.sh",
        "magnum/install-magnum-gl.sh",
        "nodejs/install-nvm.sh",
        "opencv/install-opencv-cpu.sh",
        "opengl/setup-opengl-win32.sh",
        "pixi/install-pixi.bash",
        "pixi/create-env-common.bash",
        "pixi/create-env-ml.bash",
        "conda/install-miniconda.sh",
        "conda/activate-conda-on-login.sh",
        "set-locale.sh",
    ],
)
def test_stage2_wrappers_are_source_safe_and_forward_args(
    tmp_path: Path, wrapper_relpath: str
) -> None:
    wrapper_path = STAGE2_SYSTEM / wrapper_relpath
    assert wrapper_path.is_file()

    wrapper_text = wrapper_path.read_text(encoding="utf-8")
    stage1_rel = _extract_stage1_script_relative_path(wrapper_text)

    pei_stage_dir_1 = tmp_path / "pei-stage-1"
    stage1_script = pei_stage_dir_1 / "system" / stage1_rel
    stage1_script.parent.mkdir(parents=True, exist_ok=True)
    stage1_script.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "printf 'ARG:%s\\n' \"$@\"",
                "return 7 2>/dev/null || exit 7",
                "",
            ]
        ),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["PEI_STAGE_DIR_1"] = str(pei_stage_dir_1)

    arg1 = "--flag=1"
    arg2 = "--message=hello world"

    # Executed mode: should forward args and propagate exit code.
    exec_result = subprocess.run(
        ["bash", str(wrapper_path), arg1, arg2],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert exec_result.returncode == 7, exec_result.stderr
    assert exec_result.stdout.splitlines() == [f"ARG:{arg1}", f"ARG:{arg2}"]

    # Sourced mode: must NOT exit the shell; should return same exit code and still run.
    source_result = subprocess.run(
        [
            "bash",
            "-c",
            'set +e; source "$1" "$2" "$3"; rc=$?; echo "AFTER:${rc}"; exit "${rc}"',
            "--",
            str(wrapper_path),
            arg1,
            arg2,
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert source_result.returncode == 7, source_result.stderr
    assert f"AFTER:{source_result.returncode}" in source_result.stdout
    assert f"ARG:{arg1}" in source_result.stdout
    assert f"ARG:{arg2}" in source_result.stdout


def test_stage2_hooks_can_reference_stage1_system_paths(tmp_path: Path) -> None:
    in_config = oc.OmegaConf.create(
        {
            "stage_1": {"image": {"base": "ubuntu:24.04", "output": "test:stage-1"}},
            "stage_2": {
                "image": {"output": "test:stage-2"},
                "storage": {
                    "app": {"type": "image"},
                    "data": {"type": "image"},
                    "workspace": {"type": "image"},
                },
                "custom": {
                    "on_build": [
                        "stage-1/system/opengl/setup-opengl-win32.sh",
                        "stage-1/system/nodejs/install-nvm.sh --cache-dir /hard/image/data/node-cache",
                    ],
                    "on_first_run": [
                        "stage-1/system/bun/install-bun.sh --user dev",
                        "stage-1/system/codex-cli/install-codex-cli.sh --user dev",
                    ],
                },
            },
        }
    )
    assert isinstance(in_config, oc.DictConfig)

    proc = PeiConfigProcessor.from_config(
        in_config,
        _load_compose_template(),
        project_dir=str(tmp_path),
    )
    _ = proc.process(generate_custom_script_files=False)

