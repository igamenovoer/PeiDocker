#!/usr/bin/env python3
"""
Test wrapper application for SC-4 SSH Configuration Screen testing.

This module provides a standalone wrapper around the PeiDocker GUI application
specifically configured for SC-4 testing. It uses the dev mode feature to jump
directly to the SSH Configuration screen, bypassing all other wizard steps.

This wrapper is designed for use with pytest-textual-snapshot for automated
background GUI testing without interfering with CLI operations.
"""

import sys
import tempfile
from pathlib import Path

# Add the source directory to Python path for importing PeiDocker modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pei_docker.gui.app import PeiDockerApp

# Create a fixed test directory for consistent testing
TEST_PROJECT_DIR = str(Path(__file__).parent / "tmp_sc4_test_project")

# Ensure test directory exists
Path(TEST_PROJECT_DIR).mkdir(exist_ok=True)

# Create the app instance that pytest-textual-snapshot will use
# This needs to be at module level for pytest-textual-snapshot to find it
app = PeiDockerApp(
    project_dir=TEST_PROJECT_DIR,
    dev_screen="sc-4"  # Jump directly to SSH Configuration screen
)


def create_test_app() -> PeiDockerApp:
    """
    Create a PeiDocker GUI application instance configured for SC-4 testing.
    
    This function creates an app instance with:
    - Fixed test project directory for consistent testing
    - Dev mode enabled to jump directly to SC-4
    - Default SSH configuration for testing scenarios
    
    Returns
    -------
    PeiDockerApp
        Configured application instance ready for SC-4 testing
    """
    return app


if __name__ == "__main__":
    """
    Entry point for standalone execution and pytest-textual-snapshot testing.
    
    When executed directly, this script starts the PeiDocker GUI in dev mode
    at the SC-4 SSH Configuration screen. This is the exact same behavior
    that pytest-textual-snapshot will trigger when running automated tests.
    """
    # Start the application - this will:
    # 1. Initialize the Textual application framework
    # 2. Trigger dev mode navigation to SC-4
    # 3. Display the SSH Configuration screen with wizard context
    # 4. Allow user interaction for manual testing
    app.run()