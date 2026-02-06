"""
Base tab class for PeiDocker Web GUI tabs.

This module provides the base class that all tab implementations inherit from,
providing common functionality for configuration management and validation.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional, Dict, List, Tuple

from nicegui import ui

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class BaseTab(ABC):
    """Base class for all configuration tabs."""
    
    def __init__(self, app: 'PeiDockerWebGUI') -> None:
        self.app = app
        self.container: Optional[ui.element] = None
    
    @abstractmethod
    def render(self) -> ui.element:
        """Render the tab content and return the container element."""
        pass
    
    @abstractmethod
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the tab configuration. Returns (is_valid, error_messages)."""
        pass
    
    @abstractmethod
    def get_config_data(self) -> Dict[str, Any]:
        """Get the configuration data for this tab."""
        pass
    
    @abstractmethod
    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set the configuration data for this tab."""
        pass
    
    def mark_modified(self) -> None:
        """Mark this tab as modified."""
        # Mark the UI state as modified
        self.app.ui_state.mark_modified()
    
    def create_section_header(self, title: str, description: Optional[str] = None) -> ui.element:
        """Create a consistent section header."""
        with ui.column().classes('mb-6') as header:
            ui.label(title).classes('text-xl font-bold text-gray-800')
            if description:
                ui.label(description).classes('text-gray-600 mt-1')
        return header
    
    def create_form_group(self, label: str, help_text: Optional[str] = None) -> ui.element:
        """Create a form group with label and optional help text."""
        with ui.column().classes('mb-4 w-full') as group:
            ui.label(label).classes('font-medium text-gray-700 mb-1')
            if help_text:
                ui.label(help_text).classes('text-sm text-gray-500 mb-2')
        return group
    
    def create_card(self, title: Optional[str] = None) -> ui.element:
        """Create a card container for grouping related controls."""
        with ui.card().classes('w-full p-4 mb-4') as card:
            if title:
                ui.label(title).classes('text-lg font-semibold mb-3')
        return card