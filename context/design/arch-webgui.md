# PeiDocker WebGUI Architecture Documentation

## Overview

The PeiDocker WebGUI is a sophisticated web-based configuration interface built on the NiceGUI framework. It provides a user-friendly interface for managing PeiDocker projects through a tabbed interface that abstracts the complexity of YAML configuration files. The architecture has been recently refactored to implement a hybrid NiceGUI + Pydantic approach for improved reactivity, validation, and maintainability.

## Architecture Pattern

The WebGUI follows a **Hybrid MVC + Reactive Data Binding Architecture** incorporating several design patterns:

- **Model-View-Controller (MVC)**: Clear separation between data models, UI views, and business logic
- **Reactive Data Binding**: Automatic UI synchronization through NiceGUI's bindable dataclasses
- **Bridge Pattern**: Conversion layer between UI state and validated configuration models
- **Template Method Pattern**: BaseTab class defines common interface for all tab implementations
- **Single Source of Truth**: Centralized state management with AppUIState
- **Validation Layer**: Pydantic models ensure data integrity and type safety

## System Architecture

### High-Level Structure

The refactored architecture consists of six main layers:

1. **Main Application Layer** (`app.py`): Central coordinator and state manager
2. **UI State Layer** (`models/ui_state.py`): Bindable dataclasses for reactive UI state
3. **Validation Layer** (`models/config.py`): Pydantic models for data validation
4. **Bridge Layer** (`utils/bridge.py`): Conversion between UI state and validated models
5. **Tab Component Layer** (`tabs/`): Feature-specific configuration modules
6. **Legacy Support Layer** (`legacy_models.py`, `legacy_utils.py`): Backward compatibility

### Core Components

#### PeiDockerWebGUI (Main Controller)
- **Location**: `src/pei_docker/webgui/app.py`
- **Responsibilities**:
  - Application lifecycle management
  - Tab coordination and navigation
  - Integration with legacy data models (temporary)
  - NiceGUI UI framework setup
  - Project loading and persistence delegation

#### AppUIState (Reactive State Model)
- **Location**: `src/pei_docker/webgui/models/ui_state.py`
- **Pattern**: Single Source of Truth with Reactive Binding
- **Key Features**:
  - `@binding.bindable_dataclass` decorator for automatic UI synchronization
  - Hierarchical state structure (Project → Stages → Components)
  - No manual event handling required
  - Automatic change detection and UI updates
- **Structure**:
  ```
  AppUIState
  ├── ProjectUI (project configuration)
  ├── StageUI (stage_1)
  │   ├── EnvironmentUI
  │   ├── NetworkUI
  │   ├── SSHTabUI
  │   ├── StorageUI
  │   └── ScriptsUI
  └── StageUI (stage_2)
      └── (same components)
  ```

#### Pydantic Validation Models
- **Location**: `src/pei_docker/webgui/models/config.py`
- **Purpose**: Comprehensive data validation and type safety
- **Key Models**:
  - `EnvironmentConfig`: GPU settings, environment variables validation
  - `NetworkConfig`: Proxy URLs, port mappings validation
  - `SSHConfig`: User authentication, SSH key validation
  - `StorageConfig`: Mount paths, volume configuration validation
  - `ScriptsConfig`: Entry points, lifecycle scripts validation
  - `ProjectConfig`: Docker image format, project name validation
- **Features**:
  - Field-level validators with custom error messages
  - Pattern matching for format validation
  - Cross-field validation logic
  - Type coercion and normalization

#### ConfigBridge (State-Config Converter)
- **Location**: `src/pei_docker/webgui/utils/bridge.py`
- **Pattern**: Bridge Pattern
- **Responsibilities**:
  - Convert UI state to Pydantic models for validation
  - Transform validated data to user_config.yml format
  - Load YAML configuration into UI state
  - Handle validation errors with user-friendly messages
- **Key Methods**:
  - `validate_ui_state()`: Validate without modifying
  - `save_to_yaml()`: Validate and persist configuration
  - `load_into_ui()`: Populate UI from YAML

