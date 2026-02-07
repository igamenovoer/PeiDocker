"""
Tests for custom script wrapper argument passthrough.

Goal: preserve user-provided argument text so shell expansion (e.g. `$HOME`) and
explicit quoting (e.g. `--msg="hello world"`) work at execution time.
"""

from __future__ import annotations

from pathlib import Path

import omegaconf as oc

from pei_docker.config_processor import PeiConfigProcessor


def _load_compose_template() -> oc.DictConfig:
    import pei_docker

    pkg_root = Path(pei_docker.__file__).resolve().parent
    template_path = pkg_root / "templates" / "base-image-gen.yml"
    cfg = oc.OmegaConf.load(str(template_path))
    assert isinstance(cfg, oc.DictConfig)
    return cfg


def test_custom_script_wrappers_preserve_env_vars_and_quotes(tmp_path: Path) -> None:
    in_config = oc.OmegaConf.create(
        {
            "stage_1": {
                "image": {"base": "ubuntu:24.04", "output": "test:stage-1"},
            },
            "stage_2": {
                "image": {"output": "test:stage-2"},
                "storage": {
                    "app": {"type": "image"},
                    "data": {"type": "image"},
                    "workspace": {"type": "image"},
                },
                "custom": {
                    "on_build": [
                        (
                            "stage-2/custom/test-params-echo.bash "
                            '--message="hello world" --cache-dir=$HOME/cache --flag=value'
                        )
                    ],
                    "on_first_run": [
                        (
                            "stage-2/custom/test-params-echo.bash "
                            '--message="hello world" --cache-dir=$PEI_SOFT_DATA/cache'
                        )
                    ],
                    "on_user_login": [
                        (
                            "stage-2/custom/test-params-echo.bash "
                            '--message="hello world" --path=$PEI_SOFT_DATA/cache'
                        )
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
    _ = proc.process(remove_extra=True, generate_custom_script_files=True)

    build_sh = tmp_path / "installation" / "stage-2" / "generated" / "_custom-on-build.sh"
    first_run_sh = (
        tmp_path / "installation" / "stage-2" / "generated" / "_custom-on-first-run.sh"
    )
    login_sh = tmp_path / "installation" / "stage-2" / "generated" / "_custom-on-user-login.sh"

    build_txt = build_sh.read_text(encoding="utf-8")
    first_run_txt = first_run_sh.read_text(encoding="utf-8")
    login_txt = login_sh.read_text(encoding="utf-8")

    # on_build: preserve $HOME expansion and explicit quoting.
    assert '--message="hello world"' in build_txt
    assert "--cache-dir=$HOME/cache" in build_txt
    assert "--flag=value" in build_txt
    assert "'$HOME/cache'" not in build_txt

    # runtime hooks: preserve PEI_SOFT_* tokens (expanded at runtime).
    assert "--cache-dir=$PEI_SOFT_DATA/cache" in first_run_txt
    assert "'$PEI_SOFT_DATA/cache'" not in first_run_txt

    # on_user_login uses `source` and must preserve args the same way.
    assert 'source "$DIR/../../stage-2/custom/test-params-echo.bash"' in login_txt
    assert '--message="hello world"' in login_txt
    assert "--path=$PEI_SOFT_DATA/cache" in login_txt
    assert "'$PEI_SOFT_DATA/cache'" not in login_txt
