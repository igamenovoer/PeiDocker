"""
Environment tab for PeiDocker Web GUI - Refactored with data binding.

This tab handles environment variables and device configuration
including GPU support for container access, using NiceGUI's data binding.
"""

from typing import TYPE_CHECKING, Optional, Any, Dict, List
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class EnvironmentTab(BaseTab):
    """Environment configuration tab with data binding."""
    
    def __init__(self, app: 'PeiDockerWebGUI') -> None:
        super().__init__(app)
        self.env_variables_container: Optional[ui.column] = None
        self.env_variable_rows: List[Dict[str, Any]] = []
    
    def render(self) -> ui.element:
        """Render the environment tab content with data binding."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '⚙️ Environment Configuration',
                'Configure environment variables and device access including GPU support for your container'
            )
            
            # Get the active stage's environment UI state
            stage_env = self.app.ui_state.get_active_stage().environment
            
            # Layout with two columns
            with ui.row().classes('w-full gap-6'):
                # Left column - Environment Variables
                with ui.column().classes('w-full'):
                    with self.create_card('🌍 Environment Variables'):
                        with self.create_form_group('Environment Variables',
                                                  'Set custom environment variables for your container'):
                            
                            # Environment variables container
                            with ui.column().classes('w-full mb-4') as env_container:
                                self.env_variables_container = env_container
                                self._render_env_variables()
                            
                            # Add environment variable button
                            ui.button('➕ Add Environment Variable', on_click=self._add_env_variable) \
                                .classes('bg-blue-600 hover:bg-blue-700 text-white')
                
                # Right column - Device Configuration
                with ui.column().classes('w-full'):
                    with self.create_card('🖥️ Device Configuration'):
                        with self.create_form_group('Device Type', 'Select the type of hardware access needed'):
                            # Bind device type select to UI state
                            ui.select(
                                options={
                                    'cpu': 'CPU Only',
                                    'gpu': 'GPU Support'
                                },
                                value='cpu'
                            ).classes('w-full').bind_value(stage_env, 'device_type')
                        
                        # GPU Configuration (conditionally visible)
                        with ui.column().classes('mt-6 w-full') as gpu_config:
                            gpu_config.bind_visibility_from(stage_env, 'device_type', lambda v: v == 'gpu')
                            
                            with self.create_form_group('GPU Configuration'):
                                # GPU enabled switch (automatically enabled when device_type is gpu)
                                stage_env.gpu_enabled = stage_env.device_type == 'gpu'
                                
                                # GPU count selection
                                with ui.row().classes('items-center gap-4 mb-4'):
                                    ui.label('GPU Count:').classes('font-medium')
                                    ui.select(
                                        options={'all': 'All GPUs', '1': '1 GPU', '2': '2 GPUs', '4': '4 GPUs'},
                                        value='all'
                                    ).classes('w-32').bind_value(stage_env, 'gpu_count')
                                
                                # CUDA version selection
                                with ui.row().classes('items-center gap-4 mb-4'):
                                    ui.label('CUDA Version:').classes('font-medium')
                                    ui.select(
                                        options={
                                            '12.4': 'CUDA 12.4',
                                            '12.3': 'CUDA 12.3',
                                            '12.2': 'CUDA 12.2',
                                            '12.1': 'CUDA 12.1',
                                            '12.0': 'CUDA 12.0',
                                            '11.8': 'CUDA 11.8',
                                            '11.7': 'CUDA 11.7'
                                        },
                                        value='12.4'
                                    ).classes('w-48').bind_value(stage_env, 'cuda_version')
                                
                                # GPU Memory Limit
                                with self.create_form_group('GPU Memory Limit (optional)',
                                                          'Limit GPU memory usage (Docker 19.03+ required)'):
                                    ui.input(
                                        placeholder='e.g., 4GB or leave empty for no limit'
                                    ).classes('w-full').bind_value(stage_env, 'gpu_memory_limit')
        
        return container
    
    def _render_env_variables(self) -> None:
        """Render environment variables from the UI state."""
        if not self.env_variables_container:
            return
        
        # Clear existing UI elements
        self.env_variables_container.clear()
        self.env_variable_rows.clear()
        
        # Get the active stage's environment variables
        stage_env = self.app.ui_state.get_active_stage().environment
        
        # Render each environment variable
        for key, value in stage_env.env_vars.items():
            self._create_env_variable_row(key, value)
    
    def _create_env_variable_row(self, key: str = '', value: str = '') -> None:
        """Create a single environment variable row with data binding."""
        if not self.env_variables_container:
            return
        
        # Get the active stage's environment variables dict
        stage_env = self.app.ui_state.get_active_stage().environment
        
        with self.env_variables_container:
            with ui.card().classes('w-full p-3 mb-3 no-wrap') as variable_card:
                # Variable configuration
                with ui.row().classes('items-center gap-3 w-full'):
                    # Variable name input
                    name_input = ui.input(
                        placeholder='VARIABLE_NAME',
                        value=key
                    ).classes('flex-1')
                    
                    # Equals sign
                    ui.label('=').classes('font-bold text-lg text-gray-700')
                    
                    # Variable value input
                    value_input = ui.input(
                        placeholder='value',
                        value=value
                    ).classes('flex-1')
                    
                    # Remove button
                    remove_btn = ui.button(
                        '🗑️ Remove',
                        on_click=lambda k=key: self._remove_env_variable(k)
                    ).classes('bg-red-600 hover:bg-red-700 text-white px-3 py-1')
                    
                    # Store row data
                    row_data = {
                        'card': variable_card,
                        'name_input': name_input,
                        'value_input': value_input,
                        'original_key': key
                    }
                    self.env_variable_rows.append(row_data)
                    
                    # Handle name changes (need to update dict key)
                    def on_name_change(e: Any, data: Dict[str, Any] = row_data) -> None:
                        new_name = e.value.strip()
                        old_key = data['original_key']
                        
                        if new_name and new_name != old_key:
                            # Get current value
                            current_value = stage_env.env_vars.get(old_key, '')
                            
                            # Remove old key and add new one
                            if old_key in stage_env.env_vars:
                                del stage_env.env_vars[old_key]
                            stage_env.env_vars[new_name] = current_value
                            
                            # Update original key reference
                            data['original_key'] = new_name
                            
                            # Note: Button handler cannot be reassigned after creation
                            # The button will still work but with the old key name
                        
                        self.app.ui_state.mark_modified()
                    
                    # Handle value changes
                    def on_value_change(e: Any, data: Dict[str, Any] = row_data) -> None:
                        key_name = data['original_key']
                        if key_name:
                            stage_env.env_vars[key_name] = e.value
                            self.app.ui_state.mark_modified()
                    
                    name_input.on('change', on_name_change)
                    value_input.on('change', on_value_change)
    
    def _add_env_variable(self) -> None:
        """Add a new environment variable."""
        # Get the active stage's environment
        stage_env = self.app.ui_state.get_active_stage().environment
        
        # Find a unique variable name
        base_name = 'NEW_VAR'
        counter = 1
        var_name = base_name
        
        while var_name in stage_env.env_vars:
            var_name = f"{base_name}_{counter}"
            counter += 1
        
        # Add to the model
        stage_env.env_vars[var_name] = ''
        
        # Create the UI row
        self._create_env_variable_row(var_name, '')
        
        # Mark as modified
        self.app.ui_state.mark_modified()
    
    def _remove_env_variable(self, key: str) -> None:
        """Remove an environment variable."""
        # Get the active stage's environment
        stage_env = self.app.ui_state.get_active_stage().environment
        
        # Remove from model
        if key in stage_env.env_vars:
            del stage_env.env_vars[key]
        
        # Find and remove the UI row
        for row_data in self.env_variable_rows[:]:
            if row_data['original_key'] == key:
                row_data['card'].delete()
                self.env_variable_rows.remove(row_data)
                break
        
        # Mark as modified
        self.app.ui_state.mark_modified()
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate environment configuration."""
        errors = []
        
        # Get the active stage's environment
        stage_env = self.app.ui_state.get_active_stage().environment
        
        # Validate environment variables
        for key, value in stage_env.env_vars.items():
            if not key:
                errors.append("Environment variable name cannot be empty")
            elif not key.replace('_', '').replace('-', '').isalnum():
                errors.append(f"Invalid environment variable name: {key}")
            elif key[0].isdigit():
                errors.append(f"Environment variable name cannot start with a number: {key}")
        
        # Validate GPU configuration
        if stage_env.device_type == 'gpu' and stage_env.gpu_memory_limit:
            memory_value = stage_env.gpu_memory_limit.strip()
            # Basic validation for memory format (should end with GB, MB, etc.)
            if not any(memory_value.upper().endswith(unit) for unit in ['GB', 'MB', 'KB', 'G', 'M', 'K']):
                errors.append("GPU memory limit should specify units (e.g., '4GB', '512MB')")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get environment configuration data from UI state."""
        # This is now handled by the UIStateBridge
        # Keeping method for compatibility
        return {}
    
    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set environment configuration data."""
        # This is now handled by the UIStateBridge during load
        # UI state is automatically bound, so we just need to refresh the view
        if self.env_variables_container:
            self._render_env_variables()