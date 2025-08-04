"""
PeiDocker Web GUI - Main Application

This module implements the main NiceGUI application for PeiDocker project configuration.
It provides a web-based interface with tab navigation, state management, and integration
with the existing PeiDocker CLI commands.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Any, Literal
from datetime import datetime
import copy
from enum import Enum

from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

from pei_docker.webgui.models.ui_state import AppUIState
from pei_docker.webgui.utils.ui_state_bridge import UIStateBridge
from pei_docker.webgui.legacy_utils import ProjectManager, FileOperations
from pei_docker.webgui.tabs import (
    ProjectTab, SSHTab, NetworkTab, EnvironmentTab, 
    StorageTab, ScriptsTab, SummaryTab
)

# Keep TabName enum for navigation
class TabName(Enum):
    """Tab names for navigation."""
    PROJECT = "project"
    SSH = "ssh"
    NETWORK = "network"
    ENVIRONMENT = "environment"
    STORAGE = "storage"
    SCRIPTS = "scripts"
    SUMMARY = "summary"

# App states
class AppState(Enum):
    """Application state enumeration."""
    INITIAL = "initial"  # No active project
    ACTIVE = "active"    # Project loaded and active

class PeiDockerWebGUI:
    """Main PeiDocker Web GUI Application using NiceGUI."""
    
    def __init__(self) -> None:
        # Use new UI state instead of legacy AppData
        self.ui_state = AppUIState()
        self.bridge = UIStateBridge()
        
        # Keep utility classes for now
        self.project_manager = ProjectManager()
        self.file_ops = FileOperations()
        
        # App state management
        self.app_state: AppState = AppState.INITIAL
        
        # Tab implementations
        self.tabs: Dict[TabName, Any] = {
            TabName.PROJECT: ProjectTab(self),
            TabName.SSH: SSHTab(self),
            TabName.NETWORK: NetworkTab(self),
            TabName.ENVIRONMENT: EnvironmentTab(self),
            TabName.STORAGE: StorageTab(self),
            TabName.SCRIPTS: ScriptsTab(self),
            TabName.SUMMARY: SummaryTab(self)
        }
        
        # UI components (will be created in setup_ui)
        self.header_container: Optional[ui.row] = None
        self.project_info_bar: Optional[ui.row] = None
        self.tab_nav_container: Optional[ui.row] = None
        self.content_container: Optional[ui.column] = None
        self.status_bar_container: Optional[ui.row] = None
        self.active_tab_container: Optional[ui.column] = None
    
    def setup_ui(self) -> None:
        """Setup the main UI layout."""
        # Page configuration
        ui.page_title('🐳 PeiDocker Web GUI')
        
        # Main container with full height
        with ui.column().classes('w-full h-screen'):
            self.create_header()
            self.create_project_info_bar()
            self.create_tab_navigation()
            self.create_main_content()
            self.create_status_bar()
        
        # Initialize UI state
        self.update_ui_state()
        
        # Render initial active tab if in active state
        if self.app_state == AppState.ACTIVE:
            self.render_active_tab()
    
    def create_header(self) -> None:
        """Create the header with logo and action buttons."""
        with ui.row().classes('w-full bg-blue-600 text-white p-4 items-center justify-between') as header:
            self.header_container = header
            
            # Logo
            ui.label('🐳 PeiDocker Web GUI').classes('text-xl font-bold')
            
            # Action buttons (only shown in active state)
            with ui.row().classes('gap-2') as actions:
                save_btn = ui.button('💾 Save', on_click=self.save_configuration) \
                    .classes('bg-green-600 hover:bg-green-700')
                
                configure_btn = ui.button('⚙️ Configure', on_click=self.configure_project) \
                    .classes('bg-yellow-600 hover:bg-yellow-700')
                
                download_btn = ui.button('📦 Download', on_click=self.download_project) \
                    .classes('bg-blue-500 hover:bg-blue-600')
                
                # Bind visibility manually since we track app_state separately
                self._bind_to_active_state(save_btn)
                self._bind_to_active_state(configure_btn)
                self._bind_to_active_state(download_btn)
    
    def create_project_info_bar(self) -> None:
        """Create the project info bar (shown only in active state)."""
        with ui.row().classes('w-full bg-gray-100 p-2 items-center') as info_bar:
            self.project_info_bar = info_bar
            
            ui.label('📁 Project:').classes('font-medium')
            self.project_dir_label = ui.label('')
            self._update_project_dir_label()
            
            # Status indicator
            with ui.row().classes('ml-auto items-center gap-2'):
                # Modified indicator
                self.modified_icon = ui.icon('circle', size='sm').classes('text-orange-500')
                self.modified_label = ui.label('⚠️ Unsaved changes')
                
                # Saved indicator
                self.saved_icon = ui.icon('circle', size='sm').classes('text-green-500')
                self.saved_label = ui.label('✅ All saved')
                
                # Update visibility based on modified state
                self._update_modified_indicators()
                
                # Change Project button
                ui.button('🔄 Change Project', on_click=self.change_project) \
                    .classes('bg-gray-500 hover:bg-gray-600 text-white text-sm px-3 py-1 ml-2')
            
            # Bind visibility to active state
            self._bind_to_active_state(info_bar)
    
    def create_tab_navigation(self) -> None:
        """Create the tab navigation bar."""
        with ui.row().classes('w-full bg-white border-b') as nav:
            self.tab_nav_container = nav
            
            # Tab buttons
            self.tab_buttons: Dict[TabName, ui.button] = {}
            for tab_name in TabName:
                icon_map = {
                    TabName.PROJECT: '🏗️',
                    TabName.SSH: '🔐', 
                    TabName.NETWORK: '🌐',
                    TabName.ENVIRONMENT: '⚙️',
                    TabName.STORAGE: '💾',
                    TabName.SCRIPTS: '📜',
                    TabName.SUMMARY: '📋'
                }
                
                button = ui.button(f'{icon_map[tab_name]} {tab_name.value.title()}',
                                 on_click=lambda t=tab_name: self.switch_tab(t)) \
                    .classes('px-4 py-2 border-b-2 border-transparent hover:border-blue-500')
                
                self.tab_buttons[tab_name] = button
            
            # Update active tab styling
            self._update_tab_styling()
            
            # Bind visibility to active state
            self._bind_to_active_state(nav)
    
    def create_main_content(self) -> None:
        """Create the main content area."""
        with ui.column().classes('flex-1 w-full p-6') as content:
            self.content_container = content
            
            # Initial state content (project selection)
            with ui.column().classes('max-w-md mx-auto mt-20') as initial_content:
                self.initial_content = initial_content
                ui.label('🐳 Welcome to PeiDocker Web GUI').classes('text-2xl font-bold text-center mb-8')
                
                # Project directory input
                with ui.column().classes('w-full gap-4'):
                    ui.label('📁 Project Directory:').classes('font-medium')
                    
                    # Auto-generate default project directory
                    default_project_dir = self._generate_default_project_dir()
                    project_dir_input = ui.input(
                        placeholder='Auto-generated project directory (click Generate for new path)', 
                        value=default_project_dir
                    ).classes('w-full')
                    
                    with ui.row().classes('gap-2 w-full'):
                        ui.button('📂 Browse', on_click=self.browse_directory) \
                            .classes('bg-gray-500 hover:bg-gray-600')
                        ui.button('🎲 Generate New', on_click=lambda: self.generate_temp_directory(project_dir_input)) \
                            .classes('bg-blue-500 hover:bg-blue-600')
                    
                    # Action buttons
                    with ui.row().classes('gap-4 w-full mt-6'):
                        ui.button('✨ Create Project', 
                                 on_click=lambda: self.create_project(project_dir_input.value)) \
                            .classes('flex-1 bg-green-600 hover:bg-green-700 text-white py-2')
                        
                        ui.button('📂 Load Project', 
                                 on_click=lambda: self.load_project(project_dir_input.value)) \
                            .classes('flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2')
                
                # Show only in initial state
                self._update_initial_content_visibility()
            
            # Active project content (tabs)
            with ui.column().classes('w-full') as active_content:
                self.active_content = active_content
                self.active_tab_container = ui.column().classes('w-full')
                
                # Hide in initial state
                self._update_active_content_visibility()
    
    def create_status_bar(self) -> None:
        """Create the status bar."""
        with ui.row().classes('w-full bg-gray-200 p-2 items-center text-sm') as status_bar:
            self.status_bar_container = status_bar
            
            # Stage selector
            with ui.row().classes('items-center gap-2'):
                ui.label('🏗️ Stage:').classes('font-medium')
                
                # Bind to ui_state.active_stage
                stage_select = ui.select(
                    options={1: 'Stage-1', 2: 'Stage-2'},
                    value=self.ui_state.active_stage
                ).classes('w-32')
                stage_select.on('change', self._on_stage_change)
            
            # Error indicator
            with ui.row().classes('ml-auto items-center gap-2'):
                self.error_icon = ui.icon('error', size='sm').classes('text-red-500')
                self.error_label = ui.label('')
                self._update_error_indicators()
            
            # Bind visibility to active state
            self._bind_to_active_state(status_bar)
    
    # Helper methods for state management
    def _bind_to_active_state(self, element: ui.element) -> None:
        """Bind element visibility to active app state."""
        element.visible = self.app_state == AppState.ACTIVE
    
    def _update_project_dir_label(self) -> None:
        """Update project directory label."""
        if hasattr(self, 'project_dir_label'):
            self.project_dir_label.text = self.ui_state.project.project_directory
    
    def _update_modified_indicators(self) -> None:
        """Update modified/saved indicators."""
        if hasattr(self, 'modified_icon'):
            self.modified_icon.visible = self.ui_state.modified
            self.modified_label.visible = self.ui_state.modified
            self.saved_icon.visible = not self.ui_state.modified
            self.saved_label.visible = not self.ui_state.modified
            
            if self.ui_state.last_saved:
                self.saved_label.text = f'✅ Last saved: {self.ui_state.last_saved}'
            else:
                self.saved_label.text = '✅ All saved'
    
    def _update_error_indicators(self) -> None:
        """Update error indicators."""
        if hasattr(self, 'error_icon'):
            self.error_icon.visible = self.ui_state.has_errors
            self.error_label.visible = self.ui_state.has_errors
            if self.ui_state.has_errors:
                self.error_label.text = f'❌ {self.ui_state.error_count} errors'
    
    def _update_tab_styling(self) -> None:
        """Update tab button styling based on active tab."""
        if hasattr(self, 'tab_buttons'):
            active_tab = TabName(self.ui_state.active_tab)
            for tab_name, button in self.tab_buttons.items():
                if tab_name == active_tab:
                    button.classes('px-4 py-2 border-b-2 border-blue-500 text-blue-600')
                else:
                    button.classes('px-4 py-2 border-b-2 border-transparent hover:border-blue-500')
    
    def _update_initial_content_visibility(self) -> None:
        """Update initial content visibility."""
        if hasattr(self, 'initial_content'):
            self.initial_content.visible = self.app_state == AppState.INITIAL
    
    def _update_active_content_visibility(self) -> None:
        """Update active content visibility."""
        if hasattr(self, 'active_content'):
            self.active_content.visible = self.app_state == AppState.ACTIVE
    
    def _on_stage_change(self, e: ValueChangeEventArguments) -> None:
        """Handle stage selection change."""
        self.ui_state.active_stage = e.value
        self.render_active_tab()
    
    def _generate_default_project_dir(self) -> str:
        """Generate a default project directory with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        temp_dir = tempfile.gettempdir()
        return str(Path(temp_dir) / f"peidocker-{timestamp}")
    
    # Navigation methods
    def switch_tab(self, tab_name: TabName) -> None:
        """Switch to a different tab."""
        self.ui_state.active_tab = tab_name.value
        self._update_tab_styling()
        self.render_active_tab()
    
    def render_active_tab(self) -> None:
        """Render the active tab content."""
        if self.active_tab_container:
            self.active_tab_container.clear()
            
            active_tab = TabName(self.ui_state.active_tab)
            if active_tab in self.tabs:
                with self.active_tab_container:
                    self.tabs[active_tab].render()
    
    # Project management methods
    async def create_project(self, project_dir: str) -> None:
        """Create a new project."""
        try:
            # Create project directory
            Path(project_dir).mkdir(parents=True, exist_ok=True)
            
            # Set up new UI state
            self.ui_state = AppUIState()
            self.ui_state.project.project_directory = project_dir
            self.ui_state.project.project_name = Path(project_dir).name
            
            # Switch to active state
            self.app_state = AppState.ACTIVE
            self.update_ui_state()
            
            ui.notify(f'✅ Project created: {project_dir}', type='positive')
            
            # Render first tab
            self.render_active_tab()
            
        except Exception as e:
            ui.notify(f'❌ Failed to create project: {str(e)}', type='negative')
    
    async def load_project(self, project_dir: str) -> None:
        """Load an existing project."""
        try:
            config_path = Path(project_dir) / 'user_config.yml'
            
            if config_path.exists():
                # Load configuration into UI state
                success, errors = self.bridge.load_from_yaml(str(config_path), self.ui_state)
                
                if success:
                    self.ui_state.project.project_directory = project_dir
                    self.ui_state.project.project_name = Path(project_dir).name
                    
                    # Switch to active state
                    self.app_state = AppState.ACTIVE
                    self.update_ui_state()
                    
                    ui.notify(f'✅ Project loaded: {project_dir}', type='positive')
                    
                    # Render first tab
                    self.render_active_tab()
                else:
                    ui.notify(f'❌ Failed to load project: {", ".join(errors)}', type='negative')
            else:
                ui.notify(f'❌ No configuration found in: {project_dir}', type='negative')
                
        except Exception as e:
            ui.notify(f'❌ Failed to load project: {str(e)}', type='negative')
    
    async def save_configuration(self) -> None:
        """Save the current configuration."""
        try:
            # Validate UI state
            is_valid, errors = self.bridge.validate_ui_state(self.ui_state)
            if not is_valid:
                ui.notify(f'❌ Validation errors: {", ".join(errors)}', type='negative')
                return
            
            # Save to YAML
            config_path = Path(self.ui_state.project.project_directory) / 'user_config.yml'
            success, save_errors = self.bridge.save_to_yaml(self.ui_state, str(config_path))
            
            if success:
                self.ui_state.mark_saved()
                self._update_modified_indicators()
                ui.notify('✅ Configuration saved successfully', type='positive')
            else:
                ui.notify(f'❌ Save failed: {", ".join(save_errors)}', type='negative')
                
        except Exception as e:
            ui.notify(f'❌ Failed to save configuration: {str(e)}', type='negative')
    
    async def configure_project(self) -> None:
        """Configure the project (run docker compose)."""
        ui.notify('⚙️ Configure functionality not yet implemented', type='warning')
    
    async def download_project(self) -> None:
        """Download project as archive."""
        ui.notify('📦 Download functionality not yet implemented', type='warning')
    
    def change_project(self) -> None:
        """Change to a different project."""
        # Reset to initial state
        self.app_state = AppState.INITIAL
        self.ui_state = AppUIState()
        self.update_ui_state()
    
    def browse_directory(self) -> None:
        """Browse for directory (placeholder)."""
        ui.notify('📂 Directory browser not yet implemented', type='warning')
    
    def generate_temp_directory(self, input_field: ui.input) -> None:
        """Generate a new temporary directory."""
        new_dir = self._generate_default_project_dir()
        input_field.set_value(new_dir)
    
    def update_ui_state(self) -> None:
        """Update all UI elements based on current state."""
        # Update visibility of major sections
        self._update_initial_content_visibility()
        self._update_active_content_visibility()
        
        # Update all bound elements
        if self.app_state == AppState.ACTIVE:
            self._update_project_dir_label()
            self._update_modified_indicators()
            self._update_error_indicators()
            self._update_tab_styling()
            
            # Update visibility of state-dependent elements
            if self.header_container:
                for child in self.header_container.default_slot.children:
                    self._bind_to_active_state(child)
            
            if self.project_info_bar:
                self._bind_to_active_state(self.project_info_bar)
            
            if self.tab_nav_container:
                self._bind_to_active_state(self.tab_nav_container)
            
            if self.status_bar_container:
                self._bind_to_active_state(self.status_bar_container)


# Main entry point
def create_app() -> None:
    """Create and setup the PeiDocker Web GUI application."""
    gui = PeiDockerWebGUI()
    
    @ui.page('/')
    def index() -> None:
        gui.setup_ui()
    
    ui.run(title='PeiDocker Web GUI', port=8080)


if __name__ == '__main__':
    create_app()