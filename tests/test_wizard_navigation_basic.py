#!/usr/bin/env python3
"""
Basic automated test suite for wizard navigation (TC-NAV-001)

This simplified test validates that the core navigation testing framework 
works with pytest-asyncio and the Textual testing infrastructure.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the path so we can import pei_docker
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pei_docker.gui.app import PeiDockerApp
from pei_docker.gui.screens.simple.wizard import SimpleWizardScreen
from pei_docker.gui.models.config import ProjectConfig


class TestWizardNavigationBasic:
    """Basic navigation tests to verify pytest-asyncio setup works."""
    
    @pytest.fixture
    def project_config(self):
        """Simple project config fixture."""
        config = ProjectConfig()
        config.project_dir = "D:/code/PeiDocker/test-nav-basic"
        config.project_name = "test-navigation-basic"
        return config
    
    @pytest.fixture
    def wizard(self, project_config):
        """Wizard fixture with minimal config."""
        return SimpleWizardScreen(project_config)
    
    def test_wizard_creation(self, wizard, project_config):
        """Test that wizard can be created successfully."""
        assert wizard is not None
        assert wizard.project_config == project_config
        assert hasattr(wizard, 'steps')
        assert hasattr(wizard, 'current_step')
        assert wizard.current_step == 0
    
    def test_wizard_has_expected_steps(self, wizard):
        """Test that wizard has the expected number and names of steps."""
        expected_step_names = [
            'project_info', 'ssh_config', 'proxy_config', 'apt_config', 
            'port_mapping', 'env_vars', 'device_config', 'mounts',
            'entry_point', 'custom_scripts', 'summary'
        ]
        
        assert len(wizard.steps) == len(expected_step_names)
        
        actual_step_names = [step.name for step in wizard.steps]
        assert actual_step_names == expected_step_names
    
    def test_wizard_step_structure(self, wizard):
        """Test that each wizard step has the required attributes."""
        for i, step in enumerate(wizard.steps):
            assert hasattr(step, 'name'), f"Step {i} missing 'name' attribute"
            assert hasattr(step, 'title'), f"Step {i} missing 'title' attribute"
            assert hasattr(step, 'screen_class'), f"Step {i} missing 'screen_class' attribute"
            
            assert isinstance(step.name, str), f"Step {i} name is not string"
            assert isinstance(step.title, str), f"Step {i} title is not string"
            assert callable(step.screen_class), f"Step {i} screen_class is not callable"
    
    def test_wizard_navigation_methods(self, wizard):
        """Test that wizard has the required navigation methods."""
        assert hasattr(wizard, 'action_next'), "Wizard missing action_next method"
        assert hasattr(wizard, 'action_back'), "Wizard missing action_back method"
        assert hasattr(wizard, '_validate_current_step'), "Wizard missing _validate_current_step method"
        assert hasattr(wizard, '_update_step'), "Wizard missing _update_step method"
        
        # Test that methods are callable
        assert callable(wizard.action_next)
        assert callable(wizard.action_back)
        assert callable(wizard._validate_current_step)
        assert callable(wizard._update_step)
    
    async def test_wizard_compose_structure(self, wizard):
        """Test that wizard compose method works and returns expected structure."""
        # This test verifies the fix for the MountError
        compose_result = wizard.compose()
        assert compose_result is not None
        
        # Should be able to iterate through the result without errors
        widgets = list(compose_result)
        assert len(widgets) > 0
        
        # Verify no generators are in the result (this was the bug we fixed)
        for i, widget in enumerate(widgets):
            assert not hasattr(widget, '__next__'), f"Widget {i} is a generator, not a widget"
    
    async def test_wizard_step_validation(self, wizard):
        """Test that step validation method works."""
        # Should not raise an exception
        validation_result = wizard._validate_current_step()
        assert isinstance(validation_result, bool), "Validation should return boolean"
    
    def test_wizard_current_step_management(self, wizard):
        """Test that current step can be managed."""
        # Should start at step 0
        assert wizard.current_step == 0
        
        # Should be able to change current step
        wizard.current_step = 1
        assert wizard.current_step == 1
        
        # Should be able to reset
        wizard.current_step = 0
        assert wizard.current_step == 0
    
    async def test_app_creation_and_wizard_integration(self, project_config):
        """Test that the main app can be created and integrate with wizard."""
        app = PeiDockerApp()
        assert app is not None
        
        # App should have the expected attributes
        assert hasattr(app, 'project_config')
        
        # Should be able to create a wizard with the app's project config
        app.project_config = project_config
        wizard = SimpleWizardScreen(app.project_config)
        assert wizard is not None
        assert wizard.project_config == project_config


class TestPytestAsyncioSetup:
    """Tests to verify pytest-asyncio configuration works properly."""
    
    async def test_async_function_works(self):
        """Test that async functions work with pytest-asyncio."""
        import asyncio
        
        # Simple async operation
        await asyncio.sleep(0.001)
        
        # Should be able to create and await coroutines
        async def sample_coroutine():
            return "async_result"
        
        result = await sample_coroutine()
        assert result == "async_result"
    
    async def test_textual_app_run_test_context(self):
        """Test that Textual app.run_test() context works."""
        app = PeiDockerApp()
        
        # This is the core Textual testing pattern
        async with app.run_test() as pilot:
            assert pilot is not None
            assert hasattr(pilot, 'click')
            assert hasattr(pilot, 'pause')
            
            # Basic pilot operations should work
            await pilot.pause()


def test_sync_test_also_works():
    """Test that synchronous tests still work alongside async ones."""
    assert True
    
    # Should be able to import our modules
    from pei_docker.gui.app import PeiDockerApp
    app = PeiDockerApp()
    assert app is not None


if __name__ == "__main__":
    # For manual testing during development
    pytest.main([__file__, "-v"])