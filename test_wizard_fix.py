#!/usr/bin/env python3
"""Test script to verify the wizard MountError fix."""

import sys
from pathlib import Path

# Add the src directory to the path so we can import pei_docker
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_wizard_compose():
    """Test that the wizard can be composed without MountError."""
    print("Testing wizard compose without MountError...")
    
    try:
        from pei_docker.gui.screens.simple.wizard import SimpleWizardScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        # Create project config
        project_config = ProjectConfig()
        project_config.project_dir = "D:/code/PeiDocker/test-wizard"
        project_config.project_name = "test-wizard"
        
        # Create wizard screen
        wizard = SimpleWizardScreen(project_config)
        
        # This should work without MountError now
        compose_result = wizard.compose()
        assert compose_result is not None
        
        # Verify we can iterate through the result (it should yield widgets, not generators)
        widgets = list(compose_result)
        assert len(widgets) > 0
        
        # All items should be widget instances, not generators
        for widget in widgets:
            assert not hasattr(widget, '__next__'), f"Found generator instead of widget: {type(widget)}"
        
        print("SUCCESS: Wizard composes correctly without MountError")
        return True
        
    except Exception as e:
        print(f"FAILED: Wizard compose test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wizard_step_screen_method():
    """Test that _get_current_step_screen returns proper widgets."""
    print("Testing _get_current_step_screen method...")
    
    try:
        from pei_docker.gui.screens.simple.wizard import SimpleWizardScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        project_config = ProjectConfig()
        project_config.project_dir = "D:/code/PeiDocker/test-wizard"
        project_config.project_name = "test-wizard"
        
        wizard = SimpleWizardScreen(project_config)
        
        # Test the problematic method
        step_content = wizard._get_current_step_screen()
        
        # Should be a generator that yields widgets, not a nested generator
        widgets = list(step_content)
        assert len(widgets) > 0
        
        # Verify no generators in the result
        for widget in widgets:
            assert not hasattr(widget, '__next__'), f"Found nested generator: {type(widget)}"
        
        print("SUCCESS: _get_current_step_screen yields proper widgets")
        return True
        
    except Exception as e:
        print(f"FAILED: Step screen method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wizard_steps_creation():
    """Test that wizard steps are created correctly."""
    print("Testing wizard steps creation...")
    
    try:
        from pei_docker.gui.screens.simple.wizard import SimpleWizardScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        project_config = ProjectConfig()
        wizard = SimpleWizardScreen(project_config)
        
        # Check that steps are created
        assert len(wizard.steps) > 0
        assert wizard.current_step == 0
        assert len(wizard.step_screens) == len(wizard.steps)
        
        # Check that first step has proper attributes
        first_step = wizard.steps[0]
        assert hasattr(first_step, 'name')
        assert hasattr(first_step, 'title')
        assert hasattr(first_step, 'screen_class')
        
        print(f"SUCCESS: Wizard has {len(wizard.steps)} steps configured properly")
        return True
        
    except Exception as e:
        print(f"FAILED: Wizard steps creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all wizard fix tests."""
    print("Running wizard MountError fix tests...\n")
    
    tests = [
        test_wizard_steps_creation,
        test_wizard_step_screen_method,
        test_wizard_compose,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All wizard MountError fix tests passed!")
        print("The wizard should now work without crashing when clicking Next.")
        return 0
    else:
        print("WARNING: Some tests failed. The fix may not be complete.")
        return 1

if __name__ == "__main__":
    sys.exit(main())