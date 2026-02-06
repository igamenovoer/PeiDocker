# Refactor Data Model for PeiDocker NiceGUI  
**Architecture Review & Implementation Guide**

---

## 1 Problem Statement   

The current web GUI has several data management issues:

### Current Pain Points
- **Scattered state**: Each tab maintains its own local data lists/dicts
- **Direct mutations**: Tabs modify `self.app.data.config.stage_{1,2}` directly
- **No reactivity**: Changes in one tab don't auto-update others
- **Validation duplication**: Each tab re-implements similar validation logic
- **Type safety**: Plain dictionaries provide no compile-time checks

### Example of Current Anti-Pattern
```python
# In EnvironmentTab
self.env_variables_data: List[Dict[str, Any]] = []  # Local state
# Later...
self.app.data.config.stage_1['environment']['env_vars'] = new_data  # Direct mutation
```

---

## 2 Goals

1. **🎯 Single Source of Truth** – One centralized, typed data model
2. **⚡ Real-time Reactivity** – UI updates automatically when data changes  
3. **✅ Strong Validation** – Prevent invalid configurations early
4. **💾 YAML Persistence** – Reliable save/load of `user_config.yml`
5. **🔄 Migration Support** – Seamless upgrade path for existing projects

---

## 3 **Recommended Solution: Hybrid NiceGUI + Pydantic Architecture**

Based on research in `context/hints/howto-bidirectional-data-binding-nicegui.md`, we'll use **NiceGUI's bindable dataclasses** for the UI layer with **Pydantic models** for validation and persistence.

### Why This Hybrid Approach?

| Component | Best Tool | Reason |
|-----------|-----------|---------|
| **UI Reactivity** | NiceGUI `@bindable_dataclass` | ✅ Zero-copy bidirectional binding<br>✅ Automatic widget updates<br>✅ No manual event wiring |
| **Validation** | Pydantic `BaseModel` | ✅ Rich field constraints<br>✅ Automatic type coercion<br>✅ Custom validators |
| **Persistence** | Pydantic `model_dump()` | ✅ YAML/JSON serialization<br>✅ Schema migration<br>✅ CLI tool compatibility |

### Architecture Overview

```mermaid
flowchart TD
    subgraph "UI Layer (Fast Binding)"
        UI[Tab Widgets] ↔ BD[Bindable Dataclasses]
    end
    
    subgraph "Validation Layer"
        BD -.->|on save| PY[Pydantic Models]
        PY -.->|validation errors| UI
    end
    
    subgraph "Persistence Layer"  
        PY ↔ YAML[user_config.yml]
        PY ↔ CLI[CLI Tools]
    end
```

---

## 4 Implementation Plan

### Phase 1: Create Bindable UI Models

Replace the current `AppData` with bindable dataclasses that NiceGUI can automatically sync with widgets.

```python
# src/pei_docker/webgui/models/ui_state.py
from dataclasses import dataclass, field
from typing import Dict, List
from nicegui import binding

@binding.bindable_dataclass
class EnvironmentUI:
    """UI state for environment configuration - automatically syncs with widgets"""
    
    # GPU Configuration
    gpu_enabled: bool = False
    gpu_count: str = "all"  # "all" or specific number
    cuda_version: str = "12.4"
    
    # Environment Variables  
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    # Device Configuration
    device_type: str = "cpu"  # "cpu", "gpu", "custom"

@binding.bindable_dataclass  
class NetworkUI:
    """UI state for network configuration"""
    
    # Proxy Settings
    http_proxy: str = ""
    https_proxy: str = ""
    no_proxy: str = ""
    
    # APT Configuration
    apt_mirror: str = ""
    
    # Port Mappings (simplified for UI)
    port_mappings: List[Dict[str, str]] = field(default_factory=list)

@binding.bindable_dataclass
class SSHTabUI:
    """UI state for SSH configuration"""
    
    enabled: bool = False
    port: str = "22"
    users: List[Dict[str, str]] = field(default_factory=list)

@binding.bindable_dataclass
class StorageUI:
    """UI state for storage configuration"""
    
    volumes: List[Dict[str, str]] = field(default_factory=list)
    mounts: List[Dict[str, str]] = field(default_factory=list)

@binding.bindable_dataclass
class ScriptsUI:
    """UI state for scripts configuration"""
    
    entrypoint: str = ""
    pre_build: List[str] = field(default_factory=list)
    post_build: List[str] = field(default_factory=list)

@binding.bindable_dataclass
class StageUI:
    """Complete configuration for one stage"""
    
    environment: EnvironmentUI = field(default_factory=EnvironmentUI)
    network: NetworkUI = field(default_factory=NetworkUI) 
    ssh: SSHTabUI = field(default_factory=SSHTabUI)
    storage: StorageUI = field(default_factory=StorageUI)
    scripts: ScriptsUI = field(default_factory=ScriptsUI)

@binding.bindable_dataclass
class AppUIState:
    """Complete application UI state - single source of truth"""
    
    stage_1: StageUI = field(default_factory=StageUI)
    stage_2: StageUI = field(default_factory=StageUI)
    
    # App-level state
    active_stage: int = 1
    modified: bool = False
    last_saved: str = ""
```

