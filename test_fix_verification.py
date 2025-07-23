"""
Test to verify the Screen 2 project creation fix works properly
"""

import asyncio
import os
import tempfile
import shutil
from pathlib import Path

# Import the GUI components
import sys
sys.path.insert(0, '/Users/igame/code/PeiDocker/src')

from pei_docker.gui.models.config import ProjectConfig
from pei_docker.gui.screens.startup import StartupScreen
from pei_docker.gui.app import PeiDockerApp


async def test_fixed_project_creation():
    """Test that the fixed project creation works properly"""
    print("Testing fixed project creation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_dir = os.path.join(temp_dir, "fixed-test-project")
        
        # Create a minimal project config
        config = ProjectConfig()
        config.project_dir = test_project_dir
        config.project_name = "fixed-test-project"
        
        # Create startup screen
        startup_screen = StartupScreen(config, True, "Docker version 20.10.0")
        
        print(f"Test project directory: {test_project_dir}")
        
        # Test the fixed _create_project method
        result = startup_screen._create_project()
        print(f"Fixed _create_project result: {result}")
        
        if result:
            print("SUCCESS: Project creation succeeded with the fix!")
            
            # Verify the project structure was created
            if os.path.exists(test_project_dir):
                print(f"Project directory created: {test_project_dir}")
                
                # List created files
                created_files = []
                for root, dirs, files in os.walk(test_project_dir):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), test_project_dir)
                        created_files.append(rel_path)
                
                print(f"Created files ({len(created_files)} total):")
                for file in sorted(created_files)[:10]:  # Show first 10 files
                    print(f"  - {file}")
                if len(created_files) > 10:
                    print(f"  ... and {len(created_files) - 10} more files")
                
            else:
                print("ERROR: Project directory was not created despite success result")
                return False
        else:
            print("ERROR: Project creation still failed after the fix!")
            return False
            
        return result


async def test_fallback_method():
    """Test that the fallback method works properly"""
    print("\n" + "="*50)
    print("Testing fallback method directly...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_dir = os.path.join(temp_dir, "fallback-test-project")
        
        # Create a minimal project config
        config = ProjectConfig()
        config.project_dir = test_project_dir
        config.project_name = "fallback-test-project"
        
        # Create startup screen
        startup_screen = StartupScreen(config, True, "Docker version 20.10.0")
        
        print(f"Test project directory: {test_project_dir}")
        
        # Test the fallback method directly
        result = startup_screen._create_project_fallback()
        print(f"Fallback _create_project_fallback result: {result}")
        
        if result:
            print("SUCCESS: Fallback method succeeded!")
            
            # Verify files were created
            if os.path.exists(test_project_dir):
                created_files = []
                for root, dirs, files in os.walk(test_project_dir):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), test_project_dir)
                        created_files.append(rel_path)
                
                print(f"Fallback created {len(created_files)} files")
            else:
                print("ERROR: Fallback did not create project directory")
                return False
        else:
            print("ERROR: Fallback method failed!")
            return False
            
        return result


async def test_with_headless_gui():
    """Test the actual GUI interaction with the fix"""
    print("\n" + "="*50)
    print("Testing with headless GUI (the actual Screen 2 issue)...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_dir = os.path.join(temp_dir, "gui-fixed-test-project")
        
        try:
            app = PeiDockerApp(project_dir=test_project_dir)
            
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause(0.5)
                
                print("Attempting to click Continue button...")
                
                # Try to continue from startup screen (this should now work)
                try:
                    await pilot.click("#continue")
                    await pilot.pause(2.0)  # Give more time for the project creation
                    
                    print("Continue button clicked successfully")
                    
                    # Check if we successfully moved to the wizard (screen should have changed)
                    # If we're still on startup screen, it means project creation failed
                    current_screen_type = type(app.screen).__name__
                    print(f"Current screen after Continue: {current_screen_type}")
                    
                    # Check if project directory was created
                    if os.path.exists(test_project_dir):
                        print("SUCCESS: Project directory created via GUI!")
                        
                        # List some files to confirm creation
                        created_files = []
                        for root, dirs, files in os.walk(test_project_dir):
                            for file in files:
                                rel_path = os.path.relpath(os.path.join(root, file), test_project_dir)
                                created_files.append(rel_path)
                        
                        print(f"GUI created {len(created_files)} files")
                        return True
                    else:
                        print("ERROR: GUI did not create project directory")
                        return False
                        
                except Exception as e:
                    print(f"GUI test failed with exception: {e}")
                    return False
                    
        except Exception as e:
            print(f"GUI test setup failed: {e}")
            return False


async def test_path_calculations():
    """Test that the path calculations are now correct"""
    print("\n" + "="*50)
    print("Verifying path calculations are now correct...")
    
    # Test the corrected path calculation
    startup_file = "/Users/igame/code/PeiDocker/src/pei_docker/gui/screens/startup.py"
    this_dir = os.path.dirname(startup_file)
    print(f"startup.py directory: {this_dir}")
    
    # OLD BROKEN: 3 levels up
    old_broken_path = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
    print(f"Old broken path (3 levels up): {old_broken_path}")
    old_project_files = os.path.join(old_broken_path, 'project_files')
    print(f"Old project_files path: {old_project_files}")
    print(f"Old path exists: {os.path.exists(old_project_files)}")
    
    # NEW FIXED: 2 levels up
    new_fixed_path = os.path.dirname(os.path.dirname(this_dir))
    print(f"New fixed path (2 levels up): {new_fixed_path}")
    new_project_files = os.path.join(new_fixed_path, 'project_files')
    print(f"New project_files path: {new_project_files}")
    print(f"New path exists: {os.path.exists(new_project_files)}")
    
    if os.path.exists(new_project_files) and not os.path.exists(old_project_files):
        print("SUCCESS: Path calculation is now correct!")
        return True
    else:
        print("ERROR: Path calculation still has issues")
        return False


async def main():
    """Run all fix verification tests"""
    print("VERIFYING SCREEN 2 PROJECT CREATION FIX")
    print("=" * 60)
    
    # Test 1: Path calculations
    path_result = await test_path_calculations()
    
    # Test 2: Fallback method
    fallback_result = await test_fallback_method()
    
    # Test 3: Fixed project creation
    fixed_result = await test_fixed_project_creation()
    
    # Test 4: Headless GUI test
    gui_result = await test_with_headless_gui()
    
    print("\n" + "="*60)
    print("FIX VERIFICATION SUMMARY:")
    print(f"Path calculations correct: {path_result}")
    print(f"Fallback method works: {fallback_result}")
    print(f"Fixed project creation works: {fixed_result}")
    print(f"GUI test works: {gui_result}")
    
    all_passed = all([path_result, fallback_result, fixed_result, gui_result])
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED! The Screen 2 issue is FIXED!")
        print("The fix includes:")
        print("- Primary: importlib.resources for pip install compatibility")
        print("- Fallback: Corrected path calculation (2 levels up instead of 3)")
        print("- Proper error handling and resource management")
    else:
        print("\n❌ Some tests failed. The fix may need additional work.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)