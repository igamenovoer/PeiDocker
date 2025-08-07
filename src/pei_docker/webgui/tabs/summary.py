"""
Summary tab for PeiDocker Web GUI - Refactored with data binding.

This tab provides a read-only view of the configuration with validation status
and YAML preview. All save/export actions are handled via the main app toolbar.
"""

from typing import TYPE_CHECKING, List, Tuple, Dict, Optional, Any
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab
import yaml

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class SummaryTab(BaseTab):
    """Summary and validation tab for configuration review."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.config_preview_container: Optional[ui.column] = None
        self.validation_container: Optional[ui.column] = None
    
    def render(self) -> ui.element:
        """Render the summary tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '📋 Configuration Summary',
                'Review your complete PeiDocker configuration'
            )
            
            # Validation Status
            self._create_validation_section()
            
            # Generated user_config.yml Preview
            self._create_config_preview()
            
            # Refresh the summary initially
            self.refresh_summary()
        
        return container
    
    def _create_validation_section(self) -> None:
        """Create the validation status section."""
        with self.create_card('✅ Validation Status'):
            with ui.column().classes('w-full') as validation_container:
                self.validation_container = validation_container
    
    def _create_config_preview(self) -> None:
        """Create the configuration preview section."""
        with self.create_card('📄 Generated user_config.yml Preview'):
            with ui.column().classes('w-full') as preview_container:
                self.config_preview_container = preview_container
    
    def refresh_summary(self) -> None:
        """Refresh the summary display with current configuration."""
        # Refresh validation status
        self._refresh_validation()
        
        # Refresh configuration preview
        self._refresh_config_preview()
    
    def _refresh_validation(self) -> None:
        """Refresh the validation status display."""
        if not self.validation_container:
            return
        
        self.validation_container.clear()
        
        with self.validation_container:
            # Validate using UIStateBridge
            is_valid, errors = self.app.bridge.validate_ui_state(self.app.ui_state)
            
            if is_valid:
                with ui.row().classes('items-center gap-2'):
                    ui.icon('check_circle', size='md').classes('text-green-600')
                    ui.label('Configuration is valid').classes('text-green-700 font-semibold')
            else:
                with ui.column().classes('gap-2'):
                    with ui.row().classes('items-center gap-2 mb-2'):
                        ui.icon('error', size='md').classes('text-red-600')
                        ui.label(f'Found {len(errors)} validation error(s)').classes('text-red-700 font-semibold')
                    
                    # List errors
                    for error in errors[:10]:  # Show max 10 errors
                        ui.label(f'• {error}').classes('text-red-600 text-sm ml-8')
                    
                    if len(errors) > 10:
                        ui.label(f'... and {len(errors) - 10} more errors').classes('text-red-600 text-sm ml-8 italic')
            
            # Show save status
            if self.app.ui_state.last_saved:
                ui.label(f'Last saved: {self.app.ui_state.last_saved}').classes('text-gray-600 text-sm mt-2')
            elif self.app.ui_state.modified:
                ui.label('Unsaved changes').classes('text-orange-600 text-sm mt-2')
    
    def _refresh_config_preview(self) -> None:
        """Refresh the configuration preview."""
        if not self.config_preview_container:
            return
        
        self.config_preview_container.clear()
        
        with self.config_preview_container:
            try:
                # Generate YAML preview using UIStateBridge internal method
                config_data = self.app.bridge._ui_to_user_config_format(self.app.ui_state)
                
                # Custom representer to ensure environment variables are quoted in the display
                def str_representer(dumper: Any, data: Any) -> Any:
                    # Force single quotes for strings that look like environment variables
                    if isinstance(data, str) and '=' in data:
                        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
                    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
                
                # Create a custom YAML dumper for display purposes
                class DisplayDumper(yaml.SafeDumper):
                    pass
                
                DisplayDumper.add_representer(str, str_representer)
                
                # Convert to YAML string with quotes for display clarity
                yaml_str = yaml.dump(config_data, Dumper=DisplayDumper, default_flow_style=False, 
                                   sort_keys=False, allow_unicode=True)
                
                # Display in a code block
                with ui.element('pre').classes('bg-gray-100 p-4 rounded overflow-x-auto text-sm'):
                    ui.html(f'<code class="language-yaml">{yaml_str}</code>')
                
            except Exception as e:
                ui.label(f'Error generating preview: {str(e)}').classes('text-red-600')
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the entire configuration."""
        # Use UIStateBridge for validation
        is_valid, errors = self.app.bridge.validate_ui_state(self.app.ui_state)
        return is_valid, errors
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get the complete configuration data."""
        # This tab doesn't contribute configuration data itself
        # It just displays and saves the combined data from all other tabs
        return {}
    
    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set configuration data for this tab."""
        # This tab doesn't have its own configuration to load
        # Just refresh the display
        self.refresh_summary()
    
    def create_card(self, title: Optional[str] = None) -> ui.element:
        """Create a consistent card container."""
        with ui.card().classes('w-full p-6 mb-6') as card:
            if title:
                ui.label(title).classes('text-xl font-bold text-gray-800 mb-4')
        return card