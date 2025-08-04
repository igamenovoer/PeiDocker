"""
Models package for PeiDocker Web GUI.

This package contains both UI state models (bindable dataclasses)
and validation models (Pydantic) for the refactored data architecture.
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

# Export Pydantic validation models
from pei_docker.webgui.models.config import (
    AppConfig,
    StageConfig,
    ProjectConfig,
    EnvironmentConfig,
    NetworkConfig,
    SSHConfig,
    StorageConfig,
    ScriptsConfig
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
    
    # Validation models
    'AppConfig',
    'StageConfig',
    'ProjectConfig',
    'EnvironmentConfig',
    'NetworkConfig',
    'SSHConfig',
    'StorageConfig',
    'ScriptsConfig'
]