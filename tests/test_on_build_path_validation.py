"""
Tests for stage-2 on_build path validation.

Build-time scripts (stage_2.custom.on_build) must not reference runtime-only paths:
- /soft/... (symlinks are created at container start)
- /hard/volume/... (mounted volumes are not available during `docker build`)
- $PEI_SOFT_* and $PEI_PATH_SOFT tokens (expand to /soft)
"""

from __future__ import annotations

from pathlib import Path

import omegaconf as oc
import pytest

from pei_docker.config_processor import PeiConfigProcessor


def _load_compose_template() -> oc.DictConfig:
    import pei_docker

    pkg_root = Path(pei_docker.__file__).resolve().parent
    template_path = pkg_root / "templates" / "base-image-gen.yml"
    cfg = oc.OmegaConf.load(str(template_path))
    assert isinstance(cfg, oc.DictConfig)
    return cfg


@pytest.mark.parametrize(
    "bad_entry",
    [
        "stage-2/custom/test-params-echo.bash --cache-dir=/soft/data/cache",
        "stage-2/custom/test-params-echo.bash --install-dir=/hard/volume/app/tool",
        "stage-2/custom/test-params-echo.bash --cache-dir=$PEI_SOFT_DATA/cache",
        "stage-2/custom/test-params-echo.bash --cache-dir=$PEI_PATH_SOFT/data/cache",
    ],
)
def test_stage2_on_build_rejects_runtime_only_paths(tmp_path: Path, bad_entry: str) -> None:
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
                "custom": {"on_build": [bad_entry]},
            },
        }
    )
    assert isinstance(in_config, oc.DictConfig)

    proc = PeiConfigProcessor.from_config(
        in_config,
        _load_compose_template(),
        project_dir=str(tmp_path),
    )

    with pytest.raises(ValueError, match=r"stage_2\.custom\.on_build"):
        _ = proc.process(generate_custom_script_files=False)


def test_stage2_on_build_allows_in_image_paths(tmp_path: Path) -> None:
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
                        "stage-2/custom/test-params-echo.bash --cache-dir=/hard/image/data/cache",
                        "stage-2/custom/test-params-echo.bash --tmp-dir=/tmp/peidocker",
                    ],
                    # Runtime hooks may use /soft.
                    "on_first_run": [
                        "stage-2/custom/test-params-echo.bash --cache-dir=/soft/data/cache"
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
