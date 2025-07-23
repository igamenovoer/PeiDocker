"""
Debug test for Screen 2 project creation failure issue
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


async def test_project_creation_path_issue():
    """Test to reproduce the project creation path issue"""
    print("Testing project creation path calculation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_dir = os.path.join(temp_dir, "test-project")
        
        # Create a minimal project config
        config = ProjectConfig()
        config.project_dir = test_project_dir
        config.project_name = "test-project"
        
        # Create startup screen
        startup_screen = StartupScreen(config, True, "Docker version 20.10.0")
        
        print(f"Test project directory: {test_project_dir}")
        
        # Manually test the path calculation logic
        this_dir = os.path.dirname(os.path.realpath("/Users/igame/code/PeiDocker/src/pei_docker/gui/screens/startup.py"))
        print(f"this_dir: {this_dir}")
        
        # Current broken logic: 3 levels up
        pei_docker_dir_broken = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
        print(f"pei_docker_dir (broken logic): {pei_docker_dir_broken}")
        
        project_template_dir_broken = os.path.join(pei_docker_dir_broken, 'project_files')
        print(f"project_template_dir (broken): {project_template_dir_broken}")
        print(f"Broken path exists: {os.path.exists(project_template_dir_broken)}")
        
        # Correct logic: 2 levels up to get to 'pei_docker' package root
        pei_docker_dir_correct = os.path.dirname(os.path.dirname(this_dir))
        print(f"pei_docker_dir (correct logic): {pei_docker_dir_correct}")
        
        project_template_dir_correct = os.path.join(pei_docker_dir_correct, 'project_files')
        print(f"project_template_dir (correct): {project_template_dir_correct}")
        print(f"Correct path exists: {os.path.exists(project_template_dir_correct)}")
        
        # Test the actual _create_project method
        result = startup_screen._create_project()
        print(f"_create_project result: {result}")
        
        if not result:
            print("ERROR: Project creation failed as expected due to path issue!")
        else:
            print("Project creation succeeded")
            
        return result


async def test_pip_install_simulation():
    """Simulate how paths would work after pip install"""
    print("\n" + "="*50)
    print("SIMULATING PIP INSTALL SCENARIO")
    print("="*50)
    
    # Simulate typical pip install path structure
    # After pip install, files would be in something like:
    # /usr/local/lib/python3.x/site-packages/pei_docker/gui/screens/startup.py
    
    simulated_startup_path = "/usr/local/lib/python3.11/site-packages/pei_docker/gui/screens/startup.py"
    print(f"Simulated pip install path: {simulated_startup_path}")
    
    this_dir = os.path.dirname(simulated_startup_path)
    print(f"this_dir: {this_dir}")
    
    # Current broken logic: 3 levels up
    pei_docker_dir_broken = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
    print(f"pei_docker_dir (broken logic): {pei_docker_dir_broken}")
    print(f"This would look for project_files in: {os.path.join(pei_docker_dir_broken, 'project_files')}")
    
    # Correct logic: 2 levels up to get to 'pei_docker' package root  
    pei_docker_dir_correct = os.path.dirname(os.path.dirname(this_dir))
    print(f"pei_docker_dir (correct logic): {pei_docker_dir_correct}")
    print(f"This would look for project_files in: {os.path.join(pei_docker_dir_correct, 'project_files')}")


async def test_with_headless_gui():
    """Test the actual GUI interaction that triggers the error"""
    print("\n" + "="*50)
    print("TESTING WITH HEADLESS GUI")
    print("="*50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_dir = os.path.join(temp_dir, "gui-test-project")
        
        try:
            app = PeiDockerApp(project_dir=test_project_dir)
            
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause(0.5)
                
                # Try to continue from startup screen (this should trigger the error)
                continue_button = app.query("#continue")
                if continue_button:
                    await pilot.click("#continue")
                    await pilot.pause(1.0)
                    
                    # Check if we got the error notification
                    # The error message should be "Failed to create project structure"
                    print("GUI test completed - check for error notification")
                else:
                    print("Could not find continue button")
                    
        except Exception as e:
            print(f"GUI test failed with exception: {e}")


async def main():
    """Run all debug tests"""
    print("DEBUGGING SCREEN 2 PROJECT CREATION ISSUE")
    print("=" * 60)
    
    # Test 1: Direct path calculation test
    result1 = await test_project_creation_path_issue()
    
    # Test 2: Pip install simulation
    await test_pip_install_simulation()
    
    # Test 3: Headless GUI test
    await test_with_headless_gui()
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"Direct project creation test result: {result1}")
    print("The issue is in the path calculation in startup.py line 216:")
    print("pei_docker_dir = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))")
    print("This goes up 3 levels instead of 2 levels to reach the pei_docker package root")
    print("This will be completely broken after pip install!")


if __name__ == "__main__":
    asyncio.run(main())