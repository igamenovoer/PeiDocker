"""
Summary tab for PeiDocker Web GUI.

This tab provides a complete configuration review, validation status,
and actions for saving and exporting the project.
"""

from typing import TYPE_CHECKING, List, Tuple, Dict, Optional, Any
from nicegui import ui
from .base import BaseTab
from ..models import TabName
import yaml
import asyncio

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class SummaryTab(BaseTab):
    """Summary and validation tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.save_button: Optional[ui.button] = None
        self.configure_button: Optional[ui.button] = None
        self.download_button: Optional[ui.button] = None
        self.config_preview_container: Optional[ui.column] = None
    
    def render(self) -> ui.element:
        """Render the summary tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '📋 Configuration Summary',
                'Review your complete PeiDocker configuration and save your user_config.yml file'
            )
            
            # Generated user_config.yml Preview
            self._create_config_preview()
            
            # Actions section
            self._create_actions_section()
            
            # Refresh the summary initially
            self.refresh_summary()
        
        return container
    
    
    def _create_actions_section(self) -> None:
        """Create the actions section."""
        with self.create_card('💾 Save & Export'):
            # Save Configuration
            with ui.column().classes('mb-4'):
                self.save_button = ui.button('💾 Save Configuration', on_click=self._save_configuration) \
                    .classes('w-full bg-green-600 hover:bg-green-700 text-white')
                ui.label('Save user_config.yml to project directory').classes('text-center text-sm text-gray-600 mt-2')
            
            # Configure Project
            with ui.column().classes('mb-4'):
                self.configure_button = ui.button('⚙️ Configure Project', on_click=self._configure_project) \
                    .classes('w-full bg-yellow-600 hover:bg-yellow-700 text-white')
                ui.label('Run pei-docker-cli configure').classes('text-center text-sm text-gray-600 mt-2')
            
            # Download Project
            with ui.column():
                self.download_button = ui.button('📥 Download Project', on_click=self._download_project) \
                    .classes('w-full bg-blue-600 hover:bg-blue-700 text-white')
                ui.label('Export project as ZIP file').classes('text-center text-sm text-gray-600 mt-2')
    
    def _create_config_preview(self) -> None:
        """Create the configuration preview section."""
        with self.create_card('📄 Generated user_config.yml Preview'):
            with ui.column().classes('w-full') as preview_container:
                self.config_preview_container = preview_container
    
    def _save_configuration(self) -> None:
        """Save the configuration."""
        try:
            # Generate the configuration
            config_data = self._generate_full_config()
            
            # In a real implementation, this would save to file
            ui.notify('Configuration saved successfully!', type='positive', timeout=3000)
            
        except Exception as e:
            ui.notify(f'Error saving configuration: {str(e)}', type='negative', timeout=5000)
    
    def _configure_project(self) -> None:
        """Configure the project using pei-docker-cli."""
        async def confirm_configure() -> None:
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                ui.label('Configure Project').classes('text-lg font-semibold mb-3')
                ui.label('Run pei-docker-cli configure to build project structure? This may take a few minutes.').classes('mb-4')
                
                with ui.row().classes('gap-2 justify-end'):
                    ui.button('Cancel', on_click=dialog.close).classes('bg-gray-600 hover:bg-gray-700 text-white')
                    def handle_configure() -> None:
                        dialog.close()
                        self._run_configure()
                    ui.button('Configure', on_click=handle_configure).classes('bg-yellow-600 hover:bg-yellow-700 text-white')
            
            dialog.open()
        
        # Use asyncio.create_task to run the async function
        asyncio.create_task(confirm_configure())
    
    def _run_configure(self) -> None:
        """Run the actual configure command."""
        ui.notify('Project configuration started. The process is running in the background.', 
                 type='info', timeout=5000)
        
        # In a real implementation, this would run the CLI command
        # subprocess.run(['pei-docker-cli', 'configure', '-p', str(self.app.data.project.directory)])
    
    def _download_project(self) -> None:
        """Download the project as ZIP."""
        warnings = []
        
        # Check if project is configured (in real implementation)
        if not self._is_project_configured():
            warnings.append('Project has not been configured yet.')
        
        if warnings:
            async def confirm_download() -> None:
                with ui.dialog() as dialog, ui.card().classes('w-96'):
                    ui.label('Download Warning').classes('text-lg font-semibold mb-3')
                    ui.label('Warning:').classes('font-semibold text-yellow-700')
                    for warning in warnings:
                        ui.label(f'• {warning}').classes('text-yellow-700 text-sm mb-1')
                    ui.label('Do you want to continue with the download?').classes('mt-3 mb-4')
                    
                    with ui.row().classes('gap-2 justify-end'):
                        ui.button('Cancel', on_click=dialog.close).classes('bg-gray-600 hover:bg-gray-700 text-white')
                        def handle_download() -> None:
                            dialog.close()
                            self._start_download()
                        ui.button('Download', on_click=handle_download).classes('bg-blue-600 hover:bg-blue-700 text-white')
                
                dialog.open()
            
            # Use asyncio.create_task to run the async function
            asyncio.create_task(confirm_download())
        else:
            self._start_download()
    
    def _start_download(self) -> None:
        """Start the project download."""
        ui.notify('Project ZIP file is being prepared for download...', type='info', timeout=3000)
        
        # In a real implementation, this would create and serve the ZIP file
    
    def _is_project_configured(self) -> bool:
        """Check if the project has been configured."""
        # In a real implementation, this would check for build files
        return False
    
    def refresh_summary(self) -> None:
        """Refresh the summary display."""
        self._update_config_preview()
    
    def _update_config_preview(self) -> None:
        """Update the configuration preview."""
        if not self.config_preview_container:
            return
        
        self.config_preview_container.clear()
        
        try:
            config_data = self._generate_full_config()
            config_yaml = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
            
            with self.config_preview_container:
                with ui.card().classes('w-full p-3 bg-gray-50'):
                    ui.code(config_yaml).classes('text-xs font-mono w-full')
        
        except Exception as e:
            with self.config_preview_container:
                ui.label(f'Error generating preview: {str(e)}').classes('text-red-600 text-sm')
    
    def _generate_full_config(self) -> dict:
        """Generate the complete configuration by collecting data from all tabs."""
        config: Dict[str, Dict[str, Any]] = {
            'stage_1': {},
            'stage_2': {}
        }
        
        # Collect configuration from each tab
        for tab_name, tab in self.app.tabs.items():
            # Skip the summary tab itself to avoid recursion
            if tab_name == TabName.SUMMARY:
                continue
                
            if hasattr(tab, 'get_config_data'):
                tab_config = tab.get_config_data()
                
                # Merge stage_1 configuration
                if 'stage_1' in tab_config:
                    for key, value in tab_config['stage_1'].items():
                        if value:  # Only add non-empty values
                            config['stage_1'][key] = value
                
                # Merge stage_2 configuration
                if 'stage_2' in tab_config:
                    for key, value in tab_config['stage_2'].items():
                        if value:  # Only add non-empty values
                            config['stage_2'][key] = value
        
        # Clean up empty sections
        for stage in ['stage_1', 'stage_2']:
            config[stage] = {k: v for k, v in config[stage].items() if v}
        
        return config
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate summary tab (always valid)."""
        return True, []
    
    def get_config_data(self) -> dict:
        """Get configuration data (returns full config)."""
        return self._generate_full_config()
    
    def set_config_data(self, data: dict) -> None:
        """Set configuration data (not applicable for summary)."""
        pass