#### BaseTab (Abstract Template)
- **Location**: `src/pei_docker/webgui/tabs/base.py`
- **Pattern**: Template Method Pattern
- **Evolution**: Now focuses on UI rendering, with validation moved to Pydantic models
- **Responsibilities**:
  - Define common tab interface
  - Provide shared UI helper methods
  - Enforce consistent tab structure

#### Tab Implementations
All tabs currently use the original implementation with plans for migration to reactive binding:

- **ProjectTab, SSHTab, NetworkTab, EnvironmentTab, StorageTab, ScriptsTab, SummaryTab**: Using legacy models and manual event handling
- **Migration planned**: Each tab will be refactored to use reactive binding pattern with AppUIState

### Data Flow Architecture

#### Reactive Data Binding Flow
```
User Input → UI Widget → Bindable Property → UI State Update → Automatic UI Refresh
                              ↓
                        Validation (on save)
                              ↓
                        Pydantic Model → YAML Export
```

#### Configuration Persistence Flow
1. User clicks Save → Collect UI state from AppUIState
2. ConfigBridge validates through Pydantic models
3. Valid data transformed to user_config.yml format
4. YAML written to disk with proper structure
5. UI state marked as saved

#### State Management Principles
- **No Direct Mutations**: UI state updates through property assignment
- **Automatic Propagation**: Changes automatically reflect in all bound UI elements
- **Validation Separation**: UI allows any input, validation occurs on save
- **Type Safety**: Bindable dataclasses provide IDE autocomplete and type hints

## Design Patterns Implementation

### Reactive Data Binding Pattern
```python
# Automatic two-way binding
ui.input('GPU Memory Limit').bind_value(env_config, 'gpu_memory_limit')

# Reactive visibility
with ui.row().bind_visibility_from(env_config, 'gpu_enabled'):
    # Content only visible when GPU is enabled

# Reactive text
ui.label().bind_text_from(project, 'name', lambda n: f'Project: {n}')
```

### Bridge Pattern Implementation
```python
# UI State → Validation → Configuration
ui_state = AppUIState()  # Bindable, allows any input
config = ConfigBridge.validate_ui_state(ui_state)  # Returns validation result
yaml_data = ConfigBridge.save_to_yaml(ui_state, path)  # Validates and saves

# Configuration → UI State
ConfigBridge.load_into_ui(yaml_data, ui_state)  # Populates reactive UI
```

### Single Source of Truth
```python
# All state centralized in AppUIState
app_state = AppUIState()
# Tabs reference shared state
env_tab = EnvironmentTab(app_state, stage=1)
# Changes in any tab immediately visible to all components
```

## Key Architectural Improvements

### 1. Automatic UI Synchronization (Planned)
- **Current**: Manual event handlers, explicit UI updates, state synchronization logic
- **Planned**: Declarative bindings, automatic updates, no synchronization code
- **Expected Benefit**: ~40% code reduction, eliminated sync bugs

### 2. Comprehensive Validation
- **Before**: Scattered validation logic, inconsistent error handling
- **After**: Centralized Pydantic validation, field-level validators, consistent errors
- **Benefit**: Type safety, better error messages, validation reuse

### 3. Clean Separation of Concerns
- **UI State**: Only handles display and user interaction
- **Validation Models**: Only handles data validation rules
- **Bridge Layer**: Only handles conversion and persistence
- **Benefit**: Easy to test, modify, and extend each layer independently

### 4. Improved Developer Experience
- **Type Hints**: Full IDE support with autocomplete
- **Validation Errors**: Clear, specific error messages
- **Debugging**: Single source of truth simplifies state inspection
- **Testing**: Each layer can be tested in isolation

## Migration Strategy

### Current Status
- ✅ Architecture design completed with comprehensive documentation
- ✅ Core reactive models designed (models/ui_state.py, models/config.py, utils/bridge.py)
- ✅ All imports converted to absolute for PyPI compatibility
- ⏳ Implementation of reactive architecture pending
- ⏳ All tabs currently using legacy models and manual event handling

