"""
Bridge layer for converting between UI state and configuration models.

This module provides the UIStateBridge class that handles conversions between
NiceGUI bindable dataclasses (UI state) and attrs-based configuration models
through the adapter layer, as well as YAML serialization/deserialization.
"""

from typing import Dict, List, Tuple, Any, Optional
import yaml
from pathlib import Path
import attrs
import cattrs
from omegaconf import OmegaConf

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
        """Save UI state to YAML file with validation."""
        errors = []
        
        # First validate
        is_valid, validation_errors = self.validate_ui_state(ui_state)
        if not is_valid:
            return False, validation_errors
        
        try:
            # Convert UI state to user_config.yml format
            config_data = self._ui_to_user_config_format(ui_state)
            
            # Create directory if needed
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save to YAML - let YAML handle quoting automatically
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, 
                         sort_keys=False, allow_unicode=True)
            
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
            # Step 1: First load with yaml to handle duplicates (takes last value)
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if not yaml_data:
                errors.append("Empty configuration file")
                return False, errors
            
            # Step 2: Convert to OmegaConf for variable resolution
            config = OmegaConf.create(yaml_data)
            
            # Step 3: Convert to Python dict and prepare for cattrs
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
                        if 'on_entry' in custom and custom['on_entry'] is not None:
                            on_entry = custom['on_entry']
                            if isinstance(on_entry, str):
                                # Convert string to single-element list
                                config_dict[stage]['custom']['on_entry'] = [on_entry]
            
            # Step 4: Parse into UserConfig using cattrs (proper data model)
            user_config: AttrsUserConfig = cattrs.structure(config_dict, AttrsUserConfig)
            
            # Step 5: Convert UserConfig to UI state
            self._load_user_config_into_ui(user_config, ui_state)
            
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
        if stage_config.proxy:
            ui_stage.network.proxy_enabled = True
            # Reconstruct proxy URL
            scheme = 'https' if stage_config.proxy.use_https else 'http'
            ui_stage.network.http_proxy = f"{scheme}://{stage_config.proxy.address}:{stage_config.proxy.port}"
        else:
            ui_stage.network.proxy_enabled = False
        
        # Load APT configuration (stage 1 only)
        if stage_config.apt and stage_num == 1:
            ui_stage.network.apt_mirror = stage_config.apt.repo_source or ""
        
        # Load device configuration
        if stage_config.device:
            ui_stage.environment.device_type = stage_config.device.type
        else:
            ui_stage.environment.device_type = 'cpu'
        
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
    
    def _load_custom_scripts_into_ui(self, custom: AttrsCustomScriptConfig, ui_scripts: ScriptsUI) -> None:
        """Load custom scripts from data model into UI state."""
        # Clear existing scripts
        ui_scripts.lifecycle_scripts = {
            'on_build': [],
            'on_first_run': [],
            'on_every_run': [],
            'on_user_login': []
        }
        
        # Load entry point
        if custom.on_entry:
            if len(custom.on_entry) > 0:
                entry_script = custom.on_entry[0]
                if entry_script.startswith('_inline_'):
                    ui_scripts.entry_mode = 'inline'
                    ui_scripts.entry_inline_name = entry_script.replace('_inline_', '')
                else:
                    ui_scripts.entry_mode = 'file'
                    ui_scripts.entry_file_path = entry_script
        
        # Load lifecycle scripts with unique IDs
        import uuid
        
        # Helper function to create script entry
        def create_script_entry(script_path: str) -> Dict[str, Any]:
            return {
                'id': str(uuid.uuid4()),
                'type': 'file',
                'path': script_path
            }
        
        # Load on_build scripts
        if custom.on_build:
            for script in custom.on_build:
                ui_scripts.lifecycle_scripts['on_build'].append(create_script_entry(script))
        
        # Load on_first_run scripts
        if custom.on_first_run:
            for script in custom.on_first_run:
                ui_scripts.lifecycle_scripts['on_first_run'].append(create_script_entry(script))
        
        # Load on_every_run scripts
        if custom.on_every_run:
            for script in custom.on_every_run:
                ui_scripts.lifecycle_scripts['on_every_run'].append(create_script_entry(script))
        
        # Load on_user_login scripts
        if custom.on_user_login:
            for script in custom.on_user_login:
                ui_scripts.lifecycle_scripts['on_user_login'].append(create_script_entry(script))
    
    def _load_storage_into_ui(self, storage_dict: Dict[str, AttrsStorageOption], ui_storage: StorageUI) -> None:
        """Load storage configuration from data model into UI state."""
        for name, storage_option in storage_dict.items():
            if name == 'app':
                ui_storage.app_storage_type = storage_option.type
                if storage_option.type == 'host' and storage_option.host_path:
                    ui_storage.app_host_path = storage_option.host_path
                elif storage_option.type == 'volume' and storage_option.volume_name:
                    ui_storage.app_volume_name = storage_option.volume_name
            elif name == 'data':
                ui_storage.data_storage_type = storage_option.type
                if storage_option.type == 'host' and storage_option.host_path:
                    ui_storage.data_host_path = storage_option.host_path
                elif storage_option.type == 'volume' and storage_option.volume_name:
                    ui_storage.data_volume_name = storage_option.volume_name
            elif name == 'workspace':
                ui_storage.workspace_storage_type = storage_option.type
                if storage_option.type == 'host' and storage_option.host_path:
                    ui_storage.workspace_host_path = storage_option.host_path
                elif storage_option.type == 'volume' and storage_option.volume_name:
                    ui_storage.workspace_volume_name = storage_option.volume_name
    
    def _load_mount_into_ui(self, mount_dict: Dict[str, AttrsStorageOption], ui_storage: StorageUI) -> None:
        """Load mount configuration from data model into UI state."""
        ui_storage.mounts = []
        for name, mount_option in mount_dict.items():
            # Mount types should be preserved as-is: auto-volume, manual-volume, host
            mount_type = mount_option.type
            # For mounts, image type is not allowed, default to auto-volume
            if mount_type == 'image':
                mount_type = 'auto-volume'
            
            # Determine source based on mount type
            if mount_type == 'host':
                source = mount_option.host_path or ''
            elif mount_type == 'manual-volume':
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
            image = AttrsImageConfig(
                base=ui_project.base_image,
                output=ui_project.image_output_name or ui_project.project_name or "pei-image"
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
            
            ssh = AttrsSSHConfig(
                enable=ui_stage.ssh.enabled,
                port=int(ui_stage.ssh.port) if ui_stage.ssh.port.isdigit() else 22,
                host_port=int(ui_stage.ssh.host_port) if ui_stage.ssh.host_port.isdigit() else 2222,
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
        if ui_stage.environment.device_type != 'cpu':
            device = AttrsDeviceConfig(type=ui_stage.environment.device_type)
        
        # Convert environment variables
        environment = ui_stage.environment.env_vars if ui_stage.environment.env_vars else None
        
        # Convert port mappings
        ports = None
        if ui_stage.network.port_mappings:
            ports = [
                f"{m['host']}:{m['container']}" 
                for m in ui_stage.network.port_mappings
            ]
        
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
            # For inline scripts, we'll handle this in YAML generation
            on_entry.append(f"_inline_{ui_scripts.entry_inline_name}")
        
        # Extract lifecycle scripts
        lifecycle_scripts = ui_scripts.lifecycle_scripts
        
        on_build = []
        on_first_run = []
        on_every_run = []
        on_user_login = []
        
        # Note: attrs model uses on_build, not pre_build/post_build
        if 'pre_build' in lifecycle_scripts:
            for script_data in lifecycle_scripts['pre_build']:
                if isinstance(script_data, dict) and 'path' in script_data:
                    on_build.append(script_data['path'])
                elif isinstance(script_data, str):
                    on_build.append(script_data)
        
        if 'first_run' in lifecycle_scripts:
            for script_data in lifecycle_scripts['first_run']:
                if isinstance(script_data, dict) and 'path' in script_data:
                    on_first_run.append(script_data['path'])
                elif isinstance(script_data, str):
                    on_first_run.append(script_data)
        
        if 'every_run' in lifecycle_scripts:
            for script_data in lifecycle_scripts['every_run']:
                if isinstance(script_data, dict) and 'path' in script_data:
                    on_every_run.append(script_data['path'])
                elif isinstance(script_data, str):
                    on_every_run.append(script_data)
        
        if 'user_login' in lifecycle_scripts:
            for script_data in lifecycle_scripts['user_login']:
                if isinstance(script_data, dict) and 'path' in script_data:
                    on_user_login.append(script_data['path'])
                elif isinstance(script_data, str):
                    on_user_login.append(script_data)
        
        # Only create CustomScriptConfig if we have any scripts
        if any([on_entry, on_build, on_first_run, on_every_run, on_user_login]):
            return AttrsCustomScriptConfig(
                on_build=on_build,
                on_first_run=on_first_run,
                on_every_run=on_every_run,
                on_user_login=on_user_login,
                on_entry=on_entry
            )
        
        return None
    
    def _build_storage_config(self, ui_storage: StorageUI) -> Dict[str, AttrsStorageOption]:
        """Build storage configuration from UI state."""
        storage = {}
        
        # Fixed storage entries for stage-2
        for name, prefix in [('app', 'app'), ('data', 'data'), ('workspace', 'workspace')]:
            storage_type = getattr(ui_storage, f'{prefix}_storage_type')
            
            if storage_type == 'auto-volume':
                storage[name] = AttrsStorageOption(type=StorageTypes.AutoVolume)
            elif storage_type == 'manual-volume':
                volume_name = getattr(ui_storage, f'{prefix}_volume_name')
                if volume_name:
                    storage[name] = AttrsStorageOption(
                        type=StorageTypes.ManualVolume,
                        volume_name=volume_name
                    )
            elif storage_type == 'host':
                host_path = getattr(ui_storage, f'{prefix}_host_path')
                if host_path:
                    storage[name] = AttrsStorageOption(
                        type=StorageTypes.Host,
                        host_path=host_path
                    )
            elif storage_type == 'image':
                storage[name] = AttrsStorageOption(type=StorageTypes.Image)
        
        # Additional volumes
        for volume in ui_storage.volumes:
            name = volume.get('name', '')
            if name and name not in ['app', 'data', 'workspace']:
                storage_type = volume.get('type', 'auto-volume')
                source = volume.get('source', '')
                target = volume.get('target', '')
                
                if storage_type == 'auto-volume':
                    storage[name] = AttrsStorageOption(
                        type=StorageTypes.AutoVolume,
                        dst_path=target
                    )
                elif storage_type == 'manual-volume' and source:
                    storage[name] = AttrsStorageOption(
                        type=StorageTypes.ManualVolume,
                        volume_name=source,
                        dst_path=target
                    )
                elif storage_type == 'host' and source:
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
            mount_type = mount.get('type', 'auto-volume')
            
            if name and target:  # Source is optional for auto-volume
                if mount_type == 'host':
                    if source:  # Host type requires source
                        mounts[name] = AttrsStorageOption(
                            type=StorageTypes.Host,
                            host_path=source,
                            dst_path=target
                        )
                elif mount_type == 'manual-volume':
                    if source:  # Manual volume requires source (volume name)
                        mounts[name] = AttrsStorageOption(
                            type=StorageTypes.ManualVolume,
                            volume_name=source,
                            dst_path=target
                        )
                elif mount_type == 'auto-volume':
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
        """Convert UI state to user_config.yml format."""
        # This method remains largely the same as it's converting to YAML format
        # The previous implementation already handles the conversion correctly
        
        # Convert environment variables to list format
        def env_vars_to_list(env_vars: Dict[str, str]) -> List[str]:
            return [f"{k}={v}" for k, v in env_vars.items()]
        
        # Build stage-1 configuration
        output_name = ui_state.project.image_output_name or ui_state.project.project_name or "pei-image"
        stage_1: Dict[str, Any] = {
            'image': {
                'base': ui_state.project.base_image,
                'output': f"{output_name}:stage-1"
            }
        }
        
        # Add inline scripts metadata if any
        inline_scripts_1: Dict[str, str] = {}
        inline_scripts_2: Dict[str, str] = {}
        
        # Process stage-1 inline scripts
        if ui_state.stage_1.scripts.entry_mode == "inline":
            script_name = ui_state.stage_1.scripts.entry_inline_name
            script_content = ui_state.stage_1.scripts.entry_inline_content
            if script_name and script_content:
                inline_scripts_1[script_name] = script_content
                stage_1['entry_point'] = f"/pei-docker/scripts/{script_name}"
        elif ui_state.stage_1.scripts.entry_mode == "file":
            stage_1['entry_point'] = ui_state.stage_1.scripts.entry_file_path
        
        # Add environment configuration to stage-1
        # Environment tab has separate sections for stage-1 and stage-2, save separately
        if ui_state.stage_1.environment.env_vars:
            stage_1['environment'] = env_vars_to_list(ui_state.stage_1.environment.env_vars)
        
        # Add device configuration to stage-1
        if ui_state.stage_1.environment.device_type != 'cpu':
            stage_1['device'] = {
                'type': ui_state.stage_1.environment.device_type
            }
        
        # Add network configuration to stage-1
        # Following default behavior: write to both stages
        if ui_state.stage_1.network.proxy_enabled:
            proxy_config: Dict[str, Any] = {}
            if ui_state.stage_1.network.http_proxy:
                # Extract components from proxy URL
                proxy_url = ui_state.stage_1.network.http_proxy
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
                
                proxy_config['address'] = address
                proxy_config['port'] = port
                proxy_config['enable_globally'] = True
                if use_https:
                    proxy_config['use_https'] = True
                
            stage_1['proxy'] = proxy_config
        
        if ui_state.stage_1.network.apt_mirror:
            stage_1['apt'] = {
                'repo_source': ui_state.stage_1.network.apt_mirror,
                'use_proxy': ui_state.stage_1.network.proxy_enabled
            }
        
        # Add port mappings to stage-1
        if ui_state.stage_1.network.port_mappings:
            stage_1['ports'] = [
                f"{m['host']}:{m['container']}" 
                for m in ui_state.stage_1.network.port_mappings
            ]
        
        # Add SSH configuration to stage-1 ONLY (per mapping rules)
        if ui_state.stage_1.ssh.enabled:
            # Convert users list to dict format expected by attrs
            users_dict = {}
            for user_data in ui_state.stage_1.ssh.users:
                username = user_data.get('name', '')
                if username:
                    user_config = {}
                    
                    # Only include password if not empty
                    password = user_data.get('password')
                    if password:
                        user_config['password'] = password
                    
                    # Only include uid if not empty (uid must be integer or omitted)
                    uid = user_data.get('uid', '')
                    if uid and uid.strip():
                        try:
                            user_config['uid'] = int(uid)
                        except ValueError:
                            # If not a valid integer, omit it
                            pass
                    
                    # Handle SSH keys
                    ssh_keys = user_data.get('ssh_keys', [])
                    if ssh_keys and ssh_keys[0]:
                        user_config['pubkey_text'] = ssh_keys[0]
                    
                    users_dict[username] = user_config
            
            stage_1['ssh'] = {
                'enable': True,
                'port': int(ui_state.stage_1.ssh.port),
                'host_port': int(ui_state.stage_1.ssh.host_port),
                'users': users_dict
            }
        
        # Process stage-1 custom scripts
        custom_scripts_1 = {}
        lifecycle_1 = ui_state.stage_1.scripts.lifecycle_scripts
        
        for script_type in ['on_build', 'on_first_run', 'on_every_run', 'on_user_login']:
            ui_key = script_type.replace('on_', '') if script_type != 'on_build' else 'pre_build'
            if ui_key in lifecycle_1 and lifecycle_1[ui_key]:
                script_list = []
                for script_data in lifecycle_1[ui_key]:
                    if isinstance(script_data, dict):
                        if script_data.get('type') == 'file':
                            script_list.append(script_data['path'])
                        elif script_data.get('type') == 'inline':
                            inline_name = script_data.get('name', '')
                            if inline_name:
                                script_list.append(f"/pei-docker/scripts/{inline_name}")
                                inline_scripts_1[inline_name] = script_data.get('content', '')
                if script_list:
                    custom_scripts_1[script_type] = script_list
        
        if custom_scripts_1:
            stage_1['custom'] = custom_scripts_1
        
        # Add stage-1 inline scripts to metadata
        if inline_scripts_1:
            stage_1['_inline_scripts'] = inline_scripts_1
        
        # Process stage-1 inline scripts metadata
        if ui_state.stage_1.scripts._inline_scripts_metadata:
            if '_inline_scripts' not in stage_1:
                stage_1['_inline_scripts'] = {}
            # Cast to Any to satisfy type checker - we know this is safe
            metadata: Dict[str, Any] = dict(ui_state.stage_1.scripts._inline_scripts_metadata)
            stage_1['_inline_scripts'].update(metadata)
        
        # Build stage-2 configuration
        stage_2: Dict[str, Any] = {
            'image': {
                'output': f"{output_name}:stage-2"
            }
        }
        
        # Process stage-2 inline entry point
        if ui_state.stage_2.scripts.entry_mode == "inline":
            script_name = ui_state.stage_2.scripts.entry_inline_name
            script_content = ui_state.stage_2.scripts.entry_inline_content
            if script_name and script_content:
                inline_scripts_2[script_name] = script_content
                stage_2['entry_point'] = f"/pei-docker/scripts/{script_name}"
        elif ui_state.stage_2.scripts.entry_mode == "file":
            stage_2['entry_point'] = ui_state.stage_2.scripts.entry_file_path
        
        # Add environment configuration to stage-2
        # Environment tab has separate sections for stage-1 and stage-2, save separately
        if ui_state.stage_2.environment.env_vars:
            stage_2['environment'] = env_vars_to_list(ui_state.stage_2.environment.env_vars)
        
        # Add device configuration to stage-2 (copy from GUI's single device setting)
        # Following the principle: if GUI has single section, map to both stages
        if ui_state.stage_2.environment.device_type != 'cpu':
            stage_2['device'] = {
                'type': ui_state.stage_2.environment.device_type
            }
        
        # Add network configuration to stage-2 
        # Following default behavior: write to both stages
        if ui_state.stage_2.network.proxy_enabled:
            stage2_proxy_config: Dict[str, Any] = {}
            if ui_state.stage_2.network.http_proxy:
                proxy_url = ui_state.stage_2.network.http_proxy
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
                
                stage2_proxy_config['address'] = address
                stage2_proxy_config['port'] = port
                stage2_proxy_config['enable_globally'] = True
                if use_https:
                    stage2_proxy_config['use_https'] = True
                
            stage_2['proxy'] = stage2_proxy_config
        
        # Add storage configuration to stage-2
        storage_config = self._build_yaml_storage_config(ui_state.stage_2.storage)
        if storage_config:
            stage_2['storage'] = storage_config
        
        # Process stage-2 custom scripts
        custom_scripts_2 = {}
        lifecycle_2 = ui_state.stage_2.scripts.lifecycle_scripts
        
        for script_type in ['on_build', 'on_first_run', 'on_every_run', 'on_user_login']:
            ui_key = script_type.replace('on_', '') if script_type != 'on_build' else 'pre_build'
            if ui_key in lifecycle_2 and lifecycle_2[ui_key]:
                script_list = []
                for script_data in lifecycle_2[ui_key]:
                    if isinstance(script_data, dict):
                        if script_data.get('type') == 'file':
                            script_list.append(script_data['path'])
                        elif script_data.get('type') == 'inline':
                            inline_name = script_data.get('name', '')
                            if inline_name:
                                script_list.append(f"/pei-docker/scripts/{inline_name}")
                                inline_scripts_2[inline_name] = script_data.get('content', '')
                if script_list:
                    custom_scripts_2[script_type] = script_list
        
        if custom_scripts_2:
            stage_2['custom'] = custom_scripts_2
        
        # Add stage-2 inline scripts to metadata
        if inline_scripts_2:
            stage_2['_inline_scripts'] = inline_scripts_2
        
        # Process stage-2 inline scripts metadata
        if ui_state.stage_2.scripts._inline_scripts_metadata:
            if '_inline_scripts' not in stage_2:
                stage_2['_inline_scripts'] = {}
            # Cast to Any to satisfy type checker - we know this is safe
            metadata_2: Dict[str, Any] = dict(ui_state.stage_2.scripts._inline_scripts_metadata)
            stage_2['_inline_scripts'].update(metadata_2)
        
        return {
            'stage_1': stage_1,
            'stage_2': stage_2
        }
    
    def _build_yaml_storage_config(self, storage: StorageUI) -> Dict[str, Any]:
        """Build storage configuration for YAML format."""
        config: Dict[str, Any] = {}
        
        # Fixed storage entries for stage-2
        for name, prefix in [('app', 'app'), ('data', 'data'), ('workspace', 'workspace')]:
            storage_type = getattr(storage, f'{prefix}_storage_type')
            
            if storage_type == 'auto-volume':
                config[name] = {'type': 'auto-volume'}
            elif storage_type == 'manual-volume':
                volume_name = getattr(storage, f'{prefix}_volume_name')
                if volume_name:
                    config[name] = {'type': 'manual-volume', 'volume_name': volume_name}
            elif storage_type == 'host':
                host_path = getattr(storage, f'{prefix}_host_path')
                if host_path:
                    config[name] = {'type': 'host', 'host_path': host_path}
            elif storage_type == 'image':
                config[name] = {'type': 'image'}
        
        # Additional mounts
        if storage.mounts:
            mount_config = {}
            for mount in storage.mounts:
                name = mount.get('name', '')
                source = mount.get('source', '')
                target = mount.get('target', '')
                mount_type = mount.get('type', 'host')
                
                if name and source and target:
                    if mount_type == 'host':
                        mount_config[name] = {
                            'type': 'host',
                            'host_path': source,
                            'dst_path': target
                        }
                    elif mount_type == 'manual-volume':
                        mount_config[name] = {
                            'type': 'manual-volume',
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
            device_type = device_1.get('type', 'cpu')
            ui_state.stage_1.environment.device_type = device_type
            ui_state.stage_1.environment.gpu_enabled = (device_type == 'gpu')
        else:
            ui_state.stage_1.environment.device_type = 'cpu'
            ui_state.stage_1.environment.gpu_enabled = False
        
        # Load Stage-2 device configuration
        device_2 = stage_2_data.get('device', {})
        if device_2:
            device_type = device_2.get('type', 'cpu')
            ui_state.stage_2.environment.device_type = device_type
            ui_state.stage_2.environment.gpu_enabled = (device_type == 'gpu')
        else:
            ui_state.stage_2.environment.device_type = 'cpu'
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
            
            if address:
                proxy_url = f"{scheme}://{address}:{port}"
                # Apply to both stages
                ui_state.stage_1.network.proxy_enabled = True
                ui_state.stage_1.network.http_proxy = proxy_url
                ui_state.stage_2.network.proxy_enabled = True
                ui_state.stage_2.network.http_proxy = proxy_url
        
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
            network.proxy_enabled = True
            address = proxy_config.get('address', '')
            port = proxy_config.get('port', 8080)
            scheme = 'https' if proxy_config.get('use_https', False) else 'http'
            
            if address:
                network.http_proxy = f"{scheme}://{address}:{port}"
        
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
                storage_type = config.get('type', 'auto-volume')
                setattr(storage, f'{prefix}_storage_type', storage_type)
                
                if storage_type == 'manual-volume':
                    setattr(storage, f'{prefix}_volume_name', config.get('volume_name', ''))
                elif storage_type == 'host':
                    setattr(storage, f'{prefix}_host_path', config.get('host_path', ''))
            elif isinstance(config, str):
                # Legacy format compatibility
                if config == 'auto-volume':
                    setattr(storage, f'{prefix}_storage_type', 'auto-volume')
                elif config == 'image':
                    setattr(storage, f'{prefix}_storage_type', 'image')
                elif config.startswith('volume:'):
                    setattr(storage, f'{prefix}_storage_type', 'manual-volume')
                    setattr(storage, f'{prefix}_volume_name', config[7:])
                elif config.startswith('host:'):
                    setattr(storage, f'{prefix}_storage_type', 'host')
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
                
                if mount_type == 'host':
                    mount_data['source'] = config.get('host_path', '')
                elif mount_type == 'manual-volume':
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
        entry_points_1 = custom_1.get('on_entry', [])
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
        entry_points_2 = custom_2.get('on_entry', [])
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
        lifecycle_keys = ['on_build', 'on_first_run', 'on_every_run', 'on_user_login']
        
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
                            'type': 'file',
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
                            'type': 'file',
                            'path': script_str,  # Store full path with args for compatibility
                            'content': ''  # File scripts don't have content
                        }
                        # Store parsed path and args separately if needed
                        if args:
                            script_data['script_path'] = path
                            script_data['args'] = args
                        scripts_list.append(script_data)
                scripts2.lifecycle_scripts[lifecycle_key] = scripts_list