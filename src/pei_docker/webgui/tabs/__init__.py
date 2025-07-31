"""
Tab implementations for PeiDocker Web GUI.

This module contains the individual tab implementations that provide
configuration interfaces for different aspects of PeiDocker projects.
"""

from .base import BaseTab
from .project import ProjectTab
from .ssh import SSHTab
from .network import NetworkTab
from .environment import EnvironmentTab
from .storage import StorageTab
from .scripts import ScriptsTab
from .summary import SummaryTab

__all__ = [
    'BaseTab',
    'ProjectTab', 
    'SSHTab',
    'NetworkTab',
    'EnvironmentTab', 
    'StorageTab',
    'ScriptsTab',
    'SummaryTab'
]