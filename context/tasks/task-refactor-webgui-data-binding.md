# Task: Refactor WebGUI to Use Proper Data Binding with UI State Models

## Overview
This task involves refactoring the PeiDocker WebGUI to properly utilize NiceGUI's data binding capabilities with the bindable dataclasses defined in `ui_state.py`. The current implementation loses UI state when navigating between tabs because it doesn't properly bind UI elements to a persistent data model.

## Current Problems
1. **State Loss**: Script tab (and potentially other tabs) lose their inline editor content when navigating away
2. **No Data Binding**: Most tabs manually manage state instead of using NiceGUI's binding system
3. **Legacy Models**: App uses `legacy_models.py` (AppData) instead of `ui_state.py` (AppUIState)
4. **Inconsistent State Management**: Mix of manual state updates and partial binding

## Architecture Goals
1. **Single Source of Truth**: Use `AppUIState` from `ui_state.py` as the central UI state
2. **Automatic Binding**: All UI elements bind directly to the state model
3. **Type Safety**: Follow strongly-typed principles with proper type annotations
4. **Clean Separation**: UI state models → Bridge layer → Config models → YAML

## Refactoring Plan

### Phase 1: Update Core Application Structure

#### 1.1 Modify PeiDockerWebGUI class
```python
# src/pei_docker/webgui/app.py
from pei_docker.webgui.models.ui_state import AppUIState
from pei_docker.webgui.utils.bridge import UIStateBridge

class PeiDockerWebGUI:
    def __init__(self) -> None:
        # Replace legacy AppData with AppUIState
        self.ui_state = AppUIState()
        self.bridge = UIStateBridge()
        
        # Remove legacy components
        # self.data = AppData()  # REMOVE
        
        # Update tabs to receive ui_state
        self.tabs = {
            TabName.PROJECT: ProjectTab(self),
            TabName.SSH: SSHTab(self),
            # ... etc
        }
```

#### 1.2 Update BaseTab class
```python
# src/pei_docker/webgui/tabs/base.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class BaseTab:
    def __init__(self, app: 'PeiDockerWebGUI') -> None:
        self.app = app
        self.ui_state = app.ui_state  # Direct reference to UI state
    
    def mark_modified(self) -> None:
        """Mark the configuration as modified."""
        self.ui_state.mark_modified()
```

### Phase 2: Refactor Each Tab for Data Binding

#### 2.1 Scripts Tab (Already Completed)
- ✅ Uses `bind_value()` for entry point modes
- ✅ Uses `bind_visibility_from()` for conditional UI
- ✅ Stores lifecycle scripts in `ScriptsUI` model
- ✅ Preserves state across navigation

#### 2.2 Environment Tab
```python
# src/pei_docker/webgui/tabs/environment.py
def render(self) -> ui.element:
    # Get the active stage's environment UI
    env_ui = self.ui_state.get_active_stage().environment
    
    # Device type select with binding
    self.device_type_select = ui.select(
        options={'cpu': 'CPU Only', 'gpu': 'GPU Support'}
    ).bind_value(env_ui, 'device_type').classes('w-full')
    
    # GPU configuration with visibility binding
    with ui.column() as gpu_config:
        gpu_all_switch = ui.switch('Use All GPUs').bind_value(env_ui, 'gpu_enabled')
        
        gpu_memory_input = ui.input(
            placeholder='e.g., 4GB or leave empty'
        ).bind_value(env_ui, 'gpu_memory_limit')
        
        gpu_config.bind_visibility_from(env_ui, 'device_type', lambda v: v == 'gpu')
    
    # Environment variables - need special handling for dict
    self._render_env_variables(env_ui)
```

