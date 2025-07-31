"""
Base tab class for PeiDocker Web GUI tabs.

This module provides the base class that all tab implementations inherit from,
providing common functionality for configuration management and validation.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from nicegui import ui

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class BaseTab(ABC):
    """Base class for all configuration tabs."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        self.app = app
        self.container = None
    
    @abstractmethod
    def render(self) -> ui.element:
        """Render the tab content and return the container element."""
        pass
    
    @abstractmethod
    def validate(self) -> tuple[bool, list[str]]:
        """Validate the tab configuration. Returns (is_valid, error_messages)."""
        pass
    
    @abstractmethod
    def get_config_data(self) -> dict:
        """Get the configuration data for this tab."""
        pass
    
    @abstractmethod
    def set_config_data(self, data: dict):
        """Set the configuration data for this tab."""
        pass
    
    def mark_modified(self):
        """Mark this tab as modified."""
        from ..models import TabName
        # This would need to be implemented based on which tab this is
        # For now, just mark the general configuration as modified
        self.app.data.mark_modified()
    
    def create_section_header(self, title: str, description: str = None) -> ui.element:
        """Create a consistent section header."""
        with ui.column().classes('mb-6') as header:
            ui.label(title).classes('text-xl font-bold text-gray-800')
            if description:
                ui.label(description).classes('text-gray-600 mt-1')
        return header
    
    def create_form_group(self, label: str, help_text: str = None) -> ui.element:
        """Create a form group with label and optional help text."""
        with ui.column().classes('mb-4') as group:
            ui.label(label).classes('font-medium text-gray-700 mb-1')
            if help_text:
                ui.label(help_text).classes('text-sm text-gray-500 mb-2')
        return group
    
    def create_card(self, title: str = None) -> ui.element:
        """Create a card container for grouping related controls."""
        with ui.card().classes('w-full p-4 mb-4') as card:
            if title:
                ui.label(title).classes('text-lg font-semibold mb-3')
        return card