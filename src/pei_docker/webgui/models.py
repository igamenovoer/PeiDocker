"""
Data models for PeiDocker Web GUI state management.

This module defines the data structures used to manage configuration state
in the NiceGUI web interface, including project state, tab management,
and configuration data.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from pathlib import Path
from enum import Enum

class AppState(Enum):
    """Application state enumeration."""
    INITIAL = "initial"  # No active project
    ACTIVE = "active"    # Project loaded and active

class TabName(Enum):
    """Tab names for navigation."""
    PROJECT = "project"
    SSH = "ssh"
    NETWORK = "network"
    ENVIRONMENT = "environment"
    STORAGE = "storage"
    SCRIPTS = "scripts"
    SUMMARY = "summary"

@dataclass
class ProjectState:
    """Project state information."""
    directory: Optional[Path] = None
    name: Optional[str] = None
    is_configured: bool = False
    last_configure_success: bool = True

@dataclass
class ConfigurationState:
    """Configuration state management."""
    modified: bool = False
    last_saved: Optional[str] = None
    validation_errors: Dict[str, List[str]] = field(default_factory=dict)
    
    # Configuration data
    stage_1: Dict[str, Any] = field(default_factory=dict)
    stage_2: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TabState:
    """Tab navigation state."""
    active_tab: TabName = TabName.PROJECT
    tab_errors: Dict[TabName, bool] = field(default_factory=dict)
    tab_modified: Dict[TabName, bool] = field(default_factory=dict)

@dataclass
class AppData:
    """Complete application state."""
    app_state: AppState = AppState.INITIAL
    project: ProjectState = field(default_factory=ProjectState)
    config: ConfigurationState = field(default_factory=ConfigurationState)
    tabs: TabState = field(default_factory=TabState)
    
    def reset_project(self):
        """Reset to initial state with no active project."""
        self.app_state = AppState.INITIAL
        self.project = ProjectState()
        self.config = ConfigurationState()
        self.tabs = TabState()
    
    def set_active_project(self, directory: Path, name: str = None):
        """Set active project and switch to active state."""
        self.app_state = AppState.ACTIVE
        self.project.directory = directory
        self.project.name = name or directory.name
        self.tabs.active_tab = TabName.PROJECT

    def mark_modified(self, tab: TabName = None):
        """Mark configuration as modified."""
        self.config.modified = True
        if tab:
            self.tabs.tab_modified[tab] = True
    
    def mark_saved(self):
        """Mark configuration as saved."""
        self.config.modified = False
        self.tabs.tab_modified.clear()
        from datetime import datetime
        self.config.last_saved = datetime.now().strftime("%I:%M %p")
    
    def add_validation_error(self, tab: TabName, error: str):
        """Add validation error for a tab."""
        if tab.value not in self.config.validation_errors:
            self.config.validation_errors[tab.value] = []
        self.config.validation_errors[tab.value].append(error)
        self.tabs.tab_errors[tab] = True
    
    def clear_validation_errors(self, tab: TabName = None):
        """Clear validation errors for a tab or all tabs."""
        if tab:
            self.config.validation_errors.pop(tab.value, None)
            self.tabs.tab_errors.pop(tab, None)
        else:
            self.config.validation_errors.clear()
            self.tabs.tab_errors.clear()