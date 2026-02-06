"""
Bindable UI state models for PeiDocker Web GUI.

This module defines bindable dataclasses for UI state management using NiceGUI's
binding system. These models provide automatic two-way data binding between
UI elements and data models without manual event handling.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from nicegui import binding

@binding.bindable_dataclass
class EnvironmentUI:
    """UI state for environment configuration - automatically syncs with widgets"""
    
    # Device Configuration
    device_type: str = "cpu"  # "cpu" or "gpu"
    
    # GPU Configuration (derived from device_type)
    gpu_enabled: bool = False
    
    # Environment Variables  
    env_vars: Dict[str, str] = field(default_factory=dict)

@binding.bindable_dataclass  
class NetworkUI:
    """UI state for network configuration"""
    
    # Proxy Settings
    proxy_enabled: bool = False
    http_proxy: str = ""
    
    # APT Configuration
    apt_mirror: str = ""
    
    # Port Mappings (simplified for UI)
    port_mappings: List[Dict[str, str]] = field(default_factory=list)

@binding.bindable_dataclass
class SSHTabUI:
    """UI state for SSH configuration"""
    
    enabled: bool = False
    port: str = "22"
    host_port: str = "2222"
    users: List[Dict[str, Any]] = field(default_factory=list)

@binding.bindable_dataclass
class StorageUI:
    """UI state for storage configuration"""
    
    # Stage-2 fixed storage entries
    app_storage_type: str = "auto-volume"
    app_volume_name: str = ""
    app_host_path: str = ""
    
    data_storage_type: str = "auto-volume"
    data_volume_name: str = ""
    data_host_path: str = ""
    
    workspace_storage_type: str = "auto-volume"
    workspace_volume_name: str = ""
    workspace_host_path: str = ""
    
    # General mounts for both stages
    volumes: List[Dict[str, str]] = field(default_factory=list)
    mounts: List[Dict[str, str]] = field(default_factory=list)

@binding.bindable_dataclass
class ScriptsUI:
    """UI state for scripts configuration for a single stage"""
    
    # Entry point configuration
    entry_mode: str = "none"  # "none", "file", "inline"
    entry_file_path: str = ""
    entry_inline_name: str = ""
    entry_inline_content: str = ""
    
    # Lifecycle scripts - storing as JSON for complex structure
    lifecycle_scripts: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    
    # Temporary storage for inline scripts being edited
    _inline_scripts_metadata: Dict[str, Dict[str, str]] = field(default_factory=dict)

@binding.bindable_dataclass
class ProjectUI:
    """UI state for project configuration"""
    
    # Basic project info
    project_name: str = ""
    project_directory: str = ""
    
    # Docker image configuration
    base_image: str = "ubuntu:22.04"
    image_output_name: str = ""
    
    # Template selection
    template: str = "basic"

@binding.bindable_dataclass
class StageUI:
    """Complete configuration for one stage"""
    
    environment: EnvironmentUI = field(default_factory=EnvironmentUI)
    network: NetworkUI = field(default_factory=NetworkUI) 
    ssh: SSHTabUI = field(default_factory=SSHTabUI)
    storage: StorageUI = field(default_factory=StorageUI)
    scripts: ScriptsUI = field(default_factory=ScriptsUI)

@binding.bindable_dataclass
class AppUIState:
    """Complete application UI state - single source of truth"""
    
    # Project configuration
    project: ProjectUI = field(default_factory=ProjectUI)
    
    # Stage configurations
    stage_1: StageUI = field(default_factory=StageUI)
    stage_2: StageUI = field(default_factory=StageUI)
    
    # App-level state
    modified: bool = False
    last_saved: str = ""
    
    # Navigation state
    active_tab: str = "project"
    
    # Validation state
    has_errors: bool = False
    error_count: int = 0
    
    def mark_modified(self) -> None:
        """Mark the configuration as modified."""
        self.modified = True
    
    def mark_saved(self) -> None:
        """Mark the configuration as saved."""
        self.modified = False
        from datetime import datetime
        self.last_saved = datetime.now().strftime("%I:%M %p")
    
    def merge_stages(self) -> Dict[str, Any]:
        """Merge stage-1 and stage-2 configurations.
        
        Stage-2 values override stage-1 values for shared settings.
        """
        # This is a placeholder - will be implemented in the bridge layer
        return {}
    
    def reset(self) -> None:
        """Reset the UI state to default values.
        
        This clears all configuration while maintaining object references
        for NiceGUI bindings.
        """
        # Reset project configuration
        self.project.project_name = ""
        self.project.project_directory = ""
        self.project.base_image = "ubuntu:22.04"
        self.project.image_output_name = ""
        self.project.template = "basic"
        
        # Reset stage-1 configuration
        self.stage_1.environment.device_type = "cpu"
        self.stage_1.environment.gpu_enabled = False
        self.stage_1.environment.env_vars.clear()
        
        self.stage_1.network.proxy_enabled = False
        self.stage_1.network.http_proxy = ""
        self.stage_1.network.apt_mirror = ""
        self.stage_1.network.port_mappings.clear()
        
        self.stage_1.ssh.enabled = False
        self.stage_1.ssh.port = "22"
        self.stage_1.ssh.host_port = "2222"
        self.stage_1.ssh.users.clear()
        
        self.stage_1.storage.app_storage_type = "auto-volume"
        self.stage_1.storage.app_volume_name = ""
        self.stage_1.storage.app_host_path = ""
        self.stage_1.storage.data_storage_type = "auto-volume"
        self.stage_1.storage.data_volume_name = ""
        self.stage_1.storage.data_host_path = ""
        self.stage_1.storage.workspace_storage_type = "auto-volume"
        self.stage_1.storage.workspace_volume_name = ""
        self.stage_1.storage.workspace_host_path = ""
        self.stage_1.storage.volumes.clear()
        self.stage_1.storage.mounts.clear()
        
        self.stage_1.scripts.entry_mode = "none"
        self.stage_1.scripts.entry_file_path = ""
        self.stage_1.scripts.entry_inline_name = ""
        self.stage_1.scripts.entry_inline_content = ""
        self.stage_1.scripts.lifecycle_scripts.clear()
        self.stage_1.scripts._inline_scripts_metadata.clear()
        
        # Reset stage-2 configuration
        self.stage_2.environment.device_type = "cpu"
        self.stage_2.environment.gpu_enabled = False
        self.stage_2.environment.env_vars.clear()
        
        self.stage_2.network.proxy_enabled = False
        self.stage_2.network.http_proxy = ""
        self.stage_2.network.apt_mirror = ""
        self.stage_2.network.port_mappings.clear()
        
        self.stage_2.ssh.enabled = False
        self.stage_2.ssh.port = "22"
        self.stage_2.ssh.host_port = "2222"
        self.stage_2.ssh.users.clear()
        
        self.stage_2.storage.app_storage_type = "auto-volume"
        self.stage_2.storage.app_volume_name = ""
        self.stage_2.storage.app_host_path = ""
        self.stage_2.storage.data_storage_type = "auto-volume"
        self.stage_2.storage.data_volume_name = ""
        self.stage_2.storage.data_host_path = ""
        self.stage_2.storage.workspace_storage_type = "auto-volume"
        self.stage_2.storage.workspace_volume_name = ""
        self.stage_2.storage.workspace_host_path = ""
        self.stage_2.storage.volumes.clear()
        self.stage_2.storage.mounts.clear()
        
        self.stage_2.scripts.entry_mode = "none"
        self.stage_2.scripts.entry_file_path = ""
        self.stage_2.scripts.entry_inline_name = ""
        self.stage_2.scripts.entry_inline_content = ""
        self.stage_2.scripts.lifecycle_scripts.clear()
        self.stage_2.scripts._inline_scripts_metadata.clear()
        
        # Reset app-level state
        self.modified = False
        self.last_saved = ""
        self.active_tab = "project"
        self.has_errors = False
        self.error_count = 0