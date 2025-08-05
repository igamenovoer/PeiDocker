"""
Bridge layer for converting between UI state and configuration models.

This module provides the UIStateBridge class that handles conversions between
NiceGUI bindable dataclasses (UI state) and Pydantic validation models,
as well as YAML serialization/deserialization.
"""

from typing import Dict, List, Tuple, Any, Optional
import yaml
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError

from pei_docker.webgui.models.ui_state import (
    AppUIState, StageUI, EnvironmentUI, NetworkUI, SSHTabUI,
    StorageUI, ScriptsUI, ProjectUI
)
from pei_docker.webgui.models.config import (
    AppConfig, StageConfig, EnvironmentConfig, NetworkConfig,
    SSHConfig, StorageConfig, ScriptsConfig, ProjectConfig
)


class UIStateBridge:
    """Converts between UI state models and validated config models."""
    
    def validate_ui_state(self, ui_state: AppUIState) -> Tuple[bool, List[str]]:
        """Validate current UI state without modifying it."""
        errors = []
        
        try:
            # Validate project configuration
            self._ui_project_to_pydantic(ui_state.project)
            
            # Validate stage configurations
            self._ui_stage_to_pydantic(ui_state.stage_1)
            self._ui_stage_to_pydantic(ui_state.stage_2)
            
            return True, []
            
        except ValidationError as e:
            for error in e.errors():
                field = " → ".join(str(loc) for loc in error['loc'])
                errors.append(f"{field}: {error['msg']}")
            
            return False, errors
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
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
            
            # Save to YAML
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, 
                         sort_keys=False, allow_unicode=True)
            
            return True, []
            
        except Exception as e:
            errors.append(f"Save failed: {str(e)}")
            return False, errors
    
    def load_from_yaml(self, file_path: str, ui_state: AppUIState) -> Tuple[bool, List[str]]:
        """Load YAML configuration into UI state."""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                errors.append("Empty configuration file")
                return False, errors
            
            # Clear current state and load from YAML
            self._load_into_ui(config_data, ui_state)
            
            return True, []
            
        except FileNotFoundError:
            errors.append(f"Configuration file not found: {file_path}")
            return False, errors
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML format: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Load failed: {str(e)}")
            return False, errors
    
    def ui_to_config(self, ui_state: AppUIState) -> AppConfig:
        """Convert UI state to validated Pydantic config."""
        return AppConfig(
            project=self._ui_project_to_pydantic(ui_state.project),
            stage_1=self._ui_stage_to_pydantic(ui_state.stage_1),
            stage_2=self._ui_stage_to_pydantic(ui_state.stage_2)
        )
    
    # Private conversion methods
    
    def _ui_project_to_pydantic(self, ui_project: ProjectUI) -> ProjectConfig:
        """Convert UI project state to Pydantic model."""
        # Use project_name from directory if not set
        project_name = ui_project.project_name
        if not project_name and ui_project.project_directory:
            project_name = Path(ui_project.project_directory).name
        
        return ProjectConfig(
            project_name=project_name or "untitled",
            project_directory=ui_project.project_directory or "",
            description=ui_project.description,
            base_image=ui_project.base_image,
            image_output_name=ui_project.image_output_name,
            template=ui_project.template
        )
    
    def _ui_environment_to_pydantic(self, ui_env: EnvironmentUI) -> EnvironmentConfig:
        """Convert UI environment state to Pydantic model."""
        return EnvironmentConfig(
            gpu_enabled=ui_env.gpu_enabled,
            gpu_count=ui_env.gpu_count,
            cuda_version=ui_env.cuda_version,
            env_vars=dict(ui_env.env_vars),
            device_type=ui_env.device_type,
            gpu_memory_limit=ui_env.gpu_memory_limit
        )
    
    def _ui_network_to_pydantic(self, ui_net: NetworkUI) -> NetworkConfig:
        """Convert UI network state to Pydantic model."""
        return NetworkConfig(
            proxy_enabled=ui_net.proxy_enabled,
            http_proxy=ui_net.http_proxy,
            https_proxy=ui_net.https_proxy,
            no_proxy=ui_net.no_proxy,
            apt_mirror=ui_net.apt_mirror,
            port_mappings=list(ui_net.port_mappings)
        )
    
    def _ui_ssh_to_pydantic(self, ui_ssh: SSHTabUI) -> SSHConfig:
        """Convert UI SSH state to Pydantic model."""
        return SSHConfig(
            enabled=ui_ssh.enabled,
            port=int(ui_ssh.port) if ui_ssh.port.isdigit() else 22,
            host_port=int(ui_ssh.host_port) if ui_ssh.host_port.isdigit() else 2222,
            users=list(ui_ssh.users)
        )
    
    def _ui_storage_to_pydantic(self, ui_storage: StorageUI) -> StorageConfig:
        """Convert UI storage state to Pydantic model."""
        return StorageConfig(
            app_storage_type=ui_storage.app_storage_type,
            app_volume_name=ui_storage.app_volume_name,
            app_host_path=ui_storage.app_host_path,
            data_storage_type=ui_storage.data_storage_type,
            data_volume_name=ui_storage.data_volume_name,
            data_host_path=ui_storage.data_host_path,
            workspace_storage_type=ui_storage.workspace_storage_type,
            workspace_volume_name=ui_storage.workspace_volume_name,
            workspace_host_path=ui_storage.workspace_host_path,
            volumes=list(ui_storage.volumes),
            mounts=list(ui_storage.mounts)
        )
    
    def _ui_scripts_to_pydantic(self, ui_scripts: ScriptsUI, stage_num: int) -> ScriptsConfig:
        """Convert UI scripts state to Pydantic model."""
        config = ScriptsConfig()
        
        # Map entry modes from UI to config format
        if stage_num == 1:
            entry_mode = ui_scripts.stage1_entry_mode
            if entry_mode == "file":
                config.stage1_entry_mode = "custom"
                config.stage1_entry_command = ui_scripts.stage1_entry_file_path
            elif entry_mode == "inline":
                config.stage1_entry_mode = "custom"
                # For inline scripts, we'll need to handle this specially in YAML generation
                config.stage1_entry_command = f"_inline_{ui_scripts.stage1_entry_inline_name}"
        else:
            entry_mode = ui_scripts.stage2_entry_mode
            if entry_mode == "file":
                config.stage2_entry_mode = "custom"
                config.stage2_entry_command = ui_scripts.stage2_entry_file_path
            elif entry_mode == "inline":
                config.stage2_entry_mode = "custom"
                config.stage2_entry_command = f"_inline_{ui_scripts.stage2_entry_inline_name}"
        
        # Extract lifecycle scripts from stored metadata
        lifecycle_scripts = ui_scripts.stage1_lifecycle_scripts if stage_num == 1 else ui_scripts.stage2_lifecycle_scripts
        
        for script_type in ['pre_build', 'post_build', 'first_run', 'every_run', 'user_login']:
            if script_type in lifecycle_scripts:
                script_list = []
                for script_data in lifecycle_scripts[script_type]:
                    if isinstance(script_data, dict) and 'path' in script_data:
                        script_list.append(script_data['path'])
                    elif isinstance(script_data, str):
                        script_list.append(script_data)
                setattr(config, script_type, script_list)
        
        return config
    
    def _ui_stage_to_pydantic(self, ui_stage: StageUI) -> StageConfig:
        """Convert UI stage state to Pydantic model."""
        # Determine stage number based on which stage this is
        stage_num = 1  # Default, will be overridden in actual usage
        
        return StageConfig(
            environment=self._ui_environment_to_pydantic(ui_stage.environment),
            network=self._ui_network_to_pydantic(ui_stage.network),
            ssh=self._ui_ssh_to_pydantic(ui_stage.ssh),
            storage=self._ui_storage_to_pydantic(ui_stage.storage),
            scripts=self._ui_scripts_to_pydantic(ui_stage.scripts, stage_num)
        )
    
    def _ui_to_user_config_format(self, ui_state: AppUIState) -> Dict[str, Any]:
        """Convert UI state to user_config.yml format."""
        
        # Convert environment variables to list format
        def env_vars_to_list(env_vars: Dict[str, str]) -> List[str]:
            return [f"{k}={v}" for k, v in env_vars.items()]
        
        # Build stage-1 configuration
        stage_1: Dict[str, Any] = {
            'image': {
                'base': ui_state.project.base_image,
                'output': ui_state.project.image_output_name or ui_state.project.project_name
            }
        }
        
        # Add inline scripts metadata if any
        inline_scripts_1: Dict[str, str] = {}
        inline_scripts_2: Dict[str, str] = {}
        
        # Process stage-1 inline scripts
        if ui_state.stage_1.scripts.stage1_entry_mode == "inline":
            script_name = ui_state.stage_1.scripts.stage1_entry_inline_name
            script_content = ui_state.stage_1.scripts.stage1_entry_inline_content
            if script_name and script_content:
                inline_scripts_1[script_name] = script_content
                stage_1['entry_point'] = f"/pei-docker/scripts/{script_name}"
        elif ui_state.stage_1.scripts.stage1_entry_mode == "file":
            stage_1['entry_point'] = ui_state.stage_1.scripts.stage1_entry_file_path
        
        # Add environment configuration to stage-1
        if ui_state.stage_1.environment.env_vars:
            stage_1['environment'] = env_vars_to_list(ui_state.stage_1.environment.env_vars)
        
        # Add device configuration to stage-1
        if ui_state.stage_1.environment.device_type != 'cpu':
            device_config: Dict[str, Any] = {
                'type': ui_state.stage_1.environment.device_type
            }
            if ui_state.stage_1.environment.device_type == 'gpu':
                gpu_config: Dict[str, Any] = {}
                if ui_state.stage_1.environment.gpu_count == 'all':
                    gpu_config['all'] = True
                else:
                    gpu_config['count'] = int(ui_state.stage_1.environment.gpu_count)
                if ui_state.stage_1.environment.gpu_memory_limit:
                    gpu_config['memory'] = ui_state.stage_1.environment.gpu_memory_limit
                device_config['gpu'] = gpu_config
            stage_1['device'] = device_config
        
        # Add network configuration to stage-1
        if ui_state.stage_1.network.proxy_enabled:
            proxy_config: Dict[str, Any] = {}
            if ui_state.stage_1.network.http_proxy:
                proxy_config['http'] = ui_state.stage_1.network.http_proxy
            if ui_state.stage_1.network.https_proxy:
                proxy_config['https'] = ui_state.stage_1.network.https_proxy
            if ui_state.stage_1.network.no_proxy:
                proxy_config['no_proxy'] = ui_state.stage_1.network.no_proxy
            stage_1['proxy'] = proxy_config
        
        if ui_state.stage_1.network.apt_mirror:
            stage_1['apt'] = {'mirror': ui_state.stage_1.network.apt_mirror}
        
        # Add port mappings to stage-1
        if ui_state.stage_1.network.port_mappings:
            stage_1['ports'] = [
                f"{m['host']}:{m['container']}" 
                for m in ui_state.stage_1.network.port_mappings
            ]
        
        # Add SSH configuration to stage-1
        if ui_state.stage_1.ssh.enabled:
            stage_1['ssh'] = {
                'enable': True,
                'port': int(ui_state.stage_1.ssh.port),
                'host_port': int(ui_state.stage_1.ssh.host_port),
                'users': ui_state.stage_1.ssh.users
            }
        
        # Add stage-1 inline scripts to metadata
        if inline_scripts_1:
            stage_1['_inline_scripts'] = inline_scripts_1
        
        # Process stage-1 lifecycle scripts metadata
        if ui_state.stage_1.scripts._inline_scripts_metadata:
            if '_inline_scripts' not in stage_1:
                stage_1['_inline_scripts'] = {}
            stage_1['_inline_scripts'].update(ui_state.stage_1.scripts._inline_scripts_metadata)
        
        # Build stage-2 configuration
        stage_2: Dict[str, Any] = {}
        
        # Process stage-2 inline entry point
        if ui_state.stage_2.scripts.stage2_entry_mode == "inline":
            script_name = ui_state.stage_2.scripts.stage2_entry_inline_name
            script_content = ui_state.stage_2.scripts.stage2_entry_inline_content
            if script_name and script_content:
                inline_scripts_2[script_name] = script_content
                stage_2['entry_point'] = f"/pei-docker/scripts/{script_name}"
        elif ui_state.stage_2.scripts.stage2_entry_mode == "file":
            stage_2['entry_point'] = ui_state.stage_2.scripts.stage2_entry_file_path
        
        # Add environment configuration to stage-2
        if ui_state.stage_2.environment.env_vars:
            stage_2['environment'] = env_vars_to_list(ui_state.stage_2.environment.env_vars)
        
        # Add network configuration to stage-2 (only if different from stage-1)
        if ui_state.stage_2.network.proxy_enabled:
            stage2_proxy_config: Dict[str, Any] = {}
            if ui_state.stage_2.network.http_proxy:
                stage2_proxy_config['http'] = ui_state.stage_2.network.http_proxy
            if ui_state.stage_2.network.https_proxy:
                stage2_proxy_config['https'] = ui_state.stage_2.network.https_proxy
            if ui_state.stage_2.network.no_proxy:
                stage2_proxy_config['no_proxy'] = ui_state.stage_2.network.no_proxy
            if stage2_proxy_config:
                stage_2['proxy'] = stage2_proxy_config
        
        # Add storage configuration to stage-2
        storage_config = self._build_storage_config(ui_state.stage_2.storage)
        if storage_config:
            stage_2['storage'] = storage_config
        
        # Add lifecycle scripts to stage-2
        lifecycle_scripts = {}
        scripts_meta = ui_state.stage_2.scripts.stage2_lifecycle_scripts
        
        for script_type in ['pre_build', 'post_build', 'first_run', 'every_run', 'user_login']:
            yaml_key = script_type.replace('_', '-')
            if script_type in scripts_meta and scripts_meta[script_type]:
                script_list = []
                for script_data in scripts_meta[script_type]:
                    if isinstance(script_data, dict):
                        if script_data.get('type') == 'file':
                            script_list.append(script_data['path'])
                        elif script_data.get('type') == 'inline':
                            inline_name = script_data.get('name', '')
                            if inline_name:
                                script_list.append(f"/pei-docker/scripts/{inline_name}")
                lifecycle_scripts[yaml_key] = script_list
        
        if lifecycle_scripts:
            stage_2['scripts'] = lifecycle_scripts
        
        # Add stage-2 inline scripts to metadata
        if inline_scripts_2:
            stage_2['_inline_scripts'] = inline_scripts_2
        
        # Process stage-2 lifecycle scripts metadata
        if ui_state.stage_2.scripts._inline_scripts_metadata:
            if '_inline_scripts' not in stage_2:
                stage_2['_inline_scripts'] = {}
            stage_2['_inline_scripts'].update(ui_state.stage_2.scripts._inline_scripts_metadata)
        
        return {
            'stage-1': stage_1,
            'stage-2': stage_2
        }
    
    def _build_storage_config(self, storage: StorageUI) -> Dict[str, Any]:
        """Build storage configuration from UI state."""
        config: Dict[str, Any] = {}
        
        # Fixed storage entries for stage-2
        for name, prefix in [('app', 'app'), ('data', 'data'), ('workspace', 'workspace')]:
            storage_type = getattr(storage, f'{prefix}_storage_type')
            
            if storage_type == 'auto-volume':
                config[name] = 'auto-volume'
            elif storage_type == 'manual-volume':
                volume_name = getattr(storage, f'{prefix}_volume_name')
                if volume_name:
                    config[name] = f"volume:{volume_name}"
            elif storage_type == 'host':
                host_path = getattr(storage, f'{prefix}_host_path')
                if host_path:
                    config[name] = f"host:{host_path}"
            elif storage_type == 'image':
                config[name] = 'image'
        
        # Additional mounts
        if storage.mounts:
            config['mounts'] = [
                f"{m['source']}:{m['target']}" 
                for m in storage.mounts
            ]
        
        return config
    
    def _load_into_ui(self, config_data: Dict[str, Any], ui_state: AppUIState) -> None:
        """Load YAML configuration into UI state."""
        stage_1_data = config_data.get('stage-1', {})
        stage_2_data = config_data.get('stage-2', {})
        
        # Load project configuration
        self._load_project_config(stage_1_data, ui_state.project)
        
        # Load environment configuration
        self._load_environment_config(stage_1_data, ui_state.stage_1.environment)
        self._load_environment_config(stage_2_data, ui_state.stage_2.environment)
        
        # Load network configuration
        self._load_network_config(stage_1_data, ui_state.stage_1.network)
        self._load_network_config(stage_2_data, ui_state.stage_2.network)
        
        # Load SSH configuration (stage-1 only)
        self._load_ssh_config(stage_1_data, ui_state.stage_1.ssh)
        
        # Load storage configuration (stage-2 only)
        self._load_storage_config(stage_2_data, ui_state.stage_2.storage)
        
        # Load scripts configuration
        self._load_scripts_config(stage_1_data, stage_2_data, 
                                ui_state.stage_1.scripts, 
                                ui_state.stage_2.scripts)
        
        ui_state.modified = False
    
    def _load_project_config(self, stage_1_data: Dict[str, Any], project: ProjectUI) -> None:
        """Load project configuration from YAML data."""
        image_config = stage_1_data.get('image', {})
        project.base_image = image_config.get('base', 'ubuntu:22.04')
        project.image_output_name = image_config.get('output', '')
    
    def _load_environment_config(self, stage_data: Dict[str, Any], env: EnvironmentUI) -> None:
        """Load environment configuration from YAML data."""
        # Load environment variables
        env_list = stage_data.get('environment', [])
        env.env_vars.clear()
        
        for env_str in env_list:
            if '=' in env_str:
                key, value = env_str.split('=', 1)
                env.env_vars[key.strip()] = value.strip()
        
        # Load device configuration (stage-1 only)
        device_config = stage_data.get('device', {})
        if device_config:
            env.device_type = device_config.get('type', 'cpu')
            
            if env.device_type == 'gpu':
                gpu_config = device_config.get('gpu', {})
                env.gpu_enabled = True
                if gpu_config.get('all', False):
                    env.gpu_count = 'all'
                else:
                    env.gpu_count = str(gpu_config.get('count', 1))
                env.gpu_memory_limit = gpu_config.get('memory', '')
    
    def _load_network_config(self, stage_data: Dict[str, Any], network: NetworkUI) -> None:
        """Load network configuration from YAML data."""
        # Load proxy configuration
        proxy_config = stage_data.get('proxy', {})
        if proxy_config:
            network.proxy_enabled = True
            network.http_proxy = proxy_config.get('http', '')
            network.https_proxy = proxy_config.get('https', '')
            network.no_proxy = proxy_config.get('no_proxy', '')
        
        # Load APT mirror
        apt_config = stage_data.get('apt', {})
        network.apt_mirror = apt_config.get('mirror', '')
        
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
            
            users = ssh_config.get('users', [])
            ssh.users.clear()
            ssh.users.extend(users)
    
    def _load_storage_config(self, stage_data: Dict[str, Any], storage: StorageUI) -> None:
        """Load storage configuration from YAML data."""
        storage_config = stage_data.get('storage', {})
        
        # Load fixed storage entries
        for name, prefix in [('app', 'app'), ('data', 'data'), ('workspace', 'workspace')]:
            value = storage_config.get(name, 'auto-volume')
            
            if value == 'auto-volume':
                setattr(storage, f'{prefix}_storage_type', 'auto-volume')
            elif value == 'image':
                setattr(storage, f'{prefix}_storage_type', 'image')
            elif value.startswith('volume:'):
                setattr(storage, f'{prefix}_storage_type', 'manual-volume')
                setattr(storage, f'{prefix}_volume_name', value[7:])
            elif value.startswith('host:'):
                setattr(storage, f'{prefix}_storage_type', 'host')
                setattr(storage, f'{prefix}_host_path', value[5:])
        
        # Load additional mounts
        mounts = storage_config.get('mounts', [])
        storage.mounts.clear()
        
        for mount_str in mounts:
            if ':' in mount_str:
                source, target = mount_str.split(':', 1)
                storage.mounts.append({
                    'source': source.strip(),
                    'target': target.strip()
                })
    
    def _load_scripts_config(self, stage_1_data: Dict[str, Any], stage_2_data: Dict[str, Any],
                           scripts1: ScriptsUI, scripts2: ScriptsUI) -> None:
        """Load scripts configuration from YAML data."""
        
        # Load stage-1 inline scripts metadata
        inline_scripts_1 = stage_1_data.get('_inline_scripts', {})
        scripts1._inline_scripts_metadata.clear()
        scripts1._inline_scripts_metadata.update(inline_scripts_1)
        
        # Load stage-1 entry point
        entry_point_1 = stage_1_data.get('entry_point', '')
        if entry_point_1:
            if entry_point_1.startswith('/pei-docker/scripts/'):
                # This is an inline script
                script_name = entry_point_1.replace('/pei-docker/scripts/', '')
                if script_name in inline_scripts_1:
                    scripts1.stage1_entry_mode = "inline"
                    scripts1.stage1_entry_inline_name = script_name
                    scripts1.stage1_entry_inline_content = inline_scripts_1[script_name]
            else:
                # This is a file path
                scripts1.stage1_entry_mode = "file"
                scripts1.stage1_entry_file_path = entry_point_1
        
        # Load stage-2 inline scripts metadata
        inline_scripts_2 = stage_2_data.get('_inline_scripts', {})
        scripts2._inline_scripts_metadata.clear()
        scripts2._inline_scripts_metadata.update(inline_scripts_2)
        
        # Load stage-2 entry point
        entry_point_2 = stage_2_data.get('entry_point', '')
        if entry_point_2:
            if entry_point_2.startswith('/pei-docker/scripts/'):
                script_name = entry_point_2.replace('/pei-docker/scripts/', '')
                if script_name in inline_scripts_2:
                    scripts2.stage2_entry_mode = "inline"
                    scripts2.stage2_entry_inline_name = script_name
                    scripts2.stage2_entry_inline_content = inline_scripts_2[script_name]
            else:
                scripts2.stage2_entry_mode = "file"
                scripts2.stage2_entry_file_path = entry_point_2
        
        # Load lifecycle scripts (stage-2 only)
        scripts_config = stage_2_data.get('scripts', {})
        scripts2.stage2_lifecycle_scripts.clear()
        
        for script_type in ['pre_build', 'post_build', 'first_run', 'every_run', 'user_login']:
            yaml_key = script_type.replace('_', '-')
            if yaml_key in scripts_config:
                scripts_list = []
                for script_path in scripts_config[yaml_key]:
                    if script_path.startswith('/pei-docker/scripts/'):
                        # This is an inline script
                        script_name = script_path.replace('/pei-docker/scripts/', '')
                        if script_name in inline_scripts_2:
                            scripts_list.append({
                                'type': 'inline',
                                'name': script_name,
                                'content': inline_scripts_2[script_name],
                                'path': script_path
                            })
                    else:
                        # This is a file path
                        scripts_list.append({
                            'type': 'file',
                            'path': script_path
                        })
                scripts2.stage2_lifecycle_scripts[script_type] = scripts_list