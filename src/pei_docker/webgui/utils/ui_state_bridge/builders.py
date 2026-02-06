"""
Builders for creating configuration structures from UI state.
"""

from typing import Dict, List, Any, Optional
import uuid

from pei_docker.webgui.constants import (
    CustomScriptLifecycleTypes,
    ScriptTypes,
    DeviceTypes
)
from pei_docker.user_config import (
    ImageConfig as AttrsImageConfig,
    SSHConfig as AttrsSSHConfig,
    SSHUserConfig as AttrsSSHUserConfig,
    ProxyConfig as AttrsProxyConfig,
    AptConfig as AttrsAptConfig,
    DeviceConfig as AttrsDeviceConfig,
    CustomScriptConfig as AttrsCustomScriptConfig,
    StorageOption as AttrsStorageOption,
    StorageTypes
)
from pei_docker.webgui.utils.ui_state_bridge.stage_processor import StageProcessor
from pei_docker.webgui.utils.ui_state_bridge.utils import parse_proxy_url


class ConfigBuilder:
    """Builds configuration objects from UI state."""
    
    @staticmethod
    def build_image_config(
        ui_project: Any,
        stage_num: int
    ) -> Optional[AttrsImageConfig]:
        """Build image configuration for a stage.
        
        Args:
            ui_project: ProjectUI object
            stage_num: Stage number (1 or 2)
            
        Returns:
            AttrsImageConfig object or None
        """
        output_name = ui_project.image_output_name or ui_project.project_name or "pei-image"
        
        if stage_num == 1:
            return AttrsImageConfig(
                base=ui_project.base_image or "ubuntu:22.04",
                output=f"{output_name}:stage-1"
            )
        else:
            # Stage 2 only needs output name
            return AttrsImageConfig(
                output=f"{output_name}:stage-2"
            )
    
    @staticmethod
    def build_ssh_config(
        ui_ssh: Any,
        enabled: bool
    ) -> Optional[AttrsSSHConfig]:
        """Build SSH configuration from UI state.
        
        Args:
            ui_ssh: SSHTabUI object
            enabled: Whether SSH is enabled
            
        Returns:
            AttrsSSHConfig object or None
        """
        if not enabled:
            return None
        
        users = {}
        for user_data in ui_ssh.users:
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
        ssh_port = StageProcessor.handle_port_value(ui_ssh.port, 22)
        ssh_host_port = StageProcessor.handle_port_value(ui_ssh.host_port, 2222)
        
        return AttrsSSHConfig(
            enable=enabled,
            port=ssh_port,
            host_port=ssh_host_port,
            users=users
        )
    
    @staticmethod
    def build_proxy_config(
        proxy_enabled: bool,
        http_proxy: str
    ) -> Optional[AttrsProxyConfig]:
        """Build proxy configuration from UI state.
        
        Args:
            proxy_enabled: Whether proxy is enabled
            http_proxy: HTTP proxy URL
            
        Returns:
            AttrsProxyConfig object or None
        """
        if not proxy_enabled or not http_proxy:
            return None
        
        address, port, use_https = parse_proxy_url(http_proxy)
        
        return AttrsProxyConfig(
            address=address,
            port=port,
            enable_globally=True,
            remove_after_build=False,
            use_https=use_https
        )
    
    @staticmethod
    def build_apt_config(
        apt_mirror: str,
        has_proxy: bool
    ) -> Optional[AttrsAptConfig]:
        """Build APT configuration from UI state.
        
        Args:
            apt_mirror: APT mirror URL
            has_proxy: Whether proxy is configured
            
        Returns:
            AttrsAptConfig object or None
        """
        if not apt_mirror:
            return None
        
        return AttrsAptConfig(
            repo_source=apt_mirror,
            keep_repo_after_build=True,
            use_proxy=has_proxy,
            keep_proxy_after_build=False
        )
    
    @staticmethod
    def build_device_config(device_type: str) -> Optional[AttrsDeviceConfig]:
        """Build device configuration from UI state.
        
        Args:
            device_type: Device type string
            
        Returns:
            AttrsDeviceConfig object or None
        """
        if device_type == DeviceTypes.CPU:
            return None
        return AttrsDeviceConfig(type=device_type)
    
    @staticmethod
    def build_port_mappings(port_mappings: List[Dict[str, str]]) -> Optional[List[str]]:
        """Build port mappings list from UI state.
        
        Args:
            port_mappings: List of port mapping dictionaries
            
        Returns:
            List of port mapping strings or None
        """
        if not port_mappings:
            return None
        
        # Filter out empty port mappings
        valid_ports = [
            f"{m['host']}:{m['container']}" 
            for m in port_mappings
            if m.get('host', '').strip() and m.get('container', '').strip()
        ]
        
        return valid_ports if valid_ports else None
    
    @staticmethod
    def build_custom_scripts(ui_scripts: Any) -> Optional[AttrsCustomScriptConfig]:
        """Build custom scripts configuration from UI state.
        
        Args:
            ui_scripts: ScriptsUI object
            
        Returns:
            AttrsCustomScriptConfig object or None
        """
        on_entry = []
        
        # Handle entry point
        if ui_scripts.entry_mode == "file" and ui_scripts.entry_file_path:
            on_entry.append(ui_scripts.entry_file_path)
        elif ui_scripts.entry_mode == "inline" and ui_scripts.entry_inline_name:
            # For inline scripts, use the proper path that will be written to disk
            on_entry.append(f"/pei-docker/scripts/{ui_scripts.entry_inline_name}")
        
        # Extract lifecycle scripts using StageProcessor
        lifecycle_scripts = ui_scripts.lifecycle_scripts
        
        on_build = StageProcessor.process_lifecycle_scripts(
            lifecycle_scripts,
            CustomScriptLifecycleTypes.ON_BUILD,
            lambda data: StageProcessor.extract_script_path(data)
        )
        
        on_first_run = StageProcessor.process_lifecycle_scripts(
            lifecycle_scripts,
            CustomScriptLifecycleTypes.ON_FIRST_RUN,
            lambda data: StageProcessor.extract_script_path(data)
        )
        
        on_every_run = StageProcessor.process_lifecycle_scripts(
            lifecycle_scripts,
            CustomScriptLifecycleTypes.ON_EVERY_RUN,
            lambda data: StageProcessor.extract_script_path(data)
        )
        
        on_user_login = StageProcessor.process_lifecycle_scripts(
            lifecycle_scripts,
            CustomScriptLifecycleTypes.ON_USER_LOGIN,
            lambda data: StageProcessor.extract_script_path(data)
        )
        
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
    
    @staticmethod
    def build_storage_config(ui_storage: Any) -> Dict[str, AttrsStorageOption]:
        """Build storage configuration from UI state.
        
        Args:
            ui_storage: StorageUI object
            
        Returns:
            Dictionary of storage options
        """
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
    
    @staticmethod
    def build_mount_config(ui_storage: Any) -> Dict[str, AttrsStorageOption]:
        """Build mount configuration from UI state.
        
        Args:
            ui_storage: StorageUI object
            
        Returns:
            Dictionary of mount options
        """
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