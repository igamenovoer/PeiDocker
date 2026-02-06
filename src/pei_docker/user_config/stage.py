"""
Stage configuration for PeiDocker.

This module provides the StageConfig class that represents complete configuration
for a single stage in PeiDocker's two-stage architecture.
"""

from attrs import define, field
from typing import Optional, Dict, List

from pei_docker.user_config.utils import (
    env_converter,
    env_str_to_dict,
    port_mapping_str_to_dict,
    port_mapping_dict_to_str
)
from pei_docker.user_config.image import ImageConfig
from pei_docker.user_config.ssh import SSHConfig
from pei_docker.user_config.network import ProxyConfig, AptConfig
from pei_docker.user_config.hardware import DeviceConfig
from pei_docker.user_config.scripts import CustomScriptConfig
from pei_docker.user_config.storage import StorageOption


@define(kw_only=True)
class StageConfig:
    """
    Complete configuration for a single stage in PeiDocker's two-stage architecture.
    
    Represents all configuration options available for either Stage-1 (system setup)
    or Stage-2 (application configuration). Provides a comprehensive set of options
    for Docker image customization, networking, storage, and runtime behavior.
    
    Attributes
    ----------
    image : ImageConfig, optional
        Docker image configuration specifying base and output images.
        Required for Stage-1; optional for Stage-2 (inherits from Stage-1).
    ssh : SSHConfig, optional
        SSH server configuration for container access. Only supported in Stage-1
        as SSH setup requires system-level privileges.
    proxy : ProxyConfig, optional
        HTTP proxy configuration for build and runtime networking.
        Can be used in both stages for different proxy requirements.
    apt : AptConfig, optional
        APT package manager configuration including repository mirrors.
        Only supported in Stage-1 as it affects system package management.
    environment : Dict[str, str], optional
        Environment variables for the container. Automatically converts from
        list format ("KEY=VALUE") to dictionary format for consistency.
    ports : List[str], optional
        Port mappings in Docker format (e.g., "8080:80", "9000-9010:9000-9010").
        Supports both individual ports and port ranges.
    device : DeviceConfig, optional
        Hardware device configuration (CPU/GPU access requirements).
    custom : CustomScriptConfig, optional
        Custom scripts for container lifecycle hooks (build, startup, login).
    storage : Dict[str, StorageOption], optional
        Storage configurations for Stage-2 data persistence. Maps storage
        names to storage options (volumes, host mounts, in-image).
    mount : Dict[str, StorageOption], optional
        Mount configurations for both stages. Maps mount names to storage
        options, providing flexible volume management.
        
    Methods
    -------
    get_port_mapping_as_dict() : Dict[int, int] or None
        Convert port mappings to dictionary format for programmatic access.
    set_port_mapping_from_dict(port_mapping: Dict[int, int])
        Set port mappings from dictionary format.
    get_environment_as_dict() : Dict[str, str] or None
        Get environment variables as dictionary (handles legacy list format).
        
    Examples
    --------
    Stage-1 system configuration:
        >>> stage1 = StageConfig(
        ...     image=ImageConfig(base="ubuntu:24.04", output="my-app:stage-1"),
        ...     ssh=SSHConfig(users={"admin": SSHUserConfig(password="admin123")}),
        ...     proxy=ProxyConfig(address="proxy.company.com", port=8080),
        ...     apt=AptConfig(repo_source="tuna"),
        ...     environment={"DEBIAN_FRONTEND": "noninteractive"},
        ...     device=DeviceConfig(type="gpu")
        ... )
        
    Stage-2 application configuration:
        >>> stage2 = StageConfig(
        ...     image=ImageConfig(output="my-app:stage-2"),
        ...     ports=["8080:80", "3000:3000"],
        ...     storage={
        ...         "data": StorageOption(type="host", host_path="/data")
        ...     },
        ...     custom=CustomScriptConfig(
        ...         on_first_run=["stage-2/custom/setup-app.sh"]
        ...     )
        ... )
        
    Notes
    -----
    Stage-specific restrictions:
    - SSH configuration only supported in Stage-1
    - APT configuration only supported in Stage-1  
    - Storage configuration primarily used in Stage-2
    - Both stages support proxy, environment, ports, device, custom, and mount
    
    The configuration is processed by PeiConfigProcessor to generate
    Docker Compose files and container setup scripts.
    """
    image: Optional[ImageConfig] = field(default=None)
    ssh: Optional[SSHConfig] = field(default=None)
    proxy: Optional[ProxyConfig] = field(default=None)
    apt: Optional[AptConfig] = field(default=None)
    environment: Optional[Dict[str, str]] = field(default=None, converter=env_converter)
    ports: Optional[List[str]] = field(factory=list)  # Port mappings in Docker format (e.g. "8080:80")
    device: Optional[DeviceConfig] = field(default=None)
    custom: Optional[CustomScriptConfig] = field(default=None)
    storage: Optional[Dict[str, StorageOption]] = field(factory=dict)
    mount: Optional[Dict[str, StorageOption]] = field(factory=dict)
    
    def get_port_mapping_as_dict(self) -> Optional[Dict[int, int]]:
        """
        Get port mappings as dictionary format for programmatic access.
        
        Returns
        -------
        Dict[int, int] or None
            Dictionary mapping host ports to container ports, or None
            if no port mappings are configured.
            
        Examples
        --------
        >>> config = StageConfig(ports=["8080:80", "9000-9002:9000-9002"])
        >>> config.get_port_mapping_as_dict()
        {8080: 80, 9000: 9000, 9001: 9001, 9002: 9002}
        """
        if self.ports is not None:
            return port_mapping_str_to_dict(self.ports)
        return None
        
    def set_port_mapping_from_dict(self, port_mapping: Dict[int, int]) -> None:
        """
        Set port mappings from dictionary format.
        
        Parameters
        ----------
        port_mapping : Dict[int, int]
            Dictionary mapping host ports to container ports.
            
        Examples
        --------
        >>> config = StageConfig()
        >>> config.set_port_mapping_from_dict({8080: 80, 9000: 9000})
        >>> config.ports
        ['8080:80', '9000:9000']
        """
        self.ports = port_mapping_dict_to_str(port_mapping)
        
    def get_environment_as_dict(self) -> Optional[Dict[str, str]]:
        """
        Get environment variables as dictionary format.
        
        Handles legacy list format environment variables by converting them
        to dictionary format for consistent access.
        
        Returns
        -------
        Dict[str, str] or None
            Environment variables as key-value pairs, or None if no
            environment variables are configured.
            
        Examples
        --------
        Dictionary format (modern):
            >>> config = StageConfig(environment={"NODE_ENV": "production"})
            >>> config.get_environment_as_dict()
            {'NODE_ENV': 'production'}
            
        List format (legacy, auto-converted):
            >>> config = StageConfig()
            >>> config.environment = ["NODE_ENV=production", "PORT=3000"]
            >>> config.get_environment_as_dict()
            {'NODE_ENV': 'production', 'PORT': '3000'}
        """
        if self.environment is not None and isinstance(self.environment, list):
            return env_str_to_dict(self.environment)
        else:
            return self.environment