#### 2.3 Network Tab
```python
# src/pei_docker/webgui/tabs/network.py
def render(self) -> ui.element:
    network_ui = self.ui_state.get_active_stage().network
    
    # Proxy settings with binding
    proxy_switch = ui.switch('Enable Proxy').bind_value(network_ui, 'proxy_enabled')
    
    with ui.column() as proxy_config:
        ui.input('HTTP Proxy').bind_value(network_ui, 'http_proxy')
        ui.input('HTTPS Proxy').bind_value(network_ui, 'https_proxy')
        ui.input('No Proxy').bind_value(network_ui, 'no_proxy')
        
        proxy_config.bind_visibility_from(network_ui, 'proxy_enabled')
    
    # APT Mirror
    ui.input('APT Mirror URL').bind_value(network_ui, 'apt_mirror')
    
    # Port mappings - need special handling for list
    self._render_port_mappings(network_ui)
```

#### 2.4 SSH Tab
```python
# src/pei_docker/webgui/tabs/ssh.py
def render(self) -> ui.element:
    ssh_ui = self.ui_state.get_active_stage().ssh
    
    # SSH enabled switch
    ssh_switch = ui.switch('Enable SSH').bind_value(ssh_ui, 'enabled')
    
    with ui.column() as ssh_config:
        ui.input('SSH Port').bind_value(ssh_ui, 'port')
        ui.input('Host Port').bind_value(ssh_ui, 'host_port')
        
        ssh_config.bind_visibility_from(ssh_ui, 'enabled')
    
    # Users list - need special handling
    self._render_users_list(ssh_ui)
```

#### 2.5 Storage Tab
```python
# src/pei_docker/webgui/tabs/storage.py
def render(self) -> ui.element:
    storage_ui = self.ui_state.get_active_stage().storage
    
    # App storage
    ui.select(
        options={
            'auto-volume': 'Auto-create Volume',
            'manual-volume': 'Existing Volume',
            'host': 'Host Path',
            'image': 'In Image'
        }
    ).bind_value(storage_ui, 'app_storage_type')
    
    # Similar for data and workspace storage
    # Volume/mount lists need special handling
```

#### 2.6 Project Tab
```python
# src/pei_docker/webgui/tabs/project.py
def render(self) -> ui.element:
    project_ui = self.ui_state.project
    
    ui.input('Project Name').bind_value(project_ui, 'project_name')
    ui.input('Project Directory').bind_value(project_ui, 'project_directory')
    ui.textarea('Description').bind_value(project_ui, 'description')
    ui.input('Base Image').bind_value(project_ui, 'base_image')
```

### Phase 3: Implement Bridge Layer

#### 3.1 Create UIStateBridge class
```python
# src/pei_docker/webgui/utils/bridge.py
from typing import Dict, Any, Tuple, List
from pei_docker.webgui.models.ui_state import AppUIState
from pei_docker.webgui.models.config import AppConfig, ProjectConfig, StageConfig
import yaml

class UIStateBridge:
    """Bridge between UI state models and configuration models."""
    
    def ui_state_to_config(self, ui_state: AppUIState) -> AppConfig:
        """Convert UI state to validated config model."""
        project_config = self._convert_project(ui_state.project)
        stage1_config = self._convert_stage(ui_state.stage_1)
        stage2_config = self._convert_stage(ui_state.stage_2)
        
        return AppConfig(
            project=project_config,
            stage_1=stage1_config,
            stage_2=stage2_config
        )
    
    def config_to_ui_state(self, config: AppConfig, ui_state: AppUIState) -> None:
        """Load config into UI state."""
        self._load_project(config.project, ui_state.project)
        self._load_stage(config.stage_1, ui_state.stage_1)
        self._load_stage(config.stage_2, ui_state.stage_2)
    
    def save_to_yaml(self, ui_state: AppUIState, file_path: str) -> Tuple[bool, List[str]]:
        """Convert UI state to YAML file."""
        try:
            # Validate through Pydantic
            config = self.ui_state_to_config(ui_state)
            
            # Convert to user_config.yml format
            yaml_data = self._to_user_config_format(config)
            
            # Write YAML
            with open(file_path, 'w') as f:
                yaml.dump(yaml_data, f, default_flow_style=False)
            
            return True, []
        except Exception as e:
            return False, [str(e)]
    
    def load_from_yaml(self, file_path: str, ui_state: AppUIState) -> Tuple[bool, List[str]]:
        """Load YAML into UI state."""
        try:
            with open(file_path, 'r') as f:
                yaml_data = yaml.safe_load(f)
            
            # Convert to config model
            config = self._from_user_config_format(yaml_data)
            
            # Load into UI state
            self.config_to_ui_state(config, ui_state)
            
            return True, []
        except Exception as e:
            return False, [str(e)]
```

