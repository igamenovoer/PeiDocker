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
    
    # GPU Configuration
    gpu_enabled: bool = False
    gpu_count: str = "all"  # "all" or specific number
    cuda_version: str = "12.4"
    
    # Environment Variables  
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    # Device Configuration
    device_type: str = "cpu"  # "cpu", "gpu", "custom"
    
    # GPU specific settings
    gpu_memory_limit: str = ""  # e.g., "4GB"

@binding.bindable_dataclass  
class NetworkUI:
    """UI state for network configuration"""
    
    # Proxy Settings
    proxy_enabled: bool = False
    http_proxy: str = ""
    https_proxy: str = ""
    no_proxy: str = ""
    
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
    """UI state for scripts configuration"""
    
    # Entry point configuration
    stage1_entry_mode: str = "none"  # "none", "file", "inline"
    stage1_entry_file_path: str = ""
    stage1_entry_inline_name: str = ""
    stage1_entry_inline_content: str = ""
    
    stage2_entry_mode: str = "none"  # "none", "file", "inline"
    stage2_entry_file_path: str = ""
    stage2_entry_inline_name: str = ""
    stage2_entry_inline_content: str = ""
    
    # Lifecycle scripts - storing as JSON for complex structure
    stage1_lifecycle_scripts: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    stage2_lifecycle_scripts: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    
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
    active_stage: int = 1
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
    
    def get_active_stage(self) -> StageUI:
        """Get the currently active stage configuration."""
        return self.stage_1 if self.active_stage == 1 else self.stage_2
    
    def merge_stages(self) -> Dict[str, Any]:
        """Merge stage-1 and stage-2 configurations.
        
        Stage-2 values override stage-1 values for shared settings.
        """
        # This is a placeholder - will be implemented in the bridge layer
        return {}