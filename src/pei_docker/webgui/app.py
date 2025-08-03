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

from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments

from .models import AppData, AppState, TabName, ProjectState
from .utils import ProjectManager, FileOperations, ValidationManager, RealTimeValidator
from .tabs import (
    ProjectTab, SSHTab, NetworkTab, EnvironmentTab, 
    StorageTab, ScriptsTab, SummaryTab
)

class PeiDockerWebGUI:
    """Main PeiDocker Web GUI Application using NiceGUI."""
    
    def __init__(self) -> None:
        self.data = AppData()
        self.project_manager = ProjectManager()
        self.file_ops = FileOperations()
        
        # Validation system
        self.validation_manager = ValidationManager()
        self.real_time_validator = RealTimeValidator(self.data, self.validation_manager)
        
        # Tab implementations
        self.tabs = {
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
        
        # Render initial active tab since we start in ACTIVE state
        self.render_active_tab()
    
    def create_header(self) -> None:
        """Create the header with logo and action buttons."""
        with ui.row().classes('w-full bg-blue-600 text-white p-4 items-center justify-between') as header:
            self.header_container = header
            
            # Logo
            ui.label('🐳 PeiDocker Web GUI').classes('text-xl font-bold')
            
            # Action buttons (only shown in active state)
            with ui.row().classes('gap-2') as actions:
                ui.button('💾 Save', on_click=self.save_configuration) \
                    .classes('bg-green-600 hover:bg-green-700') \
                    .bind_visibility_from(self.data, 'app_state', 
                                        lambda state: state == AppState.ACTIVE)
                
                ui.button('⚙️ Configure', on_click=self.configure_project) \
                    .classes('bg-yellow-600 hover:bg-yellow-700') \
                    .bind_visibility_from(self.data, 'app_state', 
                                        lambda state: state == AppState.ACTIVE)
                
                ui.button('📦 Download', on_click=self.download_project) \
                    .classes('bg-blue-500 hover:bg-blue-600') \
                    .bind_visibility_from(self.data, 'app_state', 
                                        lambda state: state == AppState.ACTIVE)
    
    def create_project_info_bar(self) -> None:
        """Create the project info bar (shown only in active state)."""
        with ui.row().classes('w-full bg-gray-100 p-2 items-center') as info_bar:
            self.project_info_bar = info_bar
            
            ui.label('📁 Project:').classes('font-medium')
            ui.label().bind_text_from(self.data.project, 'directory', 
                                    lambda d: str(d) if d else '')
            
            # Status indicator
            with ui.row().classes('ml-auto items-center gap-2'):
                ui.icon('circle', size='sm').classes('text-orange-500') \
                    .bind_visibility_from(self.data.config, 'modified')
                ui.label('⚠️ Unsaved changes') \
                    .bind_visibility_from(self.data.config, 'modified')
                
                ui.icon('circle', size='sm').classes('text-green-500') \
                    .bind_visibility_from(self.data.config, 'modified', lambda m: not m)
                ui.label().bind_text_from(self.data.config, 'last_saved',
                                        lambda t: f'✅ Last saved: {t}' if t else '✅ All saved') \
                    .bind_visibility_from(self.data.config, 'modified', lambda m: not m)
                
                # Change Project button
                ui.button('🔄 Change Project', on_click=self.change_project) \
                    .classes('bg-gray-500 hover:bg-gray-600 text-white text-sm px-3 py-1 ml-2')
            
            # Bind visibility to active state
            info_bar.bind_visibility_from(self.data, 'app_state', 
                                        lambda state: state == AppState.ACTIVE)
    
    def create_tab_navigation(self) -> None:
        """Create the tab navigation bar."""
        with ui.row().classes('w-full bg-white border-b') as nav:
            self.tab_nav_container = nav
            
            # Tab buttons
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
                
                # Note: bind_classes_from not available in this NiceGUI version
                # TODO: Implement class binding when NiceGUI API supports it
                # For now, styling will be static
            
            # Bind visibility to active state
            nav.bind_visibility_from(self.data, 'app_state', 
                                   lambda state: state == AppState.ACTIVE)
    
    def create_main_content(self) -> None:
        """Create the main content area."""
        with ui.column().classes('flex-1 w-full p-6') as content:
            self.content_container = content
            
            # Initial state content (project selection)
            with ui.column().classes('max-w-md mx-auto mt-20') as initial_content:
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
                
                # Bind visibility to initial state
                initial_content.bind_visibility_from(self.data, 'app_state', 
                                                   lambda state: state == AppState.INITIAL)
            
            # Active project content (tabs)
            with ui.column().classes('w-full') as active_content:
                # Tab content container - will be populated by render_active_tab()
                self.active_tab_container = ui.column().classes('w-full')
                
                # Bind visibility to active state
                active_content.bind_visibility_from(self.data, 'app_state', 
                                                  lambda state: state == AppState.ACTIVE)
    
    def create_status_bar(self) -> None:
        """Create the status bar."""
        with ui.row().classes('w-full bg-gray-800 text-white p-2 items-center justify-between') as status:
            self.status_bar_container = status
            
            # Left side - status info
            with ui.row().classes('items-center gap-2'):
                ui.icon('info', size='sm')
                ui.label('Ready').bind_text_from(self.data, 'app_state',
                                               lambda state: '🟢 Project Active' if state == AppState.ACTIVE else '⚪ No Project')
            
            # Right side - version
            ui.label('🐳 PeiDocker v0.8.0').classes('text-sm text-gray-300')
    
    def update_ui_state(self) -> None:
        """Update UI components based on current state."""
        # This will be called reactively through NiceGUI's binding system
        pass
    
    def _safe_notify(self, message: str, type: Literal['positive', 'negative', 'warning', 'info'] = 'info', timeout: int = 3000) -> None:
        """Safely notify user, handling cases where UI context might not be available."""
        try:
            ui.notify(message, type=type, timeout=timeout)
        except RuntimeError:
            # No UI context available, just print to console
            print(f"[{type.upper()}] {message}")
    
    def _load_config_into_tabs(self) -> None:
        """Load configuration data into all tabs."""
        try:
            # Get configuration data from the loaded config
            config_data = {
                'stage_1': dict(self.data.config.stage_1),
                'stage_2': dict(self.data.config.stage_2)
            }
            
            # Load configuration into each tab
            for tab_name, tab in self.tabs.items():
                try:
                    tab.set_config_data(config_data)
                except Exception as e:
                    self._safe_notify(f'⚠️ Warning: Failed to load config for {tab_name.value} tab: {str(e)}', 
                                     type='warning', timeout=3000)
                    
        except Exception as e:
            self._safe_notify(f'❌ Error loading configuration into tabs: {str(e)}', type='negative')
    
    def run_real_time_validation(self) -> None:
        """Run real-time validation and update UI indicators."""
        try:
            # Get validation errors from the real-time validator
            validation_errors = self.real_time_validator.validate_all_tabs()
            
            # Clear existing validation errors
            self.data.clear_validation_errors()
            
            # Update validation errors in data model
            for tab_name, errors in validation_errors.items():
                tab_enum = TabName(tab_name)
                for error in errors:
                    self.data.add_validation_error(tab_enum, error)
            
            # Update tab button styling based on validation state
            self._update_tab_validation_indicators()
            
            # If summary tab is active, refresh it
            if self.data.tabs.active_tab == TabName.SUMMARY:
                summary_tab = self.tabs[TabName.SUMMARY]
                if hasattr(summary_tab, 'refresh_summary'):
                    summary_tab.refresh_summary()
                    
        except Exception as e:
            print(f"Error in real-time validation: {e}")
    
    def _update_tab_validation_indicators(self) -> None:
        """Update tab button indicators based on validation state."""
        # This would update the visual indicators on tab buttons
        # The actual implementation depends on the UI binding system
        pass
    
    def _collect_config_from_tabs(self) -> None:
        """Collect configuration data from all tabs and update self.data.config."""
        try:
            # Collect data from each tab and merge into config
            for tab_name, tab in self.tabs.items():
                try:
                    tab_config = tab.get_config_data()
                    
                    # Merge stage_1 data
                    if 'stage_1' in tab_config:
                        for key, value in tab_config['stage_1'].items():
                            if value is not None:  # Only update if value is not None
                                self.data.config.stage_1[key] = value
                    
                    # Merge stage_2 data
                    if 'stage_2' in tab_config:
                        for key, value in tab_config['stage_2'].items():
                            if value is not None:  # Only update if value is not None
                                self.data.config.stage_2[key] = value
                                
                except Exception as e:
                    print(f"Error collecting config from {tab_name.value} tab: {e}")
                    
        except Exception as e:
            print(f"Error in _collect_config_from_tabs: {e}")
    
    # Event handlers
    def switch_tab(self, tab: TabName) -> None:
        """Switch to a different tab."""
        # If there are unsaved changes, show a warning dialog
        if self.data.config.modified:
            # Create dialog for unsaved changes warning
            with ui.dialog() as dialog, ui.card():
                ui.label('⚠️ Unsaved Changes').classes('text-lg font-bold mb-2')
                ui.label('You have unsaved changes. Switch tabs without saving?').classes('mb-4')
                ui.label('Your changes will be lost if you do not save.').classes('text-sm text-red-600 mb-4')
                
                with ui.row().classes('gap-2'):
                    ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                    ui.button('🔄 Switch Anyway', 
                             on_click=lambda: self._do_switch_tab(tab, dialog)) \
                        .classes('bg-red-600 hover:bg-red-700')
            dialog.open()
        else:
            # No unsaved changes, just switch
            self._do_switch_tab_direct(tab)
    
    def _do_switch_tab(self, tab: TabName, dialog: ui.dialog) -> None:
        """Handle tab switch after user confirms discarding changes."""
        dialog.close()
        
        # Create async task to reload configuration and switch tabs
        async def reload_and_switch() -> None:
            try:
                if self.data.project.directory:
                    # Load the saved user_config.yml
                    success = await self.file_ops.load_configuration(
                        self.data.project.directory,
                        self.data.config
                    )
                    if success:
                        # Load configuration into all tabs
                        self._load_config_into_tabs()
                        
                        # Now switch to the new tab
                        self._do_switch_tab_direct(tab)
                    else:
                        ui.notify('⚠️ Could not reload saved configuration', type='warning')
            except Exception as e:
                ui.notify(f'❌ Error reloading configuration: {str(e)}', type='negative')
        
        # Schedule the async task
        asyncio.create_task(reload_and_switch())
    
    def _do_switch_tab_direct(self, tab: TabName) -> None:
        """Directly switch to a tab without any checks."""
        self.data.tabs.active_tab = tab
        self.render_active_tab()
    
    def render_active_tab(self) -> None:
        """Render the content of the currently active tab."""
        # Clear current content and render active tab
        if (self.data.app_state == AppState.ACTIVE and 
            hasattr(self, 'active_tab_container') and 
            self.active_tab_container is not None):
            self.active_tab_container.clear()
            
            # Get the active tab implementation and render it
            active_tab = self.tabs[self.data.tabs.active_tab]
            
            with self.active_tab_container:
                # Center the tab content
                with ui.row().classes('w-full justify-center'):
                    # Render the tab content
                    active_tab.render()
            
            # If this is the summary tab, refresh its data
            if self.data.tabs.active_tab == TabName.SUMMARY:
                if hasattr(active_tab, 'refresh_summary'):
                    active_tab.refresh_summary()
    
    async def create_project(self, directory_path: str) -> None:
        """Create a new project."""
        if not directory_path.strip():
            ui.notify('❌ Please enter a project directory path', type='negative')
            return
        
        try:
            project_dir = Path(directory_path).resolve()
            success = await self.project_manager.create_project(project_dir)
            
            if success:
                # Set project data
                self.data.project.directory = project_dir
                self.data.project.name = project_dir.name
                self.data.app_state = AppState.ACTIVE
                
                # Initialize first tab
                self.data.tabs.active_tab = TabName.PROJECT
                self.render_active_tab()
                
                ui.notify(f'✅ Project created successfully at {project_dir}', type='positive')
            else:
                ui.notify('❌ Failed to create project', type='negative')
                
        except Exception as e:
            ui.notify(f'❌ Error creating project: {str(e)}', type='negative')
    
    async def load_project(self, directory_path: str) -> None:
        """Load an existing project."""
        if not directory_path.strip():
            self._safe_notify('❌ Please enter a project directory path', type='negative')
            return
        
        try:
            project_dir = Path(directory_path).resolve()
            
            if not project_dir.exists():
                self._safe_notify('❌ Project directory does not exist', type='negative')
                return
            
            # Check if this looks like a PeiDocker project
            config_file = project_dir / 'user_config.yml'
            if not config_file.exists():
                self._safe_notify('⚠️ No user_config.yml found in directory. Not a PeiDocker project?', type='warning')
                return
            
            # Load configuration
            success = await self.file_ops.load_configuration(project_dir, self.data.config)
            
            if success:
                # Set project data
                self.data.project.directory = project_dir
                self.data.project.name = project_dir.name
                self.data.app_state = AppState.ACTIVE
                
                # Load configuration into tabs
                self._load_config_into_tabs()
                
                # Initialize first tab
                self.data.tabs.active_tab = TabName.PROJECT
                self.render_active_tab()
                
                self._safe_notify(f'✅ Project loaded successfully from {project_dir}', type='positive')
            else:
                self._safe_notify('❌ Failed to load project configuration', type='negative')
                
        except Exception as e:
            self._safe_notify(f'❌ Error loading project: {str(e)}', type='negative')
    
    def browse_directory(self) -> None:
        """Open directory browser."""
        ui.notify('🔄 Directory browser coming soon', type='info')
    
    def _generate_default_project_dir(self) -> str:
        """Generate a default project directory path."""
        temp_dir = Path(tempfile.gettempdir()) / f"peidocker-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        return str(temp_dir)
    
    def generate_temp_directory(self, input_field: ui.input) -> None:
        """Generate a temporary directory path."""
        temp_dir = self._generate_default_project_dir()
        input_field.set_value(temp_dir)
        ui.notify('🎲 Generated new temporary directory path', type='info', timeout=2000)
    
    def change_project(self) -> None:
        """Switch to a different project (return to initial state)."""
        if self.data.config.modified:
            # Show confirmation dialog for unsaved changes
            with ui.dialog() as dialog, ui.card():
                ui.label('⚠️ Unsaved Changes').classes('text-lg font-bold mb-2')
                ui.label('You have unsaved changes. Switch to a different project?').classes('mb-4')
                ui.label('Any unsaved changes will be lost.').classes('text-sm text-red-600 mb-4')
                
                with ui.row().classes('gap-2'):
                    ui.button('Cancel', on_click=dialog.close).classes('bg-gray-500 hover:bg-gray-600')
                    ui.button('🔄 Switch Project', 
                             on_click=lambda: self._do_switch_project(dialog)) \
                        .classes('bg-red-600 hover:bg-red-700')
            dialog.open()
        else:
            self._do_change_project()
    
    def _do_switch_project(self, dialog: ui.dialog) -> None:
        """Close dialog and switch project."""
        dialog.close()
        self._do_change_project()
    
    def _do_change_project(self) -> None:
        """Actually perform the project change."""
        # Reset to initial state
        self.data.app_state = AppState.INITIAL
        self.data.project.directory = None
        self.data.project.name = None
        self.data.project.is_configured = False
        
        # Clear configuration
        self.data.config.modified = False
        self.data.config.last_saved = None
        
        # Re-render the UI to show initial state
        self.render_active_tab()
        
        ui.notify('✅ Switched to project selection', type='positive')
    
    async def save_configuration(self) -> None:
        """Save the current configuration."""
        if self.data.app_state != AppState.ACTIVE:
            return
        
        try:
            if self.data.project.directory is None:
                ui.notify('❌ No active project directory', type='negative')
                return
            
            # Collect configuration data from all tabs before saving
            self._collect_config_from_tabs()
            
            success = await self.file_ops.save_configuration(
                self.data.project.directory, 
                self.data.config
            )
            
            if success:
                self.data.mark_saved()
                ui.notify('✅ Configuration saved successfully', type='positive')
            else:
                ui.notify('❌ Failed to save configuration', type='negative')
                
        except Exception as e:
            ui.notify(f'❌ Error saving configuration: {str(e)}', type='negative')
    
    async def configure_project(self) -> None:
        """Run pei-docker-cli configure on the project."""
        if self.data.app_state != AppState.ACTIVE:
            return
        
        try:
            if self.data.project.directory is None:
                ui.notify('❌ No active project directory', type='negative')
                return
            
            success = await self.project_manager.configure_project(self.data.project.directory)
            
            if success:
                self.data.project.is_configured = True
                self.data.project.last_configure_success = True
                ui.notify('✅ Project configured successfully', type='positive')
            else:
                self.data.project.last_configure_success = False
                ui.notify('❌ Project configuration failed', type='negative')
                
        except Exception as e:
            ui.notify(f'❌ Error configuring project: {str(e)}', type='negative')
    
    async def download_project(self) -> None:
        """Create and download project ZIP file."""
        if self.data.app_state != AppState.ACTIVE:
            return
        
        try:
            if self.data.project.directory is None:
                ui.notify('❌ No active project directory', type='negative')
                return
            
            zip_path = await self.file_ops.create_project_zip(self.data.project.directory)
            if zip_path:
                # Serve the ZIP file for download
                url_path = app.add_static_file(local_file=str(zip_path), single_use=True)
                ui.download(url_path, f'{self.data.project.name}.zip')
                ui.notify('✅ Project download started', type='positive')
            else:
                ui.notify('❌ Failed to create project ZIP', type='negative')
                
        except Exception as e:
            ui.notify(f'❌ Error creating download: {str(e)}', type='negative')

def create_app(host: str = '0.0.0.0', port: int = 8080, **kwargs: Any) -> PeiDockerWebGUI:
    """Create and configure the PeiDocker Web GUI application."""
    gui = PeiDockerWebGUI()
    gui.setup_ui()
    return gui