"""
Models package for PeiDocker Web GUI.

This package contains both UI state models (bindable dataclasses)
and validation models (Pydantic) for the refactored data architecture.
"""

# Import old models for backward compatibility during migration
# These are from the legacy_models.py file in the parent webgui directory
from pei_docker.webgui.legacy_models import AppData, AppState, TabName, ProjectState

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
    # Old models for compatibility
    'AppData',
    'AppState',
    'TabName',
    'ProjectState',
    
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