### Phase 2: Update Tab Implementation Pattern

Transform tabs to use direct binding instead of manual event handling:

```python
# src/pei_docker/webgui/tabs/environment.py (refactored)
from nicegui import ui
from ..models.ui_state import AppUIState

class EnvironmentTab:
    def __init__(self, app_state: AppUIState, stage: int):
        self.state = app_state
        self.stage = stage
        self.env_config = getattr(app_state, f'stage_{stage}').environment
    
    def render(self):
        """Render environment tab with automatic binding"""
        
        with ui.column().classes('w-full'):
            # GPU Configuration - automatically synced!
            ui.switch('Enable GPU').bind_value(self.env_config, 'gpu_enabled')
            
            with ui.row().bind_visibility_from(self.env_config, 'gpu_enabled'):
                ui.select(['all', '1', '2', '4'], label='GPU Count').bind_value(
                    self.env_config, 'gpu_count'
                )
                ui.input('CUDA Version').bind_value(self.env_config, 'cuda_version')
            
            # Environment Variables
            self.render_env_vars()
    
    def render_env_vars(self):
        """Render environment variables section"""
        
        with ui.column():
            ui.label('Environment Variables').classes('text-lg font-semibold')
            
            # Show current variables (auto-updates when dict changes)
            @ui.refreshable
            def env_var_list():
                for key, value in self.env_config.env_vars.items():
                    with ui.row().classes('items-center gap-2'):
                        ui.input('Key', value=key).classes('w-40')
                        ui.input('Value', value=value).classes('flex-1') 
                        ui.button('❌', on_click=lambda k=key: self.remove_env_var(k))
            
            env_var_list()
            
            # Add new variable
            ui.button('+ Add Variable', on_click=self.add_env_var)
    
    def add_env_var(self):
        """Add new environment variable"""
        self.env_config.env_vars[f'NEW_VAR_{len(self.env_config.env_vars)}'] = ''
        self.state.modified = True  # Triggers UI update automatically
    
    def remove_env_var(self, key: str):
        """Remove environment variable"""
        self.env_config.env_vars.pop(key, None)
        self.state.modified = True
```

### Phase 3: Add Pydantic Validation Layer

Create Pydantic models for validation and persistence:

```python
# src/pei_docker/webgui/models/config.py
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional

class EnvironmentConfig(BaseModel):
    """Pydantic model for environment validation"""
    
    gpu_enabled: bool = False
    gpu_count: str = Field(default="all", regex=r"^(all|\d+)$")
    cuda_version: str = Field(default="12.4", regex=r"^\d+\.\d+$")
    env_vars: Dict[str, str] = Field(default_factory=dict)
    device_type: str = Field(default="cpu", regex=r"^(cpu|gpu|custom)$")
    
    @validator('env_vars')
    def validate_env_vars(cls, v):
        """Ensure environment variable names are valid"""
        for key in v.keys():
            if not key.replace('_', '').isalnum():
                raise ValueError(f"Invalid environment variable name: {key}")
        return v

class NetworkConfig(BaseModel):
    """Pydantic model for network validation"""
    
    http_proxy: str = ""
    https_proxy: str = ""
    no_proxy: str = ""
    apt_mirror: str = ""
    port_mappings: List[Dict[str, str]] = Field(default_factory=list)
    
    @validator('http_proxy', 'https_proxy')
    def validate_proxy_url(cls, v):
        """Validate proxy URL format"""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("Proxy URL must start with http:// or https://")
        return v

class AppConfig(BaseModel):
    """Complete validated configuration"""
    
    stage_1: dict  # Will contain all stage configs
    stage_2: dict
    
    class Config:
        extra = "forbid"  # Reject unknown fields
```

### Phase 4: Bridge Layer

Create utilities to convert between UI state and Pydantic models:

