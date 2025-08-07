"""
Environment tab for PeiDocker Web GUI - Refactored with data binding.

This tab handles environment variables and device configuration
including GPU support for container access, using NiceGUI's data binding.
Shows both Stage-1 and Stage-2 configurations separately.
"""

from typing import TYPE_CHECKING, Optional, Any, Dict, List
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab
from pei_docker.webgui.constants import DeviceTypes

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class EnvironmentTab(BaseTab):
    """Environment configuration tab with data binding."""
    
    def __init__(self, app: 'PeiDockerWebGUI') -> None:
        super().__init__(app)
        # Separate containers for each stage's environment variables
        self.stage1_env_container: Optional[ui.column] = None
        self.stage2_env_container: Optional[ui.column] = None
        self.stage1_env_rows: List[Dict[str, Any]] = []
        self.stage2_env_rows: List[Dict[str, Any]] = []
    
    def render(self) -> ui.element:
        """Render the environment tab content with data binding for both stages."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '⚙️ Environment Configuration',
                'Configure environment variables and device access for both stages'
            )
            
            # Stage-1 Environment Configuration
            with self.create_card('🏗️ Stage-1 Environment'):
                self._render_stage_environment('stage1', self.app.ui_state.stage_1.environment)
            
            # Stage-2 Environment Configuration  
            with self.create_card('🏗️ Stage-2 Environment'):
                self._render_stage_environment('stage2', self.app.ui_state.stage_2.environment)
        
        return container
    
    def _render_stage_environment(self, stage: str, stage_env: Any) -> None:
        """Render environment configuration for a specific stage."""
        # Layout with two columns
        with ui.row().classes('w-full gap-6'):
            # Left column - Environment Variables
            with ui.column().classes('w-full'):
                with self.create_form_group('Environment Variables',
                                          'Set custom environment variables. These will be saved in YAML format as \'VAR=value\''):
                    
                    # Environment variables container
                    with ui.column().classes('w-full mb-4') as env_container:
                        if stage == 'stage1':
                            self.stage1_env_container = env_container
                        else:
                            self.stage2_env_container = env_container
                        self._render_env_variables(stage, stage_env)
                    
                    # Add environment variable button
                    ui.button('➕ Add Environment Variable', 
                             on_click=lambda s=stage, se=stage_env: self._add_env_variable(s, se)) \
                        .classes('bg-blue-600 hover:bg-blue-700 text-white') \
                        .props(f'data-testid="{stage}-add-env-var-btn"')
            
            # Right column - Device Configuration
            with ui.column().classes('w-full'):
                with self.create_form_group('Device Type', 'Select the type of hardware access needed'):
                    # Bind device type select to UI state
                    device_select = ui.select(
                        options={
                            DeviceTypes.CPU: 'CPU Only',
                            DeviceTypes.GPU: 'GPU Support'
                        },
                        value=DeviceTypes.CPU
                    ).classes('w-full').bind_value(stage_env, 'device_type') \
                        .props(f'data-testid="{stage}-device-type-select"')
                    
                    # Update gpu_enabled when device_type changes
                    def on_device_change(e: Any, env: Any = stage_env) -> None:
                        env.gpu_enabled = (e.value == DeviceTypes.GPU)
                        self.app.ui_state.mark_modified()
                    
                    device_select.on_value_change(lambda e, se=stage_env: on_device_change(e, se))
                
                # GPU Configuration (conditionally visible)
                with ui.column().classes('mt-6 w-full') as gpu_config:
                    gpu_config.bind_visibility_from(stage_env, 'device_type', lambda v: v == DeviceTypes.GPU)
                    
                    with self.create_form_group('GPU Configuration', 
                                              'GPU support enabled - all available GPUs will be accessible in the container. To control GPU usage, you can either modify the generated docker compose file directly, or use "CUDA_VISIBLE_DEVICES" environment variable inside container.'):
                        pass
    
    def _render_env_variables(self, stage: str, stage_env: Any) -> None:
        """Render environment variables from the UI state for a specific stage."""
        container = self.stage1_env_container if stage == 'stage1' else self.stage2_env_container
        rows = self.stage1_env_rows if stage == 'stage1' else self.stage2_env_rows
        
        if not container:
            return
        
        # Clear existing UI elements
        container.clear()
        rows.clear()
        
        # Render each environment variable
        for key, value in stage_env.env_vars.items():
            self._create_env_variable_row(stage, stage_env, key, value)
    
    def _create_env_variable_row(self, stage: str, stage_env: Any, key: str = '', value: str = '') -> None:
        """Create a single environment variable row with data binding."""
        container = self.stage1_env_container if stage == 'stage1' else self.stage2_env_container
        rows = self.stage1_env_rows if stage == 'stage1' else self.stage2_env_rows
        
        if not container:
            return
        
        with container:
            with ui.card().classes('w-full p-3 mb-3 no-wrap') as variable_card:
                # Variable configuration
                with ui.row().classes('items-center gap-3 w-full'):
                    # Variable name input
                    name_input = ui.input(
                        placeholder='VARIABLE_NAME',
                        value=key
                    ).classes('flex-1').props(f'data-testid="{stage}-env-var-name-{key}"')
                    
                    # Equals sign
                    ui.label('=').classes('font-bold text-lg text-gray-700')
                    
                    # Variable value input
                    value_input = ui.input(
                        placeholder='value',
                        value=value
                    ).classes('flex-1').props(f'data-testid="{stage}-env-var-value-{key}"')
                    
                    # Remove button
                    remove_btn = ui.button(
                        '🗑️ Remove',
                        on_click=lambda k=key, s=stage, se=stage_env: self._remove_env_variable(s, se, k)
                    ).classes('bg-red-600 hover:bg-red-700 text-white px-3 py-1') \
                        .props(f'data-testid="{stage}-remove-env-var-{key}"')
                    
                    # Store row data
                    row_data = {
                        'card': variable_card,
                        'name_input': name_input,
                        'value_input': value_input,
                        'original_key': key
                    }
                    rows.append(row_data)
                    
                    # Handle name changes (need to update dict key)
                    def on_name_change(e: Any, data: Dict[str, Any] = row_data, env: Any = stage_env) -> None:
                        new_name = e.value.strip()
                        old_key = data['original_key']
                        
                        if new_name and new_name != old_key:
                            # Get current value
                            current_value = env.env_vars.get(old_key, '')
                            
                            # Remove old key and add new one
                            if old_key in env.env_vars:
                                del env.env_vars[old_key]
                            env.env_vars[new_name] = current_value
                            
                            # Update original key reference
                            data['original_key'] = new_name
                        
                        self.app.ui_state.mark_modified()
                    
                    # Handle value changes
                    def on_value_change(e: Any, data: Dict[str, Any] = row_data, env: Any = stage_env) -> None:
                        key_name = data['original_key']
                        if key_name:
                            env.env_vars[key_name] = e.value
                            self.app.ui_state.mark_modified()
                    
                    name_input.on_value_change(on_name_change)
                    value_input.on_value_change(on_value_change)
    
    def _add_env_variable(self, stage: str, stage_env: Any) -> None:
        """Add a new environment variable for a specific stage."""
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
        self._create_env_variable_row(stage, stage_env, var_name, '')
        
        # Mark as modified
        self.app.ui_state.mark_modified()
    
    def _remove_env_variable(self, stage: str, stage_env: Any, key: str) -> None:
        """Remove an environment variable from a specific stage."""
        rows = self.stage1_env_rows if stage == 'stage1' else self.stage2_env_rows
        
        # Remove from model
        if key in stage_env.env_vars:
            del stage_env.env_vars[key]
        
        # Find and remove the UI row
        for row_data in rows[:]:
            if row_data['original_key'] == key:
                row_data['card'].delete()
                rows.remove(row_data)
                break
        
        # Mark as modified
        self.app.ui_state.mark_modified()
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate environment configuration for both stages."""
        errors = []
        
        # Validate Stage-1 environment variables
        for key, value in self.app.ui_state.stage_1.environment.env_vars.items():
            if not key:
                errors.append("Stage-1: Environment variable name cannot be empty")
            elif not key.replace('_', '').replace('-', '').isalnum():
                errors.append(f"Stage-1: Invalid environment variable name: {key}")
            elif key[0].isdigit():
                errors.append(f"Stage-1: Environment variable name cannot start with a number: {key}")
        
        # Validate Stage-2 environment variables
        for key, value in self.app.ui_state.stage_2.environment.env_vars.items():
            if not key:
                errors.append("Stage-2: Environment variable name cannot be empty")
            elif not key.replace('_', '').replace('-', '').isalnum():
                errors.append(f"Stage-2: Invalid environment variable name: {key}")
            elif key[0].isdigit():
                errors.append(f"Stage-2: Environment variable name cannot start with a number: {key}")
        
        # No additional GPU validation needed - device_type is either CPU or GPU
        
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
        if self.stage1_env_container:
            self._render_env_variables('stage1', self.app.ui_state.stage_1.environment)
        if self.stage2_env_container:
            self._render_env_variables('stage2', self.app.ui_state.stage_2.environment)