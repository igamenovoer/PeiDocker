"""
Utilities package for PeiDocker Web GUI.

This package contains utility modules including the bridge layer
for converting between UI state and Pydantic models.
"""

# Import from existing utils.py (now legacy_utils.py) for backward compatibility
from pei_docker.webgui.legacy_utils import ProjectManager, FileOperations, ValidationManager, RealTimeValidator

# Import new utilities
from pei_docker.webgui.utils.bridge import ConfigBridge

__all__ = [
    # Old utilities
    'ProjectManager',
    'FileOperations', 
    'ValidationManager',
    'RealTimeValidator',
    # New utilities
    'ConfigBridge'
]