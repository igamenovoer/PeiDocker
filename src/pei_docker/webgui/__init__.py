"""
PeiDocker Web GUI - NiceGUI Implementation

This module provides a web-based interface for PeiDocker project configuration
using the NiceGUI framework. The GUI offers a browser-based alternative to the
textual CLI interface with the same configuration capabilities.

Key Features:
- Single-page web application with tab-based navigation
- Two-state design: Initial (no project) and Active project states
- Memory-first configuration management with explicit save
- Integration with existing PeiDocker CLI commands
- Real-time validation and reactive UI updates
"""

from pei_docker.webgui.app import PeiDockerWebGUI

__all__ = ['PeiDockerWebGUI']