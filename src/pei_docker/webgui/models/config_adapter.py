"""
Adapter layer for converting attrs-based CLI models to pydantic-compatible interfaces.

This module provides adapters that make attrs-based configuration models from
user_config.py compatible with the pydantic-expecting GUI code, eliminating
the need for duplicate model definitions.
"""

from typing import Protocol, Dict, List, Any, Optional, runtime_checkable, Union
from dataclasses import dataclass
from pathlib import Path

# Import attrs-based models from CLI
from pei_docker.user_config import (
    UserConfig as AttrsUserConfig,
    StageConfig as AttrsStageConfig,
    ImageConfig as AttrsImageConfig,
    SSHConfig as AttrsSSHConfig,
    SSHUserConfig as AttrsSSHUserConfig,
    ProxyConfig as AttrsProxyConfig,
    AptConfig as AttrsAptConfig,
    DeviceConfig as AttrsDeviceConfig,
    CustomScriptConfig as AttrsCustomScriptConfig,
    StorageOption as AttrsStorageOption,
    StorageTypes,
    port_mapping_str_to_dict,
    port_mapping_dict_to_str,
    env_str_to_dict,
    env_dict_to_str,
)


# Protocol definitions for each configuration type
@runtime_checkable
class ImageConfigProtocol(Protocol):
    """Protocol for image configuration."""
    base: Optional[str]
    output: Optional[str]


@runtime_checkable
class SSHUserConfigProtocol(Protocol):
    """Protocol for SSH user configuration."""
    name: str
    password: Optional[str]
    uid: Optional[int]
    ssh_keys: List[str]


@runtime_checkable
class SSHConfigProtocol(Protocol):
    """Protocol for SSH configuration."""
    enabled: bool
    port: int
    host_port: int
    users: List[Dict[str, Any]]


@runtime_checkable
class NetworkConfigProtocol(Protocol):
    """Protocol for network configuration (merges proxy and ports)."""
    proxy_enabled: bool
    http_proxy: str
    https_proxy: str
    no_proxy: str
    apt_mirror: str
    port_mappings: List[Dict[str, str]]


@runtime_checkable
class EnvironmentConfigProtocol(Protocol):
    """Protocol for environment configuration (merges device and env vars)."""
    gpu_enabled: bool
    gpu_count: str
    cuda_version: str
    env_vars: Dict[str, str]
    device_type: str
    gpu_memory_limit: str


@runtime_checkable
class StorageConfigProtocol(Protocol):
    """Protocol for storage configuration."""
    app_storage_type: str
    app_volume_name: str
    app_host_path: str
    data_storage_type: str
    data_volume_name: str
    data_host_path: str
    workspace_storage_type: str
    workspace_volume_name: str
    workspace_host_path: str
    volumes: List[Dict[str, str]]
    mounts: List[Dict[str, str]]


@runtime_checkable
class ScriptsConfigProtocol(Protocol):
    """Protocol for scripts configuration."""
    stage1_entry_mode: str
    stage1_entry_command: str
    stage1_entry_params: str
    stage2_entry_mode: str
    stage2_entry_command: str
    stage2_entry_params: str
    pre_build: List[str]
    post_build: List[str]
    first_run: List[str]
    every_run: List[str]
    user_login: List[str]


# Adapter implementations
@dataclass
class ImageConfigAdapter:
    """Adapter for ImageConfig."""
    _config: AttrsImageConfig
    
    @property
    def base(self) -> Optional[str]:
        return self._config.base
    
    @property
    def output(self) -> Optional[str]:
        return self._config.output


@dataclass
class SSHConfigAdapter:
    """Adapter for SSHConfig with field mapping."""
    _config: AttrsSSHConfig
    
    @property
    def enabled(self) -> bool:
        """Map 'enable' to 'enabled'."""
        return self._config.enable
    
    @property
    def port(self) -> int:
        return self._config.port
    
    @property
    def host_port(self) -> int:
        """Provide default if None."""
        return self._config.host_port or 2222
    
    @property
    def users(self) -> List[Dict[str, Any]]:
        """Convert dict[str, SSHUserConfig] to List[Dict[str, Any]]."""
        users = []
        for username, user_config in self._config.users.items():
            user_dict = {
                'name': username,
                'password': user_config.password,
                'uid': user_config.uid,
                'ssh_keys': self._extract_ssh_keys(user_config)
            }
            users.append(user_dict)
        return users
    
    def _extract_ssh_keys(self, user: AttrsSSHUserConfig) -> List[str]:
        """Extract SSH keys from user config."""
        keys = []
        if user.pubkey_text:
            keys.append(user.pubkey_text)
        if user.pubkey_file:
            keys.append(f"file:{user.pubkey_file}")
        return keys


