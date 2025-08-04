"""
Bridge layer for converting between UI state and Pydantic models.

This module provides utilities to convert between NiceGUI bindable dataclasses
and Pydantic validation models, handling data transformation, validation,
and YAML serialization.
"""

from typing import Dict, List, Tuple, Any
import yaml
from pydantic import ValidationError
from nicegui import ui

from pei_docker.webgui.models.ui_state import (
    AppUIState, StageUI, EnvironmentUI, NetworkUI, SSHTabUI,
    StorageUI, ScriptsUI, ProjectUI
)
from pei_docker.webgui.models.config import (
    StageConfig, EnvironmentConfig, NetworkConfig,
    SSHConfig, StorageConfig, ScriptsConfig, ProjectConfig
)

class ConfigBridge:
    """Converts between UI state and validated config models"""
    
    @staticmethod
    def validate_ui_state(ui_state: AppUIState) -> Tuple[bool, List[str]]:
        """Validate current UI state without modifying it"""
        errors = []
        
        try:
            # Validate project configuration
            ConfigBridge._ui_project_to_pydantic(ui_state.project)
            
            # Validate stage configurations
            ConfigBridge._ui_stage_to_pydantic(ui_state.stage_1, "stage_1")
            ConfigBridge._ui_stage_to_pydantic(ui_state.stage_2, "stage_2")
            
            return True, []
            
        except ValidationError as e:
            for error in e.errors():
                field = " → ".join(str(loc) for loc in error['loc'])
                errors.append(f"{field}: {error['msg']}")
            
            return False, errors
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
    
    @staticmethod
    def _ui_project_to_pydantic(ui_project: ProjectUI) -> ProjectConfig:
        """Convert UI project state to Pydantic model"""
        return ProjectConfig(
            project_name=ui_project.project_name,
            project_directory=ui_project.project_directory,
            description=ui_project.description,
            base_image=ui_project.base_image,
            image_output_name=ui_project.image_output_name,
            template=ui_project.template
        )
    
    @staticmethod
    def _ui_environment_to_pydantic(ui_env: EnvironmentUI) -> EnvironmentConfig:
        """Convert UI environment state to Pydantic model"""
        return EnvironmentConfig(
            gpu_enabled=ui_env.gpu_enabled,
            gpu_count=ui_env.gpu_count,
            cuda_version=ui_env.cuda_version,
            env_vars=dict(ui_env.env_vars),
            device_type=ui_env.device_type,
            gpu_memory_limit=ui_env.gpu_memory_limit
        )
    
    @staticmethod
    def _ui_network_to_pydantic(ui_net: NetworkUI) -> NetworkConfig:
        """Convert UI network state to Pydantic model"""
        return NetworkConfig(
            proxy_enabled=ui_net.proxy_enabled,
            http_proxy=ui_net.http_proxy,
            https_proxy=ui_net.https_proxy,
            no_proxy=ui_net.no_proxy,
            apt_mirror=ui_net.apt_mirror,
            port_mappings=list(ui_net.port_mappings)
        )
    
    @staticmethod
    def _ui_ssh_to_pydantic(ui_ssh: SSHTabUI) -> SSHConfig:
        """Convert UI SSH state to Pydantic model"""
        return SSHConfig(
            enabled=ui_ssh.enabled,
            port=int(ui_ssh.port) if ui_ssh.port else 22,
            host_port=int(ui_ssh.host_port) if ui_ssh.host_port else 2222,
            users=list(ui_ssh.users)
        )
    
    @staticmethod
    def _ui_storage_to_pydantic(ui_storage: StorageUI) -> StorageConfig:
        """Convert UI storage state to Pydantic model"""
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
    
    @staticmethod
    def _ui_scripts_to_pydantic(ui_scripts: ScriptsUI) -> ScriptsConfig:
        """Convert UI scripts state to Pydantic model"""
        return ScriptsConfig(
            stage1_entry_mode=ui_scripts.stage1_entry_mode,
            stage1_entry_command=ui_scripts.stage1_entry_command,
            stage1_entry_params=ui_scripts.stage1_entry_params,
            stage2_entry_mode=ui_scripts.stage2_entry_mode,
            stage2_entry_command=ui_scripts.stage2_entry_command,
            stage2_entry_params=ui_scripts.stage2_entry_params,
            pre_build=list(ui_scripts.pre_build),
            post_build=list(ui_scripts.post_build),
            first_run=list(ui_scripts.first_run),
            every_run=list(ui_scripts.every_run),
            user_login=list(ui_scripts.user_login)
        )
    
    @staticmethod
    def _ui_stage_to_pydantic(ui_stage: StageUI, stage_name: str) -> StageConfig:
        """Convert UI stage state to Pydantic model"""
        return StageConfig(
            environment=ConfigBridge._ui_environment_to_pydantic(ui_stage.environment),
            network=ConfigBridge._ui_network_to_pydantic(ui_stage.network),
            ssh=ConfigBridge._ui_ssh_to_pydantic(ui_stage.ssh),
            storage=ConfigBridge._ui_storage_to_pydantic(ui_stage.storage),
            scripts=ConfigBridge._ui_scripts_to_pydantic(ui_stage.scripts)
        )
    
    @staticmethod
    def save_to_yaml(ui_state: AppUIState, file_path: str) -> bool:
        """Save UI state to YAML with validation"""
        
        is_valid, errors = ConfigBridge.validate_ui_state(ui_state)
        
        if not is_valid:
            ui.notify(f"Validation failed: {'; '.join(errors[:3])}", type='negative')
            return False
        
        try:
            # Convert UI state to user_config.yml format
            config_data = ConfigBridge._ui_to_user_config_format(ui_state)
            
            # Save to YAML
            with open(file_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
            
            ui.notify('Configuration saved successfully!', type='positive')
            ui_state.mark_saved()
            return True
            
        except Exception as e:
            ui.notify(f"Save failed: {str(e)}", type='negative')
            return False
    
    @staticmethod
    def _ui_to_user_config_format(ui_state: AppUIState) -> Dict[str, Any]:
        """Convert UI state to user_config.yml format"""
        
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
        
        # Add environment configuration to stage-1
        if ui_state.stage_1.environment.env_vars:
            stage_1['environment'] = env_vars_to_list(ui_state.stage_1.environment.env_vars)
        
        # Add device configuration to stage-1
        if ui_state.stage_1.environment.device_type != 'cpu':
            device_config: Dict[str, Any] = {
                'type': ui_state.stage_1.environment.device_type
            }
            if ui_state.stage_1.environment.device_type == 'gpu':
                gpu_config: Dict[str, Any] = {
                    'all': ui_state.stage_1.environment.gpu_count == 'all'
                }
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
        
        # Build stage-2 configuration
        stage_2: Dict[str, Any] = {'image': {}}
        
        # Add environment configuration to stage-2
        if ui_state.stage_2.environment.env_vars:
            stage_2['environment'] = env_vars_to_list(ui_state.stage_2.environment.env_vars)
        
        # Add network configuration to stage-2 (inherits proxy from stage-1)
        if ui_state.stage_2.network.proxy_enabled:
            stage2_proxy_config: Dict[str, Any] = {}
            if ui_state.stage_2.network.http_proxy:
                stage2_proxy_config['http'] = ui_state.stage_2.network.http_proxy
            if ui_state.stage_2.network.https_proxy:
                stage2_proxy_config['https'] = ui_state.stage_2.network.https_proxy
            if ui_state.stage_2.network.no_proxy:
                stage2_proxy_config['no_proxy'] = ui_state.stage_2.network.no_proxy
            stage_2['proxy'] = stage2_proxy_config
        
        # Add storage configuration to stage-2
        storage_config = ConfigBridge._build_storage_config(ui_state.stage_2.storage)
        if storage_config:
            stage_2['storage'] = storage_config
        
        # Add scripts configuration
        scripts_config = ConfigBridge._build_scripts_config(
            ui_state.stage_1.scripts,
            ui_state.stage_2.scripts
        )
        if scripts_config:
            stage_1.update(scripts_config.get('stage_1', {}))
            stage_2.update(scripts_config.get('stage_2', {}))
        
        return {
            'stage-1': stage_1,
            'stage-2': stage_2
        }
    
    @staticmethod
    def _build_storage_config(storage: StorageUI) -> Dict[str, Any]:
        """Build storage configuration from UI state"""
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
    
    @staticmethod
    def _build_scripts_config(scripts1: ScriptsUI, scripts2: ScriptsUI) -> Dict[str, Any]:
        """Build scripts configuration from UI state"""
        config: Dict[str, Any] = {'stage_1': {}, 'stage_2': {}}
        
        # Entry point configuration
        for stage_num, scripts in [(1, scripts1), (2, scripts2)]:
            stage_key = f'stage_{stage_num}'
            entry_mode = getattr(scripts, f'stage{stage_num}_entry_mode')
            
            if entry_mode != 'default':
                entry_cmd = getattr(scripts, f'stage{stage_num}_entry_command')
                entry_params = getattr(scripts, f'stage{stage_num}_entry_params')
                
                if entry_mode == 'custom' and entry_cmd:
                    config[stage_key]['entry_point'] = entry_cmd
                elif entry_mode == 'custom_param' and entry_cmd:
                    config[stage_key]['entry_point'] = f"{entry_cmd} {entry_params}".strip()
        
        # Lifecycle scripts (only in stage-2)
        lifecycle_scripts = {}
        for script_type in ['pre_build', 'post_build', 'first_run', 'every_run', 'user_login']:
            scripts_list = getattr(scripts2, script_type)
            if scripts_list:
                lifecycle_scripts[script_type.replace('_', '-')] = scripts_list
        
        if lifecycle_scripts:
            config['stage_2']['scripts'] = lifecycle_scripts
        
        return config if any(config.values()) else {}
    
    @staticmethod
    def load_into_ui(config_data: Dict[str, Any], ui_state: AppUIState) -> None:
        """Load YAML configuration into UI state"""
        try:
            stage_1_data = config_data.get('stage-1', {})
            stage_2_data = config_data.get('stage-2', {})
            
            # Load project configuration
            ConfigBridge._load_project_config(stage_1_data, ui_state.project)
            
            # Load environment configuration
            ConfigBridge._load_environment_config(stage_1_data, ui_state.stage_1.environment)
            ConfigBridge._load_environment_config(stage_2_data, ui_state.stage_2.environment)
            
            # Load network configuration
            ConfigBridge._load_network_config(stage_1_data, ui_state.stage_1.network)
            ConfigBridge._load_network_config(stage_2_data, ui_state.stage_2.network)
            
            # Load SSH configuration (stage-1 only)
            ConfigBridge._load_ssh_config(stage_1_data, ui_state.stage_1.ssh)
            
            # Load storage configuration (stage-2 only)
            ConfigBridge._load_storage_config(stage_2_data, ui_state.stage_2.storage)
            
            # Load scripts configuration
            ConfigBridge._load_scripts_config(stage_1_data, stage_2_data, 
                                            ui_state.stage_1.scripts, 
                                            ui_state.stage_2.scripts)
            
            ui_state.modified = False
            
        except Exception as e:
            ui.notify(f"Error loading configuration: {str(e)}", type='negative')
            raise
    
    @staticmethod
    def _load_project_config(stage_1_data: Dict[str, Any], project: ProjectUI) -> None:
        """Load project configuration from YAML data"""
        image_config = stage_1_data.get('image', {})
        project.base_image = image_config.get('base', 'ubuntu:22.04')
        project.image_output_name = image_config.get('output', '')
    
    @staticmethod
    def _load_environment_config(stage_data: Dict[str, Any], env: EnvironmentUI) -> None:
        """Load environment configuration from YAML data"""
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
                env.gpu_count = 'all' if gpu_config.get('all', True) else '1'
                env.gpu_memory_limit = gpu_config.get('memory', '')
    
    @staticmethod
    def _load_network_config(stage_data: Dict[str, Any], network: NetworkUI) -> None:
        """Load network configuration from YAML data"""
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
    
    @staticmethod
    def _load_ssh_config(stage_data: Dict[str, Any], ssh: SSHTabUI) -> None:
        """Load SSH configuration from YAML data"""
        ssh_config = stage_data.get('ssh', {})
        if ssh_config:
            ssh.enabled = ssh_config.get('enable', False)
            ssh.port = str(ssh_config.get('port', 22))
            ssh.host_port = str(ssh_config.get('host_port', 2222))
            
            users = ssh_config.get('users', [])
            ssh.users.clear()
            ssh.users.extend(users)
    
    @staticmethod
    def _load_storage_config(stage_data: Dict[str, Any], storage: StorageUI) -> None:
        """Load storage configuration from YAML data"""
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
    
    @staticmethod
    def _load_scripts_config(stage_1_data: Dict[str, Any], stage_2_data: Dict[str, Any],
                           scripts1: ScriptsUI, scripts2: ScriptsUI) -> None:
        """Load scripts configuration from YAML data"""
        # Load entry points
        for stage_num, stage_data, scripts in [(1, stage_1_data, scripts1), 
                                               (2, stage_2_data, scripts2)]:
            entry_point = stage_data.get('entry_point', '')
            if entry_point:
                if ' ' in entry_point:
                    cmd, params = entry_point.split(' ', 1)
                    setattr(scripts, f'stage{stage_num}_entry_mode', 'custom_param')
                    setattr(scripts, f'stage{stage_num}_entry_command', cmd)
                    setattr(scripts, f'stage{stage_num}_entry_params', params)
                else:
                    setattr(scripts, f'stage{stage_num}_entry_mode', 'custom')
                    setattr(scripts, f'stage{stage_num}_entry_command', entry_point)
        
        # Load lifecycle scripts (stage-2 only)
        scripts_config = stage_2_data.get('scripts', {})
        for script_type in ['pre_build', 'post_build', 'first_run', 'every_run', 'user_login']:
            yaml_key = script_type.replace('_', '-')
            if yaml_key in scripts_config:
                scripts_list = getattr(scripts2, script_type)
                scripts_list.clear()
                scripts_list.extend(scripts_config[yaml_key])