### Phase 4: Handle Complex Data Types

#### 4.1 Dictionary Binding (Environment Variables)
```python
class EnvironmentTab:
    def _render_env_variables(self, env_ui: EnvironmentUI) -> None:
        """Render environment variables with dict binding."""
        with ui.column() as container:
            self.env_container = container
            
            # Render existing variables
            for key, value in env_ui.env_vars.items():
                self._add_env_var_row(key, value, env_ui)
            
            # Add button
            ui.button('Add Variable', on_click=lambda: self._add_env_var_row('', '', env_ui))
    
    def _add_env_var_row(self, key: str, value: str, env_ui: EnvironmentUI) -> None:
        """Add a single environment variable row."""
        var_id = str(uuid.uuid4())
        
        with self.env_container:
            with ui.row() as row:
                key_input = ui.input(value=key, placeholder='VARIABLE_NAME')
                ui.label('=')
                value_input = ui.input(value=value, placeholder='value')
                
                # Update dict on change
                def update_var():
                    # Remove old key if it changed
                    if key and key != key_input.value:
                        env_ui.env_vars.pop(key, None)
                    
                    # Set new value
                    if key_input.value:
                        env_ui.env_vars[key_input.value] = value_input.value
                    
                    self.ui_state.mark_modified()
                
                key_input.on('change', update_var)
                value_input.on('change', update_var)
                
                # Remove button
                def remove_var():
                    if key_input.value in env_ui.env_vars:
                        del env_ui.env_vars[key_input.value]
                    row.delete()
                    self.ui_state.mark_modified()
                
                ui.button('Remove', on_click=remove_var)
```

#### 4.2 List Binding (Port Mappings, Users)
```python
class NetworkTab:
    def _render_port_mappings(self, network_ui: NetworkUI) -> None:
        """Render port mappings list."""
        with ui.column() as container:
            self.port_container = container
            
            # Render existing mappings
            for i, mapping in enumerate(network_ui.port_mappings):
                self._add_port_mapping_row(i, mapping, network_ui)
            
            # Add button
            ui.button('Add Port Mapping', 
                     on_click=lambda: self._add_new_port_mapping(network_ui))
    
    def _add_port_mapping_row(self, index: int, mapping: Dict[str, str], 
                              network_ui: NetworkUI) -> None:
        """Add a single port mapping row."""
        with self.port_container:
            with ui.row() as row:
                host_input = ui.input(value=mapping.get('host', ''), 
                                     placeholder='Host port')
                ui.label('→')
                container_input = ui.input(value=mapping.get('container', ''), 
                                          placeholder='Container port')
                
                # Update list on change
                def update_mapping():
                    network_ui.port_mappings[index] = {
                        'host': host_input.value,
                        'container': container_input.value
                    }
                    self.ui_state.mark_modified()
                
                host_input.on('change', update_mapping)
                container_input.on('change', update_mapping)
                
                # Remove button
                def remove_mapping():
                    network_ui.port_mappings.pop(index)
                    row.delete()
                    # Re-render to fix indices
                    self.port_container.clear()
                    self._render_port_mappings(network_ui)
                
                ui.button('Remove', on_click=remove_mapping)
```

### Phase 5: Update Save/Load Operations

#### 5.1 Save Configuration
```python
# In PeiDockerWebGUI
async def save_configuration(self) -> None:
    """Save the current configuration."""
    # Validate UI state
    errors = self.bridge.validate_ui_state(self.ui_state)
    if errors:
        ui.notify(f'Validation errors: {", ".join(errors)}', type='negative')
        return
    
    # Save to YAML
    config_path = Path(self.ui_state.project.project_directory) / 'user_config.yml'
    success, errors = self.bridge.save_to_yaml(self.ui_state, str(config_path))
    
    if success:
        self.ui_state.mark_saved()
        ui.notify('Configuration saved successfully', type='positive')
    else:
        ui.notify(f'Save failed: {", ".join(errors)}', type='negative')
```

