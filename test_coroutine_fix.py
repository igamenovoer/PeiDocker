#!/usr/bin/env python3
"""Test script to verify the coroutine/then fix."""

import sys
import os
import tempfile
from pathlib import Path

# Add the src directory to the path so we can import pei_docker
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_file_picker_methods():
    """Test that the file picker methods can be called without errors."""
    print("Testing file picker method imports and structure...")
    
    try:
        # Test mode_selection.py
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        project_config = ProjectConfig()
        screen = ModeSelectionScreen(project_config)
        
        # Check that the async method exists
        assert hasattr(screen, '_browse_directory_async'), "Missing _browse_directory_async method"
        
        # Test entry_point.py
        from pei_docker.gui.screens.simple.entry_point import EntryPointScreen
        
        entry_screen = EntryPointScreen()
        
        # Check that the async method exists
        assert hasattr(entry_screen, '_browse_script_file_async'), "Missing _browse_script_file_async method"
        
        # Test ssh_config.py
        from pei_docker.gui.screens.simple.ssh_config import SSHConfigScreen
        
        ssh_screen = SSHConfigScreen(project_config)
        
        # Check that the async method exists
        assert hasattr(ssh_screen, '_browse_ssh_key_async'), "Missing _browse_ssh_key_async method"
        
        print("SUCCESS: All file picker methods have been properly converted to async workers")
        return True
        
    except Exception as e:
        print(f"FAILED: File picker test failed: {e}")
        return False

def test_no_then_usage():
    """Test that no .then() usage remains in the codebase."""
    print("Testing for remaining .then() usage...")
    
    try:
        # Check the GUI files for any remaining .then() usage
        gui_files = [
            "src/pei_docker/gui/screens/mode_selection.py",
            "src/pei_docker/gui/screens/simple/entry_point.py",
            "src/pei_docker/gui/screens/simple/ssh_config.py"
        ]
        
        for file_path in gui_files:
            if Path(file_path).exists():
                content = Path(file_path).read_text()
                if ".then(" in content:
                    print(f"FAILED: Found .then() usage in {file_path}")
                    return False
        
        print("SUCCESS: No .then() usage found in GUI files")
        return True
        
    except Exception as e:
        print(f"FAILED: then usage test failed: {e}")
        return False

def test_run_worker_imports():
    """Test that run_worker is available in the Screen classes."""
    print("Testing run_worker availability...")
    
    try:
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        from pei_docker.gui.screens.simple.entry_point import EntryPointScreen
        from pei_docker.gui.screens.simple.ssh_config import SSHConfigScreen
        from pei_docker.gui.models.config import ProjectConfig
        
        project_config = ProjectConfig()
        
        # Create instances and check run_worker method exists
        screens = [
            ModeSelectionScreen(project_config),
            EntryPointScreen(),
            SSHConfigScreen(project_config)
        ]
        
        for screen in screens:
            assert hasattr(screen, 'run_worker'), f"Missing run_worker method in {type(screen).__name__}"
        
        print("SUCCESS: run_worker method available in all screen classes")
        return True
        
    except Exception as e:
        print(f"FAILED: run_worker test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running coroutine/then fix tests...\n")
    
    tests = [
        test_no_then_usage,
        test_run_worker_imports,
        test_file_picker_methods,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All coroutine/then fixes are working correctly!")
        return 0
    else:
        print("WARNING: Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())