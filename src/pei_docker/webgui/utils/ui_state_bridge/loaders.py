"""
Loaders for loading configuration data into UI state.
"""

from typing import Dict, List, Any, Optional, Tuple
import uuid

from pei_docker.webgui.constants import (
    CustomScriptLifecycleTypes,
    ScriptTypes,
    DeviceTypes,
    EntryModes
)
from pei_docker.user_config import (
    UserConfig as AttrsUserConfig,
    StageConfig as AttrsStageConfig,
    CustomScriptConfig as AttrsCustomScriptConfig,
    StorageOption as AttrsStorageOption,
    StorageTypes
)
from pei_docker.webgui.models.ui_state import (
    AppUIState, StageUI, ProjectUI, StorageUI, ScriptsUI
)
from pei_docker.webgui.utils.ui_state_bridge.stage_processor import StageProcessor
from pei_docker.webgui.utils.ui_state_bridge.utils import build_proxy_url


class ConfigLoader:
    """Loads configuration data into UI state."""
    
    def load_user_config_into_ui(
        self,
        user_config: AttrsUserConfig,
        ui_state: AppUIState
    ) -> None:
        """Convert UserConfig (peidocker data model) to UI state.
        
        Args:
            user_config: AttrsUserConfig object
            ui_state: AppUIState object to populate
        """
        # Reset UI state
        ui_state.reset()
        
        # Load stage-1 configuration
        if user_config.stage_1:
            self._load_stage_config_into_ui(
                user_config.stage_1,
                ui_state.stage_1,
                ui_state.project,
                1
            )
        
        # Load stage-2 configuration  
        if user_config.stage_2:
            self._load_stage_config_into_ui(
                user_config.stage_2,
                ui_state.stage_2,
                ui_state.project,
                2
            )
        
        # Mark as not modified after loading
        ui_state.modified = False
    
    def _load_stage_config_into_ui(
        self,
        stage_config: AttrsStageConfig,
        ui_stage: StageUI,
        ui_project: ProjectUI,
        stage_num: int
    ) -> None:
        """Load a stage configuration from the data model into UI state.
        
        Args:
            stage_config: AttrsStageConfig object
            ui_stage: StageUI object to populate
            ui_project: ProjectUI object for project settings
            stage_num: Stage number (1 or 2)
        """
        # Load image configuration (stage 1 only loads base image to project)
        if stage_config.image and stage_num == 1:
            if stage_config.image.base:
                ui_project.base_image = stage_config.image.base
            if stage_config.image.output:
                ui_project.image_output_name = stage_config.image.output
        
        # Load SSH configuration (stage 1 only)
        if stage_config.ssh and stage_num == 1:
            self._load_ssh_config(stage_config.ssh, ui_stage.ssh)
        
        # Load proxy configuration
        if stage_config.proxy and stage_config.proxy.address and stage_config.proxy.port:
            ui_stage.network.proxy_enabled = True
            ui_stage.network.http_proxy = build_proxy_url(
                stage_config.proxy.address,
                stage_config.proxy.port,
                stage_config.proxy.use_https
            )
        else:
            ui_stage.network.proxy_enabled = False
            ui_stage.network.http_proxy = ""
        
        # Load APT configuration (stage 1 only)
        if stage_config.apt and stage_num == 1:
            ui_stage.network.apt_mirror = stage_config.apt.repo_source or ""
        
        # Load device configuration
        if stage_config.device:
            ui_stage.environment.device_type = stage_config.device.type
        else:
            ui_stage.environment.device_type = DeviceTypes.CPU
        
        # Load environment variables
        if stage_config.environment:
            ui_stage.environment.env_vars = dict(stage_config.environment)
        
        # Load port mappings
        if stage_config.ports:
            ui_stage.network.port_mappings = []
            for port_str in stage_config.ports:
                if ':' in port_str:
                    host_port, container_port = port_str.split(':', 1)
                    ui_stage.network.port_mappings.append({
                        'host': host_port,
                        'container': container_port
                    })
        
        # Load custom scripts
        if stage_config.custom:
            self._load_custom_scripts_into_ui(stage_config.custom, ui_stage.scripts)
        
        # Load storage configuration (stage 2 only)
        if stage_config.storage and stage_num == 2:
            self._load_storage_into_ui(stage_config.storage, ui_stage.storage)
        
        # Load mount configuration
        if stage_config.mount:
            self._load_mount_into_ui(stage_config.mount, ui_stage.storage)
    
    def _load_ssh_config(self, ssh_config: Any, ui_ssh: Any) -> None:
        """Load SSH configuration into UI state.
        
        Args:
            ssh_config: AttrsSSHConfig object
            ui_ssh: SSHTabUI object
        """
        ui_ssh.enabled = ssh_config.enable
        ui_ssh.port = str(ssh_config.port)
        ui_ssh.host_port = str(ssh_config.host_port)
        
        # Load SSH users
        ui_ssh.users = []
        for username, user_config in ssh_config.users.items():
            user_data = {
                'name': username,
                'password': user_config.password or '',
                'uid': str(user_config.uid) if user_config.uid is not None else '',
                'ssh_keys': [user_config.pubkey_text] if user_config.pubkey_text else []
            }
            ui_ssh.users.append(user_data)
    
    def _load_custom_scripts_into_ui(
        self,
        custom: AttrsCustomScriptConfig,
        ui_scripts: ScriptsUI
    ) -> None:
        """Load custom scripts from data model into UI state.
        
        Args:
            custom: AttrsCustomScriptConfig object
            ui_scripts: ScriptsUI object
        """
        # Clear existing scripts
        ui_scripts.lifecycle_scripts = {
            CustomScriptLifecycleTypes.ON_BUILD: [],
            CustomScriptLifecycleTypes.ON_FIRST_RUN: [],
            CustomScriptLifecycleTypes.ON_EVERY_RUN: [],
            CustomScriptLifecycleTypes.ON_USER_LOGIN: []
        }
        
        # Load entry point (for file-based scripts only, inline handled separately)
        if custom.on_entry:
            if len(custom.on_entry) > 0:
                entry_script = custom.on_entry[0]
                # Only set as file if not already set as inline by metadata loader
                if ui_scripts.entry_mode != EntryModes.INLINE:
                    ui_scripts.entry_mode = EntryModes.FILE
                    ui_scripts.entry_file_path = entry_script
        
        # Helper function to create script entry
        def create_script_entry(script_path: str) -> Dict[str, Any]:
            return {
                'id': str(uuid.uuid4()),
                'type': ScriptTypes.FILE,
                'path': script_path
            }
        
        # Load lifecycle scripts
        if custom.on_build:
            for script in custom.on_build:
                ui_scripts.lifecycle_scripts[CustomScriptLifecycleTypes.ON_BUILD].append(
                    create_script_entry(script)
                )
        
        if custom.on_first_run:
            for script in custom.on_first_run:
                ui_scripts.lifecycle_scripts[CustomScriptLifecycleTypes.ON_FIRST_RUN].append(
                    create_script_entry(script)
                )
        
        if custom.on_every_run:
            for script in custom.on_every_run:
                ui_scripts.lifecycle_scripts[CustomScriptLifecycleTypes.ON_EVERY_RUN].append(
                    create_script_entry(script)
                )
        
        if custom.on_user_login:
            for script in custom.on_user_login:
                ui_scripts.lifecycle_scripts[CustomScriptLifecycleTypes.ON_USER_LOGIN].append(
                    create_script_entry(script)
                )
    
    def _load_storage_into_ui(
        self,
        storage_dict: Dict[str, AttrsStorageOption],
        ui_storage: StorageUI
    ) -> None:
        """Load storage configuration from data model into UI state.
        
        Args:
            storage_dict: Dictionary of storage options
            ui_storage: StorageUI object
        """
        for name, storage_option in storage_dict.items():
            if name == 'app':
                ui_storage.app_storage_type = storage_option.type
                if storage_option.type == StorageTypes.Host and storage_option.host_path:
                    ui_storage.app_host_path = storage_option.host_path
                elif storage_option.type == StorageTypes.ManualVolume and storage_option.volume_name:
                    ui_storage.app_volume_name = storage_option.volume_name
            elif name == 'data':
                ui_storage.data_storage_type = storage_option.type
                if storage_option.type == StorageTypes.Host and storage_option.host_path:
                    ui_storage.data_host_path = storage_option.host_path
                elif storage_option.type == StorageTypes.ManualVolume and storage_option.volume_name:
                    ui_storage.data_volume_name = storage_option.volume_name
            elif name == 'workspace':
                ui_storage.workspace_storage_type = storage_option.type
                if storage_option.type == StorageTypes.Host and storage_option.host_path:
                    ui_storage.workspace_host_path = storage_option.host_path
                elif storage_option.type == StorageTypes.ManualVolume and storage_option.volume_name:
                    ui_storage.workspace_volume_name = storage_option.volume_name
    
    def _load_mount_into_ui(
        self,
        mount_dict: Dict[str, AttrsStorageOption],
        ui_storage: StorageUI
    ) -> None:
        """Load mount configuration from data model into UI state.
        
        Args:
            mount_dict: Dictionary of mount options
            ui_storage: StorageUI object
        """
        ui_storage.mounts = []
        for name, mount_option in mount_dict.items():
            # Mount types should be preserved as-is
            mount_type = mount_option.type
            # For mounts, image type is not allowed, default to auto-volume
            if mount_type == StorageTypes.Image:
                mount_type = StorageTypes.AutoVolume
            
            # Determine source based on mount type
            if mount_type == StorageTypes.Host:
                source = mount_option.host_path or ''
            elif mount_type == StorageTypes.ManualVolume:
                source = mount_option.volume_name or ''
            else:  # auto-volume
                source = ''  # Auto-generated, no source needed
            
            mount_entry = {
                'name': name,
                'source': source,
                'target': mount_option.dst_path or f'/mnt/{name}',
                'type': mount_type
            }
            ui_storage.mounts.append(mount_entry)
    
    def load_inline_scripts_metadata(
        self,
        config: Any,
        ui_state: AppUIState
    ) -> None:
        """Load inline scripts metadata from OmegaConf config.
        
        Args:
            config: OmegaConf config object
            ui_state: AppUIState object
        """
        # Process stage-1 inline scripts
        StageProcessor.process_inline_scripts_metadata(
            config,
            'stage_1',
            ui_state.stage_1.scripts
        )
        
        # Process stage-2 inline scripts
        StageProcessor.process_inline_scripts_metadata(
            config,
            'stage_2',
            ui_state.stage_2.scripts
        )