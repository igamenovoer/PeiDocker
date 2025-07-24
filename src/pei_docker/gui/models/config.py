"""
Configuration Data Models for PeiDocker GUI.

This module provides strongly-typed data models for managing PeiDocker project
configuration. The models use Python dataclasses to represent the hierarchical
structure of a PeiDocker configuration, including SSH settings, proxy configuration,
device options, and mount points.

The configuration follows a two-stage architecture:
- Stage 1: System-level setup (base image, SSH, proxy, APT mirrors, etc.)
- Stage 2: Application-level configuration (custom mounts, scripts, entry points)

All models can be serialized to the user_config.yml format expected by the
PeiDocker core engine.

Classes
-------
SSHUser : SSH user account configuration
SSHConfig : SSH server configuration
ProxyConfig : HTTP proxy configuration  
DeviceConfig : Hardware device configuration (CPU/GPU)
MountConfig : Volume mount configuration
Stage1Config : Stage-1 system configuration
Stage2Config : Stage-2 application configuration
ProjectConfig : Complete project configuration with serialization methods

Notes
-----
The models maintain backward compatibility with the existing PeiDocker
YAML configuration format and provide type safety for the GUI application.
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass 
class SSHUser:
    """
    SSH user account configuration.
    
    Represents a single SSH user account that will be created in the Docker
    container with specified authentication methods and system properties.
    
    Attributes
    ----------
    name : str
        Username for the SSH account.
    password : str
        Password for the SSH account. Should not contain spaces or commas
        due to implementation constraints.
    uid : int, default 1100
        User ID for the account. Default is 1100 to avoid conflicts with
        system users (typically in 1000-1099 range).
    pubkey_text : str, optional
        SSH public key text for key-based authentication. If provided,
        enables passwordless SSH access. Default is None.
    privkey_file : str, optional
        Path to SSH private key file. Supports absolute paths and tilde
        expansion for user home directory. Default is None.
        
    Notes
    -----
    For security, avoid using UIDs in the 1000-1099 range as they may
    conflict with system users and groups in Ubuntu images.
    """
    name: str
    password: str
    uid: int = 1100
    pubkey_text: Optional[str] = None
    privkey_file: Optional[str] = None


@dataclass
class SSHConfig:
    """
    SSH server configuration for Docker container.
    
    Manages SSH server setup including port mapping, user accounts,
    and root access settings. The SSH server enables remote terminal
    access to the running container.
    
    Attributes
    ----------
    enable : bool, default True
        Whether to enable SSH server in the container.
    port : int, default 22
        Port number for SSH server inside the container.
    host_port : int, default 2222
        Port number on the host machine that maps to the container SSH port.
    users : List[SSHUser], default empty list
        List of SSH user accounts to create in the container.
    root_enabled : bool, default False
        Whether to enable SSH access for the root user.
    root_password : str, default "root"
        Password for root SSH access when root_enabled is True.
        
    Notes
    -----
    SSH provides the primary method for interactive access to containers.
    When disabled, users must use docker exec commands for container access.
    """
    enable: bool = True
    port: int = 22
    host_port: int = 2222
    users: List[SSHUser] = field(default_factory=list)
    root_enabled: bool = False
    root_password: str = "root"


@dataclass
class ProxyConfig:
    """
    HTTP proxy configuration for container networking.
    
    Configures HTTP/HTTPS proxy settings for the Docker container,
    enabling internet access through a proxy server during build
    and/or runtime.
    
    Attributes
    ----------
    enable : bool, default False
        Whether to enable proxy configuration.
    port : int, default 8080
        Port number of the proxy server on the host machine.
    build_only : bool, default True
        If True, proxy is only used during Docker image build process.
        If False, proxy remains available during container runtime.
        
    Notes
    -----
    The proxy configuration sets http_proxy and https_proxy environment
    variables using the format http://host.docker.internal:{port}.
    """
    enable: bool = False
    port: int = 8080
    build_only: bool = True


@dataclass
class DeviceConfig:
    """
    Hardware device configuration for container access.
    
    Specifies hardware device access requirements, primarily for
    GPU support in machine learning and graphics applications.
    
    Attributes
    ----------
    device_type : str, default "cpu"
        Type of device access required. Valid values are "cpu" or "gpu".
        
    Notes
    -----
    GPU support requires NVIDIA Docker runtime, compatible GPU drivers,
    and CUDA-compatible base images. No automatic GPU detection is performed.
    """
    device_type: str = "cpu"  # "cpu" or "gpu"


@dataclass
class MountConfig:
    """
    Volume mount configuration for data persistence.
    
    Defines how external storage is mounted into the container,
    supporting various mount types including Docker volumes,
    host directories, and in-image storage.
    
    Attributes
    ----------
    mount_type : str
        Type of mount. Valid values: "auto-volume", "manual-volume", 
        "host", "image".
    dst_path : str
        Destination path inside the container where the mount appears.
    src_path : str, optional
        Source path for host mounts or volume identifier for manual volumes.
        Not used for auto-volume or image mounts. Default is None.
    name : str, optional
        Name identifier for the mount configuration. Default is None.
        
    Notes
    -----
    Mount types:
    - auto-volume: Docker volume created automatically
    - manual-volume: Existing Docker volume (requires name)
    - host: Host directory mounted into container
    - image: Data stored inside the Docker image
    """
    mount_type: str  # "auto-volume", "manual-volume", "host", "image"
    dst_path: str
    src_path: Optional[str] = None
    name: Optional[str] = None


@dataclass
class Stage1Config:
    """
    Stage-1 system-level configuration.
    
    Represents the first stage of PeiDocker's two-stage build architecture,
    focusing on system-level setup including base image selection, SSH server,
    proxy configuration, package repositories, and system dependencies.
    
    Attributes
    ----------
    base_image : str, default "ubuntu:24.04"
        Base Docker image to build upon. Should be a valid Docker Hub image.
    output_image : str, default ""
        Name for the output image after Stage-1 build. Auto-generated if empty.
    ssh : SSHConfig
        SSH server configuration including users and authentication.
    proxy : ProxyConfig
        HTTP proxy configuration for build and runtime networking.
    apt_mirror : str, default "default"
        APT repository mirror to use. Options: "default", "tuna", "aliyun", 
        "163", "ustc", "cn".
    ports : List[str], default empty list
        Additional port mappings in "host:container" format (e.g., "8080:80").
    environment : List[str], default empty list
        Environment variables in "KEY=VALUE" format.
    device : DeviceConfig
        Hardware device configuration (CPU/GPU access).
    mounts : Dict[str, MountConfig], default empty dict
        Volume mount configurations keyed by mount name.
    custom_entry : str, optional
        Path to custom entry point script. Default is None.
    custom_scripts : Dict[str, List[str]], default empty dict
        Custom lifecycle scripts organized by hook type ("on_build", 
        "on_first_run", "on_every_run", "on_user_login").
        
    Notes
    -----
    Stage-1 creates the system foundation that Stage-2 builds upon.
    All system-level configurations should be specified here rather
    than in Stage-2 to maintain the separation of concerns.
    """
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


@dataclass
class Stage2Config:
    """
    Stage-2 application-level configuration.
    
    Represents the second stage of PeiDocker's two-stage build architecture,
    focusing on application-specific configurations that build upon the
    Stage-1 system foundation.
    
    Attributes
    ----------
    output_image : str, default ""
        Name for the final output image after Stage-2 build. Auto-generated if empty.
    mounts : Dict[str, MountConfig], default empty dict
        Volume mount configurations that override Stage-1 mounts.
    custom_entry : str, optional
        Path to custom entry point script that overrides Stage-1 entry point.
        Default is None.
    custom_scripts : Dict[str, List[str]], default empty dict
        Custom lifecycle scripts that extend or override Stage-1 scripts.
        Organized by hook type ("on_build", "on_first_run", "on_every_run", 
        "on_user_login").
        
    Notes
    -----
    Stage-2 configurations are applied after Stage-1 and can override
    Stage-1 settings. This is particularly important for mounts and
    entry points where Stage-2 completely replaces Stage-1 configurations.
    """
    output_image: str = ""
    mounts: Dict[str, MountConfig] = field(default_factory=dict)
    custom_entry: Optional[str] = None
    custom_scripts: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ProjectConfig:
    """
    Complete project configuration for PeiDocker.
    
    This is the root configuration object that contains all settings
    needed to generate a complete PeiDocker project, including both
    Stage-1 and Stage-2 configurations.
    
    Attributes
    ----------
    project_name : str, default ""
        Name of the project, used for Docker image naming and directory
        structure. Must follow Docker image naming conventions.
    project_dir : str, default ""
        Absolute path to the project directory where configuration
        files and build artifacts will be stored.
    stage_1 : Stage1Config
        System-level configuration for the first build stage.
    stage_2 : Stage2Config
        Application-level configuration for the second build stage.
        
    Notes
    -----
    This class serves as the central state object for the GUI application,
    maintaining all user configuration choices as they navigate through
    the wizard screens. Changes are kept in memory until explicitly
    saved to user_config.yml.
    """
    project_name: str = ""
    project_dir: str = ""
    stage_1: Stage1Config = field(default_factory=Stage1Config)
    stage_2: Stage2Config = field(default_factory=Stage2Config)
    
    def to_user_config_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to user_config.yml compatible dictionary.
        
        This method serializes the complete project configuration into the
        hierarchical dictionary format expected by the PeiDocker core engine.
        The output can be written directly to user_config.yml.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary containing the serialized configuration with 'stage_1'
            and optionally 'stage_2' keys. Only includes Stage-2 if it contains
            non-default configurations.
            
        Notes
        -----
        The serialization process:
        1. Always includes stage_1 with all configured options
        2. Only includes stage_2 if it has custom mounts, scripts, entry points,
           or output image settings
        3. Maintains backward compatibility with existing user_config.yml format
        4. Handles optional fields by omitting them when they have default values
        
        Examples
        --------
        Basic configuration with SSH enabled:
            >>> config = ProjectConfig()
        >>> config.project_name = "my-project"
        >>> config.stage_1.ssh.users.append(SSHUser("user", "pass"))
        >>> result = config.to_user_config_dict()
        >>> "stage_1" in result
        True
        """
        config: Dict[str, Any] = {}
        
        # Stage 1
        stage1_dict: Dict[str, Any] = {
            "image": {
                "base": self.stage_1.base_image,
                "output": self.stage_1.output_image
            }
        }
        
        if self.stage_1.ssh.enable:
            users_dict: Dict[str, Any] = {}
            for user in self.stage_1.ssh.users:
                users_dict[user.name] = {
                    "password": user.password,
                    "uid": user.uid
                }
                if user.pubkey_text:
                    users_dict[user.name]["pubkey_text"] = user.pubkey_text
                if user.privkey_file:
                    users_dict[user.name]["privkey_file"] = user.privkey_file
            
            if self.stage_1.ssh.root_enabled:
                users_dict["root"] = {"password": self.stage_1.ssh.root_password}
            
            stage1_dict["ssh"] = {
                "enable": True,
                "port": self.stage_1.ssh.port,
                "host_port": self.stage_1.ssh.host_port,
                "users": users_dict
            }
        else:
            stage1_dict["ssh"] = {"enable": False}
        
        if self.stage_1.proxy.enable:
            stage1_dict["proxy"] = {
                "enable": True,
                "port": self.stage_1.proxy.port,
                "build_only": self.stage_1.proxy.build_only
            }
        else:
            stage1_dict["proxy"] = {"enable": False}
        
        if self.stage_1.apt_mirror != "default":
            stage1_dict["apt"] = {"repo_source": self.stage_1.apt_mirror}
        
        if self.stage_1.ports:
            stage1_dict["ports"] = self.stage_1.ports
        
        if self.stage_1.environment:
            stage1_dict["environment"] = self.stage_1.environment
        
        if self.stage_1.device.device_type != "cpu":
            stage1_dict["device"] = {"type": self.stage_1.device.device_type}
        
        if self.stage_1.mounts:
            stage1_mount_dict: Dict[str, Any] = {}
            for name, mount in self.stage_1.mounts.items():
                mount_config = {
                    "type": mount.mount_type,
                    "dst_path": mount.dst_path
                }
                if mount.src_path:
                    mount_config["src_path"] = mount.src_path
                if mount.name:
                    mount_config["name"] = mount.name
                stage1_mount_dict[name] = mount_config
            stage1_dict["mount"] = stage1_mount_dict
        
        if self.stage_1.custom_entry:
            stage1_dict["custom"] = {"on_entry": self.stage_1.custom_entry}
        
        if self.stage_1.custom_scripts:
            if "custom" not in stage1_dict:
                stage1_dict["custom"] = {}
            stage1_dict["custom"].update(self.stage_1.custom_scripts)
        
        config["stage_1"] = stage1_dict
        
        # Stage 2 (if needed)
        if (self.stage_2.mounts or self.stage_2.custom_entry or 
            self.stage_2.custom_scripts or self.stage_2.output_image):
            stage2_dict: Dict[str, Any] = {}
            
            if self.stage_2.output_image:
                stage2_dict["image"] = {"output": self.stage_2.output_image}
            
            if self.stage_2.mounts:
                stage2_mount_dict: Dict[str, Any] = {}
                for name, mount in self.stage_2.mounts.items():
                    mount_config = {
                        "type": mount.mount_type,
                        "dst_path": mount.dst_path
                    }
                    if mount.src_path:
                        mount_config["src_path"] = mount.src_path
                    if mount.name:
                        mount_config["name"] = mount.name
                    stage2_mount_dict[name] = mount_config
                stage2_dict["mount"] = stage2_mount_dict
            
            if self.stage_2.custom_entry:
                stage2_dict["custom"] = {"on_entry": self.stage_2.custom_entry}
            
            if self.stage_2.custom_scripts:
                if "custom" not in stage2_dict:
                    stage2_dict["custom"] = {}
                stage2_dict["custom"].update(self.stage_2.custom_scripts)
            
            config["stage_2"] = stage2_dict
        
        return config