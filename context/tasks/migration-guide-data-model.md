# Data Model Refactoring Migration Guide

This guide explains how to migrate from the current scattered state management to the new bindable dataclass architecture.

## Summary of Changes

The refactoring introduces three key components:
1. **Bindable UI State Models** (`models/ui_state.py`) - NiceGUI bindable dataclasses for automatic UI synchronization
2. **Pydantic Validation Models** (`models/config.py`) - Type-safe validation and serialization
3. **Bridge Layer** (`utils/bridge.py`) - Converts between UI state and validated config for YAML persistence

## Migration Steps

### Step 1: Update Imports

Replace old imports:
```python
# OLD
from .models import AppData, AppState, TabName, ProjectState

# NEW  
from .models import AppData, AppState, TabName, ProjectState  # Keep for compatibility
from .models.ui_state import AppUIState
from .utils.bridge import ConfigBridge
```

### Step 2: Update App Initialization

```python
# OLD
class PeiDockerWebGUI:
    def __init__(self):
        self.data = AppData()
        
# NEW
class PeiDockerWebGUI:
    def __init__(self):
        # Keep old data for compatibility during migration
        self.data = AppData()
        # Add new bindable state
        self.ui_state = AppUIState()
```

### Step 3: Update Tab Creation

```python
# OLD
self.tabs = {
    TabName.ENVIRONMENT: EnvironmentTab(self),
    # ... other tabs
}

# NEW - Pass AppUIState to refactored tabs
self.tabs = {
    TabName.ENVIRONMENT: EnvironmentTabRefactored(self.ui_state, stage=1),
    # ... keep other tabs as-is during migration
}
```

### Step 4: Tab Implementation Changes

For each tab being migrated:

```python
# OLD EnvironmentTab
class EnvironmentTab(BaseTab):
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.env_variables_data: List[Dict[str, Any]] = []
        
    def _add_env_variable(self, name='', value=''):
        # Manual UI element creation
        # Manual event handling
        # Manual state updates
        
# NEW EnvironmentTab
class EnvironmentTab(BaseTab):
    def __init__(self, app_state: 'AppUIState', stage: int):
        self.state = app_state
        self.env_config = getattr(app_state, f'stage_{stage}').environment
        
    def render(self):
        # Automatic binding
        ui.select(options={'cpu': 'CPU Only', 'gpu': 'GPU Support'})
            .bind_value(self.env_config, 'device_type')
```

### Step 5: Update Save/Load Operations

```python
# OLD
def save_configuration(self):
    config_data = self._collect_config_from_tabs()
    # Manual YAML generation
    
# NEW  
def save_configuration(self):
    success = ConfigBridge.save_to_yaml(
        self.ui_state, 
        str(self.project_directory / "user_config.yml")
    )
```

## Key Benefits After Migration

1. **Automatic UI Updates**: No manual event handling needed
2. **Type Safety**: IDE autocompletion and error detection  
3. **Centralized Validation**: All validation in Pydantic models
4. **Simpler Code**: ~50% reduction in tab implementation code
5. **Better Performance**: NiceGUI's efficient binding system

## Migration Order Recommendation

1. **Phase 1**: Create new models alongside existing code
2. **Phase 2**: Migrate one simple tab (e.g., EnvironmentTab) 
3. **Phase 3**: Test thoroughly with both old and new tabs
4. **Phase 4**: Migrate remaining tabs one by one
5. **Phase 5**: Remove old AppData and models.py

## Compatibility During Migration

The system can run with both old and new models simultaneously:
- Old tabs continue using `self.app.data`
- New tabs use `self.state` (AppUIState)
- Bridge layer handles conversion when saving

## Example: Environment Variables

### Before (Manual Binding)
```python
# Creating UI elements manually
name_input = ui.input(placeholder='VARIABLE_NAME', value=name)
value_input = ui.input(placeholder='value', value=value)

# Manual event handling
name_input.on('input', lambda e: self._on_env_variable_change(data))

# Manual state update
self.app.data.config.stage_1['environment'] = env_list
```

### After (Automatic Binding)
```python
# Environment variables are just a dict
self.env_config.env_vars["NEW_VAR"] = "value"

# UI automatically updates via @refreshable
@ui.refreshable
def env_list():
    for key, value in self.env_config.env_vars.items():
        ui.label(f'{key}={value}')
```

## Testing the Migration

Use the provided test scripts:
- `tmp/tests/test_bindable_isolated.py` - Tests basic binding functionality
- `tmp/tests/test_refactored_data_model.py` - Tests full integration

## Troubleshooting

1. **Import Errors**: Ensure `__init__.py` files exist in models/ and utils/ directories
2. **Binding Not Working**: Check that models use `@binding.bindable_dataclass` decorator
3. **Validation Errors**: Review Pydantic model constraints in config.py
4. **State Not Persisting**: Ensure ConfigBridge is used for save/load operations