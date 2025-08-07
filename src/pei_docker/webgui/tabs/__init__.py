"""
Tab implementations for PeiDocker Web GUI.

This module contains the individual tab implementations that provide
configuration interfaces for different aspects of PeiDocker projects.
"""

from pei_docker.webgui.tabs.base import BaseTab
from pei_docker.webgui.tabs.project import ProjectTab
from pei_docker.webgui.tabs.ssh import SSHTab
from pei_docker.webgui.tabs.network import NetworkTab
from pei_docker.webgui.tabs.environment import EnvironmentTab
from pei_docker.webgui.tabs.storage import StorageTab
from pei_docker.webgui.tabs.scripts import ScriptsTab
from pei_docker.webgui.tabs.summary import SummaryTab

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