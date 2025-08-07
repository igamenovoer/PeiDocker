"""
Bridge layer for converting between UI state and configuration models.

This module provides the UIStateBridge class that handles conversions between
NiceGUI bindable dataclasses (UI state) and attrs-based configuration models
through the adapter layer, as well as YAML serialization/deserialization.
"""

from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import attrs
import cattrs
from omegaconf import OmegaConf

from pei_docker.webgui.constants import (
    CustomScriptLifecycleTypes,
    DeviceTypes,
    ScriptTypes,
    EntryModes
)
from pei_docker.webgui.models.ui_state import (
    AppUIState, StageUI, NetworkUI, SSHTabUI,
    StorageUI, ScriptsUI, ProjectUI
)
from pei_docker.webgui.models.config_adapter import (
    create_app_config_adapter,
    AppConfigAdapter
)
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
    env_str_to_dict
)


class UIStateBridge:
    """Converts between UI state models and attrs configuration models."""
    
    def validate_ui_state(self, ui_state: AppUIState) -> Tuple[bool, List[str]]:
        """Validate current UI state without modifying it."""
        errors = []
        
        try:
            # Convert UI state to attrs config for validation
            _ = self._ui_to_attrs_config(ui_state)
            
            # attrs validation happens during object construction
            # If we get here, validation passed
            return True, []
            
        except (TypeError, ValueError, attrs.exceptions.NotAnAttrsClassError) as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
            return False, errors
    
    def save_to_yaml(self, ui_state: AppUIState, file_path: str) -> Tuple[bool, List[str]]:
        """Save UI state to YAML file with validation.
        
        Data flow: GUI state -> ui-data-model -> peidocker-data-model -> OmegaConf -> YAML file
        """
        errors = []
        
        # First validate
        is_valid, validation_errors = self.validate_ui_state(ui_state)
        if not is_valid:
            return False, validation_errors
        
        try:
            # Step 1: Convert UI state to attrs UserConfig (peidocker-data-model)
            attrs_config = self._ui_to_attrs_config(ui_state)
            
            # Step 2: Convert attrs config to dict using cattrs
            config_dict = cattrs.unstructure(attrs_config)
            
            # Step 3: Process inline scripts and other metadata
            config_dict = self._add_inline_scripts_metadata(config_dict, ui_state)
            
            # Step 4: Clean up the config dict (remove None values, empty dicts, etc.)
            config_dict = self._clean_config_dict(config_dict)
            
            # Step 5: Create directory if needed
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Step 6: Save using OmegaConf for better structured data handling
            conf = OmegaConf.create(config_dict)
            OmegaConf.save(conf, file_path)
            
            return True, []
            
        except Exception as e:
            errors.append(f"Save failed: {str(e)}")
            return False, errors
    
    def load_from_yaml(self, file_path: str, ui_state: AppUIState) -> Tuple[bool, List[str]]:
        """Load YAML configuration into UI state using proper data flow.
        
        Flow: user_config.yml -> OmegaConf -> UserConfig (peidocker model) -> UI state
        """
        errors = []
        
        try:
            # Step 1: Load YAML file directly with OmegaConf (handles duplicates, takes last value)
            config = OmegaConf.load(file_path)
            
            if not config:
                errors.append("Empty configuration file")
                return False, errors
            
            # Step 2: Convert to Python dict and prepare for cattrs
            config_dict = OmegaConf.to_container(config, resolve=True)
            
            # Step 3: Apply pre-processing transformations (same as in config_processor.py)
            if isinstance(config_dict, dict):
                for stage in ['stage_1', 'stage_2']:
                    if stage not in config_dict:
                        continue
                    
                    # Handle environment conversion from list to dict
                    if 'environment' in config_dict[stage]:
                        env = config_dict[stage]['environment']
                        if env is not None and isinstance(env, list):
                            config_dict[stage]['environment'] = env_str_to_dict(env)
                    
                    # Handle on_entry conversion from string to list
                    if 'custom' in config_dict[stage] and config_dict[stage]['custom'] is not None:
                        custom = config_dict[stage]['custom']
                        if CustomScriptLifecycleTypes.ON_ENTRY in custom and custom[CustomScriptLifecycleTypes.ON_ENTRY] is not None:
                            on_entry = custom[CustomScriptLifecycleTypes.ON_ENTRY]
                            if isinstance(on_entry, str):
                                # Convert string to single-element list
                                config_dict[stage]['custom'][CustomScriptLifecycleTypes.ON_ENTRY] = [on_entry]
            
            # Step 4: Parse into UserConfig using cattrs (proper data model)
            user_config: AttrsUserConfig = cattrs.structure(config_dict, AttrsUserConfig)
            
            # Step 5: Convert UserConfig to UI state
            self._load_user_config_into_ui(user_config, ui_state)
            
            # Step 6: Load inline scripts metadata (not part of UserConfig structure)
            self._load_inline_scripts_metadata(config, ui_state)
            
            return True, []
            
        except FileNotFoundError:
            errors.append(f"Configuration file not found: {file_path}")
            return False, errors
        except (TypeError, ValueError) as e:
            errors.append(f"Invalid configuration structure: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Load failed: {str(e)}")
            return False, errors
    
    def _load_user_config_into_ui(self, user_config: AttrsUserConfig, ui_state: AppUIState) -> None:
        """Convert UserConfig (peidocker data model) to UI state.
        
        This replaces the old _load_into_ui method with a proper data-model-driven approach.
        """
        # Reset UI state
        ui_state.reset()
        
        # Load stage-1 configuration
        if user_config.stage_1:
            self._load_stage_config_into_ui(user_config.stage_1, ui_state.stage_1, ui_state.project, 1)
        
        # Load stage-2 configuration  
        if user_config.stage_2:
            self._load_stage_config_into_ui(user_config.stage_2, ui_state.stage_2, ui_state.project, 2)
        
        # Mark as not modified after loading
        ui_state.modified = False
    
    def _load_stage_config_into_ui(self, stage_config: AttrsStageConfig, ui_stage: StageUI, ui_project: ProjectUI, stage_num: int) -> None:
        """Load a stage configuration from the data model into UI state."""
        # Load image configuration (stage 1 only loads base image to project)
        if stage_config.image and stage_num == 1:
            if stage_config.image.base:
                ui_project.base_image = stage_config.image.base
            if stage_config.image.output:
                ui_project.image_output_name = stage_config.image.output
        
        # Load SSH configuration (stage 1 only)
        if stage_config.ssh and stage_num == 1:
            ui_stage.ssh.enabled = stage_config.ssh.enable
            ui_stage.ssh.port = str(stage_config.ssh.port)
            ui_stage.ssh.host_port = str(stage_config.ssh.host_port)
            
            # Load SSH users
            ui_stage.ssh.users = []
            for username, user_config in stage_config.ssh.users.items():
                user_data = {
                    'name': username,
                    'password': user_config.password or '',
                    'uid': str(user_config.uid) if user_config.uid is not None else '',
                    'ssh_keys': [user_config.pubkey_text] if user_config.pubkey_text else []
                }
                ui_stage.ssh.users.append(user_data)
        
        # Load proxy configuration
        if stage_config.proxy and stage_config.proxy.address and stage_config.proxy.port:
            ui_stage.network.proxy_enabled = True
            # Reconstruct proxy URL
            scheme = 'https' if stage_config.proxy.use_https else 'http'
            ui_stage.network.http_proxy = f"{scheme}://{stage_config.proxy.address}:{stage_config.proxy.port}"
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
    
    def _load_inline_scripts_metadata(self, config: Any, ui_state: AppUIState) -> None:
        """Load inline scripts metadata from OmegaConf config."""
        # Process stage-1 inline scripts
        if 'stage_1' in config and '_inline_scripts' in config.stage_1:
            inline_scripts_1 = config.stage_1._inline_scripts
            ui_state.stage_1.scripts._inline_scripts_metadata.clear()
            ui_state.stage_1.scripts._inline_scripts_metadata.update(dict(inline_scripts_1))
            
            # Check if entry point is an inline script
            if 'custom' in config.stage_1 and CustomScriptLifecycleTypes.ON_ENTRY in config.stage_1.custom:
                entry_points = config.stage_1.custom[CustomScriptLifecycleTypes.ON_ENTRY]
                if entry_points and len(entry_points) > 0:
                    entry_point = entry_points[0]
                    if entry_point.startswith('/pei-docker/scripts/'):
                        script_name = entry_point.replace('/pei-docker/scripts/', '')
                        if script_name in inline_scripts_1:
                            ui_state.stage_1.scripts.entry_mode = EntryModes.INLINE
                            ui_state.stage_1.scripts.entry_inline_name = script_name
                            ui_state.stage_1.scripts.entry_inline_content = inline_scripts_1[script_name]
        
        # Process stage-2 inline scripts
        if 'stage_2' in config and '_inline_scripts' in config.stage_2:
            inline_scripts_2 = config.stage_2._inline_scripts
            ui_state.stage_2.scripts._inline_scripts_metadata.clear()
            ui_state.stage_2.scripts._inline_scripts_metadata.update(dict(inline_scripts_2))
            
            # Check if entry point is an inline script
            if 'custom' in config.stage_2 and CustomScriptLifecycleTypes.ON_ENTRY in config.stage_2.custom:
                entry_points = config.stage_2.custom[CustomScriptLifecycleTypes.ON_ENTRY]
                if entry_points and len(entry_points) > 0:
                    entry_point = entry_points[0]
                    if entry_point.startswith('/pei-docker/scripts/'):
                        script_name = entry_point.replace('/pei-docker/scripts/', '')
                        if script_name in inline_scripts_2:
                            ui_state.stage_2.scripts.entry_mode = EntryModes.INLINE
                            ui_state.stage_2.scripts.entry_inline_name = script_name
                            ui_state.stage_2.scripts.entry_inline_content = inline_scripts_2[script_name]
    
    def _load_custom_scripts_into_ui(self, custom: AttrsCustomScriptConfig, ui_scripts: ScriptsUI) -> None:
        """Load custom scripts from data model into UI state."""
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
                # Only set as file if not already set as inline by _load_inline_scripts_metadata
                if ui_scripts.entry_mode != EntryModes.INLINE:
                    ui_scripts.entry_mode = EntryModes.FILE
                    ui_scripts.entry_file_path = entry_script
        
        # Load lifecycle scripts with unique IDs
        import uuid
        
        # Helper function to create script entry
        def create_script_entry(script_path: str) -> Dict[str, Any]:
            return {
                'id': str(uuid.uuid4()),
                'type': ScriptTypes.FILE,
                'path': script_path
            }
        
        # Load on_build scripts
        if custom.on_build:
            for script in custom.on_build:
                ui_scripts.lifecycle_scripts[CustomScriptLifecycleTypes.ON_BUILD].append(create_script_entry(script))
        
        # Load on_first_run scripts
        if custom.on_first_run:
            for script in custom.on_first_run:
                ui_scripts.lifecycle_scripts[CustomScriptLifecycleTypes.ON_FIRST_RUN].append(create_script_entry(script))
        
        # Load on_every_run scripts
        if custom.on_every_run:
            for script in custom.on_every_run:
                ui_scripts.lifecycle_scripts[CustomScriptLifecycleTypes.ON_EVERY_RUN].append(create_script_entry(script))
        
        # Load on_user_login scripts
        if custom.on_user_login:
            for script in custom.on_user_login:
                ui_scripts.lifecycle_scripts[CustomScriptLifecycleTypes.ON_USER_LOGIN].append(create_script_entry(script))
    
    def _load_storage_into_ui(self, storage_dict: Dict[str, AttrsStorageOption], ui_storage: StorageUI) -> None:
        """Load storage configuration from data model into UI state."""
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
    
    def _load_mount_into_ui(self, mount_dict: Dict[str, AttrsStorageOption], ui_storage: StorageUI) -> None:
        """Load mount configuration from data model into UI state."""
        ui_storage.mounts = []
        for name, mount_option in mount_dict.items():
            # Mount types should be preserved as-is: auto-volume, manual-volume, host
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
    
    def ui_to_config(self, ui_state: AppUIState) -> AppConfigAdapter:
        """Convert UI state to attrs-based config through adapter."""
        attrs_config = self._ui_to_attrs_config(ui_state)
        project_info = self._extract_project_info(ui_state.project)
        return create_app_config_adapter(attrs_config, project_info)
    
    # Private conversion methods
    
    def _ui_to_attrs_config(self, ui_state: AppUIState) -> AttrsUserConfig:
        """Convert UI state to attrs UserConfig."""
        stage_1 = self._ui_stage_to_attrs(ui_state.stage_1, ui_state.project, 1)
        stage_2 = self._ui_stage_to_attrs(ui_state.stage_2, ui_state.project, 2)
        
        return AttrsUserConfig(
            stage_1=stage_1,
            stage_2=stage_2
        )
    
    def _ui_stage_to_attrs(self, ui_stage: StageUI, ui_project: ProjectUI, stage_num: int) -> Optional[AttrsStageConfig]:
        """Convert UI stage to attrs StageConfig."""
        # Build image config
        image = None
        if stage_num == 1:
            output_name = ui_project.image_output_name or ui_project.project_name or "pei-image"
            image = AttrsImageConfig(
                base=ui_project.base_image or "ubuntu:22.04",
                output=f"{output_name}:stage-1"
            )
        else:
            # Stage 2 only needs output name
            output_name = ui_project.image_output_name or ui_project.project_name or "pei-image"
            image = AttrsImageConfig(
                output=f"{output_name}:stage-2"
            )
        
        # Build SSH config (stage 1 only)
        ssh = None
        if stage_num == 1 and ui_stage.ssh.enabled:
            users = {}
            for user_data in ui_stage.ssh.users:
                username = user_data.get('name', '')
                if username:
                    # Convert uid string to int if present and valid
                    uid_str = user_data.get('uid', '')
                    uid = None
                    if uid_str and uid_str.strip():
                        try:
                            uid = int(uid_str)
                        except ValueError:
                            pass  # Keep uid as None if not a valid integer
                    
                    user_config = AttrsSSHUserConfig(
                        password=user_data.get('password'),
                        uid=uid,
                        pubkey_text=user_data.get('ssh_keys', [None])[0] if user_data.get('ssh_keys') else None
                    )
                    users[username] = user_config
            
            # Handle port values that might be int or str
            ssh_port_value: int = 22  # Default value
            if isinstance(ui_stage.ssh.port, str):
                ssh_port_value = int(ui_stage.ssh.port) if ui_stage.ssh.port.isdigit() else 22
            elif isinstance(ui_stage.ssh.port, int):
                ssh_port_value = ui_stage.ssh.port
                
            ssh_host_port_value: int = 2222  # Default value
            if isinstance(ui_stage.ssh.host_port, str):
                ssh_host_port_value = int(ui_stage.ssh.host_port) if ui_stage.ssh.host_port.isdigit() else 2222
            elif isinstance(ui_stage.ssh.host_port, int):
                ssh_host_port_value = ui_stage.ssh.host_port
            
            ssh = AttrsSSHConfig(
                enable=ui_stage.ssh.enabled,
                port=ssh_port_value,
                host_port=ssh_host_port_value,
                users=users
            )
        
        # Build proxy config
        proxy = None
        if ui_stage.network.proxy_enabled and ui_stage.network.http_proxy:
            # Extract address and port from proxy URL
            proxy_url = ui_stage.network.http_proxy
            if '://' in proxy_url:
                scheme, rest = proxy_url.split('://', 1)
                use_https = scheme == 'https'
            else:
                rest = proxy_url
                use_https = False
            
            if ':' in rest:
                address, port_str = rest.rsplit(':', 1)
                try:
                    port = int(port_str)
                except ValueError:
                    port = 8080
            else:
                address = rest
                port = 8080
            
            proxy = AttrsProxyConfig(
                address=address,
                port=port,
                enable_globally=True,
                remove_after_build=False,
                use_https=use_https
            )
        
        # Build APT config (stage 1 only)
        apt = None
        if stage_num == 1 and ui_stage.network.apt_mirror:
            apt = AttrsAptConfig(
                repo_source=ui_stage.network.apt_mirror,
                keep_repo_after_build=True,
                use_proxy=proxy is not None,
                keep_proxy_after_build=False
            )
        
        # Build device config
        device = None
        if ui_stage.environment.device_type != DeviceTypes.CPU:
            device = AttrsDeviceConfig(type=ui_stage.environment.device_type)
        
        # Convert environment variables
        environment = ui_stage.environment.env_vars if ui_stage.environment.env_vars else None
        
        # Convert port mappings
        ports = None
        if ui_stage.network.port_mappings:
            # Filter out empty port mappings
            valid_ports = [
                f"{m['host']}:{m['container']}" 
                for m in ui_stage.network.port_mappings
                if m.get('host', '').strip() and m.get('container', '').strip()
            ]
            if valid_ports:
                ports = valid_ports
        
        # Build custom scripts config
        custom = self._build_custom_scripts(ui_stage.scripts, stage_num)
        
        # Build storage config (stage 2 only)
        storage = None
        if stage_num == 2:
            storage = self._build_storage_config(ui_stage.storage)
        
        # Build mount config
        mount = self._build_mount_config(ui_stage.storage)
        
        return AttrsStageConfig(
            image=image,
            ssh=ssh,
            proxy=proxy,
            apt=apt,
            environment=environment,
            ports=ports,
            device=device,
            custom=custom,
            storage=storage,
            mount=mount
        )
    
    def _build_custom_scripts(self, ui_scripts: ScriptsUI, stage_num: int) -> Optional[AttrsCustomScriptConfig]:
        """Build custom scripts configuration from UI state."""
        on_entry = []
        
        # Handle entry point
        if ui_scripts.entry_mode == "file" and ui_scripts.entry_file_path:
            on_entry.append(ui_scripts.entry_file_path)
        elif ui_scripts.entry_mode == "inline" and ui_scripts.entry_inline_name:
            # For inline scripts, use the proper path that will be written to disk
            on_entry.append(f"/pei-docker/scripts/{ui_scripts.entry_inline_name}")
        
        # Extract lifecycle scripts
        lifecycle_scripts = ui_scripts.lifecycle_scripts
        
        on_build = []
        on_first_run = []
        on_every_run = []
        on_user_login = []
        
        # Use constants for lifecycle types to avoid typos
        if CustomScriptLifecycleTypes.ON_BUILD in lifecycle_scripts:
            for script_data in lifecycle_scripts[CustomScriptLifecycleTypes.ON_BUILD]:
                if isinstance(script_data, dict):
                    if script_data.get('type') == ScriptTypes.FILE and 'path' in script_data:
                        on_build.append(script_data['path'])
                    elif script_data.get('type') == ScriptTypes.INLINE and 'name' in script_data:
                        # For inline scripts, use the proper path
                        on_build.append(f"/pei-docker/scripts/{script_data['name']}")
                elif isinstance(script_data, str):
                    on_build.append(script_data)
        
        if CustomScriptLifecycleTypes.ON_FIRST_RUN in lifecycle_scripts:
            for script_data in lifecycle_scripts[CustomScriptLifecycleTypes.ON_FIRST_RUN]:
                if isinstance(script_data, dict):
                    if script_data.get('type') == ScriptTypes.FILE and 'path' in script_data:
                        on_first_run.append(script_data['path'])
                    elif script_data.get('type') == ScriptTypes.INLINE and 'name' in script_data:
                        on_first_run.append(f"/pei-docker/scripts/{script_data['name']}")
                elif isinstance(script_data, str):
                    on_first_run.append(script_data)
        
        if CustomScriptLifecycleTypes.ON_EVERY_RUN in lifecycle_scripts:
            for script_data in lifecycle_scripts[CustomScriptLifecycleTypes.ON_EVERY_RUN]:
                if isinstance(script_data, dict):
                    if script_data.get('type') == ScriptTypes.FILE and 'path' in script_data:
                        on_every_run.append(script_data['path'])
                    elif script_data.get('type') == ScriptTypes.INLINE and 'name' in script_data:
                        on_every_run.append(f"/pei-docker/scripts/{script_data['name']}")
                elif isinstance(script_data, str):
                    on_every_run.append(script_data)
        
        if CustomScriptLifecycleTypes.ON_USER_LOGIN in lifecycle_scripts:
            for script_data in lifecycle_scripts[CustomScriptLifecycleTypes.ON_USER_LOGIN]:
                if isinstance(script_data, dict):
                    if script_data.get('type') == ScriptTypes.FILE and 'path' in script_data:
                        on_user_login.append(script_data['path'])
                    elif script_data.get('type') == ScriptTypes.INLINE and 'name' in script_data:
                        on_user_login.append(f"/pei-docker/scripts/{script_data['name']}")
                elif isinstance(script_data, str):
                    on_user_login.append(script_data)
        
        # Only create CustomScriptConfig if we have any scripts
        if any([on_entry, on_build, on_first_run, on_every_run, on_user_login]):
            # AttrsCustomScriptConfig expects lists, not None for empty lists
            return AttrsCustomScriptConfig(
                on_build=on_build if on_build else [],
                on_first_run=on_first_run if on_first_run else [],
                on_every_run=on_every_run if on_every_run else [],
                on_user_login=on_user_login if on_user_login else [],
                on_entry=on_entry if on_entry else []
            )
        
        return None
    
    def _build_storage_config(self, ui_storage: StorageUI) -> Dict[str, AttrsStorageOption]:
        """Build storage configuration from UI state."""
        storage = {}
        
        # Fixed storage entries for stage-2
        for name, prefix in [('app', 'app'), ('data', 'data'), ('workspace', 'workspace')]:
            storage_type = getattr(ui_storage, f'{prefix}_storage_type')
            
            if storage_type == StorageTypes.AutoVolume:
                storage[name] = AttrsStorageOption(type=StorageTypes.AutoVolume)
            elif storage_type == StorageTypes.ManualVolume:
                volume_name = getattr(ui_storage, f'{prefix}_volume_name')
                if volume_name:
                    storage[name] = AttrsStorageOption(
                        type=StorageTypes.ManualVolume,
                        volume_name=volume_name
                    )
            elif storage_type == StorageTypes.Host:
                host_path = getattr(ui_storage, f'{prefix}_host_path')
                if host_path:
                    storage[name] = AttrsStorageOption(
                        type=StorageTypes.Host,
                        host_path=host_path
                    )
            elif storage_type == StorageTypes.Image:
                storage[name] = AttrsStorageOption(type=StorageTypes.Image)
        
        # Additional volumes
        for volume in ui_storage.volumes:
            name = volume.get('name', '')
            if name and name not in ['app', 'data', 'workspace']:
                storage_type = volume.get('type', StorageTypes.AutoVolume)
                source = volume.get('source', '')
                target = volume.get('target', '')
                
                if storage_type == StorageTypes.AutoVolume:
                    storage[name] = AttrsStorageOption(
                        type=StorageTypes.AutoVolume,
                        dst_path=target
                    )
                elif storage_type == StorageTypes.ManualVolume and source:
                    storage[name] = AttrsStorageOption(
                        type=StorageTypes.ManualVolume,
                        volume_name=source,
                        dst_path=target
                    )
                elif storage_type == StorageTypes.Host and source:
                    storage[name] = AttrsStorageOption(
                        type=StorageTypes.Host,
                        host_path=source,
                        dst_path=target
                    )
        
        return storage
    
    def _build_mount_config(self, ui_storage: StorageUI) -> Dict[str, AttrsStorageOption]:
        """Build mount configuration from UI state."""
        mounts = {}
        
        for mount in ui_storage.mounts:
            name = mount.get('name', '')
            source = mount.get('source', '')
            target = mount.get('target', '')
            mount_type = mount.get('type', StorageTypes.AutoVolume)
            
            if name and target:  # Source is optional for auto-volume
                if mount_type == StorageTypes.Host:
                    if source:  # Host type requires source
                        mounts[name] = AttrsStorageOption(
                            type=StorageTypes.Host,
                            host_path=source,
                            dst_path=target
                        )
                elif mount_type == StorageTypes.ManualVolume:
                    if source:  # Manual volume requires source (volume name)
                        mounts[name] = AttrsStorageOption(
                            type=StorageTypes.ManualVolume,
                            volume_name=source,
                            dst_path=target
                        )
                elif mount_type == StorageTypes.AutoVolume:
                    # Auto-volume doesn't require source
                    mounts[name] = AttrsStorageOption(
                        type=StorageTypes.AutoVolume,
                        dst_path=target
                    )
        
        return mounts
    
    def _extract_project_info(self, ui_project: ProjectUI) -> Dict[str, Any]:
        """Extract project information for adapter."""
        return {
            'project_name': ui_project.project_name or "untitled",
            'project_directory': ui_project.project_directory or "",
            'base_image': ui_project.base_image,
            'image_output_name': ui_project.image_output_name,
            'template': ui_project.template
        }
    
    def _ui_to_user_config_format(self, ui_state: AppUIState) -> Dict[str, Any]:
        """Convert UI state to user_config.yml format.
        
        Data flow: UI state -> peidocker-data-model (attrs) -> dict -> YAML format
        This ensures consistency with save_to_yaml and eliminates code duplication.
        """
        try:
            # Step 1: Convert UI state to attrs UserConfig (peidocker-data-model)
            # This reuses all the existing conversion logic and validation
            attrs_config = self._ui_to_attrs_config(ui_state)
            
            # Step 2: Convert attrs config to dict using cattrs
            # This gives us the proper YAML-ready structure
            config_dict = cattrs.unstructure(attrs_config)
            
            # Step 3: Add inline scripts metadata (not part of UserConfig structure)
            config_dict = self._add_inline_scripts_metadata(config_dict, ui_state)
            
            # Step 4: Clean up the config dict (remove None values, empty dicts, etc.)
            # This makes the YAML cleaner and more readable
            config_dict = self._clean_config_dict(config_dict)
            
            return config_dict
            
        except Exception as e:
            # If conversion fails, return a minimal config
            # This ensures the summary tab doesn't break
            return {
                'stage_1': {'image': {'base': 'ubuntu:latest', 'output': 'pei-image:stage-1'}},
                'stage_2': {'image': {'output': 'pei-image:stage-2'}}
            }
    
    def _build_yaml_storage_config(self, storage: StorageUI) -> Dict[str, Any]:
        """Build storage configuration for YAML format."""
        config: Dict[str, Any] = {}
        
        # Fixed storage entries for stage-2
        for name, prefix in [('app', 'app'), ('data', 'data'), ('workspace', 'workspace')]:
            storage_type = getattr(storage, f'{prefix}_storage_type')
            
            if storage_type == StorageTypes.AutoVolume:
                config[name] = {'type': StorageTypes.AutoVolume}
            elif storage_type == StorageTypes.ManualVolume:
                volume_name = getattr(storage, f'{prefix}_volume_name')
                if volume_name:
                    config[name] = {'type': StorageTypes.ManualVolume, 'volume_name': volume_name}
            elif storage_type == StorageTypes.Host:
                host_path = getattr(storage, f'{prefix}_host_path')
                if host_path:
                    config[name] = {'type': StorageTypes.Host, 'host_path': host_path}
            elif storage_type == StorageTypes.Image:
                config[name] = {'type': StorageTypes.Image}
        
        # Additional mounts
        if storage.mounts:
            mount_config = {}
            for mount in storage.mounts:
                name = mount.get('name', '')
                source = mount.get('source', '')
                target = mount.get('target', '')
                mount_type = mount.get('type', StorageTypes.Host)
                
                if name and source and target:
                    if mount_type == StorageTypes.Host:
                        mount_config[name] = {
                            'type': StorageTypes.Host,
                            'host_path': source,
                            'dst_path': target
                        }
                    elif mount_type == StorageTypes.ManualVolume:
                        mount_config[name] = {
                            'type': StorageTypes.ManualVolume,
                            'volume_name': source,
                            'dst_path': target
                        }
            
            if mount_config:
                config['mount'] = mount_config
        
        return config
    
    def _load_into_ui(self, config_data: Dict[str, Any], ui_state: AppUIState) -> None:
        """Load YAML configuration into UI state.
        
        Implements mapping rules from gui-to-core-data-mapping.md:
        - SSH: Load from stage-2 if exists in both, otherwise from whichever has it
        - Device: Load from stage-2 if exists in both, otherwise from whichever has it
        - Environment: Merge variables with stage-2 overriding stage-1
        - Network: Load from stage-2 if exists in both, otherwise from whichever has it
        """
        stage_1_data = config_data.get('stage_1', config_data.get('stage-1', {}))
        stage_2_data = config_data.get('stage_2', config_data.get('stage-2', {}))
        
        # Load project configuration
        self._load_project_config(stage_1_data, ui_state.project)
        
        # Load environment configuration (separate for each stage, no merging)
        self._load_environment_config_separate(stage_1_data, stage_2_data, ui_state)
        
        # Load network configuration following default behavior
        self._load_network_config_default(stage_1_data, stage_2_data, ui_state)
        
        # Load SSH configuration following default behavior
        self._load_ssh_config_default(stage_1_data, stage_2_data, ui_state)
        
        # Load device configuration following default behavior
        self._load_device_config_default(stage_1_data, stage_2_data, ui_state)
        
        # Load storage configuration (stage-2 only - has separate sections)
        self._load_storage_config(stage_2_data, ui_state.stage_2.storage)
        
        # Load scripts configuration (has separate sections)
        self._load_scripts_config(stage_1_data, stage_2_data, 
                                ui_state.stage_1.scripts, 
                                ui_state.stage_2.scripts)
        
        ui_state.modified = False
    
    def _load_project_config(self, stage_1_data: Dict[str, Any], project: ProjectUI) -> None:
        """Load project configuration from YAML data."""
        image_config = stage_1_data.get('image', {})
        project.base_image = image_config.get('base', 'ubuntu:22.04')
        project.image_output_name = image_config.get('output', '')
    
    def _load_environment_config_separate(self, stage_1_data: Dict[str, Any], stage_2_data: Dict[str, Any], ui_state: AppUIState) -> None:
        """Load environment configuration separately for each stage.
        
        Since the environment tab has separate sections for stage-1 and stage-2,
        no special mapping is needed - each stage keeps its own environment variables.
        """
        # Load stage-1 environment variables
        stage_1_env_vars: Dict[str, str] = {}
        stage_1_env_list = stage_1_data.get('environment', [])
        for env_str in stage_1_env_list:
            if '=' in env_str:
                key, value = env_str.split('=', 1)
                stage_1_env_vars[key.strip()] = value.strip()
        
        # Load stage-2 environment variables
        stage_2_env_vars: Dict[str, str] = {}
        stage_2_env_list = stage_2_data.get('environment', [])
        for env_str in stage_2_env_list:
            if '=' in env_str:
                key, value = env_str.split('=', 1)
                stage_2_env_vars[key.strip()] = value.strip()
        
        # Apply environment variables to their respective stages
        ui_state.stage_1.environment.env_vars = stage_1_env_vars
        ui_state.stage_2.environment.env_vars = stage_2_env_vars
    
    def _load_device_config_default(self, stage_1_data: Dict[str, Any], stage_2_data: Dict[str, Any], ui_state: AppUIState) -> None:
        """Load device configuration separately for each stage.
        
        Each stage now has its own independent device configuration.
        """
        # Load Stage-1 device configuration
        device_1 = stage_1_data.get('device', {})
        if device_1:
            device_type = device_1.get('type', DeviceTypes.CPU)
            ui_state.stage_1.environment.device_type = device_type
            ui_state.stage_1.environment.gpu_enabled = (device_type == DeviceTypes.GPU)
        else:
            ui_state.stage_1.environment.device_type = DeviceTypes.CPU
            ui_state.stage_1.environment.gpu_enabled = False
        
        # Load Stage-2 device configuration
        device_2 = stage_2_data.get('device', {})
        if device_2:
            device_type = device_2.get('type', DeviceTypes.CPU)
            ui_state.stage_2.environment.device_type = device_type
            ui_state.stage_2.environment.gpu_enabled = (device_type == DeviceTypes.GPU)
        else:
            ui_state.stage_2.environment.device_type = DeviceTypes.CPU
            ui_state.stage_2.environment.gpu_enabled = False
    
    def _load_network_config_default(self, stage_1_data: Dict[str, Any], stage_2_data: Dict[str, Any], ui_state: AppUIState) -> None:
        """Load network configuration following default behavior.
        
        Default behavior: if exists in both stages, load from stage-2;
        if exists in single stage, load from that stage.
        """
        # For each network setting, apply default behavior
        # Proxy configuration
        proxy_1 = stage_1_data.get('proxy', {})
        proxy_2 = stage_2_data.get('proxy', {})
        proxy_config = proxy_2 if proxy_2 else proxy_1
        
        if proxy_config:
            address = proxy_config.get('address', '')
            port = proxy_config.get('port', 8080)
            scheme = 'https' if proxy_config.get('use_https', False) else 'http'
            
            if address and port:
                proxy_url = f"{scheme}://{address}:{port}"
                # Apply to both stages
                ui_state.stage_1.network.proxy_enabled = True
                ui_state.stage_1.network.http_proxy = proxy_url
                ui_state.stage_2.network.proxy_enabled = True
                ui_state.stage_2.network.http_proxy = proxy_url
            else:
                # Clear proxy settings if invalid
                ui_state.stage_1.network.proxy_enabled = False
                ui_state.stage_1.network.http_proxy = ""
                ui_state.stage_2.network.proxy_enabled = False
                ui_state.stage_2.network.http_proxy = ""
        
        # APT configuration
        apt_1 = stage_1_data.get('apt', {})
        apt_2 = stage_2_data.get('apt', {})
        apt_config = apt_2 if apt_2 else apt_1
        
        if apt_config:
            apt_mirror = apt_config.get('repo_source', '')
            # Apply to both stages
            ui_state.stage_1.network.apt_mirror = apt_mirror
            ui_state.stage_2.network.apt_mirror = apt_mirror
        
        # Port mappings - load separately for each stage
        # Note: Only load port mappings, not the entire network config
        # to avoid overriding the default behavior we just applied
        ports_1 = stage_1_data.get('ports', [])
        ports_2 = stage_2_data.get('ports', [])
        
        # Load port mappings for stage-1
        ui_state.stage_1.network.port_mappings.clear()
        for port_str in ports_1:
            if ':' in port_str:
                host, container = port_str.split(':', 1)
                ui_state.stage_1.network.port_mappings.append({
                    'host': host.strip(),
                    'container': container.strip()
                })
        
        # Load port mappings for stage-2
        ui_state.stage_2.network.port_mappings.clear()
        for port_str in ports_2:
            if ':' in port_str:
                host, container = port_str.split(':', 1)
                ui_state.stage_2.network.port_mappings.append({
                    'host': host.strip(),
                    'container': container.strip()
                })
    
    def _load_ssh_config_default(self, stage_1_data: Dict[str, Any], stage_2_data: Dict[str, Any], ui_state: AppUIState) -> None:
        """Load SSH configuration following default behavior.
        
        Default behavior for reading: if exists in both stages, load from stage-2;
        if exists in single stage, load from that stage.
        Note: SSH is written to stage-1 ONLY, but we still follow default read behavior.
        """
        ssh_1 = stage_1_data.get('ssh', {})
        ssh_2 = stage_2_data.get('ssh', {})
        
        # Use stage-2 if exists, otherwise stage-1
        ssh_config = ssh_2 if ssh_2 else ssh_1
        
        if ssh_config:
            # Apply to stage-1 UI (SSH tab is in stage-1)
            # Create a temporary dict with the SSH config to load
            temp_data = {'ssh': ssh_config}
            self._load_ssh_config(temp_data, ui_state.stage_1.ssh)
    
    def _load_network_config(self, stage_data: Dict[str, Any], network: NetworkUI) -> None:
        """Load network configuration from YAML data."""
        # Load proxy configuration
        proxy_config = stage_data.get('proxy', {})
        if proxy_config:
            address = proxy_config.get('address', '')
            port = proxy_config.get('port', 8080)
            scheme = 'https' if proxy_config.get('use_https', False) else 'http'
            
            if address and port:
                network.proxy_enabled = True
                network.http_proxy = f"{scheme}://{address}:{port}"
            else:
                network.proxy_enabled = False
                network.http_proxy = ""
        
        # Load APT configuration
        apt_config = stage_data.get('apt', {})
        if apt_config:
            network.apt_mirror = apt_config.get('repo_source', '')
        
        # Load port mappings
        ports = stage_data.get('ports', [])
        network.port_mappings.clear()
        
        for port_str in ports:
            if ':' in port_str:
                host, container = port_str.split(':', 1)
                network.port_mappings.append({
                    'host': host.strip(),
                    'container': container.strip()
                })
    
    def _load_ssh_config(self, stage_data: Dict[str, Any], ssh: SSHTabUI) -> None:
        """Load SSH configuration from YAML data."""
        ssh_config = stage_data.get('ssh', {})
        if ssh_config:
            ssh.enabled = ssh_config.get('enable', False)
            ssh.port = str(ssh_config.get('port', 22))
            ssh.host_port = str(ssh_config.get('host_port', 2222))
            
            # Convert users dict to list format
            users_dict = ssh_config.get('users', {})
            ssh.users.clear()
            
            for username, user_config in users_dict.items():
                user_data = {
                    'name': username,
                    'password': user_config.get('password'),
                    'uid': user_config.get('uid')
                }
                
                # Extract SSH keys
                ssh_keys = []
                if user_config.get('pubkey_text'):
                    ssh_keys.append(user_config['pubkey_text'])
                elif user_config.get('pubkey_file'):
                    ssh_keys.append(f"file:{user_config['pubkey_file']}")
                
                if ssh_keys:
                    user_data['ssh_keys'] = ssh_keys
                
                ssh.users.append(user_data)
    
    def _load_storage_config(self, stage_data: Dict[str, Any], storage: StorageUI) -> None:
        """Load storage configuration from YAML data."""
        storage_config = stage_data.get('storage', {})
        
        # Load fixed storage entries
        for name, prefix in [('app', 'app'), ('data', 'data'), ('workspace', 'workspace')]:
            config = storage_config.get(name, {})
            
            if isinstance(config, dict):
                storage_type = config.get('type', StorageTypes.AutoVolume)
                setattr(storage, f'{prefix}_storage_type', storage_type)
                
                if storage_type == StorageTypes.ManualVolume:
                    setattr(storage, f'{prefix}_volume_name', config.get('volume_name', ''))
                elif storage_type == StorageTypes.Host:
                    setattr(storage, f'{prefix}_host_path', config.get('host_path', ''))
            elif isinstance(config, str):
                # Legacy format compatibility
                if config == StorageTypes.AutoVolume:
                    setattr(storage, f'{prefix}_storage_type', StorageTypes.AutoVolume)
                elif config == StorageTypes.Image:
                    setattr(storage, f'{prefix}_storage_type', StorageTypes.Image)
                elif config.startswith('volume:'):
                    setattr(storage, f'{prefix}_storage_type', StorageTypes.ManualVolume)
                    setattr(storage, f'{prefix}_volume_name', config[7:])
                elif config.startswith('host:'):
                    setattr(storage, f'{prefix}_storage_type', StorageTypes.Host)
                    setattr(storage, f'{prefix}_host_path', config[5:])
        
        # Load additional mounts
        mount_config = storage_config.get('mount', {})
        storage.mounts.clear()
        
        for name, config in mount_config.items():
            if isinstance(config, dict):
                mount_type = config.get('type', 'host')
                mount_data = {
                    'name': name,
                    'type': mount_type,
                    'target': config.get('dst_path', f'/mnt/{name}')
                }
                
                if mount_type == StorageTypes.Host:
                    mount_data['source'] = config.get('host_path', '')
                elif mount_type == StorageTypes.ManualVolume:
                    mount_data['source'] = config.get('volume_name', '')
                
                storage.mounts.append(mount_data)
    
    def _load_scripts_config(self, stage_1_data: Dict[str, Any], stage_2_data: Dict[str, Any],
                           scripts1: ScriptsUI, scripts2: ScriptsUI) -> None:
        """Load scripts configuration from YAML data."""
        import uuid
        
        # Helper function to generate script ID
        def generate_script_id(stage: str, lifecycle: str, script_type: str) -> str:
            return f'{stage}-{lifecycle}-{script_type}-{str(uuid.uuid4()).replace("-", "")[:8]}'
        
        # Helper function to parse script path with arguments
        def parse_script_with_args(script_str: str) -> Tuple[str, str]:
            """Parse script string to separate path and arguments.
            Returns (path, args) tuple."""
            # Handle quoted strings properly
            import shlex
            try:
                parts = shlex.split(script_str)
                if parts:
                    path = parts[0]
                    # Rejoin the remaining parts as arguments
                    args = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    return path, args
            except (ValueError, SyntaxError):
                # Fallback for simple parsing when shlex fails (e.g., unbalanced quotes)
                parts = script_str.split(None, 1)
                if len(parts) == 2:
                    return parts[0], parts[1]
            return script_str.strip(), ''
        
        # Load stage-1 inline scripts metadata
        inline_scripts_1 = stage_1_data.get('_inline_scripts', {})
        scripts1._inline_scripts_metadata.clear()
        scripts1._inline_scripts_metadata.update(inline_scripts_1)
        
        # Load stage-1 entry point
        custom_1 = stage_1_data.get('custom', {})
        entry_points_1 = custom_1.get(CustomScriptLifecycleTypes.ON_ENTRY, [])
        if entry_points_1:
            entry_point_1 = entry_points_1[0]
            if entry_point_1.startswith('/pei-docker/scripts/'):
                # This is an inline script
                script_name = entry_point_1.replace('/pei-docker/scripts/', '')
                if script_name in inline_scripts_1:
                    scripts1.entry_mode = "inline"
                    scripts1.entry_inline_name = script_name
                    scripts1.entry_inline_content = inline_scripts_1[script_name]
            else:
                # This is a file path (might have arguments)
                path, args = parse_script_with_args(entry_point_1)
                scripts1.entry_mode = "file"
                scripts1.entry_file_path = entry_point_1  # Keep full path with args for now
        
        # Load stage-2 inline scripts metadata
        inline_scripts_2 = stage_2_data.get('_inline_scripts', {})
        scripts2._inline_scripts_metadata.clear()
        scripts2._inline_scripts_metadata.update(inline_scripts_2)
        
        # Load stage-2 entry point
        custom_2 = stage_2_data.get('custom', {})
        entry_points_2 = custom_2.get(CustomScriptLifecycleTypes.ON_ENTRY, [])
        if entry_points_2:
            entry_point_2 = entry_points_2[0]
            if entry_point_2.startswith('/pei-docker/scripts/'):
                script_name = entry_point_2.replace('/pei-docker/scripts/', '')
                if script_name in inline_scripts_2:
                    scripts2.entry_mode = "inline"
                    scripts2.entry_inline_name = script_name
                    scripts2.entry_inline_content = inline_scripts_2[script_name]
            else:
                # This is a file path (might have arguments)
                path, args = parse_script_with_args(entry_point_2)
                scripts2.entry_mode = "file"
                scripts2.entry_file_path = entry_point_2  # Keep full path with args for now
        
        # Load lifecycle scripts
        scripts1.lifecycle_scripts.clear()
        scripts2.lifecycle_scripts.clear()
        
        # Use the correct UI keys that match what the scripts tab expects
        lifecycle_keys = CustomScriptLifecycleTypes.get_all_types()
        
        # Load stage-1 lifecycle scripts
        for lifecycle_key in lifecycle_keys:
            if lifecycle_key in custom_1:
                scripts_list = []
                for script_str in custom_1[lifecycle_key]:
                    if script_str.startswith('/pei-docker/scripts/'):
                        # This is an inline script
                        script_name = script_str.replace('/pei-docker/scripts/', '')
                        if script_name in inline_scripts_1:
                            scripts_list.append({
                                'id': generate_script_id('stage1', lifecycle_key, 'inline'),
                                'type': 'inline',
                                'name': script_name,
                                'content': inline_scripts_1[script_name],
                                'path': script_str
                            })
                    else:
                        # This is a file path with possible arguments
                        path, args = parse_script_with_args(script_str)
                        script_data = {
                            'id': generate_script_id('stage1', lifecycle_key, 'file'),
                            'type': ScriptTypes.FILE,
                            'path': script_str,  # Store full path with args for compatibility
                            'content': ''  # File scripts don't have content
                        }
                        # Store parsed path and args separately if needed
                        if args:
                            script_data['script_path'] = path
                            script_data['args'] = args
                        scripts_list.append(script_data)
                scripts1.lifecycle_scripts[lifecycle_key] = scripts_list
        
        # Load stage-2 lifecycle scripts
        for lifecycle_key in lifecycle_keys:
            if lifecycle_key in custom_2:
                scripts_list = []
                for script_str in custom_2[lifecycle_key]:
                    if script_str.startswith('/pei-docker/scripts/'):
                        script_name = script_str.replace('/pei-docker/scripts/', '')
                        if script_name in inline_scripts_2:
                            scripts_list.append({
                                'id': generate_script_id('stage2', lifecycle_key, 'inline'),
                                'type': 'inline',
                                'name': script_name,
                                'content': inline_scripts_2[script_name],
                                'path': script_str
                            })
                    else:
                        # This is a file path with possible arguments
                        path, args = parse_script_with_args(script_str)
                        script_data = {
                            'id': generate_script_id('stage2', lifecycle_key, 'file'),
                            'type': ScriptTypes.FILE,
                            'path': script_str,  # Store full path with args for compatibility
                            'content': ''  # File scripts don't have content
                        }
                        # Store parsed path and args separately if needed
                        if args:
                            script_data['script_path'] = path
                            script_data['args'] = args
                        scripts_list.append(script_data)
                scripts2.lifecycle_scripts[lifecycle_key] = scripts_list
    
    def _add_inline_scripts_metadata(self, config_dict: Dict[str, Any], ui_state: AppUIState) -> Dict[str, Any]:
        """Add inline scripts metadata to the configuration dictionary.
        
        This preserves inline script content as metadata in the YAML for reconstruction.
        """
        result = config_dict.copy()
        
        # Process stage-1 inline scripts
        if 'stage_1' in result:
            inline_scripts_1 = {}
            
            # Check entry point
            if ui_state.stage_1.scripts.entry_mode == "inline":
                script_name = ui_state.stage_1.scripts.entry_inline_name
                script_content = ui_state.stage_1.scripts.entry_inline_content
                if script_name and script_content:
                    inline_scripts_1[script_name] = script_content
            
            # Check lifecycle scripts
            for lifecycle_key, scripts in ui_state.stage_1.scripts.lifecycle_scripts.items():
                for script_data in scripts:
                    if isinstance(script_data, dict) and script_data.get('type') == 'inline':
                        name = script_data.get('name', '')
                        content = script_data.get('content', '')
                        if name and content:
                            inline_scripts_1[name] = content
            
            # Add metadata from _inline_scripts_metadata if present
            if ui_state.stage_1.scripts._inline_scripts_metadata:
                # _inline_scripts_metadata is Dict[str, Dict[str, str]]
                # We need to flatten it to Dict[str, str] for inline_scripts
                for name, metadata in ui_state.stage_1.scripts._inline_scripts_metadata.items():
                    if name not in inline_scripts_1 and 'content' in metadata:
                        inline_scripts_1[name] = metadata['content']
            
            if inline_scripts_1:
                result['stage_1']['_inline_scripts'] = inline_scripts_1
        
        # Process stage-2 inline scripts
        if 'stage_2' in result:
            inline_scripts_2 = {}
            
            # Check entry point
            if ui_state.stage_2.scripts.entry_mode == "inline":
                script_name = ui_state.stage_2.scripts.entry_inline_name
                script_content = ui_state.stage_2.scripts.entry_inline_content
                if script_name and script_content:
                    inline_scripts_2[script_name] = script_content
            
            # Check lifecycle scripts
            for lifecycle_key, scripts in ui_state.stage_2.scripts.lifecycle_scripts.items():
                for script_data in scripts:
                    if isinstance(script_data, dict) and script_data.get('type') == 'inline':
                        name = script_data.get('name', '')
                        content = script_data.get('content', '')
                        if name and content:
                            inline_scripts_2[name] = content
            
            # Add metadata from _inline_scripts_metadata if present
            if ui_state.stage_2.scripts._inline_scripts_metadata:
                # _inline_scripts_metadata is Dict[str, Dict[str, str]]
                # We need to flatten it to Dict[str, str] for inline_scripts
                for name, metadata in ui_state.stage_2.scripts._inline_scripts_metadata.items():
                    if name not in inline_scripts_2 and 'content' in metadata:
                        inline_scripts_2[name] = metadata['content']
            
            if inline_scripts_2:
                result['stage_2']['_inline_scripts'] = inline_scripts_2
        
        return result
    
    def _clean_config_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up the configuration dictionary by removing None values and empty structures.
        
        This ensures the YAML output is clean and doesn't contain empty structures like
        'proxy: {}' or port mappings like '- ':''.
        """
        def clean_value(value: Any) -> Any:
            """Recursively clean a value."""
            if value is None:
                return None
            elif isinstance(value, dict):
                cleaned_dict: Dict[str, Any] = {}
                for k, v in value.items():
                    cleaned_v = clean_value(v)
                    # Skip None values and empty dicts (except for special keys like _inline_scripts)
                    if cleaned_v is not None and (not isinstance(cleaned_v, dict) or cleaned_v or k.startswith('_')):
                        cleaned_dict[k] = cleaned_v
                return cleaned_dict if cleaned_dict else None
            elif isinstance(value, list):
                cleaned_list: List[Any] = []
                for item in value:
                    cleaned_item = clean_value(item)
                    # Skip None values and empty strings in lists
                    if cleaned_item is not None and cleaned_item != '':
                        # Special handling for port mappings - skip invalid ones
                        if isinstance(cleaned_item, str) and ':' in cleaned_item:
                            parts = cleaned_item.split(':')
                            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                                cleaned_list.append(cleaned_item)
                        else:
                            cleaned_list.append(cleaned_item)
                return cleaned_list if cleaned_list else None
            else:
                return value
        
        result = {}
        for key, value in config_dict.items():
            cleaned_value = clean_value(value)
            if cleaned_value is not None:
                result[key] = cleaned_value
        
        return result