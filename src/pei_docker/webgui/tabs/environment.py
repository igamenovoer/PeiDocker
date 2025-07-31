"""
Environment tab for PeiDocker Web GUI.

This tab handles environment variables and device configuration
including GPU support for container access.
"""

from typing import TYPE_CHECKING
from nicegui import ui
from .base import BaseTab

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class EnvironmentTab(BaseTab):
    """Environment configuration tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.env_variables_container = None
        self.device_type_select = None
        self.gpu_config_container = None
        self.gpu_all_switch = None
        self.gpu_memory_input = None
        self.env_variable_count = 0
        self.env_variables_data = []
    
    def render(self) -> ui.element:
        """Render the environment tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '⚙️ Environment Configuration',
                'Configure environment variables and device access including GPU support for your container'
            )
            
            # Layout with two columns
            with ui.row().classes('w-full gap-6'):
                # Left column - Environment Variables
                with ui.column().classes('flex-1'):
                    with self.create_card('🌍 Environment Variables'):
                        with self.create_form_group('Environment Variables', 
                                                  'Set custom environment variables for your container'):
                            
                            # Environment variables container
                            with ui.column().classes('w-full mb-4') as env_container:
                                self.env_variables_container = env_container
                            
                            # Add environment variable button
                            ui.button('➕ Add Environment Variable', on_click=self._add_env_variable) \
                                .classes('bg-blue-600 hover:bg-blue-700 text-white')
                
                # Right column - Device Configuration
                with ui.column().classes('flex-1'):
                    with self.create_card('🖥️ Device Configuration'):
                        with self.create_form_group('Device Type', 'Select the type of hardware access needed'):
                            self.device_type_select = ui.select(
                                options={
                                    'cpu': 'CPU Only',
                                    'gpu': 'GPU Support'
                                },
                                value='cpu'
                            ).classes('max-w-md')
                            self.device_type_select.on('change', self._on_device_type_change)
                        
                        # GPU Configuration (initially hidden)
                        with ui.column().classes('mt-6') as gpu_config:
                            self.gpu_config_container = gpu_config
                            
                            with self.create_form_group('GPU Configuration'):
                                # Use all GPUs toggle
                                with ui.row().classes('items-center gap-4 mb-4'):
                                    self.gpu_all_switch = ui.switch('Use All GPUs', value=True)
                                    self.gpu_all_switch.on('change', self._on_gpu_config_change)
                                
                                with ui.column().classes('ml-2'):
                                    ui.label('Grant access to all available GPU devices') \
                                        .classes('text-sm text-gray-600 mb-4')
                                
                                # GPU Memory Limit
                                with self.create_form_group('GPU Memory Limit (optional)', 
                                                          'Limit GPU memory usage (Docker 19.03+ required)'):
                                    self.gpu_memory_input = ui.input(
                                        placeholder='e.g., 4GB or leave empty for no limit'
                                    ).classes('max-w-md')
                                    self.gpu_memory_input.on('input', self._on_gpu_config_change)
                        
                        # Hide GPU config initially
                        gpu_config.bind_visibility_from(self.device_type_select, 'value', lambda v: v == 'gpu')
            
            # Add initial example environment variables
            self._add_env_variable('NODE_ENV', 'development')
            self._add_env_variable('DEBUG', 'true')
        
        return container
    
    def _add_env_variable(self, name: str = '', value: str = ''):
        """Add a new environment variable configuration."""
        variable_id = f'env-variable-{self.env_variable_count}'
        
        with self.env_variables_container:
            with ui.card().classes('w-full p-3 mb-3') as variable_card:
                # Variable configuration
                with ui.row().classes('items-center gap-3'):
                    # Variable name input
                    name_input = ui.input(
                        placeholder='VARIABLE_NAME',
                        value=name
                    ).classes('flex-1')
                    
                    # Equals sign
                    ui.label('=').classes('font-bold text-lg text-gray-700')
                    
                    # Variable value input
                    value_input = ui.input(
                        placeholder='value',
                        value=value
                    ).classes('flex-1')
                    
                    # Remove button
                    ui.button('🗑️', on_click=lambda: self._remove_env_variable(variable_card, variable_id)) \
                        .classes('bg-red-600 hover:bg-red-700 text-white w-10 h-10 rounded')
                
                # Store variable data
                variable_data = {
                    'id': variable_id,
                    'name_input': name_input,
                    'value_input': value_input,
                    'card': variable_card
                }
                
                # Add event handlers
                name_input.on('input', lambda e, data=variable_data: self._on_env_variable_change(data))
                value_input.on('input', lambda e, data=variable_data: self._on_env_variable_change(data))
                
                self.env_variables_data.append(variable_data)
        
        self.env_variable_count += 1
        self._update_env_variables_config()
    
    def _remove_env_variable(self, variable_card, variable_id):
        """Remove an environment variable configuration."""
        variable_card.delete()
        
        # Remove from data list
        self.env_variables_data = [
            data for data in self.env_variables_data 
            if data['id'] != variable_id
        ]
        
        self._update_env_variables_config()
        self.mark_modified()
    
    def _on_env_variable_change(self, variable_data):
        """Handle environment variable input changes."""
        self._update_env_variables_config()
        self.mark_modified()
    
    def _on_device_type_change(self, e):
        """Handle device type selection changes."""
        device_type = e.value
        
        # Update configuration
        if 'device' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['device'] = {}
        
        self.app.data.config.stage_1['device']['type'] = device_type
        
        # Reset GPU config when switching to CPU
        if device_type == 'cpu':
            self.app.data.config.stage_1['device'].pop('gpu', None)
        
        self.mark_modified()
    
    def _on_gpu_config_change(self, e=None):
        """Handle GPU configuration changes."""
        if self.device_type_select.value != 'gpu':
            return
        
        # Update configuration
        if 'device' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['device'] = {}
        if 'gpu' not in self.app.data.config.stage_1['device']:
            self.app.data.config.stage_1['device']['gpu'] = {}
        
        gpu_config = self.app.data.config.stage_1['device']['gpu']
        
        # Update GPU all setting
        if self.gpu_all_switch:
            gpu_config['all'] = self.gpu_all_switch.value
        
        # Update GPU memory limit
        if self.gpu_memory_input:
            memory_limit = self.gpu_memory_input.value.strip()
            if memory_limit:
                gpu_config['memory'] = memory_limit
            else:
                gpu_config.pop('memory', None)
        
        self.mark_modified()
    
    def _update_env_variables_config(self):
        """Update the environment variables configuration."""
        env_vars = {}
        
        for variable_data in self.env_variables_data:
            name = variable_data['name_input'].value.strip()
            value = variable_data['value_input'].value.strip()
            
            if name and value:
                env_vars[name] = value
        
        # Update configuration
        if 'environment' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['environment'] = {}
        
        self.app.data.config.stage_1['environment']['variables'] = env_vars
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate environment configuration."""
        errors = []
        
        # Validate environment variables
        variable_names = set()
        
        for i, variable_data in enumerate(self.env_variables_data):
            name = variable_data['name_input'].value.strip()
            value = variable_data['value_input'].value.strip()
            
            if name or value:  # If either field has content
                if not name:
                    errors.append(f"Environment variable {i+1}: Variable name is required")
                elif not value:
                    errors.append(f"Environment variable {i+1}: Variable value is required")
                else:
                    # Check for valid variable name format
                    if not name.isidentifier():
                        errors.append(f"Environment variable {i+1}: '{name}' is not a valid variable name")
                    
                    # Check for duplicate names
                    if name in variable_names:
                        errors.append(f"Environment variable {i+1}: Duplicate variable name '{name}'")
                    else:
                        variable_names.add(name)
        
        # Validate GPU configuration
        if self.device_type_select and self.device_type_select.value == 'gpu':
            if self.gpu_memory_input and self.gpu_memory_input.value.strip():
                memory_value = self.gpu_memory_input.value.strip()
                # Basic validation for memory format (should end with GB, MB, etc.)
                if not any(memory_value.upper().endswith(unit) for unit in ['GB', 'MB', 'KB', 'G', 'M', 'K']):
                    errors.append("GPU memory limit should specify units (e.g., '4GB', '512MB')")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> dict:
        """Get environment configuration data."""
        return {
            'stage_1': {
                'environment': self.app.data.config.stage_1.get('environment', {}),
                'device': self.app.data.config.stage_1.get('device', {})
            }
        }
    
    def set_config_data(self, data: dict):
        """Set environment configuration data."""
        stage_1_config = data.get('stage_1', {})
        
        # Set device configuration
        device_config = stage_1_config.get('device', {})
        if self.device_type_select:
            self.device_type_select.set_value(device_config.get('type', 'cpu'))
        
        # Set GPU configuration
        gpu_config = device_config.get('gpu', {})
        if self.gpu_all_switch:
            self.gpu_all_switch.set_value(gpu_config.get('all', True))
        
        if self.gpu_memory_input:
            self.gpu_memory_input.set_value(gpu_config.get('memory', ''))
        
        # Set environment variables
        env_config = stage_1_config.get('environment', {})
        variables = env_config.get('variables', {})
        
        # Clear existing variables
        if self.env_variables_container:
            self.env_variables_container.clear()
            self.env_variables_data = []
            self.env_variable_count = 0
        
        # Add loaded environment variables
        for name, value in variables.items():
            self._add_env_variable(name, str(value))
        
        # If no variables were loaded, add the default examples
        if not variables:
            self._add_env_variable('NODE_ENV', 'development')
            self._add_env_variable('DEBUG', 'true')