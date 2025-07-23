# List of GUI Pydantic Models

**Generated:** July 24, 2025  
**Directory:** `src/pei_docker/gui/`  
**Status:** No Pydantic Models Found  

## Summary

After comprehensive analysis of the PeiDocker GUI module, **no Pydantic models were found**. The GUI module uses alternative data modeling approaches instead of Pydantic.

## Data Modeling Approaches Used in GUI

### 1. Python Dataclasses (`@dataclass`)
**Location:** `src/pei_docker/gui/models/config.py`

The GUI module exclusively uses Python's standard `dataclass` decorator for data models:

#### SSHUser
```python
@dataclass 
class SSHUser:
    """SSH user configuration."""
    name: str
    password: str
    uid: int = 1100
    pubkey_text: Optional[str] = None
    privkey_file: Optional[str] = None
```

#### SSHConfig
```python
@dataclass
class SSHConfig:
    """SSH configuration."""
    enable: bool = True
    port: int = 22
    host_port: int = 2222
    users: List[SSHUser] = field(default_factory=list)
    root_enabled: bool = False
    root_password: str = "root"
```

#### ProxyConfig
```python
@dataclass
class ProxyConfig:
    """Proxy configuration."""
    enable: bool = False
    port: int = 8080
    build_only: bool = True
```

#### DeviceConfig
```python
@dataclass
class DeviceConfig:
    """Device configuration."""
    device_type: str = "cpu"  # "cpu" or "gpu"
```

#### MountConfig
```python
@dataclass
class MountConfig:
    """Mount configuration."""
    mount_type: str  # "auto-volume", "manual-volume", "host", "image"
    dst_path: str
    src_path: Optional[str] = None
    name: Optional[str] = None
```

#### Stage1Config
```python
@dataclass
class Stage1Config:
    """Stage-1 configuration."""
    base_image: str = "ubuntu:24.04"
    output_image: str = ""
    ssh: SSHConfig = field(default_factory=SSHConfig)
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    apt_mirror: str = "default"
    ports: List[str] = field(default_factory=list)
    environment: List[str] = field(default_factory=list)
    device: DeviceConfig = field(default_factory=DeviceConfig)
    mounts: Dict[str, MountConfig] = field(default_factory=dict)
    custom_entry: Optional[str] = None
    custom_scripts: Dict[str, List[str]] = field(default_factory=dict)
```

#### Stage2Config
```python
@dataclass
class Stage2Config:
    """Stage-2 configuration."""
    output_image: str = ""
    mounts: Dict[str, MountConfig] = field(default_factory=dict)
    custom_entry: Optional[str] = None
    custom_scripts: Dict[str, List[str]] = field(default_factory=dict)
```

#### ProjectConfig
```python
@dataclass
class ProjectConfig:
    """Complete project configuration."""
    project_name: str = ""
    project_dir: str = ""
    stage_1: Stage1Config = field(default_factory=Stage1Config)
    stage_2: Stage2Config = field(default_factory=Stage2Config)
```

**Methods:**
- `to_user_config_dict(self) -> Dict`: Converts GUI models to user_config.yml compatible dictionary

### 2. Textual Message Classes
**Purpose:** Inter-component communication in the Textual framework

#### ConfigUpdated (forms.py)
```python
class ConfigUpdated(Message):
    """Message sent when configuration is updated."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__()
        self.config = config
```

#### ConfigReady Messages (multiple screen files)
Found in various screen files with similar structure:
```python
class ConfigReady(Message):
    """Message sent when configuration is ready."""
    
    def __init__(self, [data]: [type]) -> None:
        super().__init__()
        self.[data] = [data]
```

**Locations:**
- `env_vars.py`: `ConfigReady(variables: list[str])`
- `mounts.py`: `ConfigReady(stage1_mounts: list[MountConfig], stage2_mounts: list[MountConfig])`
- `entry_point.py`: `ConfigReady(stage1_entrypoint: str, stage2_entrypoint: str)`
- `proxy_config.py`: `ConfigReady(config: ProxyConfig)`
- `apt_config.py`: `ConfigReady(mirror: str)`
- `device_config.py`: `ConfigReady(config: DeviceConfig)`
- `port_mapping.py`: `ConfigReady(mappings: list[str])`
- `custom_scripts.py`: `ConfigReady(stage1_scripts: Dict[str, List[str]], stage2_scripts: Dict[str, List[str]])`

#### BackPressed Messages
Simple message classes with no additional data:
```python
class BackPressed(Message):
    """Message sent when back button is pressed."""
    pass
```

### 3. Textual Validator Classes
**Location:** `src/pei_docker/gui/widgets/inputs.py`

Custom validation classes extending Textual's `Validator`:

#### DockerImageValidator
```python
class DockerImageValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Validate Docker image name format."""
```

#### EnvironmentVariableValidator
```python
class EnvironmentVariableValidator(Validator):  
    def validate(self, value: str) -> ValidationResult:
        """Validate environment variable format."""
```

#### PortMappingValidator
```python
class PortMappingValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Validate port mapping format."""
```

#### PortNumberValidator  
```python
class PortNumberValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Validate port number."""
```

#### UserIDValidator
```python
class UserIDValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Validate user ID."""
```

## Architecture Notes

### Why No Pydantic Models?

The GUI module uses Python's standard `dataclass` approach instead of Pydantic for several possible reasons:

1. **Simplicity**: Dataclasses are part of the Python standard library and don't require additional dependencies
2. **GUI-specific needs**: The models are primarily for internal GUI state management, not API validation
3. **Textual integration**: The Textual framework has its own validation system for form inputs
4. **Performance**: Dataclasses have less overhead than Pydantic for simple data structures

### Validation Strategy

Instead of Pydantic's model-level validation, the GUI uses:

1. **Input-level validation**: Custom Textual validators for form inputs
2. **Manual validation**: Utility functions in `file_utils.py` for specific validation needs
3. **Type hints**: Leverages Python's type system for static analysis

### Data Flow

```
GUI Dataclass Models → to_user_config_dict() → YAML Configuration → CLI Processing
```

The GUI models serve as an intermediate representation that gets converted to the CLI's configuration format through the `to_user_config_dict()` method.

## Conclusion

The PeiDocker GUI module does not use Pydantic models. Instead, it employs a simpler architecture using:

- **8 Dataclass models** for configuration data
- **Multiple Message classes** for Textual framework communication  
- **5 Validator classes** for input validation
- **1 conversion method** to bridge GUI and CLI data models

This approach prioritizes simplicity and direct integration with the Textual framework over the advanced validation and serialization features that Pydantic provides.
