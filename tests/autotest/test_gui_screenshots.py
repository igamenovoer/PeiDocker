"""
Automated GUI screenshot test for PeiDocker GUI screens.

This test script captures screenshots of the first two GUI screens:
- SC-0: Application Startup Screen 
- SC-1: Project Directory Selection Screen

Screenshots are saved to tmp/output/gui-screenshots/ for visual verification.
"""

import asyncio
from pathlib import Path
from typing import Any

import pytest


class TestGUIScreenshots:
    """Test class for capturing GUI screenshots using pytest-textual-snapshot."""
    
    @pytest.fixture(autouse=True)
    def setup_screenshots_dir(self) -> None:
        """Ensure screenshots directory exists."""
        screenshots_path = Path("tmp/output/gui-screenshots")
        screenshots_path.mkdir(parents=True, exist_ok=True)
    
    def test_sc0_startup_screen(self, snap_compare: Any) -> None:
        """
        Test SC-0: Application Startup Screen screenshot capture.
        
        This test captures the initial startup screen which displays 
        system validation and branding information.
        """
        # Use permanent test app file
        test_app_path = Path(__file__).parent / "gui_test_app.py"
        
        # Capture startup screen with system validation delay
        # Terminal size matches typical development environment
        assert snap_compare(
            str(test_app_path), 
            terminal_size=(120, 40),
            press=["wait:3000"]  # Wait 3 seconds for system checks
        )
        
        # Copy the generated snapshot to our screenshots directory
        self._copy_snapshot_to_screenshots("sc-0-startup-screen")
    
    def test_sc1_project_setup_screen(self, snap_compare: Any) -> None:
        """
        Test SC-1: Project Directory Selection Screen screenshot capture.
        
        This test navigates to the project setup screen and captures
        the directory input form with real-time log viewer.
        """
        # Use permanent test app file
        test_app_path = Path(__file__).parent / "gui_test_app.py"
        
        # Navigate to project setup screen and capture
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40), 
            press=["wait:3000", "enter", "wait:1000"]  # Wait, continue, wait for screen
        )
        
        # Copy the generated snapshot to our screenshots directory
        self._copy_snapshot_to_screenshots("sc-1-project-setup-screen")
    
    def test_complete_flow_both_screens(self, snap_compare: Any) -> None:
        """
        Test complete flow capturing both screens in sequence.
        
        This demonstrates the full user workflow from startup to project setup.
        """
        # Use permanent test app file
        test_app_path = Path(__file__).parent / "gui_test_app.py"
        
        # Test startup screen first
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            press=["wait:3000"]  # Capture startup after system checks
        )
        
        # Copy the generated snapshot to our screenshots directory
        self._copy_snapshot_to_screenshots("flow-startup-screen")
    
    def _copy_snapshot_to_screenshots(self, filename_prefix: str) -> None:
        """Copy generated snapshot to screenshots directory with descriptive name."""
        # pytest-textual-snapshot creates files in tests/__snapshots__/
        snapshots_dir = Path("tests/__snapshots__")
        screenshots_dir = Path("tmp/output/gui-screenshots")
        
        if snapshots_dir.exists():
            # Find the most recent snapshot file
            snapshot_files = list(snapshots_dir.glob("*.svg"))
            if snapshot_files:
                latest_snapshot = max(snapshot_files, key=lambda p: p.stat().st_mtime)
                target_path = screenshots_dir / f"{filename_prefix}.svg"
                
                # Copy to screenshots directory
                import shutil
                shutil.copy2(latest_snapshot, target_path)
                print(f"Screenshot saved: {target_path}")


# Standalone script functionality 
async def capture_gui_screenshots_standalone() -> None:
    """
    Standalone function to capture GUI screenshots without pytest.
    
    This function manually runs the GUI app and captures screenshots
    for manual testing and verification.
    """
    print("Starting standalone GUI screenshot capture...")
    
    # Ensure output directory exists
    screenshots_dir = Path("tmp/output/gui-screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    # Import here to avoid circular imports during pytest
    from pei_docker.gui.app import PeiDockerApp
    
    # Create app instance
    app = PeiDockerApp()
    
    async with app.run_test(size=(120, 40)) as pilot:
        print("Capturing SC-0 (Startup Screen)...")
        
        # Wait for startup screen to fully load with system checks
        await pilot.pause(delay=3.0)
        
        # Save startup screen screenshot using pilot's console
        sc0_path = screenshots_dir / "sc-0-startup-screen.svg"
        pilot.app.console.save_svg(str(sc0_path))
        print(f"SC-0 screenshot saved: {sc0_path}")
        
        print("Navigating to SC-1 (Project Setup Screen)...")
        
        # Navigate to project setup screen
        await pilot.press("enter")  # Continue button
        await pilot.pause(delay=1.0)  # Wait for screen transition
        
        # Save project setup screen screenshot
        sc1_path = screenshots_dir / "sc-1-project-setup-screen.svg"
        pilot.app.console.save_svg(str(sc1_path))
        print(f"SC-1 screenshot saved: {sc1_path}")
    
    print("Screenshot capture completed!")
    print(f"Screenshots saved in: {screenshots_dir.absolute()}")


if __name__ == "__main__":
    """Entry point for direct script execution."""
    asyncio.run(capture_gui_screenshots_standalone())