"""
User Configuration Data Structures for PeiDocker.

This module defines type-safe data structures for PeiDocker configuration management
using the attrs library. It provides comprehensive validation, conversion, and
utility functions for handling Docker container configuration in a structured way.

The configuration follows PeiDocker's two-stage architecture:
- Stage 1: System-level setup (base image, SSH, proxy, APT repositories)
- Stage 2: Application-level configuration (custom mounts, scripts, entry points)

Data Structure Hierarchy
------------------------
UserConfig
├── stage_1: StageConfig
│   ├── image: ImageConfig (base and output image names)
│   ├── ssh: SSHConfig (SSH server and user configurations)
│   ├── proxy: ProxyConfig (HTTP proxy settings)
│   ├── apt: AptConfig (APT repository mirror settings)
│   ├── device: DeviceConfig (CPU/GPU hardware configuration)
│   ├── custom: CustomScriptConfig (lifecycle hook scripts)
│   ├── storage: Dict[str, StorageOption] (volume configurations)
│   ├── ports: List[str] (port mappings)
│   └── environment: Dict[str, str] (environment variables)
└── stage_2: StageConfig (same structure as stage_1)

Configuration Features
----------------------
- Type-safe validation with attrs decorators
- Automatic format conversion (list ↔ dict for environment variables)
- SSH key validation with multiple authentication methods
- Port mapping with range support ("8000-8010:9000-9010")
- Storage abstraction supporting Docker volumes, host mounts, and in-image storage
- Custom script lifecycle hooks (on_build, on_first_run, on_every_run, on_user_login)

Utility Functions
-----------------
port_mapping_str_to_dict : Convert port mapping strings to dictionary
port_mapping_dict_to_str : Convert port mapping dictionary to strings
env_str_to_dict : Convert environment variable strings to dictionary
env_dict_to_str : Convert environment variable dictionary to strings

Validation Features
-------------------
- SSH public/private key format validation
- Port range consistency checking
- Storage type validation with required field enforcement
- Password format validation (no spaces or commas)
- Environment variable format validation
- Custom script entry point constraints

Notes
-----
All data classes use attrs with kw_only=True for better API clarity.
Validation happens during object construction via __attrs_post_init__ methods.
The module supports both string and structured formats for flexible configuration.
"""

# Import all public classes and functions from submodules
from pei_docker.user_config.utils import (
    port_mapping_str_to_dict,
    port_mapping_dict_to_str,
    env_str_to_dict,
    env_dict_to_str,
    env_converter
)
from pei_docker.user_config.image import ImageConfig
from pei_docker.user_config.ssh import SSHUserConfig, SSHConfig
from pei_docker.user_config.network import ProxyConfig, AptConfig
from pei_docker.user_config.hardware import DeviceConfig
from pei_docker.user_config.scripts import CustomScriptConfig
from pei_docker.user_config.storage import StorageTypes, StorageOption
from pei_docker.user_config.stage import StageConfig
from pei_docker.user_config.config import UserConfig

# Maintain backward compatibility with the original __all__ list
__all__ = [
    'ImageConfig',
    'SSHUserConfig',
    'SSHConfig',
    'ProxyConfig',
    'AptConfig',
    'DeviceConfig',
    'CustomScriptConfig',
    'StorageOption',
    'StageConfig',
    'StorageTypes',
    'UserConfig',
    'port_mapping_str_to_dict',
    'port_mapping_dict_to_str',
    'env_str_to_dict',
    'env_dict_to_str',
]