```python
# src/pei_docker/webgui/utils/bridge.py
from ..models.ui_state import AppUIState
from ..models.config import AppConfig, EnvironmentConfig
from pydantic import ValidationError
from nicegui import ui

class ConfigBridge:
    """Converts between UI state and validated config models"""
    
    @staticmethod
    def validate_ui_state(ui_state: AppUIState) -> tuple[bool, list[str]]:
        """Validate current UI state without modifying it"""
        errors = []
        
        try:
            # Convert UI state to Pydantic model for validation
            env1 = EnvironmentConfig(**ui_state.stage_1.environment.__dict__)
            env2 = EnvironmentConfig(**ui_state.stage_2.environment.__dict__)
            # ... validate other sections
            
            return True, []
            
        except ValidationError as e:
            for error in e.errors():
                field = " → ".join(str(loc) for loc in error['loc'])
                errors.append(f"{field}: {error['msg']}")
            
            return False, errors
    
    @staticmethod
    def save_to_yaml(ui_state: AppUIState, file_path: str) -> bool:
        """Save UI state to YAML with validation"""
        
        is_valid, errors = ConfigBridge.validate_ui_state(ui_state)
        
        if not is_valid:
            ui.notify(f"Validation failed: {'; '.join(errors)}", type='negative')
            return False
        
        try:
            # Create validated Pydantic model
            config = AppConfig(
                stage_1=ConfigBridge._ui_to_dict(ui_state.stage_1),
                stage_2=ConfigBridge._ui_to_dict(ui_state.stage_2)
            )
            
            # Save to YAML
            with open(file_path, 'w') as f:
                yaml.dump(config.dict(), f, default_flow_style=False)
            
            ui.notify('Configuration saved successfully!', type='positive')
            ui_state.modified = False
            return True
            
        except Exception as e:
            ui.notify(f"Save failed: {str(e)}", type='negative')
            return False
```

### Phase 5: Update App Bootstrap

Modify the main app to use the new state system:

```python
# src/pei_docker/webgui/app.py (key changes)
from .models.ui_state import AppUIState
from .utils.bridge import ConfigBridge

class PeiDockerWebGUI:
    def __init__(self):
        # Single source of truth - all tabs bind to this
        self.ui_state = AppUIState()
        
        # Tab implementations get the shared state
        self.tabs = {
            TabName.ENVIRONMENT: EnvironmentTab(self.ui_state, 1),
            TabName.NETWORK: NetworkTab(self.ui_state, 1),
            # ... other tabs
        }
    
    def save_configuration(self):
        """Save current UI state to YAML"""
        if self.project_directory:
            config_path = self.project_directory / "user_config.yml"
            ConfigBridge.save_to_yaml(self.ui_state, str(config_path))
    
    def load_configuration(self, config_path: str):
        """Load YAML into UI state"""
        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
            
            # Populate UI state from loaded data
            ConfigBridge.load_into_ui(config_data, self.ui_state)
            ui.notify('Configuration loaded!', type='positive')
            
        except Exception as e:
            ui.notify(f'Load failed: {str(e)}', type='negative')
```

---

## 5 Migration Strategy

### Step 1: Create New Models (Non-Breaking)
- Add `models/ui_state.py` alongside existing `models.py`
- Add `models/config.py` for Pydantic validation
- Add `utils/bridge.py` for conversion

### Step 2: Refactor One Tab at a Time
- Start with **Environment Tab** (simplest structure)
- Update tab to use bindable dataclass
- Test thoroughly before moving to next tab

### Step 3: Update App Bootstrap
- Modify `app.py` to create `AppUIState` instance
- Pass to tab constructors instead of old `AppData`

### Step 4: Remove Legacy Code
- Delete old `AppData` model once all tabs migrated
- Clean up unused validation logic

---

## 6 Benefits After Refactor

### For Developers
- **Type Safety**: IDE autocompletion and error detection
- **Simpler Code**: No manual event wiring for UI updates
- **Easier Testing**: Pure data models can be unit tested
- **Clear Boundaries**: UI logic separate from validation logic

### For Users  
- **Instant Updates**: Changes in one tab immediately reflect in others
- **Better Validation**: Errors caught before saving to YAML
- **Reliable Save/Load**: Schema migration handles old configs gracefully

### Example: Cross-Tab Reactivity
```python
# User enables GPU in Environment tab
environment_tab.gpu_enabled = True

# Summary tab automatically shows GPU information
# Network tab automatically shows GPU-related port options
# No manual event handling needed!
```

---

## 7 Action Checklist

### Phase 1: Foundation (Week 1)
- [ ] Create `src/pei_docker/webgui/models/ui_state.py` 
- [ ] Create `src/pei_docker/webgui/models/config.py` (Pydantic)
- [ ] Create `src/pei_docker/webgui/utils/bridge.py`
- [ ] Add tests for new models

### Phase 2: First Tab Migration (Week 2)  
- [ ] Refactor `EnvironmentTab` to use `AppUIState`
- [ ] Test all environment functionality works
- [ ] Verify save/load with validation

### Phase 3: Remaining Tabs (Week 3-4)
- [ ] Migrate `NetworkTab`, `SSHTab`, `StorageTab`, `ScriptsTab`
- [ ] Update `SummaryTab` to show data from `AppUIState`
- [ ] Test cross-tab reactivity

### Phase 4: Cleanup (Week 5)
- [ ] Update `app.py` to use new state system
- [ ] Remove legacy `AppData` and related code
- [ ] Update documentation and examples

---

## 8 Key Success Metrics

1. **Reduced Lines of Code**: Eliminate manual event handling 
2. **Faster UI Updates**: Instant cross-tab synchronization
3. **Better Error Handling**: Validation errors show specific field/rule
4. **Maintainability**: New tabs easier to implement

*This refactor will significantly improve the development experience while providing a more responsive and reliable interface for users.*
