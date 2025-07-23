# List of GUI Data Models

**Generated:** July 24, 2025  
**Directory:** `src/pei_docker/gui/`  
**Type:** Python Dataclasses (No Pydantic)

## Summary

The PeiDocker GUI module uses Python's standard `@dataclass` decorator instead of Pydantic models for data modeling.

## Configuration Models
**Location:** `src/pei_docker/gui/models/config.py`

### SSHUser
```python
name: str
password: str
uid: int = 1100
pubkey_text: Optional[str] = None
privkey_file: Optional[str] = None
```

### SSHConfig
```python
enable: bool = True
port: int = 22
host_port: int = 2222
users: List[SSHUser] = field(default_factory=list)
root_enabled: bool = False
root_password: str = "root"
```

### ProxyConfig
```python
enable: bool = False
port: int = 8080
build_only: bool = True
```

### DeviceConfig
```python
device_type: str = "cpu"  # "cpu" or "gpu"
```

### MountConfig
```python
mount_type: str  # "auto-volume", "manual-volume", "host", "image"
dst_path: str
src_path: Optional[str] = None
name: Optional[str] = None
```

### Stage1Config
```python
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

### Stage2Config
```python
output_image: str = ""
mounts: Dict[str, MountConfig] = field(default_factory=dict)
custom_entry: Optional[str] = None
custom_scripts: Dict[str, List[str]] = field(default_factory=dict)
```

### ProjectConfig
```python
project_name: str = ""
project_dir: str = ""
stage_1: Stage1Config = field(default_factory=Stage1Config)
stage_2: Stage2Config = field(default_factory=Stage2Config)

# Methods:
to_user_config_dict() -> Dict  # Converts to CLI format
```

## Message Classes
**Purpose:** Textual framework inter-component communication

### ConfigUpdated (forms.py)
```python
config: Dict[str, Any]
```

### ConfigReady Messages (various screens)
- `env_vars.py`: `variables: list[str]`
- `mounts.py`: `stage1_mounts: list[MountConfig], stage2_mounts: list[MountConfig]`
- `entry_point.py`: `stage1_entrypoint: str, stage2_entrypoint: str`
- `proxy_config.py`: `config: ProxyConfig`
- `apt_config.py`: `mirror: str`
- `device_config.py`: `config: DeviceConfig`
- `port_mapping.py`: `mappings: list[str]`
- `custom_scripts.py`: `stage1_scripts: Dict[str, List[str]], stage2_scripts: Dict[str, List[str]]`

### BackPressed Messages
Simple message classes with no properties (just signals).

## Validator Classes
**Location:** `src/pei_docker/gui/widgets/inputs.py`

- **DockerImageValidator**: Validates Docker image name format
- **EnvironmentVariableValidator**: Validates KEY=VALUE format
- **PortMappingValidator**: Validates port mapping format  
- **PortNumberValidator**: Validates port numbers
- **UserIDValidator**: Validates user IDs

## Architecture Notes

**Why Dataclasses over Pydantic:**
- Standard library (no dependencies)
- GUI-specific internal state management
- Integration with Textual's validation system
- Lower overhead for simple data structures

**Data Flow:**
```
GUI Dataclasses → to_user_config_dict() → YAML → CLI Processing
```
