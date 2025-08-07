# Architecture Documentation: PeiDocker WebGUI Data Models

## Architecture Pattern

The PeiDocker WebGUI follows a **Model-View-ViewModel (MVVM)** pattern enhanced with a **Bridge Pattern** for data transformation. This architecture provides clear separation of concerns between the user interface, business logic, and data persistence layers.

### Key Architectural Components

1. **UI-Data-Model** (View Model) - NiceGUI bindable dataclasses for reactive UI state
2. **Business-Data-Model** (Model) - Pydantic models for validation and business logic
3. **UI-to-Business-Bridge** (Bridge) - Transformation layer between UI and business models
4. **User Config YAML** (Persistence) - File-based configuration storage
5. **Web UI Components** (View) - NiceGUI-based user interface components

## Package Structure Diagram

![Package Structure](arch-webgui-data-models/package_structure.svg)

```plantuml
@startuml package_structure
!define RECTANGLE class

package "pei_docker.webgui" {
    package "models" {
        RECTANGLE ui_state [
            ui_state.py
            --
            AppUIState
            StageUI
            EnvironmentUI
            NetworkUI
            SSHTabUI
            StorageUI
            ScriptsUI
            ProjectUI
        ]
        
        RECTANGLE config [
            config.py
            --
            AppConfig
            StageConfig
            EnvironmentConfig
            NetworkConfig
            SSHConfig
            StorageConfig
            ScriptsConfig
            ProjectConfig
        ]
    }
    
    package "utils" {
        RECTANGLE ui_state_bridge [
            ui_state_bridge.py
            --
            UIStateBridge
        ]
    }
    
    package "tabs" {
        RECTANGLE base [
            base.py
            --
            BaseTab
        ]
        
        RECTANGLE project_tab [
            project.py
            --
            ProjectTab
        ]
        
        RECTANGLE other_tabs [
            ssh.py
            network.py
            environment.py
            storage.py
            scripts.py
            summary.py
        ]
    }
    
    RECTANGLE app [
        app.py
        --
        PeiDockerWebGUI
        TabName
        AppState
    ]
}

package "pei_docker.templates" {
    RECTANGLE config_template [
        config-template-full.yml
        --
        Master template for
        user_config.yml
    ]
}

ui_state_bridge --> ui_state : transforms
ui_state_bridge --> config : validates
ui_state_bridge --> config_template : generates YAML

app --> ui_state : manages
app --> ui_state_bridge : uses
app --> project_tab : contains
app --> other_tabs : contains

project_tab --|> base
other_tabs --|> base

base --> app : references
@enduml
```

## Data Model Class Diagram

![Data Models](arch-webgui-data-models/data_models.svg)

