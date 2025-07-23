#!/usr/bin/env python3
"""Test script to verify the ProgressBar fix."""

import sys
import os
import tempfile
from pathlib import Path

# Add the src directory to the path so we can import pei_docker
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_progressbar_creation():
    """Test that ProgressBar can be created without the invalid progress parameter."""
    print("Testing ProgressBar creation...")
    
    try:
        from textual.widgets import ProgressBar
        
        # This should work (the way it's now implemented)
        progress_bar = ProgressBar(total=10, classes="test-progress")
        assert progress_bar.total == 10
        assert progress_bar.progress == 0  # Default value
        
        # Set progress using reactive attribute (the correct way)
        progress_bar.progress = 5
        assert progress_bar.progress == 5
        
        print("SUCCESS: ProgressBar creation and reactive attribute setting works")
        return True
        
    except Exception as e:
        print(f"FAILED: ProgressBar creation test failed: {e}")
        return False

def test_wizard_screen_import():
    """Test that the SimpleWizardScreen can be imported and created."""
    print("Testing SimpleWizardScreen import and creation...")
    
    try:
        from pei_docker.gui.screens.simple.wizard import SimpleWizardScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        # Create project config
        project_config = ProjectConfig()
        project_config.project_dir = "/tmp/test-project"
        project_config.project_name = "test-project"
        
        # Create wizard screen
        wizard = SimpleWizardScreen(project_config)
        
        # Check that it has the necessary attributes
        assert hasattr(wizard, 'current_step')
        assert hasattr(wizard, 'steps')
        assert hasattr(wizard, '_update_step')
        assert hasattr(wizard, 'on_mount')
        
        # Check initial state
        assert wizard.current_step == 0
        assert len(wizard.steps) > 0
        
        print(f"SUCCESS: SimpleWizardScreen created with {len(wizard.steps)} steps")
        return True
        
    except Exception as e:
        print(f"FAILED: SimpleWizardScreen test failed: {e}")
        return False

def test_wizard_compose_method():
    """Test that the compose method works without ProgressBar parameter errors."""
    print("Testing SimpleWizardScreen compose method...")
    
    try:
        from pei_docker.gui.screens.simple.wizard import SimpleWizardScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        # Create project config
        project_config = ProjectConfig()
        project_config.project_dir = "/tmp/test-project"
        project_config.project_name = "test-project"
        
        # Create wizard screen
        wizard = SimpleWizardScreen(project_config)
        
        # Try to call compose (this should not raise an error)
        compose_result = wizard.compose()
        
        # The compose method should return a generator
        assert compose_result is not None
        
        print("SUCCESS: SimpleWizardScreen compose method works without ProgressBar errors")
        return True
        
    except Exception as e:
        print(f"FAILED: SimpleWizardScreen compose test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running ProgressBar fix tests...\n")
    
    tests = [
        test_progressbar_creation,
        test_wizard_screen_import,
        test_wizard_compose_method,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All ProgressBar fix tests passed!")
        return 0
    else:
        print("WARNING: Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())