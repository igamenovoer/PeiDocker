"""
Environment tab for PeiDocker Web GUI.

This tab handles environment variables and device configuration
including GPU support for container access.
"""

from typing import TYPE_CHECKING, Optional, Any, Dict, List
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class EnvironmentTab(BaseTab):
    """Environment configuration tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI') -> None:
        super().__init__(app)
        self.env_variables_container: Optional[ui.column] = None
        self.device_type_select: Optional[ui.select] = None
        self.gpu_config_container: Optional[ui.column] = None
        self.gpu_all_switch: Optional[ui.switch] = None
        self.gpu_memory_input: Optional[ui.input] = None
        self.env_variable_count: int = 0
        self.env_variables_data: List[Dict[str, Any]] = []
    
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
                with ui.column().classes('w-full'):
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
                with ui.column().classes('w-full'):
                    with self.create_card('🖥️ Device Configuration'):
                        with self.create_form_group('Device Type', 'Select the type of hardware access needed'):
                            self.device_type_select = ui.select(
                                options={
                                    'cpu': 'CPU Only',
                                    'gpu': 'GPU Support'
                                },
                                value='cpu'
                            ).classes('w-full')
                            self.device_type_select.on('change', self._on_device_type_change)
                        
                        # GPU Configuration (initially hidden)
                        with ui.column().classes('mt-6 w-full') as gpu_config:
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
                                    ).classes('w-full')
                                    self.gpu_memory_input.on('input', self._on_gpu_config_change)
                        
                        # Hide GPU config initially
                        gpu_config.bind_visibility_from(self.device_type_select, 'value', lambda v: v == 'gpu')
            
            # Clear and initialize data when rendering
            self.env_variables_data = []
            self.env_variable_count = 0
            
            # Reload configuration from current state
            self.set_config_data({
                'stage_1': dict(self.app.data.config.stage_1),
                'stage_2': dict(self.app.data.config.stage_2)
            })
        
        return container
    
    def _add_env_variable(self, name: str = '', value: str = '') -> None:
        """Add a new environment variable configuration."""
        variable_id = f'env-variable-{self.env_variable_count}'
        
        if self.env_variables_container:
            with self.env_variables_container:
                with ui.card().classes('w-full p-3 mb-3 no-wrap') as variable_card:
                    # Variable configuration
                    with ui.row().classes('items-center gap-3 w-full'):
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
                        ui.button('🗑️ Remove', on_click=lambda: self._remove_env_variable(variable_card, variable_id)) \
                            .classes('bg-red-600 hover:bg-red-700 text-white px-3 py-1')
                    
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
    
    def _remove_env_variable(self, variable_card: ui.card, variable_id: str) -> None:
        """Remove an environment variable configuration."""
        variable_card.delete()
        
        # Remove from data list
        self.env_variables_data = [
            data for data in self.env_variables_data 
            if data['id'] != variable_id
        ]
        
        self._update_env_variables_config()
        self.mark_modified()
    
    def _on_env_variable_change(self, variable_data: Dict[str, Any]) -> None:
        """Handle environment variable input changes."""
        self._update_env_variables_config()
        self.mark_modified()
    
    def _on_device_type_change(self, e: Any) -> None:
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
    
    def _on_gpu_config_change(self, e: Optional[Any] = None) -> None:
        """Handle GPU configuration changes."""
        if not self.device_type_select or self.device_type_select.value != 'gpu':
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
    
    def _update_env_variables_config(self) -> None:
        """Update the environment variables configuration for both stages."""
        env_vars = {}
        
        for variable_data in self.env_variables_data:
            name = variable_data['name_input'].value.strip()
            value = variable_data['value_input'].value.strip()
            
            if name and value:
                env_vars[name] = value
        
        # Update configuration for both stages
        if 'environment' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['environment'] = []
        if 'environment' not in self.app.data.config.stage_2:
            self.app.data.config.stage_2['environment'] = []
        
        # Save as list format ['KEY=VALUE', ...] to both stages
        env_list = [f"{k}={v}" for k, v in env_vars.items()]
        self.app.data.config.stage_1['environment'] = env_list
        self.app.data.config.stage_2['environment'] = env_list
    
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
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get environment configuration data from UI components."""
        # Extract environment variables from UI
        env_vars = []
        for variable_data in self.env_variables_data:
            name = variable_data['name_input'].value.strip()
            value = variable_data['value_input'].value.strip()
            if name and value:
                env_vars.append(f"{name}={value}")
        
        # Extract device configuration from UI
        device_config: Dict[str, Any] = {
            'type': self.device_type_select.value if self.device_type_select else 'cpu'
        }
        
        # Add GPU configuration if GPU is selected
        if self.device_type_select and self.device_type_select.value == 'gpu':
            gpu_config: Dict[str, Any] = {
                'all': self.gpu_all_switch.value if self.gpu_all_switch else True
            }
            if self.gpu_memory_input and self.gpu_memory_input.value.strip():
                gpu_config['memory'] = self.gpu_memory_input.value.strip()
            device_config['gpu'] = gpu_config
        
        # Return configuration for both stages with same environment variables
        return {
            'stage_1': {
                'environment': env_vars,
                'device': device_config
            },
            'stage_2': {
                'environment': env_vars
            }
        }
    
    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set environment configuration data from both stages.
        
        This method can be invoked before the UI elements for this tab are
        rendered (e.g., when the project is first loaded and `_load_config_into_tabs`
        iterates through all tabs).  In that scenario the containers used to
        display environment variables are not available yet.  Performing the
        usual update workflow would therefore:
        
        1. Skip adding UI elements because the containers are `None`.
        2. Call `_update_env_variables_config`, which detects an empty
           `env_variables_data` list and consequently **overwrites** the loaded
           configuration with an empty environment list.
        
        To prevent this destructive behaviour we detect the "UI-not-ready"
        state early and **exit without touching either the UI or the in-memory
        configuration**.  Once the tab is actually rendered `render()` will
        call `set_config_data` again, this time with fully initialised UI
        containers, allowing the environment variables to be displayed and kept
        intact.
        """
        # Guard: if UI containers are not yet ready, do nothing to avoid wiping config
        if self.env_variables_container is None:
            return
        
        stage_1_config = data.get('stage_1', {})
        stage_2_config = data.get('stage_2', {})
        
        # Set device configuration (only in stage-1)
        device_config = stage_1_config.get('device', {})
        if self.device_type_select:
            self.device_type_select.set_value(device_config.get('type', 'cpu'))
        
        # Set GPU configuration
        gpu_config = device_config.get('gpu', {})
        if self.gpu_all_switch:
            self.gpu_all_switch.set_value(gpu_config.get('all', True))
        
        if self.gpu_memory_input:
            self.gpu_memory_input.set_value(gpu_config.get('memory', ''))
        
        # Combine environment variables from both stages
        # Stage-2 overrides stage-1 for duplicate keys
        combined_vars = {}
        
        # First, add stage-1 environment variables
        stage_1_env = stage_1_config.get('environment', [])
        if isinstance(stage_1_env, list):
            for env_str in stage_1_env:
                if '=' in env_str:
                    key, value = env_str.split('=', 1)
                    combined_vars[key.strip()] = value.strip()
        elif isinstance(stage_1_env, dict):
            for key, value in stage_1_env.get('variables', {}).items():
                combined_vars[key] = str(value)
        
        # Then, add/override with stage-2 environment variables
        stage_2_env = stage_2_config.get('environment', [])
        if isinstance(stage_2_env, list):
            for env_str in stage_2_env:
                if '=' in env_str:
                    key, value = env_str.split('=', 1)
                    combined_vars[key.strip()] = value.strip()
        elif isinstance(stage_2_env, dict):
            for key, value in stage_2_env.get('variables', {}).items():
                combined_vars[key] = str(value)
        
        # Clear existing variables
        if self.env_variables_container:
            self.env_variables_container.clear()
            self.env_variables_data = []
            self.env_variable_count = 0
        
        # Add combined environment variables
        for name, value in combined_vars.items():
            self._add_env_variable(name, str(value))