```plantuml
@startuml data_models
!define BINDABLE_DATACLASS class
!define PYDANTIC_MODEL class

package "UI Data Models (NiceGUI Bindable)" {
    BINDABLE_DATACLASS AppUIState {
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
        +mark_modified(): None
        +mark_saved(): None
        +get_active_stage(): StageUI
        +merge_stages(): Dict[str, Any]
    }
    
    BINDABLE_DATACLASS StageUI {
        +environment: EnvironmentUI
        +network: NetworkUI
        +ssh: SSHTabUI
        +storage: StorageUI
        +scripts: ScriptsUI
    }
    
    BINDABLE_DATACLASS EnvironmentUI {
        +gpu_enabled: bool
        +gpu_count: str
        +cuda_version: str
        +env_vars: Dict[str, str]
        +device_type: str
        +gpu_memory_limit: str
    }
    
    BINDABLE_DATACLASS NetworkUI {
        +proxy_enabled: bool
        +http_proxy: str
        +https_proxy: str
        +no_proxy: str
        +apt_mirror: str
        +port_mappings: List[Dict[str, str]]
    }
    
    BINDABLE_DATACLASS ProjectUI {
        +project_name: str
        +project_directory: str
        +description: str
        +base_image: str
        +image_output_name: str
        +template: str
    }
}

package "Business Data Models (Pydantic)" {
    PYDANTIC_MODEL AppConfig {
        +project: ProjectConfig
        +stage_1: StageConfig
        +stage_2: StageConfig
        --
        +to_user_config_yaml(): Dict[str, Any]
    }
    
    PYDANTIC_MODEL StageConfig {
        +environment: EnvironmentConfig
        +network: NetworkConfig
        +ssh: SSHConfig
        +storage: StorageConfig
        +scripts: ScriptsConfig
    }
    
    PYDANTIC_MODEL EnvironmentConfig {
        +gpu_enabled: bool
        +gpu_count: str
        +cuda_version: str
        +env_vars: Dict[str, str]
        +device_type: str
        +gpu_memory_limit: str
        --
        +validate_env_vars(): Dict[str, str]
        +validate_gpu_memory(): str
    }
    
    PYDANTIC_MODEL NetworkConfig {
        +proxy_enabled: bool
        +http_proxy: str
        +https_proxy: str
        +no_proxy: str
        +apt_mirror: str
        +port_mappings: List[Dict[str, str]]
        --
        +validate_proxy_url(): str
        +validate_port_mappings(): List[Dict[str, str]]
    }
    
    PYDANTIC_MODEL ProjectConfig {
        +project_name: str
        +project_directory: str
        +description: str
        +base_image: str
        +image_output_name: str
        +template: str
        --
        +validate_project_name(): str
        +validate_base_image(): str
    }
}

class UIStateBridge {
    --
    +validate_ui_state(ui_state): Tuple[bool, List[str]]
    +save_to_yaml(ui_state, file_path): Tuple[bool, List[str]]
    +load_from_yaml(file_path, ui_state): Tuple[bool, List[str]]
    +ui_to_config(ui_state): AppConfig
    --
    -_ui_project_to_pydantic(): ProjectConfig
    -_ui_environment_to_pydantic(): EnvironmentConfig
    -_ui_network_to_pydantic(): NetworkConfig
    -_ui_stage_to_pydantic(): StageConfig
    -_ui_to_user_config_format(): Dict[str, Any]
    -_load_into_ui(): None
}

AppUIState *-- StageUI : contains
StageUI *-- EnvironmentUI : contains
StageUI *-- NetworkUI : contains
AppUIState *-- ProjectUI : contains

AppConfig *-- StageConfig : contains
StageConfig *-- EnvironmentConfig : contains
StageConfig *-- NetworkConfig : contains
AppConfig *-- ProjectConfig : contains

UIStateBridge ..> AppUIState : transforms
UIStateBridge ..> AppConfig : validates
UIStateBridge ..> "user_config.yml" : generates/loads

note right of UIStateBridge : Bridge Pattern\nTransforms between\nUI and Business models
@enduml
```

## Data Flow Sequence Diagram

![Data Flow Sequence](arch-webgui-data-models/data_flow_sequence.svg)

```plantuml
@startuml data_flow_sequence
participant "User" as U
participant "NiceGUI Components" as UI
participant "AppUIState" as UIS
participant "UIStateBridge" as Bridge
participant "AppConfig" as BC
participant "user_config.yml" as YAML

== User Configuration Flow ==
U -> UI: Edit configuration
UI -> UIS: Update bindable data
note right: NiceGUI's binding system\nautomatically syncs UI and data
UIS -> UIS: mark_modified()

== Validation Flow ==
U -> UI: Save configuration
UI -> Bridge: validate_ui_state(ui_state)
Bridge -> BC: Create Pydantic models
BC -> BC: Validate data constraints
BC -> Bridge: Return validation results
Bridge -> UI: Return (is_valid, errors)

alt Validation Success
    UI -> Bridge: save_to_yaml(ui_state, file_path)
    Bridge -> Bridge: _ui_to_user_config_format()
    Bridge -> YAML: Write YAML file
    Bridge -> UIS: mark_saved()
    Bridge -> UI: Return success
else Validation Failure
    UI -> U: Show error messages
end

== Load Configuration Flow ==
U -> UI: Load existing project
UI -> Bridge: load_from_yaml(file_path, ui_state)
Bridge -> YAML: Read YAML file
Bridge -> Bridge: _load_into_ui()
Bridge -> UIS: Update all UI state
UIS -> UI: Trigger UI updates
note right: NiceGUI binding system\nautomatically updates UI
Bridge -> UI: Return success

== Stage Merging Flow ==
U -> UI: Switch between stages
UI -> UIS: set active_stage
UIS -> UIS: get_active_stage()
UI -> Bridge: Generate merged config
Bridge -> Bridge: _ui_to_user_config_format()
Bridge -> UI: Return merged YAML structure
@enduml
```

## Integration with PeiDocker Core

### Connection to user_config.yml

