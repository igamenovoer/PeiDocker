"""
Models package for PeiDocker Web GUI.

This package contains both UI state models (bindable dataclasses)
and configuration adapters for the refactored data architecture.
"""

# Export bindable UI state models
from pei_docker.webgui.models.ui_state import (
    AppUIState,
    StageUI,
    ProjectUI,
    EnvironmentUI,
    NetworkUI,
    SSHTabUI,
    StorageUI,
    ScriptsUI
)

# Export adapter types that replace Pydantic models
from pei_docker.webgui.models.config_adapter import (
    AppConfigAdapter as AppConfig,
    StageConfigAdapter as StageConfig,
    ProjectConfigAdapter as ProjectConfig,
    EnvironmentConfigAdapter as EnvironmentConfig,
    NetworkConfigAdapter as NetworkConfig,
    SSHConfigAdapter as SSHConfig,
    StorageConfigAdapter as StorageConfig,
    ScriptsConfigAdapter as ScriptsConfig
)

__all__ = [
    # UI State models
    'AppUIState',
    'StageUI',
    'ProjectUI',
    'EnvironmentUI',
    'NetworkUI',
    'SSHTabUI',
    'StorageUI',
    'ScriptsUI',
    
    # Configuration models (now using adapters)
    'AppConfig',
    'StageConfig',
    'ProjectConfig',
    'EnvironmentConfig',
    'NetworkConfig',
    'SSHConfig',
    'StorageConfig',
    'ScriptsConfig'
]