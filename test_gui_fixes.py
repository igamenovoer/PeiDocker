#!/usr/bin/env python3
"""Test script to verify GUI bug fixes."""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the src directory to the path so we can import pei_docker
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_project_creation():
    """Test the project creation logic."""
    print("Testing project creation logic...")
    
    # Import the project creation code
    from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
    from pei_docker.gui.models.config import ProjectConfig
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_dir = Path(temp_dir) / "test-project"
        
        # Create project config
        project_config = ProjectConfig()
        project_config.project_dir = str(test_project_dir)
        project_config.project_name = "test-project"
        
        # Create screen instance
        screen = ModeSelectionScreen(project_config)
        
        # Test the _create_project method
        try:
            success = screen._create_project()
            if success:
                print("SUCCESS: Project creation successful")
                
                # Check if required files were created
                required_files = [
                    "stage-1.Dockerfile",
                    "stage-2.Dockerfile", 
                    "user_config.yml",
                    "compose-template.yml"
                ]
                
                missing_files = []
                for file in required_files:
                    if not (test_project_dir / file).exists():
                        missing_files.append(file)
                
                if missing_files:
                    print(f"WARNING: Missing files: {missing_files}")
                else:
                    print("SUCCESS: All required files created")
                    
                return True
            else:
                print("FAILED: Project creation failed")
                return False
                
        except Exception as e:
            print(f"FAILED: Project creation failed with exception: {e}")
            return False

def test_file_picker_imports():
    """Test that textual-fspicker imports work correctly."""
    print("Testing textual-fspicker imports...")
    
    try:
        from textual_fspicker import SelectDirectory, FileOpen
        
        # Test that we can create instances without parameters (as per our fix)
        select_dir = SelectDirectory()
        file_open = FileOpen()
        
        print("SUCCESS: textual-fspicker imports and instantiation successful")
        return True
        
    except Exception as e:
        print(f"FAILED: textual-fspicker test failed: {e}")
        return False

def test_gui_app_imports():
    """Test that all GUI components can be imported."""
    print("Testing GUI component imports...")
    
    try:
        from pei_docker.gui.app import PeiDockerApp
        from pei_docker.gui.screens.startup import StartupScreen
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        from pei_docker.gui.widgets.inputs import DockerImageInput, PortNumberInput
        from pei_docker.gui.widgets.dialogs import ErrorDialog
        
        print("SUCCESS: All GUI components imported successfully")
        return True
        
    except Exception as e:
        print(f"FAILED: GUI import test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running GUI bug fix tests...\n")
    
    tests = [
        test_gui_app_imports,
        test_file_picker_imports,
        test_project_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All tests passed! Bug fixes appear to be working.")
        return 0
    else:
        print("WARNING: Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())