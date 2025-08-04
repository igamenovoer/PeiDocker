"""
Pydantic validation models for PeiDocker Web GUI configuration.

This module defines Pydantic models for validation and persistence of
configuration data, ensuring data integrity and providing automatic
type coercion and validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, List, Optional, Any, Union
import re

class EnvironmentConfig(BaseModel):
    """Pydantic model for environment validation"""
    
    model_config = ConfigDict(extra="forbid")
    
    gpu_enabled: bool = False
    gpu_count: str = Field(default="all", pattern=r"^(all|\d+)$")
    cuda_version: str = Field(default="12.4", pattern=r"^\d+\.\d+$")
    env_vars: Dict[str, str] = Field(default_factory=dict)
    device_type: str = Field(default="cpu", pattern=r"^(cpu|gpu|custom)$")
    gpu_memory_limit: str = ""
    
    @field_validator('env_vars')
    @classmethod
    def validate_env_vars(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Ensure environment variable names are valid"""
        for key in v.keys():
            if not key.replace('_', '').replace('-', '').isalnum():
                raise ValueError(f"Invalid environment variable name: {key}")
            if key.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                raise ValueError(f"Environment variable name cannot start with a number: {key}")
        return v
    
    @field_validator('gpu_memory_limit')
    @classmethod
    def validate_gpu_memory(cls, v: str) -> str:
        """Validate GPU memory limit format"""
        if not v:
            return v
        # Check if it ends with valid units
        if not re.match(r'^\d+(\.\d+)?\s*[KMGT]?B?$', v.upper()):
            raise ValueError("GPU memory limit must be in format like '4GB', '512MB', '1.5G'")
        return v

