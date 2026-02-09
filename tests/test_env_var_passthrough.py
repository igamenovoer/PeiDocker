"""
Tests for passthrough marker utilities and environment variable substitution.
"""
import pytest
from omegaconf import OmegaConf

from pei_docker import pei_utils

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
             pei_utils.validate_passthrough_marker("{{VAR-NAME}}") # hyphens not allowed in shell var names usually, strict check?
             
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
        with pytest.raises(ValueError, match="Config value contains forbidden"):
            pei_utils.validate_no_leftover_substitution(cfg_bad)
            
        # Invalid nested
        cfg_nested = OmegaConf.create({"section": {"key": "${VAR}"}})
        with pytest.raises(ValueError):
            pei_utils.validate_no_leftover_substitution(cfg_nested)