The `user_config.yml` file serves as the **primary interface** between the WebGUI and the PeiDocker CLI system. This YAML file follows a specific schema that the PeiDocker CLI understands:

#### YAML Structure Mapping

```yaml
# Generated by WebGUI -> Used by PeiDocker CLI
stage-1:
  image:
    base: ubuntu:22.04          # From ProjectUI.base_image
    output: pei-image:stage-1   # From ProjectUI.image_output_name
  
  environment:                  # From EnvironmentUI.env_vars
    - "VAR1=value1"
    - "VAR2=value2"
  
  device:                       # From EnvironmentUI.device_type
    type: gpu
    gpu:
      all: true                 # From EnvironmentUI.gpu_count
      memory: "4GB"             # From EnvironmentUI.gpu_memory_limit
  
  proxy:                        # From NetworkUI proxy settings
    http: "http://proxy:8080"
    https: "https://proxy:8080"
  
  ssh:                          # From SSHTabUI
    enable: true
    port: 22
    host_port: 2222
    users: [...]

stage-2:
  storage:                      # From StorageUI
    app: "auto-volume"
    data: "host:/data"
    workspace: "volume:ws-vol"
    mounts:
      - "/host/path:/container/path"
  
  scripts:                      # From ScriptsUI
    pre-build: [...]
    post-build: [...]
    first-run: [...]
```

### Bridge Pattern Implementation

The `UIStateBridge` class implements the **Bridge Pattern** to decouple the UI representation from the business logic:

1. **UI-to-Business Transformation**:
   - Converts NiceGUI bindable dataclasses to Pydantic models
   - Applies business validation rules
   - Ensures data integrity before persistence

2. **Business-to-YAML Transformation**:
   - Converts validated business models to `user_config.yml` format
   - Handles complex data structure transformations
   - Manages inline script embedding and metadata

3. **YAML-to-UI Transformation**:
   - Loads existing configurations back into UI state
   - Reconstructs UI-specific metadata from YAML
   - Maintains UI state consistency

### Integration Points with PeiDocker CLI

The WebGUI integrates with PeiDocker's core functionality through several key points:

1. **Configuration Generation**: 
   - WebGUI generates `user_config.yml` files that PeiDocker CLI commands consume
   - The `pei-docker-cli configure` command processes these YAML files

2. **Template System**:
   - WebGUI uses the master template from `src/pei_docker/templates/config-template-full.yml`
   - Ensures compatibility with PeiDocker's expected configuration format

3. **Docker Compose Generation**:
   - The generated `user_config.yml` drives Docker Compose file generation
   - Stage-1 and Stage-2 configurations map to Docker build stages

4. **Project Directory Structure**:
   - WebGUI respects PeiDocker's project directory conventions
   - Manages paths relative to installation directories

## Key Architectural Benefits

### 1. Separation of Concerns
- **UI State**: Handles reactive UI updates and user interactions
- **Business Logic**: Validates data and enforces business rules
- **Data Persistence**: Manages file I/O and format conversion

### 2. Data Binding with NiceGUI
- **Automatic Synchronization**: UI elements automatically update when data changes
- **Type Safety**: Bindable dataclasses provide compile-time type checking
- **Reactive Updates**: Changes propagate immediately to the UI

### 3. Validation Pipeline
- **Client-Side Validation**: Immediate feedback through Pydantic validators
- **Business Rule Enforcement**: Consistent validation across UI and CLI
- **Error Handling**: Structured error reporting with field-level precision

### 4. Bidirectional Data Flow
- **UI → Business**: User inputs validated and transformed to business models
- **Business → YAML**: Business models serialized to PeiDocker-compatible format
- **YAML → UI**: Existing configurations loaded back into UI state

### 5. Extensibility
- **Plugin Architecture**: New configuration sections can be added easily
- **Validation Rules**: Business rules centralized in Pydantic models
- **UI Components**: Modular tab system for feature organization

## Technology Stack

- **Frontend Framework**: NiceGUI (Python-based web UI framework)
- **Data Binding**: NiceGUI's bindable dataclass system
- **Validation**: Pydantic models with custom validators
- **Serialization**: PyYAML for configuration file handling
- **Architecture Pattern**: MVVM with Bridge Pattern
- **Backend**: FastAPI (underlying NiceGUI framework)

This architecture ensures that the WebGUI remains maintainable, extensible, and fully compatible with PeiDocker's existing CLI-based workflow while providing a modern, reactive user interface for configuration management.
