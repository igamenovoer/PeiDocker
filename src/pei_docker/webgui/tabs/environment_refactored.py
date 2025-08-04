"""
Environment tab for PeiDocker Web GUI (Refactored with bindable dataclasses).

This tab handles environment variables and device configuration
including GPU support for container access, using NiceGUI's bindable
dataclasses for automatic UI synchronization.
"""

from typing import TYPE_CHECKING, Optional, Any, Dict, List
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab

if TYPE_CHECKING:
    from pei_docker.webgui.models.ui_state import AppUIState

class EnvironmentTab(BaseTab):
    """Environment configuration tab with reactive data binding."""
    
    def __init__(self, app_state: 'AppUIState', stage: int) -> None:
        # Store reference to app state instead of old app
        self.state = app_state
        self.stage = stage
        # Get reference to the appropriate stage's environment config
        self.env_config = getattr(app_state, f'stage_{stage}').environment
        
        # UI element references for dynamic content
        self.env_vars_container: Optional[ui.column] = None
        self.env_var_inputs: Dict[str, Dict[str, ui.input]] = {}
    
    def render(self) -> ui.element:
        """Render environment tab with automatic binding."""
        
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
                            self.env_vars_container = ui.column().classes('w-full mb-4')
                            self.render_env_vars()
                            
                            # Add environment variable button
                            ui.button('➕ Add Environment Variable', on_click=self.add_env_var) \
                                .classes('bg-blue-600 hover:bg-blue-700 text-white')
                
                # Right column - Device Configuration
                with ui.column().classes('w-full'):
                    with self.create_card('🖥️ Device Configuration'):
                        with self.create_form_group('Device Type', 'Select the type of hardware access needed'):
                            # Device type select - automatically synced!
                            ui.select(
                                options={
                                    'cpu': 'CPU Only',
                                    'gpu': 'GPU Support'
                                },
                                label='Device Type'
                            ).bind_value(self.env_config, 'device_type').classes('w-full')
                        
                        # GPU Configuration (conditionally visible)
                        with ui.column().classes('mt-6 w-full').bind_visibility_from(
                            self.env_config, 'device_type', lambda v: v == 'gpu'
                        ):
                            with self.create_form_group('GPU Configuration'):
                                # GPU enabled switch (redundant with device_type but kept for clarity)
                                ui.switch('Enable GPU').bind_value(self.env_config, 'gpu_enabled')
                                
                                # GPU count selection
                                with ui.row().classes('items-center gap-4 mb-4'):
                                    ui.select(
                                        ['all', '1', '2', '4'], 
                                        value='all',
                                        label='GPU Count'
                                    ).bind_value(self.env_config, 'gpu_count').classes('w-48')
                                    
                                    ui.input(
                                        'CUDA Version',
                                        placeholder='12.4'
                                    ).bind_value(self.env_config, 'cuda_version').classes('w-32')
                                
                                # GPU Memory Limit
                                with self.create_form_group('GPU Memory Limit (optional)',
                                                          'Limit GPU memory usage (Docker 19.03+ required)'):
                                    ui.input(
                                        placeholder='e.g., 4GB or leave empty for no limit'
                                    ).bind_value(self.env_config, 'gpu_memory_limit').classes('w-full')
            
            # Watch for GPU enablement changes
            self.env_config.__class__.__dict__['device_type'].fget  # Access property descriptor
            # When device_type changes to 'gpu', enable gpu_enabled
            ui.timer(0.1, lambda: self._sync_gpu_enabled())
        
        return container
    
    def _sync_gpu_enabled(self) -> None:
        """Sync GPU enabled state with device type."""
        if self.env_config.device_type == 'gpu':
            self.env_config.gpu_enabled = True
        else:
            self.env_config.gpu_enabled = False
    
    @ui.refreshable
    def render_env_vars(self) -> None:
        """Render environment variables section with automatic updates."""
        if not self.env_vars_container:
            return
            
        with self.env_vars_container:
            # Clear previous inputs tracking
            self.env_var_inputs.clear()
            
            # Render each environment variable
            for key, value in list(self.env_config.env_vars.items()):
                with ui.card().classes('w-full p-3 mb-3') as card:
                    with ui.row().classes('items-center gap-3 w-full'):
                        # Variable name input
                        key_input = ui.input(
                            placeholder='VARIABLE_NAME',
                            value=key
                        ).classes('flex-1')
                        
                        # Store original key for tracking
                        original_key = key
                        
                        # Handle key changes
                        key_input.on('blur', lambda e, ok=original_key, ki=key_input: 
                                    self._update_env_var_key(ok, ki.value))
                        
                        # Equals sign
                        ui.label('=').classes('font-bold text-lg text-gray-700')
                        
                        # Variable value input - directly bound to the dict value
                        value_input = ui.input(
                            placeholder='value',
                            value=value
                        ).classes('flex-1')
                        
                        # Handle value changes
                        value_input.on('input', lambda e, k=key, vi=value_input:
                                      self._update_env_var_value(k, vi.value))
                        
                        # Remove button
                        ui.button(
                            '🗑️ Remove',
                            on_click=lambda k=key: self.remove_env_var(k)
                        ).classes('bg-red-600 hover:bg-red-700 text-white px-3 py-1')
                        
                        # Track inputs for this variable
                        self.env_var_inputs[key] = {
                            'key_input': key_input,
                            'value_input': value_input,
                            'card': card
                        }
    
    def add_env_var(self) -> None:
        """Add new environment variable."""
        # Generate unique key
        counter = len(self.env_config.env_vars) + 1
        new_key = f'NEW_VAR_{counter}'
        
        # Ensure key is unique
        while new_key in self.env_config.env_vars:
            counter += 1
            new_key = f'NEW_VAR_{counter}'
        
        # Add to dict - this triggers UI update automatically
        self.env_config.env_vars[new_key] = ''
        self.state.modified = True
        
        # Refresh the environment variables display
        self.render_env_vars.refresh()
    
    def remove_env_var(self, key: str) -> None:
        """Remove environment variable."""
        if key in self.env_config.env_vars:
            del self.env_config.env_vars[key]
            self.state.modified = True
            # Refresh the display
            self.render_env_vars.refresh()
    
    def _update_env_var_key(self, old_key: str, new_key: str) -> None:
        """Update environment variable key."""
        if old_key == new_key or not new_key.strip():
            return
        
        # Check if new key already exists
        if new_key in self.env_config.env_vars:
            ui.notify(f"Variable '{new_key}' already exists", type='warning')
            # Reset to old key
            if old_key in self.env_var_inputs:
                self.env_var_inputs[old_key]['key_input'].set_value(old_key)
            return
        
        # Update the key
        if old_key in self.env_config.env_vars:
            value = self.env_config.env_vars[old_key]
            del self.env_config.env_vars[old_key]
            self.env_config.env_vars[new_key] = value
            self.state.modified = True
            
            # Refresh display to update tracking
            self.render_env_vars.refresh()
    
    def _update_env_var_value(self, key: str, value: str) -> None:
        """Update environment variable value."""
        if key in self.env_config.env_vars:
            self.env_config.env_vars[key] = value
            self.state.modified = True
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate environment configuration."""
        errors = []
        
        # Validate environment variables
        variable_names = set()
        
        for key, value in self.env_config.env_vars.items():
            if not key.strip():
                errors.append("Environment variable name cannot be empty")
            elif not value.strip():
                errors.append(f"Environment variable '{key}' has no value")
            else:
                # Check for valid variable name format
                if not key.replace('_', '').replace('-', '').isalnum():
                    errors.append(f"Environment variable '{key}' contains invalid characters")
                elif key[0].isdigit():
                    errors.append(f"Environment variable '{key}' cannot start with a number")
                
                # Check for duplicate names (shouldn't happen with dict, but just in case)
                if key in variable_names:
                    errors.append(f"Duplicate environment variable: '{key}'")
                else:
                    variable_names.add(key)
        
        # Validate GPU configuration
        if self.env_config.device_type == 'gpu' and self.env_config.gpu_memory_limit.strip():
            memory_value = self.env_config.gpu_memory_limit.strip()
            # Basic validation for memory format
            if not any(memory_value.upper().endswith(unit) for unit in ['GB', 'MB', 'KB', 'G', 'M', 'K']):
                errors.append("GPU memory limit should specify units (e.g., '4GB', '512MB')")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get environment configuration data from bindable state."""
        # Convert environment variables dict to list format
        env_vars = [f"{k}={v}" for k, v in self.env_config.env_vars.items() if k and v]
        
        # Build device configuration
        device_config: Dict[str, Any] = {
            'type': self.env_config.device_type
        }
        
        # Add GPU configuration if GPU is selected
        if self.env_config.device_type == 'gpu':
            gpu_config: Dict[str, Any] = {
                'all': self.env_config.gpu_count == 'all'
            }
            if self.env_config.gpu_memory_limit.strip():
                gpu_config['memory'] = self.env_config.gpu_memory_limit.strip()
            device_config['gpu'] = gpu_config
        
        # Return configuration for both stages
        stage_config = {
            'environment': env_vars,
            'device': device_config
        }
        
        # For stage 2, we don't need device config
        if self.stage == 2:
            return {
                f'stage_{self.stage}': {
                    'environment': env_vars
                }
            }
        
        return {
            f'stage_{self.stage}': stage_config
        }
    
    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set environment configuration data.
        
        This is called by the bridge layer when loading from YAML.
        The bridge layer handles the conversion, so this might not be needed
        in the refactored version.
        """
        # This method might be simplified or removed since the bridge layer
        # now handles loading data directly into the bindable state
        pass
    
    def mark_modified(self) -> None:
        """Mark configuration as modified."""
        if hasattr(self, 'state'):
            self.state.mark_modified()