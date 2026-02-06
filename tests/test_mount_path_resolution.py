"""
Tests for mount/storage path resolution rules.

These tests cover the bug where mount keys colliding with storage keywords
(`app`, `data`, `workspace`) could override mount `dst_path` during compose
generation.
"""

from __future__ import annotations

from pathlib import Path
import logging

import omegaconf as oc
import pytest

from pei_docker.config_processor import PeiConfigProcessor
from pei_docker.user_config.stage import StageConfig
from pei_docker.user_config.storage import StorageOption
from pei_docker.pei_utils import load_yaml_file_with_duplicate_key_check


def _load_compose_template() -> oc.DictConfig:
    import pei_docker

    pkg_root = Path(pei_docker.__file__).resolve().parent
    template_path = pkg_root / "templates" / "base-image-gen.yml"
    cfg = oc.OmegaConf.load(str(template_path))
    assert isinstance(cfg, oc.DictConfig)
    return cfg


def test_mount_requires_absolute_dst_path() -> None:
    with pytest.raises(ValueError, match=r"absolute container path"):
        _ = StageConfig(
            mount={"m": StorageOption(type="auto-volume", dst_path="relative/path")}
        )


def test_storage_keys_are_fixed() -> None:
    with pytest.raises(ValueError, match=r"Invalid storage key"):
        _ = StageConfig(storage={"custom": StorageOption(type="auto-volume")})


def test_yaml_duplicate_keys_are_rejected(tmp_path: Path) -> None:
    p = tmp_path / "user_config.yml"
    p.write_text(
        "\n".join(
            [
                "stage_1:",
                "  image:",
                "    base: ubuntu:24.04",
                "    output: test:stage-1",
                "stage_2:",
                "  image:",
                "    output: test:stage-2",
                "  mount:",
                "    data:",
                "      type: auto-volume",
                "      dst_path: /a",
                "    data:",
                "      type: auto-volume",
                "      dst_path: /b",
                "",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"Duplicate key"):
        _ = load_yaml_file_with_duplicate_key_check(str(p))


def test_mount_name_can_match_storage_keyword(tmp_path: Path) -> None:
    in_config = oc.OmegaConf.create(
        {
            "stage_1": {
                "image": {"base": "ubuntu:24.04", "output": "test:stage-1"},
            },
            "stage_2": {
                "image": {"output": "test:stage-2"},
                "storage": {
                    "app": {"type": "image"},
                    "data": {"type": "auto-volume"},
                    "workspace": {"type": "image"},
                },
                "mount": {
                    "data": {"type": "auto-volume", "dst_path": "/custom/data"},
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
    out_compose = proc.process(generate_custom_script_files=False)

    stage2_vols = oc.OmegaConf.select(out_compose, "services.stage-2.volumes")
    assert stage2_vols is not None
    assert "data:/hard/volume/data" in stage2_vols
    assert "mount_data:/custom/data" in stage2_vols

    volumes_section = oc.OmegaConf.select(out_compose, "volumes")
    assert volumes_section is not None
    assert "data" in volumes_section
    assert "mount_data" in volumes_section


def test_duplicate_container_destinations_warn(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)

    in_config = oc.OmegaConf.create(
        {
            "stage_1": {
                "image": {"base": "ubuntu:24.04", "output": "test:stage-1"},
            },
            "stage_2": {
                "image": {"output": "test:stage-2"},
                "storage": {
                    "app": {"type": "image"},
                    "data": {"type": "auto-volume"},
                    "workspace": {"type": "image"},
                },
                "mount": {
                    "other": {
                        "type": "host",
                        "host_path": "/host/data",
                        "dst_path": "/hard/volume/data",
                    },
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

    assert "Multiple volume mappings target the same container path" in caplog.text
