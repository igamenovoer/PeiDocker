"""
Task 2 Implementation: Automated GUI User Input Simulation Test

This test script implements Task 2 requirements:
- Create UUID-based run directory for logs and screenshots
- Simulate user input on the GUI screens  
- Navigate to screen 1 and input specific values
- Take screenshots after each interaction
- Log all actions during test execution

Requirements:
- Input to project directory field: './tmp/autotest/build-autotest'
- Input to project name field: 'autotest-project'
- Click continue button
- Capture screenshots throughout the process
"""

import asyncio
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest


class TestGUIUserInputTask2:
    """Test class for Task 2: GUI user input simulation with logging."""
    
    def setup_method(self):
        """Initialize test with UUID-based run directory."""
        self.run_id = str(uuid.uuid4())
        self.run_log_dir = Path(f"tmp/autotest/run-{self.run_id}")
        self.logs_dir = self.run_log_dir / "logs"
        self.screenshots_dir = self.run_log_dir / "screenshots"
        
    @pytest.fixture(autouse=True)
    def setup_test_environment(self) -> None:
        """Setup test environment with UUID-based directories and logging."""
        self._setup_environment()
    
    def _setup_environment(self) -> None:
        """Internal setup method that can be called directly."""
        # Create run-log-dir with UUID
        self.run_log_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        log_file = self.logs_dir / f"task2_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"=== Task 2 Test Started ===")
        self.logger.info(f"Run ID: {self.run_id}")
        self.logger.info(f"Run log directory: {self.run_log_dir.absolute()}")
        self.logger.info(f"Logs directory: {self.logs_dir.absolute()}")
        self.logger.info(f"Screenshots directory: {self.screenshots_dir.absolute()}")
    
    def test_task2_user_input_simulation(self, snap_compare: Any) -> None:
        """
        Task 2: Simulate user input and take screenshots.
        
        This test implements the complete Task 2 workflow:
        1. Start the app and navigate to screen 1
        2. Input './tmp/autotest/build-autotest' to project directory field
        3. Input 'autotest-project' to project name field
        4. Click continue button
        5. Take screenshots after each major step
        """
        self.logger.info("Starting Task 2 user input simulation test")
        
        # Get test app path
        test_app_path = Path(__file__).parent / "gui_test_app.py"
        self.logger.info(f"Using test app: {test_app_path}")
        
        # Step 1: Capture startup screen (SC-0)
        self.logger.info("Step 1: Capturing startup screen (SC-0)")
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            press=["wait:3000"]  # Wait for system validation
        )
        self._save_snapshot("step1_sc0_startup_screen")
        self.logger.info("Step 1 completed: SC-0 startup screen captured")
        
        # Step 2: Navigate to screen 1 (SC-1) 
        self.logger.info("Step 2: Navigating to project setup screen (SC-1)")
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            press=["wait:3000", "enter", "wait:1000"]  # Wait, continue, wait for screen
        )
        self._save_snapshot("step2_sc1_project_setup_screen")
        self.logger.info("Step 2 completed: SC-1 project setup screen captured")
        
        # Step 3: Input project directory path
        self.logger.info("Step 3: Inputting project directory path")
        project_dir = "./tmp/autotest/build-autotest"
        self.logger.info(f"Project directory input: {project_dir}")
        
        # Navigate to project directory field and input the path
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            press=[
                "wait:3000",          # Wait for startup
                "enter",              # Navigate to SC-1
                "wait:1000",          # Wait for screen load
                "tab",                # Move to project directory field
                "ctrl+a",             # Select all existing text
                *list(project_dir),   # Type the project directory path
                "wait:500"            # Wait for input processing
            ]
        )
        self._save_snapshot("step3_project_directory_input")
        self.logger.info("Step 3 completed: Project directory path inputted")
        
        # Step 4: Input project name
        self.logger.info("Step 4: Inputting project name")
        project_name = "autotest-project"
        self.logger.info(f"Project name input: {project_name}")
        
        # Navigate to project name field and input the name
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            press=[
                "wait:3000",          # Wait for startup
                "enter",              # Navigate to SC-1
                "wait:1000",          # Wait for screen load
                "tab",                # Move to project directory field
                "ctrl+a",             # Select all in directory field
                *list(project_dir),   # Type the project directory path
                "tab",                # Move to project name field
                "ctrl+a",             # Select all existing text in name field
                *list(project_name),  # Type the project name
                "wait:500"            # Wait for input processing
            ]
        )
        self._save_snapshot("step4_project_name_input")
        self.logger.info("Step 4 completed: Project name inputted")
        
        # Step 5: Click continue button and capture final state
        self.logger.info("Step 5: Clicking continue button")
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            press=[
                "wait:3000",          # Wait for startup
                "enter",              # Navigate to SC-1
                "wait:1000",          # Wait for screen load
                "tab",                # Move to project directory field
                "ctrl+a",             # Select all in directory field
                *list(project_dir),   # Type the project directory path
                "tab",                # Move to project name field
                "ctrl+a",             # Select all in name field
                *list(project_name),  # Type the project name
                "tab",                # Move to continue button (or use Enter)
                "enter",              # Click continue/submit
                "wait:2000"           # Wait for next screen or processing
            ]
        )
        self._save_snapshot("step5_continue_button_clicked")
        self.logger.info("Step 5 completed: Continue button clicked")
        
        self.logger.info("=== Task 2 Test Completed Successfully ===")
        self.logger.info(f"All screenshots saved in: {self.screenshots_dir.absolute()}")
        self.logger.info(f"Test logs saved in: {self.logs_dir.absolute()}")
    
    async def test_task2_manual_pilot_simulation(self) -> None:
        """
        Alternative implementation using manual pilot control for more precise input.
        
        This test uses the async pilot directly for more granular control over
        user input simulation, allowing for better verification of each step.
        """
        self.logger.info("Starting Task 2 manual pilot simulation")
        
        # Import the GUI app for direct testing
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        from pei_docker.gui.app import PeiDockerApp
        
        # Create test build directory
        build_dir = Path("./tmp/autotest/build-autotest")
        build_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Created test build directory: {build_dir.absolute()}")
        
        # Create app and run test
        app = PeiDockerApp()
        async with app.run_test(size=(120, 40)) as pilot:
            
            # Step 1: Capture startup screen
            self.logger.info("Manual Test Step 1: Capturing startup screen")
            await pilot.pause(delay=3.0)  # Wait for system checks
            self._save_pilot_screenshot(pilot, "manual_step1_startup")
            
            # Step 2: Navigate to SC-1 
            self.logger.info("Manual Test Step 2: Navigating to project setup")
            await pilot.press("enter")  # Continue button
            await pilot.pause(delay=1.0)
            self._save_pilot_screenshot(pilot, "manual_step2_project_setup")
            
            # Step 3: Input project directory
            self.logger.info("Manual Test Step 3: Inputting project directory")
            # Try to focus on project directory input field
            await pilot.press("tab")  # Navigate to directory field
            await pilot.press("ctrl+a")  # Select all text
            # Type the project directory path
            project_dir = "./tmp/autotest/build-autotest"
            for char in project_dir:
                await pilot.press(char)
            await pilot.pause(delay=0.5)
            self._save_pilot_screenshot(pilot, "manual_step3_directory_input")
            
            # Step 4: Input project name
            self.logger.info("Manual Test Step 4: Inputting project name")
            await pilot.press("tab")  # Navigate to project name field
            await pilot.press("ctrl+a")  # Select all text
            # Type the project name
            project_name = "autotest-project"
            for char in project_name:
                await pilot.press(char)
            await pilot.pause(delay=0.5)
            self._save_pilot_screenshot(pilot, "manual_step4_project_name")
            
            # Step 5: Click continue
            self.logger.info("Manual Test Step 5: Clicking continue button")
            await pilot.press("tab")  # Navigate to continue button
            await pilot.press("enter")  # Press continue
            await pilot.pause(delay=2.0)  # Wait for next screen
            self._save_pilot_screenshot(pilot, "manual_step5_continue_clicked")
        
        self.logger.info("Manual pilot simulation completed successfully")
    
    def _save_snapshot(self, filename_prefix: str) -> None:
        """Save snapshot from pytest-textual-snapshot to screenshots directory."""
        # pytest-textual-snapshot creates files in tests/__snapshots__/
        snapshots_dir = Path("tests/__snapshots__")
        
        if snapshots_dir.exists():
            # Find the most recent snapshot file
            snapshot_files = list(snapshots_dir.glob("**/*.svg"))
            if snapshot_files:
                latest_snapshot = max(snapshot_files, key=lambda p: p.stat().st_mtime)
                target_path = self.screenshots_dir / f"{filename_prefix}.svg"
                
                # Copy to screenshots directory
                import shutil
                shutil.copy2(latest_snapshot, target_path)
                self.logger.info(f"Screenshot saved: {target_path}")
            else:
                self.logger.warning("No snapshot files found to copy")
        else:
            self.logger.warning(f"Snapshots directory not found: {snapshots_dir}")
    
    def _save_pilot_screenshot(self, pilot, filename_prefix: str) -> None:
        """Save screenshot directly from pilot console."""
        target_path = self.screenshots_dir / f"{filename_prefix}.svg"
        pilot.app.console.save_svg(str(target_path))
        self.logger.info(f"Pilot screenshot saved: {target_path}")


# Standalone execution for manual testing
async def run_task2_standalone():
    """Standalone function to run Task 2 simulation without pytest."""
    print("Starting Task 2 standalone execution...")
    
    # Create test instance
    test_instance = TestGUIUserInputTask2()
    test_instance._setup_environment()
    
    # Run the manual pilot simulation
    await test_instance.test_task2_manual_pilot_simulation()
    
    print(f"Task 2 completed! Check results in: {test_instance.run_log_dir}")


if __name__ == "__main__":
    """Entry point for direct script execution."""
    asyncio.run(run_task2_standalone())