@dataclass
class NetworkConfigAdapter:
    """Adapter that merges ProxyConfig, AptConfig, and port mappings."""
    _proxy: Optional[AttrsProxyConfig]
    _apt: Optional[AttrsAptConfig]
    _ports: Optional[List[str]]
    
    @property
    def proxy_enabled(self) -> bool:
        return bool(self._proxy and self._proxy.address and self._proxy.port)
    
    @property
    def http_proxy(self) -> str:
        if not self._proxy or not self._proxy.address or not self._proxy.port:
            return ""
        scheme = "https" if self._proxy.use_https else "http"
        return f"{scheme}://{self._proxy.address}:{self._proxy.port}"
    
    @property
    def apt_mirror(self) -> str:
        return self._apt.repo_source if self._apt and self._apt.repo_source else ""
    
    @property
    def port_mappings(self) -> List[Dict[str, str]]:
        """Convert port mapping strings to list of dicts."""
        if not self._ports:
            return []
        
        port_dict = port_mapping_str_to_dict(self._ports)
        return [
            {'host': str(host), 'container': str(container)}
            for host, container in port_dict.items()
        ]


@dataclass
class EnvironmentConfigAdapter:
    """Adapter that merges DeviceConfig and environment variables."""
    _device: Optional[AttrsDeviceConfig]
    _env_vars: Optional[Dict[str, str]]
    
    @property
    def gpu_enabled(self) -> bool:
        return self._device is not None and self._device.type == "gpu"
    
    @property
    def gpu_count(self) -> str:
        return "all" if self.gpu_enabled else "0"
    
    @property
    def cuda_version(self) -> str:
        return "12.4"  # Default CUDA version
    
    @property
    def env_vars(self) -> Dict[str, str]:
        return self._env_vars or {}
    
    @property
    def device_type(self) -> str:
        if not self._device:
            return "cpu"
        return self._device.type
    
    @property
    def gpu_memory_limit(self) -> str:
        return ""  # Not supported in attrs model


@dataclass
class StorageConfigAdapter:
    """Adapter for storage configuration."""
    _storage: Optional[Dict[str, AttrsStorageOption]]
    _mount: Optional[Dict[str, AttrsStorageOption]]
    
    def _get_storage_config(self, key: str) -> Optional[AttrsStorageOption]:
        """Get storage config by key."""
        if self._storage and key in self._storage:
            return self._storage[key]
        return None
    
    @property
    def app_storage_type(self) -> str:
        config = self._get_storage_config('app')
        return config.type if config else "auto-volume"
    
    @property
    def app_volume_name(self) -> str:
        config = self._get_storage_config('app')
        return config.volume_name or "" if config else ""
    
    @property
    def app_host_path(self) -> str:
        config = self._get_storage_config('app')
        return config.host_path or "" if config else ""
    
    @property
    def data_storage_type(self) -> str:
        config = self._get_storage_config('data')
        return config.type if config else "auto-volume"
    
    @property
    def data_volume_name(self) -> str:
        config = self._get_storage_config('data')
        return config.volume_name or "" if config else ""
    
    @property
    def data_host_path(self) -> str:
        config = self._get_storage_config('data')
        return config.host_path or "" if config else ""
    
    @property
    def workspace_storage_type(self) -> str:
        config = self._get_storage_config('workspace')
        return config.type if config else "auto-volume"
    
    @property
    def workspace_volume_name(self) -> str:
        config = self._get_storage_config('workspace')
        return config.volume_name or "" if config else ""
    
    @property
    def workspace_host_path(self) -> str:
        config = self._get_storage_config('workspace')
        return config.host_path or "" if config else ""
    
    @property
    def volumes(self) -> List[Dict[str, str]]:
        """Convert general storage to volume list."""
        volumes = []
        if self._storage:
            for name, config in self._storage.items():
                if name not in ['app', 'data', 'workspace']:
                    volumes.append({
                        'name': name,
                        'type': config.type,
                        'source': config.volume_name or config.host_path or "",
                        'target': config.dst_path or f"/mnt/{name}"
                    })
        return volumes
    
    @property
    def mounts(self) -> List[Dict[str, str]]:
        """Convert mount configurations."""
        mounts = []
        if self._mount:
            for name, config in self._mount.items():
                mounts.append({
                    'name': name,
                    'type': config.type,
                    'source': config.volume_name or config.host_path or "",
                    'target': config.dst_path or f"/mnt/{name}"
                })
        return mounts


