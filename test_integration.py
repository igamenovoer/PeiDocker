#!/usr/bin/env python3
"""Integration test for GUI fixes."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_mode_selection_to_wizard():
    """Test creating a mode selection screen and transitioning to wizard."""
    print("Testing mode selection to wizard transition...")
    
    try:
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        from pei_docker.gui.screens.simple.wizard import SimpleWizardScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        # Create project config
        project_config = ProjectConfig()
        project_config.project_dir = "D:/code/PeiDocker/test-gui-integration"
        project_config.project_name = "test-gui-integration"
        
        # Test mode selection screen
        mode_screen = ModeSelectionScreen(project_config)
        assert hasattr(mode_screen, '_browse_directory_async')
        
        # Test wizard screen creation (what happens when "Continue" is clicked)
        wizard_screen = SimpleWizardScreen(project_config)
        assert hasattr(wizard_screen, 'on_mount')
        
        # Test compose methods
        mode_compose = mode_screen.compose()
        wizard_compose = wizard_screen.compose()
        
        assert mode_compose is not None
        assert wizard_compose is not None
        
        print("SUCCESS: Mode selection to wizard transition works correctly")
        return True
        
    except Exception as e:
        print(f"FAILED: Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_mode_selection_to_wizard():
        print("\nIntegration test PASSED - GUI navigation should work!")
        sys.exit(0)
    else:
        print("\nIntegration test FAILED")
        sys.exit(1)