#### 5.2 Load Configuration
```python
async def load_project(self, project_dir: str) -> None:
    """Load a project from directory."""
    config_path = Path(project_dir) / 'user_config.yml'
    
    if config_path.exists():
        success, errors = self.bridge.load_from_yaml(str(config_path), self.ui_state)
        
        if success:
            self.ui_state.project.project_directory = project_dir
            ui.notify('Project loaded successfully', type='positive')
        else:
            ui.notify(f'Load failed: {", ".join(errors)}', type='negative')
    else:
        # New project
        self.ui_state = AppUIState()  # Reset to defaults
        self.ui_state.project.project_directory = project_dir
```

### Phase 6: Type Safety Implementation

#### 6.1 Add Type Stubs
```python
# src/pei_docker/webgui/types.py
from typing import TypedDict, Literal, Union

class PortMapping(TypedDict):
    host: str
    container: str

class SSHUser(TypedDict):
    name: str
    uid: int
    password: str
    ssh_keys: List[Dict[str, str]]

StorageType = Literal['auto-volume', 'manual-volume', 'host', 'image']
DeviceType = Literal['cpu', 'gpu', 'custom']
```

#### 6.2 Run MyPy Validation
```bash
# Add to development workflow
pixi run -e dev mypy src/pei_docker/webgui/ --strict
```

## Testing Plan

### 1. Unit Tests for Bridge Layer
```python
# tests/test_ui_bridge.py
def test_ui_to_config_conversion():
    ui_state = AppUIState()
    ui_state.project.project_name = "test-project"
    
    bridge = UIStateBridge()
    config = bridge.ui_state_to_config(ui_state)
    
    assert config.project.project_name == "test-project"

def test_config_validation():
    ui_state = AppUIState()
    ui_state.project.project_name = "invalid name!"  # Invalid characters
    
    bridge = UIStateBridge()
    with pytest.raises(ValidationError):
        bridge.ui_state_to_config(ui_state)
```

### 2. Integration Tests
```python
# tests/test_webgui_integration.py
def test_state_persistence_across_tabs():
    """Test that state persists when switching tabs."""
    # Create app
    # Add inline script in scripts tab
    # Switch to another tab
    # Switch back to scripts tab
    # Verify inline script content is preserved
```

### 3. Manual Testing Checklist
- [ ] Scripts tab preserves inline editor content
- [ ] Environment variables persist across navigation
- [ ] SSH users maintain their configuration
- [ ] Port mappings don't lose data
- [ ] Storage settings remain consistent
- [ ] All validations work correctly
- [ ] Save/load operations work properly

## Migration Steps

1. **Backup Current Code**: Create a branch for the refactoring
2. **Update Core First**: Modify PeiDockerWebGUI and BaseTab
3. **Refactor One Tab at a Time**: Start with Scripts (done), then Environment
4. **Test Each Tab**: Ensure data binding works before moving to next
5. **Implement Bridge Layer**: After all tabs are updated
6. **Update Save/Load**: Connect to new bridge layer
7. **Run Full Test Suite**: Ensure nothing is broken
8. **Type Check Everything**: Run mypy with strict mode

## Success Criteria

1. **No State Loss**: All UI elements preserve their values when navigating
2. **Automatic Updates**: Changes in UI immediately reflect in data model
3. **Type Safety**: MyPy passes with no errors
4. **Clean Architecture**: Clear separation between UI, data models, and persistence
5. **Maintainable Code**: Easy to add new fields or tabs in the future

## Risks and Mitigations

1. **Risk**: Breaking existing functionality
   - **Mitigation**: Incremental refactoring, comprehensive testing

2. **Risk**: Performance issues with reactive binding
   - **Mitigation**: Profile and optimize, use debouncing where needed

3. **Risk**: Complex data structures (lists, dicts) binding issues
   - **Mitigation**: Custom handlers for complex types, thorough testing

4. **Risk**: Type incompatibilities between UI and config models
   - **Mitigation**: Bridge layer handles all conversions with validation