@dataclass
class ScriptsConfigAdapter:
    """Adapter for scripts configuration."""
    _custom: Optional[AttrsCustomScriptConfig]
    _stage_name: str
    
    @property
    def stage1_entry_mode(self) -> str:
        if self._stage_name != "stage_1" or not self._custom:
            return "default"
        return "custom" if self._custom.on_entry else "default"
    
    @property
    def stage1_entry_command(self) -> str:
        if self._stage_name != "stage_1" or not self._custom:
            return ""
        entry = self._custom.get_entry_script()
        if entry:
            # Extract command from script path
            parts = entry.split()
            return parts[0] if parts else ""
        return ""
    
    @property
    def stage1_entry_params(self) -> str:
        if self._stage_name != "stage_1" or not self._custom:
            return ""
        entry = self._custom.get_entry_script()
        if entry:
            # Extract params from script path
            parts = entry.split()
            return " ".join(parts[1:]) if len(parts) > 1 else ""
        return ""
    
    @property
    def stage2_entry_mode(self) -> str:
        if self._stage_name != "stage_2" or not self._custom:
            return "default"
        return "custom" if self._custom.on_entry else "default"
    
    @property
    def stage2_entry_command(self) -> str:
        if self._stage_name != "stage_2" or not self._custom:
            return ""
        entry = self._custom.get_entry_script()
        if entry:
            parts = entry.split()
            return parts[0] if parts else ""
        return ""
    
    @property
    def stage2_entry_params(self) -> str:
        if self._stage_name != "stage_2" or not self._custom:
            return ""
        entry = self._custom.get_entry_script()
        if entry:
            parts = entry.split()
            return " ".join(parts[1:]) if len(parts) > 1 else ""
        return ""
    
    @property
    def pre_build(self) -> List[str]:
        return self._custom.on_build if self._custom else []
    
    @property
    def post_build(self) -> List[str]:
        return []  # Not supported in attrs model
    
    @property
    def first_run(self) -> List[str]:
        return self._custom.on_first_run if self._custom else []
    
    @property
    def every_run(self) -> List[str]:
        return self._custom.on_every_run if self._custom else []
    
    @property
    def user_login(self) -> List[str]:
        return self._custom.on_user_login if self._custom else []


@dataclass
class StageConfigAdapter:
    """Adapter for complete stage configuration."""
    _stage_config: Optional[AttrsStageConfig]
    _stage_name: str
    
    @property
    def environment(self) -> EnvironmentConfigAdapter:
        if not self._stage_config:
            return EnvironmentConfigAdapter(None, None)
        return EnvironmentConfigAdapter(
            self._stage_config.device,
            self._stage_config.environment
        )
    
    @property
    def network(self) -> NetworkConfigAdapter:
        if not self._stage_config:
            return NetworkConfigAdapter(None, None, None)
        return NetworkConfigAdapter(
            self._stage_config.proxy,
            self._stage_config.apt,
            self._stage_config.ports
        )
    
    @property
    def ssh(self) -> SSHConfigAdapter:
        if not self._stage_config or not self._stage_config.ssh:
            # Return a default disabled SSH config
            from pei_docker.user_config import SSHConfig
            return SSHConfigAdapter(SSHConfig(enable=False))
        return SSHConfigAdapter(self._stage_config.ssh)
    
    @property
    def storage(self) -> StorageConfigAdapter:
        if not self._stage_config:
            return StorageConfigAdapter(None, None)
        return StorageConfigAdapter(
            self._stage_config.storage,
            self._stage_config.mount
        )
    
    @property
    def scripts(self) -> ScriptsConfigAdapter:
        if not self._stage_config:
            return ScriptsConfigAdapter(None, self._stage_name)
        return ScriptsConfigAdapter(
            self._stage_config.custom,
            self._stage_name
        )


@dataclass
class ProjectConfigAdapter:
    """Adapter for project configuration."""
    project_name: str = ""
    project_directory: str = ""
    base_image: str = "ubuntu:22.04"
    image_output_name: str = ""
    template: str = "basic"


@dataclass
class AppConfigAdapter:
    """Adapter for complete application configuration."""
    _user_config: Optional[AttrsUserConfig]
    _project_config: ProjectConfigAdapter
    
    @property
    def project(self) -> ProjectConfigAdapter:
        return self._project_config
    
    @property
    def stage_1(self) -> StageConfigAdapter:
        if not self._user_config:
            return StageConfigAdapter(None, "stage_1")
        return StageConfigAdapter(self._user_config.stage_1, "stage_1")
    
    @property
    def stage_2(self) -> StageConfigAdapter:
        if not self._user_config:
            return StageConfigAdapter(None, "stage_2")
        return StageConfigAdapter(self._user_config.stage_2, "stage_2")


# Factory functions for creating adapters from dictionaries
def create_attrs_config_from_dict(config_dict: Dict[str, Any]) -> AttrsUserConfig:
    """Create attrs UserConfig from dictionary data."""
    # This will use attrs' built-in validation
    return AttrsUserConfig(**config_dict)


def create_app_config_adapter(
    user_config: Optional[AttrsUserConfig],
    project_info: Optional[Dict[str, Any]] = None
) -> AppConfigAdapter:
    """Create complete app config adapter."""
    project_config = ProjectConfigAdapter()
    if project_info:
        project_config.project_name = project_info.get('project_name', '')
        project_config.project_directory = project_info.get('project_directory', '')
        project_config.base_image = project_info.get('base_image', 'ubuntu:22.04')
        project_config.image_output_name = project_info.get('image_output_name', '')
        project_config.template = project_info.get('template', 'basic')
    
    return AppConfigAdapter(user_config, project_config)