#!/usr/bin/env python3
"""Test script to verify the scrolling viewport fix."""

import sys
import os
import tempfile
from pathlib import Path

# Add the src directory to the path so we can import pei_docker
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_vertical_scroll_import():
    """Test that VerticalScroll can be imported properly."""
    print("Testing VerticalScroll import...")
    
    try:
        from textual.containers import VerticalScroll
        
        # Test that we can create an instance
        scroll_container = VerticalScroll()
        assert scroll_container is not None
        
        print("SUCCESS: VerticalScroll imported and instantiated correctly")
        return True
        
    except Exception as e:
        print(f"FAILED: VerticalScroll import test failed: {e}")
        return False

def test_mode_selection_with_scroll():
    """Test that ModeSelectionScreen uses VerticalScroll properly."""
    print("Testing ModeSelectionScreen with VerticalScroll...")
    
    try:
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        # Create project config
        project_config = ProjectConfig()
        project_config.project_dir = "D:/code/PeiDocker/test-scrolling"
        project_config.project_name = "test-scrolling"
        
        # Create mode selection screen
        mode_screen = ModeSelectionScreen(project_config)
        
        # Test that compose method works with VerticalScroll
        compose_result = mode_screen.compose()
        assert compose_result is not None
        
        # Check that the screen has the necessary CSS for scrolling
        css = mode_screen.DEFAULT_CSS
        assert "VerticalScroll" in css
        assert "overflow: auto" in css
        
        print("SUCCESS: ModeSelectionScreen properly uses VerticalScroll")
        return True
        
    except Exception as e:
        print(f"FAILED: ModeSelectionScreen scrolling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_screen_css_properties():
    """Test that the CSS properties for scrolling are properly defined."""
    print("Testing CSS properties for scrolling...")
    
    try:
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        project_config = ProjectConfig()
        mode_screen = ModeSelectionScreen(project_config)
        
        css = mode_screen.DEFAULT_CSS
        
        # Check that essential CSS properties are present
        required_css_elements = [
            "ModeSelectionScreen",
            "VerticalScroll", 
            "overflow: auto",
            "width: 100%",
            "height: 100%"
        ]
        
        for css_element in required_css_elements:
            if css_element not in css:
                print(f"FAILED: Missing CSS element: {css_element}")
                return False
        
        print("SUCCESS: All required CSS properties for scrolling are present")
        return True
        
    except Exception as e:
        print(f"FAILED: CSS properties test failed: {e}")
        return False

def test_screen_functionality_preserved():
    """Test that existing screen functionality is preserved after scrolling changes."""
    print("Testing that existing functionality is preserved...")
    
    try:
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        project_config = ProjectConfig()
        mode_screen = ModeSelectionScreen(project_config)
        
        # Check that key methods still exist
        required_methods = [
            '_validate_project_dir',
            '_browse_directory_async',
            'on_input_changed',
            'action_back',
            'action_continue',
            '_create_project'
        ]
        
        for method in required_methods:
            if not hasattr(mode_screen, method):
                print(f"FAILED: Missing method: {method}")
                return False
        
        # Check that key attributes still exist
        required_attributes = [
            'project_config',
            'selected_mode',
            'project_dir_valid'
        ]
        
        for attr in required_attributes:
            if not hasattr(mode_screen, attr):
                print(f"FAILED: Missing attribute: {attr}")
                return False
        
        print("SUCCESS: All existing functionality is preserved")
        return True
        
    except Exception as e:
        print(f"FAILED: Functionality preservation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running scrolling viewport fix tests...\n")
    
    tests = [
        test_vertical_scroll_import,
        test_mode_selection_with_scroll,
        test_screen_css_properties,
        test_screen_functionality_preserved,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All scrolling viewport fix tests passed!")
        print("The content should now be scrollable when it exceeds the terminal height.")
        return 0
    else:
        print("WARNING: Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())