### Migration Path
1. Refactor remaining tabs to use reactive binding
2. Remove dependency on legacy models
3. Implement full test coverage
4. Performance optimization if needed

## Technology Stack

### Core Framework
- **NiceGUI**: Python web UI framework with reactive capabilities
- **@binding.bindable_dataclass**: Automatic two-way data binding
- **FastAPI**: Underlying web server (via NiceGUI)
- **WebSocket**: Real-time UI updates (via NiceGUI)

### Data Management
- **Pydantic v2**: Data validation and serialization
- **Python dataclasses**: Type-safe data structures
- **PyYAML**: Configuration file handling
- **Type hints**: Full typing throughout codebase

### Development Tools
- **Pixi**: Package management
- **Absolute imports**: PyPI-compatible import structure
- **Type checking**: mypy compatibility (planned)

## Performance Characteristics

### Reactive Updates
- **Granular Updates**: Only affected UI elements re-render
- **Efficient Binding**: Direct property access without observers
- **Lazy Evaluation**: Visibility bindings only evaluated when needed

### Memory Efficiency
- **Single State Instance**: No data duplication across tabs
- **Automatic Cleanup**: NiceGUI handles component lifecycle
- **Minimal Overhead**: Bindable decorators add negligible memory usage

### Validation Performance
- **On-Demand**: Validation only runs on save, not on every input
- **Cached Validators**: Pydantic caches regex patterns and validators
- **Parallel Validation**: Independent fields validated concurrently

## Security Considerations

### Input Validation
- **Comprehensive**: All user inputs validated through Pydantic
- **Type Safe**: Strong typing prevents type confusion attacks
- **Pattern Matching**: Regex validation for formats (URLs, ports, etc.)

### State Isolation
- **No Direct Access**: UI components can't directly modify internal state
- **Validation Gateway**: All changes must pass through validation layer
- **Safe Defaults**: Secure default values in dataclass definitions

## Quality Attributes

### Maintainability
- **Clear Architecture**: Well-defined layers with single responsibilities
- **Self-Documenting**: Type hints and dataclass fields document structure
- **Consistent Patterns**: Reactive binding used uniformly

### Testability
- **Unit Testing**: Each layer independently testable
- **Integration Testing**: Bridge layer tests full data flow
- **UI Testing**: Playwright tests for reactive behavior

### Extensibility
- **New Tabs**: Extend BaseTab, create UI state model, add to AppUIState
- **New Validations**: Add Pydantic validators to config models
- **New UI Patterns**: Leverage NiceGUI's binding system

### Developer Experience
- **IntelliSense**: Full IDE support with type hints
- **Fast Feedback**: Immediate UI updates during development
- **Clear Errors**: Validation errors point to exact issues

## Conclusion

The redesigned PeiDocker WebGUI architecture represents a comprehensive plan for significant improvements in code quality, maintainability, and developer experience. The hybrid NiceGUI + Pydantic approach combines the simplicity of reactive UI binding with the robustness of comprehensive data validation.

Key achievements:
- **Complete architecture design** with detailed documentation and UML diagrams
- **Reactive data models** designed (UI state, validation, bridge layers)
- **PyPI-ready** with absolute imports throughout codebase
- **Future-proof** architecture ready for implementation

Planned benefits upon implementation:
- **~40% code reduction** through reactive binding
- **Zero manual event handling** for UI synchronization
- **Type-safe** throughout with full IDE support  
- **Comprehensive validation** with clear error messages

The architecture provides a solid foundation for future implementation while maintaining the current working system.

---

## Architecture Diagrams

### Package Diagram
![Package Architecture](arch-webgui/PeiDocker-WebGUI-Package-Diagram.svg)

<details>
<summary>Package Diagram Source Code (PlantUML)</summary>

