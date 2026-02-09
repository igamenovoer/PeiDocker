"""
Tests for passthrough marker utilities and environment variable substitution.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from omegaconf import OmegaConf
import omegaconf as oc
import yaml

from pei_docker import pei_utils
from pei_docker.config_processor import PeiConfigProcessor

class TestPassthroughMarkers:
    def test_parse_valid_markers(self):
        """Test parsing of valid {{VAR}} and {{VAR:-default}} markers."""
        # Simple variable
        assert pei_utils.is_passthrough_marker("{{VAR}}")
        assert pei_utils.is_passthrough_marker("{{  VAR  }}")  # Whitespace trimming
        
        # Variable with default
        assert pei_utils.is_passthrough_marker("{{VAR:-default}}")
        assert pei_utils.is_passthrough_marker("{{ VAR :- default }}")
        
        # Variable with empty default
        assert pei_utils.is_passthrough_marker("{{VAR:-}}")

    def test_parse_invalid_markers(self):
        """Test rejection of invalid markers."""
        # Malformed braces
        assert not pei_utils.is_passthrough_marker("{VAR}")
        assert not pei_utils.is_passthrough_marker("{{VAR}")
        
        # Invalid variable names
        with pytest.raises(ValueError, match="Invalid variable name"):
            pei_utils.validate_passthrough_marker("{{1VAR}}")
        
        with pytest.raises(ValueError, match="Invalid variable name"):
            pei_utils.validate_passthrough_marker("{{VAR-NAME}}")
             
        # Nested braces (not allowed in default)
        with pytest.raises(ValueError, match="Default value cannot contain"):
            pei_utils.validate_passthrough_marker("{{VAR:-{{NESTED}}}}")

    def test_rewrite_markers(self):
        """Test rewriting {{...}} to ${...} for Compose output."""
        # Simple rewrite
        assert pei_utils.rewrite_passthrough_markers("Image: {{TAG}}") == "Image: ${TAG}"
        
        # Rewrite with default
        assert pei_utils.rewrite_passthrough_markers("Port: {{PORT:-8080}}") == "Port: ${PORT:-8080}"
        
        # Multiple markers
        assert pei_utils.rewrite_passthrough_markers("{{REGISTRY}}/{{IMAGE}}:{{TAG}}") == "${REGISTRY}/${IMAGE}:${TAG}"
        
        # Mixed content
        assert pei_utils.rewrite_passthrough_markers("prefix-{{VAR}}-suffix") == "prefix-${VAR}-suffix"

    def test_rewrite_rejects_unclosed_marker(self):
        """Unclosed markers must fail with a clear error."""
        with pytest.raises(ValueError, match="Unclosed passthrough marker"):
            pei_utils.rewrite_passthrough_markers("oops {{VAR")

    def test_rewrite_container(self):
        """Test recursive rewrite of containers."""
        data = {
            "image": "{{IMAGE}}",
            "ports": ["{{HOST_PORT}}:80"],
            "labels": {"com.example.ver": "{{VERSION:-latest}}"},
            "literal": "no-change"
        }
        
        expected = {
            "image": "${IMAGE}",
            "ports": ["${HOST_PORT}:80"],
            "labels": {"com.example.ver": "${VERSION:-latest}"},
            "literal": "no-change"
        }
        
        assert pei_utils.rewrite_passthrough_markers_in_container(data) == expected

class TestConfigTimeSubstitutionErrors:
    def test_reject_leftover_substitution(self):
        """Test rejection of ${...} sequences remaining in config."""
        
        # Valid config (no markers)
        cfg = OmegaConf.create({"key": "value"})
        pei_utils.validate_no_leftover_substitution(cfg)
        
        # Invalid config
        cfg_bad = OmegaConf.create({"key": "val-${LEFTOVER}"})
        with pytest.raises(ValueError, match="forbidden leftover config-time substitution"):
            processed = pei_utils.process_config_env_substitution(cfg_bad)
            pei_utils.validate_no_leftover_substitution(processed)
            
        # Invalid nested
        cfg_nested = OmegaConf.create({"section": {"key": "${VAR}"}})
        with pytest.raises(ValueError):
            processed = pei_utils.process_config_env_substitution(cfg_nested)
            pei_utils.validate_no_leftover_substitution(processed)

    def test_reject_nested_default_leftover(self):
        cfg = OmegaConf.create({"key": "${A:-${B}}"})
        processed = pei_utils.process_config_env_substitution(cfg)
        with pytest.raises(ValueError, match="forbidden leftover config-time substitution"):
            pei_utils.validate_no_leftover_substitution(processed)

    def test_mixed_mode_string_allows_passthrough_when_substitution_resolves(self, monkeypatch):
        monkeypatch.setenv("PROJECT_NAME", "app")
        cfg = OmegaConf.create({"key": "${PROJECT_NAME}-{{TAG:-dev}}"})
        processed = pei_utils.process_config_env_substitution(cfg)
        pei_utils.validate_no_leftover_substitution(processed)
        assert processed["key"] == "app-{{TAG:-dev}}"


def _load_compose_template() -> oc.DictConfig:
    import pei_docker

    pkg_root = Path(pei_docker.__file__).resolve().parent
    template_path = pkg_root / "templates" / "base-image-gen.yml"
    cfg = oc.OmegaConf.load(str(template_path))
    assert isinstance(cfg, oc.DictConfig)
    return cfg


def _emit_compose_yaml(out_compose: oc.DictConfig) -> str:
    plain = oc.OmegaConf.to_container(out_compose, resolve=True)
    plain = pei_utils.rewrite_passthrough_markers_in_container(plain)
    return yaml.safe_dump(
        plain,
        default_flow_style=False,
        sort_keys=False,
        indent=2,
    )


def test_compose_emission_rewrites_passthrough_markers(tmp_path: Path) -> None:
    in_config = OmegaConf.create(
        {
            "stage_1": {
                "image": {"base": "ubuntu:24.04", "output": "test:stage-1"},
            },
            "stage_2": {
                "image": {"output": "test:{{TAG:-dev}}"},
                "storage": {
                    "app": {"type": "image"},
                    "data": {"type": "image"},
                    "workspace": {"type": "image"},
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
    out_compose = proc.process(remove_extra=True, generate_custom_script_files=False)
    yml = _emit_compose_yaml(out_compose)

    assert "${TAG:-dev}" in yml
    assert "{{TAG:-dev}}" not in yml


def test_port_strings_concatenate_and_rewrite_passthrough(tmp_path: Path) -> None:
    in_config = OmegaConf.create(
        {
            "stage_1": {
                "image": {"base": "ubuntu:24.04", "output": "test:stage-1"},
                "ports": ["8000:80"],
                "ssh": {"enable": True, "port": 22, "host_port": 2222},
            },
            "stage_2": {
                "image": {"output": "test:stage-2"},
                "ports": ["{{WEB_PORT:-8080}}:80"],
                "storage": {
                    "app": {"type": "image"},
                    "data": {"type": "image"},
                    "workspace": {"type": "image"},
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
    out_compose = proc.process(remove_extra=True, generate_custom_script_files=False)
    yml = _emit_compose_yaml(out_compose)

    parsed = yaml.safe_load(yml)
    ports = parsed["services"]["stage-2"]["ports"]
    assert ports == ["8000:80", "${WEB_PORT:-8080}:80", "2222:22"]


def test_reject_passthrough_markers_in_custom_script_entries(tmp_path: Path) -> None:
    in_config = OmegaConf.create(
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
                    "on_first_run": ["stage-2/custom/setup.sh --tag={{TAG:-dev}}"],
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
    with pytest.raises(ValueError, match="not supported in generated scripts"):
        _ = proc.process(remove_extra=True, generate_custom_script_files=False)


def test_reject_passthrough_markers_when_env_baking_enabled(tmp_path: Path) -> None:
    template = _load_compose_template()
    oc.OmegaConf.update(
        template,
        "services.stage-1.build.args.PEI_BAKE_ENV_STAGE_1",
        True,
    )

    in_config = OmegaConf.create(
        {
            "stage_1": {
                "image": {"base": "ubuntu:24.04", "output": "test:stage-1"},
                "environment": {"BAKED": "{{SHOULD_FAIL}}"},
            },
        }
    )
    assert isinstance(in_config, oc.DictConfig)

    proc = PeiConfigProcessor.from_config(
        in_config,
        template,
        project_dir=str(tmp_path),
    )
    with pytest.raises(ValueError, match="cannot be baked"):
        _ = proc.process(remove_extra=True, generate_custom_script_files=False)
