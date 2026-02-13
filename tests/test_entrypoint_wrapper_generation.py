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


def test_custom_on_entry_wrapper_generation_and_legacy_cleanup(tmp_path: Path) -> None:
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
                    "on_entry": [
                        (
                            "stage-2/custom/app-entrypoint.sh "
                            "--mode=prod --message='hello world'"
                        )
                    ]
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

    stage2_entry = (
        tmp_path / "installation" / "stage-2" / "generated" / "_custom-on-entry.sh"
    )
    stage1_entry = (
        tmp_path / "installation" / "stage-1" / "generated" / "_custom-on-entry.sh"
    )
    assert stage2_entry.is_file()
    assert stage1_entry.is_file()

    stage2_txt = stage2_entry.read_text(encoding="utf-8")
    assert 'target_script="$PEI_STAGE_DIR_2/../stage-2/custom/app-entrypoint.sh"' in stage2_txt
    assert "exec bash \"$target_script\" --mode=prod '--message=hello world' \"$@\"" in stage2_txt
    assert "Custom on-entry target script not found" in stage2_txt

    # Stage-1 on_entry is unset in this config, so wrapper must be empty.
    assert stage1_entry.read_text(encoding="utf-8") == ""

    assert not (
        tmp_path / "installation" / "stage-2" / "internals" / "custom-entry-path"
    ).exists()
    assert not (
        tmp_path / "installation" / "stage-2" / "internals" / "custom-entry-args"
    ).exists()


def test_generated_hook_wrappers_use_verbose_guard(tmp_path: Path) -> None:
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
                    "on_first_run": ["stage-2/custom/test-script.sh --flag=1"],
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

    first_run_wrapper = (
        tmp_path / "installation" / "stage-2" / "generated" / "_custom-on-first-run.sh"
    )
    wrapper_txt = first_run_wrapper.read_text(encoding="utf-8")

    assert 'if [ "${PEI_ENTRYPOINT_VERBOSE:-0}" = "1" ]; then' in wrapper_txt
    assert 'echo "Executing $DIR/_custom-on-first-run.sh"' in wrapper_txt
    assert 'bash "$DIR/../../stage-2/custom/test-script.sh" --flag=1' in wrapper_txt