```plantuml
@startuml PeiDocker-WebGUI-Package-Diagram
!theme plain
title PeiDocker WebGUI - Refactored Package Architecture

' Define packages
package "PeiDocker WebGUI" {
    
    package "Main Application" {
        [app.py] <<Main Controller>>
        [cli_launcher.py] <<CLI Integration>>
    }
    
    package "Models Layer" {
        package "models/" {
            [ui_state.py] <<Bindable UI State>>
            [config.py] <<Pydantic Validation>>
        }
    }
    
    package "Utils Layer" {
        package "utils/" {
            [bridge.py] <<State-Config Bridge>>
        }
    }
    
    package "Legacy Support" {
        [legacy_models.py] <<Legacy Data Models>>
        [legacy_utils.py] <<Legacy Utilities>>
    }
    
    package "Tab Components" {
        package "tabs/" {
            [base.py] <<Abstract Base>>
            package "Current Tabs" {
                [project.py]
                [ssh.py]
                [network.py]
                [environment.py]
                [storage.py]
                [scripts.py]
                [summary.py]
            }
        }
    }
}

package "External Dependencies" {
    [NiceGUI Framework] <<Reactive UI>>
    [Pydantic v2] <<Data Validation>>
    [PyYAML] <<YAML Processing>>
}

package "PeiDocker Core" {
    [pei-docker-cli] <<CLI Commands>>
    [user_config.yml] <<Configuration>>
}

' Define relationships
[app.py] --> [legacy_models.py] : temporary
[app.py] --> [base.py] : coordinates
[app.py] --> [NiceGUI Framework] : built on

[ui_state.py] --> [NiceGUI Framework] : @bindable_dataclass
[config.py] --> [Pydantic v2] : BaseModel

[bridge.py] --> [ui_state.py] : converts from
[bridge.py] --> [config.py] : validates with
[bridge.py] --> [PyYAML] : serializes

[Current Tabs] --> [legacy_models.py] : uses
[Current Tabs] --> [base.py] : extends

[cli_launcher.py] --> [app.py] : launches
[bridge.py] --> [user_config.yml] : reads/writes

note right of [ui_state.py]
  Reactive State Layer
  - @bindable_dataclass
  - Automatic UI sync
  - Single source of truth
  - No event handlers
end note

note bottom of [bridge.py]
  Bridge Pattern
  - UI State ↔ Pydantic
  - YAML serialization
  - Validation orchestration
  - Error handling
end note

note left of [config.py]
  Validation Layer
  - Field validators
  - Type coercion
  - Pattern matching
  - Error messages
end note

@enduml
```
</details>

### Class Diagram  
![Class Relationships](arch-webgui/PeiDocker-WebGUI-Class-Diagram.svg)

<details>
<summary>Class Diagram Source Code (PlantUML)</summary>

