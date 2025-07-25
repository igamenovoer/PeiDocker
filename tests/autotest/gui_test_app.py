#!/usr/bin/env python3
"""
Test application for GUI screenshot capture.
This is a wrapper around the main PeiDocker GUI app for testing purposes.
"""

import sys
from pathlib import Path

# Add the src directory to path so we can import pei_docker
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pei_docker.gui.app import PeiDockerApp

if __name__ == "__main__":
    app = PeiDockerApp()
    app.run()