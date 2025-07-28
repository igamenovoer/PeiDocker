#!/usr/bin/env python3
"""
Background GUI Testing for SC-4: SSH Configuration Screen

This test module provides comprehensive background testing for the SSH Configuration
screen using pytest-textual-snapshot framework. Tests validate the visual output,
user interactions, and state management without interfering with CLI operations.

The tests leverage the dev mode feature to jump directly to SC-4, eliminating
the need for manual navigation through multiple wizard screens.
"""

import sys
from pathlib import Path
from typing import Any

import pytest

# Add source directory to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestSSHConfigBackground:
    """Background testing for SC-4 SSH Configuration Screen."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self) -> None:
        """Setup test environment and ensure output directories exist."""
        # Create screenshots output directory for manual verification
        screenshots_dir = Path("tmp/output/gui-screenshots")
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure __snapshots__ directory will be created by pytest-textual-snapshot
        snapshots_dir = Path("tests/__snapshots__")
        snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def test_sc4_initial_state_ssh_enabled(self, snap_compare: Any) -> None:
        """
        Test SC-4 initial state with SSH enabled (default configuration).
        
        This test captures the SSH configuration screen in its default state
        where SSH is enabled and shows the full configuration form including
        ports, user credentials, and advanced options.
        """
        # Use dev mode wrapper for direct SC-4 navigation
        test_app_path = Path(__file__).parent / "gui_sc4_test_app.py"
        
        # Jump directly to SC-4 and capture initial state
        # Using dev mode eliminates need for manual wizard navigation
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            press=["wait:3000"]  # Wait for dev mode screen mounting
        )
    
    def test_sc4_ssh_disabled_state(self, snap_compare: Any) -> None:
        """
        Test SC-4 when SSH is disabled showing warning message.
        
        This test verifies that when SSH is disabled, the configuration
        form is hidden and appropriate warning message is displayed.
        """
        test_app_path = Path(__file__).parent / "gui_sc4_test_app.py"
        
        async def disable_ssh_and_capture(pilot):
            """Navigate to SSH disabled state and capture screenshot."""
            # Wait for SC-4 to mount in dev mode
            await pilot.pause(delay=3.0)
            
            # Click "No" radio button to disable SSH
            await pilot.click("#ssh_no")
            await pilot.pause(delay=1.0)
            
            # Verify warning message is displayed
            # This creates a screenshot showing the disabled state
        
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            run_before=disable_ssh_and_capture
        )
    
    def test_sc4_advanced_options_expanded(self, snap_compare: Any) -> None:
        """
        Test SC-4 with advanced SSH options (public key auth and root access) enabled.
        
        This test captures the full expanded form with all advanced options
        visible, including public key authentication and root access fields.
        """
        test_app_path = Path(__file__).parent / "gui_sc4_test_app.py"
        
        async def expand_advanced_options(pilot):
            """Enable advanced options and capture expanded form."""
            # Wait for SC-4 to mount
            await pilot.pause(delay=3.0)
            
            # Enable public key authentication
            await pilot.click("#public_key_auth")
            await pilot.pause(delay=0.5)
            
            # Enable root SSH access
            await pilot.click("#root_ssh_access")
            await pilot.pause(delay=0.5)
            
            # Now the form shows all advanced fields including:
            # - SSH public key input field
            # - Root password input field
            # - Both warning messages
        
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            run_before=expand_advanced_options
        )
    
    def test_sc4_user_input_interaction(self, snap_compare: Any) -> None:
        """
        Test SC-4 with user input in various fields showing real-time updates.
        
        This test validates that user input is properly captured and displayed
        in the SSH configuration form fields with real-time validation.
        """
        test_app_path = Path(__file__).parent / "gui_sc4_test_app.py"
        
        async def simulate_user_input(pilot):
            """Simulate user input across multiple SSH configuration fields."""
            # Wait for SC-4 to mount
            await pilot.pause(delay=3.0)
            
            # Update SSH container port
            ssh_port_input = await pilot.query_one("#ssh_container_port")
            await pilot.click("#ssh_container_port")
            await pilot.press("ctrl+a")  # Select all
            await pilot.press("2222")    # New port value
            await pilot.pause(delay=0.3)
            
            # Update SSH host port
            await pilot.click("#ssh_host_port")
            await pilot.press("ctrl+a")  # Select all
            await pilot.press("2223")    # New host port
            await pilot.pause(delay=0.3)
            
            # Update SSH username
            await pilot.click("#ssh_user")
            await pilot.press("ctrl+a")  # Select all
            await pilot.press("developer")  # New username
            await pilot.pause(delay=0.3)
            
            # Update SSH password
            await pilot.click("#ssh_password")
            await pilot.press("ctrl+a")  # Select all
            await pilot.press("secure123")  # New password
            await pilot.pause(delay=0.3)
            
            # Update UID
            await pilot.click("#ssh_uid")
            await pilot.press("ctrl+a")  # Select all
            await pilot.press("1200")    # New UID
            await pilot.pause(delay=0.5)
            
            # This captures the form with all user-entered values
        
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            run_before=simulate_user_input
        )
    
    def test_sc4_validation_errors(self, snap_compare: Any) -> None:
        """
        Test SC-4 validation error display for invalid inputs.
        
        This test captures how validation errors are displayed when users
        enter invalid data in SSH configuration fields.
        """
        test_app_path = Path(__file__).parent / "gui_sc4_test_app.py"
        
        async def trigger_validation_errors(pilot):
            """Enter invalid data to trigger validation error display."""
            # Wait for SC-4 to mount
            await pilot.pause(delay=3.0)
            
            # Enter invalid port number (out of range)
            await pilot.click("#ssh_container_port")
            await pilot.press("ctrl+a")
            await pilot.press("99999")   # Invalid port > 65535
            await pilot.press("tab")     # Trigger validation by moving focus
            await pilot.pause(delay=0.5)
            
            # Enter invalid username (starts with number)
            await pilot.click("#ssh_user")
            await pilot.press("ctrl+a")
            await pilot.press("123user") # Invalid username format
            await pilot.press("tab")     # Trigger validation
            await pilot.pause(delay=0.5)
            
            # Enter invalid password (contains spaces)
            await pilot.click("#ssh_password")
            await pilot.press("ctrl+a")
            await pilot.press("bad password")  # Invalid: contains space
            await pilot.press("tab")     # Trigger validation
            await pilot.pause(delay=0.5)
            
            # This captures validation error states
        
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            run_before=trigger_validation_errors
        )
    
    def test_sc4_public_key_scenarios(self, snap_compare: Any) -> None:
        """
        Test SC-4 public key authentication scenarios including system key reference.
        
        This test validates the public key input field behavior including
        the special '~' system key reference functionality.
        """
        test_app_path = Path(__file__).parent / "gui_sc4_test_app.py"
        
        async def test_public_key_input(pilot):
            """Test public key input with system key reference."""
            # Wait for SC-4 to mount
            await pilot.pause(delay=3.0)
            
            # Enable public key authentication
            await pilot.click("#public_key_auth")
            await pilot.pause(delay=0.5)
            
            # Enter system key reference
            await pilot.click("#ssh_public_key")
            await pilot.press("~")  # System key reference
            await pilot.pause(delay=0.5)
            
            # This captures the public key field with system reference
            # and shows the help text about '~' usage
        
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            run_before=test_public_key_input
        )
    
    def test_sc4_wizard_navigation_context(self, snap_compare: Any) -> None:
        """
        Test SC-4 within wizard context showing progress and navigation.
        
        This test captures how SC-4 appears within the wizard framework
        with step progress indicators and navigation buttons visible.
        """
        test_app_path = Path(__file__).parent / "gui_sc4_test_app.py"
        
        # This test captures the complete wizard context including:
        # - Step 2 of 11 indicator
        # - SSH Configuration title
        # - Progress bar showing step 2
        # - Previous/Next navigation buttons
        # - Full SSH configuration form
        assert snap_compare(
            str(test_app_path),
            terminal_size=(120, 40),
            press=["wait:3000"]
        )
    
    def test_sc4_responsive_layout(self, snap_compare: Any) -> None:
        """
        Test SC-4 responsive layout behavior at different terminal sizes.
        
        This test validates that the SSH configuration screen adapts
        properly to different terminal dimensions.
        """
        test_app_path = Path(__file__).parent / "gui_sc4_test_app.py"
        
        async def test_different_sizes(pilot):
            """Test layout at different terminal dimensions."""
            # Start with standard size and wait for mount
            await pilot.pause(delay=3.0)
            
            # Test wider terminal (common on modern displays)
            await pilot.resize_terminal(160, 50)
            await pilot.pause(delay=1.0)
            
            # This captures the layout in wider terminal
        
        assert snap_compare(
            str(test_app_path),
            terminal_size=(160, 50),
            run_before=test_different_sizes
        )
    
    def _copy_snapshot_for_manual_review(self, test_name: str) -> None:
        """
        Copy generated pytest snapshot to manual review directory.
        
        This helper method copies pytest-textual-snapshot generated SVG files
        to a manual review directory for visual inspection outside of pytest.
        """
        snapshots_dir = Path("tests/__snapshots__/test_gui_sc4_ssh_config")
        manual_dir = Path("tmp/output/gui-screenshots")
        
        if snapshots_dir.exists():
            # Find the most recent snapshot matching our test
            snapshot_files = list(snapshots_dir.glob(f"*{test_name}*.svg"))
            if snapshot_files:
                latest = max(snapshot_files, key=lambda p: p.stat().st_mtime)
                target = manual_dir / f"sc4-{test_name}.svg"
                
                import shutil
                shutil.copy2(latest, target)
                print(f"SC-4 screenshot copied: {target}")


# Standalone execution for development testing
async def manual_sc4_testing():
    """
    Manual testing function for SC-4 development and debugging.
    
    This function provides a way to manually test SC-4 interactions
    without running the full pytest suite.
    """
    print("Starting manual SC-4 SSH Configuration testing...")
    
    # Ensure screenshot directory exists
    screenshots_dir = Path("tmp/output/gui-screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    # Import here to avoid issues during pytest execution
    from pei_docker.gui.app import PeiDockerApp
    import tempfile
    
    # Create temporary project directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary project directory: {temp_dir}")
        
        # Create app instance with dev mode pointing to SC-4
        app = PeiDockerApp(project_dir=temp_dir, dev_screen="sc-4")
        
        async with app.run_test(size=(120, 40)) as pilot:
            print("Capturing SC-4 initial state...")
            
            # Wait for dev mode to jump to SC-4
            await pilot.pause(delay=3.0)
            
            # Save initial state screenshot
            initial_path = screenshots_dir / "sc4-manual-initial-state.svg"
            pilot.app.console.save_svg(str(initial_path))
            print(f"Initial state captured: {initial_path}")
            
            print("Testing SSH disable interaction...")
            
            # Test SSH disable functionality
            await pilot.click("#ssh_no")
            await pilot.pause(delay=1.0)
            
            # Save disabled state screenshot
            disabled_path = screenshots_dir / "sc4-manual-ssh-disabled.svg"
            pilot.app.console.save_svg(str(disabled_path))
            print(f"SSH disabled state captured: {disabled_path}")
            
            print("Testing advanced options...")
            
            # Re-enable SSH first
            await pilot.click("#ssh_yes")
            await pilot.pause(delay=0.5)
            
            # Enable advanced options
            await pilot.click("#public_key_auth")
            await pilot.pause(delay=0.5)
            await pilot.click("#root_ssh_access")
            await pilot.pause(delay=0.5)
            
            # Save advanced options screenshot
            advanced_path = screenshots_dir / "sc4-manual-advanced-options.svg"
            pilot.app.console.save_svg(str(advanced_path))
            print(f"Advanced options state captured: {advanced_path}")
    
    print("Manual SC-4 testing completed!")
    print(f"Screenshots saved in: {screenshots_dir.absolute()}")


if __name__ == "__main__":
    """Entry point for direct script execution during development."""
    import asyncio
    asyncio.run(manual_sc4_testing())