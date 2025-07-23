"""Configuration data models for the GUI."""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass 
class SSHUser:
    """SSH user configuration."""
    name: str
    password: str
    uid: int = 1100
    pubkey_text: Optional[str] = None
    privkey_file: Optional[str] = None


@dataclass
class SSHConfig:
    """SSH configuration."""
    enable: bool = True
    port: int = 22
    host_port: int = 2222
    users: List[SSHUser] = field(default_factory=list)
    root_enabled: bool = False
    root_password: str = "root"


@dataclass
class ProxyConfig:
    """Proxy configuration."""
    enable: bool = False
    port: int = 8080
    build_only: bool = True


@dataclass
class DeviceConfig:
    """Device configuration."""
    device_type: str = "cpu"  # "cpu" or "gpu"


@dataclass
class MountConfig:
    """Mount configuration."""
    mount_type: str  # "auto-volume", "manual-volume", "host", "image"
    dst_path: str
    src_path: Optional[str] = None
    name: Optional[str] = None


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


@dataclass
class Stage2Config:
    """Stage-2 configuration."""
    output_image: str = ""
    mounts: Dict[str, MountConfig] = field(default_factory=dict)
    custom_entry: Optional[str] = None
    custom_scripts: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ProjectConfig:
    """Complete project configuration."""
    project_name: str = ""
    project_dir: str = ""
    stage_1: Stage1Config = field(default_factory=Stage1Config)
    stage_2: Stage2Config = field(default_factory=Stage2Config)
    
    def to_user_config_dict(self) -> Dict[str, Any]:
        """Convert to user_config.yml compatible dictionary."""
        config = {}
        
        # Stage 1
        stage1_dict = {
            "image": {
                "base": self.stage_1.base_image,
                "output": self.stage_1.output_image
            }
        }
        
        if self.stage_1.ssh.enable:
            users_dict = {}
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
            mount_dict = {}
            for name, mount in self.stage_1.mounts.items():
                mount_config = {
                    "type": mount.mount_type,
                    "dst_path": mount.dst_path
                }
                if mount.src_path:
                    mount_config["src_path"] = mount.src_path
                if mount.name:
                    mount_config["name"] = mount.name
                mount_dict[name] = mount_config
            stage1_dict["mount"] = mount_dict
        
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
            stage2_dict = {}
            
            if self.stage_2.output_image:
                stage2_dict["image"] = {"output": self.stage_2.output_image}
            
            if self.stage_2.mounts:
                mount_dict = {}
                for name, mount in self.stage_2.mounts.items():
                    mount_config = {
                        "type": mount.mount_type,
                        "dst_path": mount.dst_path
                    }
                    if mount.src_path:
                        mount_config["src_path"] = mount.src_path
                    if mount.name:
                        mount_config["name"] = mount.name
                    mount_dict[name] = mount_config
                stage2_dict["mount"] = mount_dict
            
            if self.stage_2.custom_entry:
                stage2_dict["custom"] = {"on_entry": self.stage_2.custom_entry}
            
            if self.stage_2.custom_scripts:
                if "custom" not in stage2_dict:
                    stage2_dict["custom"] = {}
                stage2_dict["custom"].update(self.stage_2.custom_scripts)
            
            config["stage_2"] = stage2_dict
        
        return config