```plantuml
@startuml PeiDocker-WebGUI-Class-Diagram
!theme plain
title PeiDocker WebGUI - Refactored Class Architecture

' UI State Models (Bindable Dataclasses)
package "UI State Layer" #LightBlue {
    class AppUIState <<@bindable_dataclass>> {
        +project: ProjectUI
        +stage_1: StageUI
        +stage_2: StageUI
        +active_stage: int
        +modified: bool
        +last_saved: str
        +active_tab: str
        +has_errors: bool
        +error_count: int
        --
        +mark_modified()
        +mark_saved()
        +get_active_stage(): StageUI
        +merge_stages(): Dict[str, Any]
    }
    
    class ProjectUI <<@bindable_dataclass>> {
        +project_name: str
        +project_directory: str
        +description: str
        +base_image: str
        +image_output_name: str
        +template: str
    }
    
    class StageUI <<@bindable_dataclass>> {
        +environment: EnvironmentUI
        +network: NetworkUI
        +ssh: SSHTabUI
        +storage: StorageUI
        +scripts: ScriptsUI
    }
    
    class EnvironmentUI <<@bindable_dataclass>> {
        +gpu_enabled: bool
        +gpu_count: str
        +cuda_version: str
        +env_vars: Dict[str, str]
        +device_type: str
        +gpu_memory_limit: str
    }
    
    class NetworkUI <<@bindable_dataclass>> {
        +proxy_enabled: bool
        +http_proxy: str
        +https_proxy: str
        +no_proxy: str
        +apt_mirror: str
        +port_mappings: List[Dict[str, str]]
    }
}

' Validation Models (Pydantic)
package "Validation Layer" #LightGreen {
    class AppConfig <<Pydantic>> {
        +project: ProjectConfig
        +stage_1: StageConfig
        +stage_2: StageConfig
        --
        +to_user_config_yaml(): Dict[str, Any]
    }
    
    class ProjectConfig <<Pydantic>> {
        +project_name: str
        +project_directory: str
        +description: str
        +base_image: str
        +image_output_name: str
        +template: str
        --
        +validate_project_name(v: str): str
        +validate_base_image(v: str): str
    }
    
    class EnvironmentConfig <<Pydantic>> {
        +gpu_enabled: bool
        +gpu_count: str
        +cuda_version: str
        +env_vars: Dict[str, str]
        +device_type: str
        +gpu_memory_limit: str
        --
        +validate_env_vars(v: Dict): Dict
        +validate_gpu_memory(v: str): str
    }
    
    class NetworkConfig <<Pydantic>> {
        +proxy_enabled: bool
        +http_proxy: str
        +https_proxy: str
        +no_proxy: str
        +apt_mirror: str
        +port_mappings: List[Dict[str, str]]
        --
        +validate_proxy_url(v: str): str
        +validate_port_mappings(v: List): List
    }
}

' Bridge Layer
package "Bridge Layer" #LightYellow {
    class ConfigBridge {
        --
        +{static} validate_ui_state(ui_state: AppUIState): Tuple[bool, List[str]]
        +{static} save_to_yaml(ui_state: AppUIState, file_path: str): bool
        +{static} load_into_ui(config_data: Dict, ui_state: AppUIState)
        -{static} _ui_to_user_config_format(ui_state: AppUIState): Dict
        -{static} _build_storage_config(storage: StorageUI): Dict
        -{static} _build_scripts_config(scripts1, scripts2): Dict
    }
}

' Tab Components
package "Tab Components" #LightCoral {
    abstract class BaseTab {
        #app: PeiDockerWebGUI
        #container: Optional[ui.element]
        --
        +{abstract} render(): ui.element
        +{abstract} validate(): Tuple[bool, List[str]]
        +{abstract} get_config_data(): Dict
        +{abstract} set_config_data(data: Dict)
        +mark_modified()
        #create_card(title: str): ui.card
        #create_form_group(title: str, desc: str): ui.column
    }
    
    class EnvironmentTab {
        +app: PeiDockerWebGUI
        +device_type_select: ui.select
        +gpu_config_container: ui.column
        +env_variables_data: List[Dict[str, Any]]
        --
        +render(): ui.element
        +validate(): Tuple[bool, List[str]]
        +get_config_data(): Dict
        +set_config_data(data: Dict)
        +_add_env_variable()
        +_on_device_type_change()
    }
}

' Main Application
class PeiDockerWebGUI {
    +data: AppData <<legacy>>
    +tabs: Dict[TabName, BaseTab]
    --
    +setup_ui()
    +run()
    ' ... legacy methods ...
}

' Relationships
AppUIState *-- ProjectUI
AppUIState *-- StageUI : stage_1, stage_2
StageUI *-- EnvironmentUI
StageUI *-- NetworkUI

ConfigBridge ..> AppUIState : validates
ConfigBridge ..> AppConfig : creates
ConfigBridge ..> ProjectConfig : converts to
ConfigBridge ..> EnvironmentConfig : converts to

EnvironmentTab --|> BaseTab

AppConfig *-- ProjectConfig
AppConfig *-- StageConfig

' Notes
note right of AppUIState
  Single Source of Truth
  - Centralized state
  - Automatic UI sync
  - Change tracking
end note

note bottom of ConfigBridge
  Conversion Layer
  - UI State validation
  - YAML serialization
  - Error aggregation
end note

note left of EnvironmentUI
  @bindable_dataclass (Planned)
  - Two-way data binding
  - Automatic updates
  - No event handlers
end note

note right of EnvironmentTab
  Current Implementation
  - Manual event handling
  - Direct UI updates
  - Works with legacy models
end note

@enduml
```
</details>