class NetworkConfig(BaseModel):
    """Pydantic model for network validation"""
    
    model_config = ConfigDict(extra="forbid")
    
    proxy_enabled: bool = False
    http_proxy: str = ""
    https_proxy: str = ""
    no_proxy: str = ""
    apt_mirror: str = ""
    port_mappings: List[Dict[str, str]] = Field(default_factory=list)
    
    @field_validator('http_proxy', 'https_proxy')
    @classmethod
    def validate_proxy_url(cls, v: str) -> str:
        """Validate proxy URL format"""
        if v and not v.startswith(('http://', 'https://', 'socks5://')):
            raise ValueError("Proxy URL must start with http://, https://, or socks5://")
        return v
    
    @field_validator('port_mappings')
    @classmethod
    def validate_port_mappings(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate port mapping entries"""
        for mapping in v:
            if 'host' not in mapping or 'container' not in mapping:
                raise ValueError("Port mapping must have 'host' and 'container' fields")
            
            # Validate port numbers
            try:
                host_port = int(mapping['host'])
                container_port = int(mapping['container'])
                if not (1 <= host_port <= 65535) or not (1 <= container_port <= 65535):
                    raise ValueError("Port numbers must be between 1 and 65535")
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError("Port numbers must be integers")
                raise
        return v

class SSHConfig(BaseModel):
    """Pydantic model for SSH validation"""
    
    model_config = ConfigDict(extra="forbid")
    
    enabled: bool = False
    port: int = Field(default=22, ge=1, le=65535)
    host_port: int = Field(default=2222, ge=1, le=65535)
    users: List[Dict[str, Any]] = Field(default_factory=list)
    
    @field_validator('users')
    @classmethod
    def validate_users(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate SSH users configuration"""
        usernames = set()
        
        for user in v:
            if 'name' not in user:
                raise ValueError("SSH user must have a 'name' field")
            
            username = user['name']
            if not re.match(r'^[a-z_][a-z0-9_-]{0,31}$', username):
                raise ValueError(f"Invalid username format: {username}")
            
            if username in usernames:
                raise ValueError(f"Duplicate username: {username}")
            usernames.add(username)
            
            # Validate authentication method
            if 'password' not in user and 'ssh_keys' not in user:
                raise ValueError(f"User {username} must have either password or SSH keys")
                
        return v

class StorageConfig(BaseModel):
    """Pydantic model for storage validation"""
    
    model_config = ConfigDict(extra="forbid")
    
    # Stage-2 fixed storage entries
    app_storage_type: str = Field(default="auto-volume", pattern=r"^(auto-volume|manual-volume|host|image)$")
    app_volume_name: str = ""
    app_host_path: str = ""
    
    data_storage_type: str = Field(default="auto-volume", pattern=r"^(auto-volume|manual-volume|host|image)$")
    data_volume_name: str = ""
    data_host_path: str = ""
    
    workspace_storage_type: str = Field(default="auto-volume", pattern=r"^(auto-volume|manual-volume|host|image)$")
    workspace_volume_name: str = ""
    workspace_host_path: str = ""
    
    volumes: List[Dict[str, str]] = Field(default_factory=list)
    mounts: List[Dict[str, str]] = Field(default_factory=list)
    
    @field_validator('volumes', 'mounts')
    @classmethod
    def validate_mount_entries(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Validate volume and mount entries"""
        for entry in v:
            if 'source' not in entry or 'target' not in entry:
                raise ValueError("Mount entry must have 'source' and 'target' fields")
            
            # Target must be absolute path
            if not entry['target'].startswith('/'):
                raise ValueError(f"Target path must be absolute: {entry['target']}")
                
        return v

class ScriptsConfig(BaseModel):
    """Pydantic model for scripts validation"""
    
    model_config = ConfigDict(extra="forbid")
    
    # Entry point configuration
    stage1_entry_mode: str = Field(default="default", pattern=r"^(default|custom|custom_param)$")
    stage1_entry_command: str = ""
    stage1_entry_params: str = ""
    
    stage2_entry_mode: str = Field(default="default", pattern=r"^(default|custom|custom_param)$")
    stage2_entry_command: str = ""
    stage2_entry_params: str = ""
    
    # Lifecycle scripts
    pre_build: List[str] = Field(default_factory=list)
    post_build: List[str] = Field(default_factory=list)
    first_run: List[str] = Field(default_factory=list)
    every_run: List[str] = Field(default_factory=list)
    user_login: List[str] = Field(default_factory=list)
    
    @field_validator('stage1_entry_command', 'stage2_entry_command')
    @classmethod
    def validate_entry_command(cls, v: str) -> str:
        """Validate entry command format"""
        if v and ' ' in v:
            raise ValueError("Entry command should not contain spaces. Use parameters field for arguments.")
        return v

class ProjectConfig(BaseModel):
    """Pydantic model for project validation"""
    
    model_config = ConfigDict(extra="forbid")
    
    project_name: str = Field(..., min_length=1, max_length=100)
    project_directory: str = Field(..., min_length=1)
    description: str = ""
    base_image: str = Field(default="ubuntu:22.04", min_length=1)
    image_output_name: str = ""
    template: str = Field(default="basic")
    
    @field_validator('project_name')
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Validate project name format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Project name can only contain letters, numbers, hyphens, and underscores")
        return v
    
    @field_validator('base_image')
    @classmethod
    def validate_base_image(cls, v: str) -> str:
        """Validate Docker image format"""
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*(/[a-zA-Z0-9._-]+)*(:[a-zA-Z0-9._-]+)?$', v):
            raise ValueError("Invalid Docker image format")
        return v

class StageConfig(BaseModel):
    """Complete validated configuration for one stage"""
    
    model_config = ConfigDict(extra="forbid")
    
    environment: EnvironmentConfig = Field(default_factory=EnvironmentConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    ssh: SSHConfig = Field(default_factory=SSHConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    scripts: ScriptsConfig = Field(default_factory=ScriptsConfig)

class AppConfig(BaseModel):
    """Complete validated application configuration"""
    
    model_config = ConfigDict(extra="forbid")
    
    project: ProjectConfig
    stage_1: StageConfig = Field(default_factory=StageConfig)
    stage_2: StageConfig = Field(default_factory=StageConfig)
    
    def to_user_config_yaml(self) -> Dict[str, Any]:
        """Convert to user_config.yml format"""
        # This method will be implemented in the bridge layer
        # It needs to transform the validated data into the expected YAML structure
        return {}