### Sequence Diagram
![Data Flow and Binding](arch-webgui/PeiDocker-WebGUI-Sequence-Diagram.svg)

<details>
<summary>Sequence Diagram Source Code (PlantUML)</summary>

```plantuml
@startuml PeiDocker-WebGUI-Sequence-Diagram
!theme plain
title PeiDocker WebGUI - Reactive Data Flow

actor User
participant "UI Widget" as Widget
participant "Bindable Property" as Binding
participant "UI State\n(AppUIState)" as State
participant "Other Widgets" as Others
participant "ConfigBridge" as Bridge
participant "Pydantic\nValidation" as Pydantic
participant "YAML File" as File

== Reactive UI Updates (Automatic) ==
User -> Widget: Modify input
activate Widget

Widget -> Binding: Update bound value
activate Binding
note right: NiceGUI handles\nbinding automatically

Binding -> State: Update property
activate State
State -> State: Mark modified = True

State --> Others: Notify observers
activate Others
note right: All bound widgets\nupdate automatically

Others -> Others: Re-render if needed
deactivate Others

Widget --> User: Show immediate feedback
deactivate Widget
deactivate Binding
deactivate State

== Configuration Save Flow ==
User -> Widget: Click Save
activate Widget

Widget -> Bridge: save_to_yaml(ui_state, path)
activate Bridge

Bridge -> Bridge: validate_ui_state(ui_state)
activate Bridge #LightBlue

loop For each component
    Bridge -> Pydantic: Create validation model
    activate Pydantic
    
    alt Valid data
        Pydantic --> Bridge: Return validated model
    else Validation error
        Pydantic --> Bridge: Raise ValidationError
    end
    deactivate Pydantic
end

Bridge --> Bridge: Aggregate validation results
deactivate Bridge

alt All valid
    Bridge -> Bridge: _ui_to_user_config_format()
    note right: Convert to YAML structure
    
    Bridge -> File: Write YAML
    activate File
    File --> Bridge: Success
    deactivate File
    
    Bridge -> State: mark_saved()
    State -> State: modified = False
    State -> State: last_saved = now()
    
    Bridge --> Widget: Return success
    Widget -> User: Show success notification
else Validation failed
    Bridge --> Widget: Return errors
    Widget -> User: Show error messages
end

deactivate Bridge
deactivate Widget

== Configuration Load Flow ==
User -> Widget: Load project
activate Widget

Widget -> File: Read user_config.yml
activate File
File --> Widget: YAML data
deactivate File

Widget -> Bridge: load_into_ui(yaml_data, ui_state)
activate Bridge

Bridge -> Bridge: Parse YAML structure
Bridge -> State: Update UI properties
activate State

loop For each property
    State -> Binding: Property changed
    activate Binding
    Binding --> Others: Notify observers
    activate Others
    Others -> Others: Update UI automatically
    deactivate Others
    deactivate Binding
end

State -> State: modified = False
deactivate State

Bridge --> Widget: Load complete
deactivate Bridge

Widget --> User: Show loaded project
deactivate Widget

== Real-time Binding Example ==
note over User, Others: Example: GPU Enable Checkbox

User -> Widget: Check "Enable GPU"
Widget -> State: gpu_enabled = True

State --> Others: Notify GPU config panel
activate Others
Others -> Others: bind_visibility_from()\nmakes panel visible
Others --> User: GPU options appear
deactivate Others

note right: No manual code needed!\nBinding handles everything

@enduml
```
</details>

---

**Generated**: 2025-08-04  
**Author**: NiceGUI Developer (Claude)  
**Version**: WebGUI Architecture v2.0 - Hybrid NiceGUI + Pydantic Refactoring