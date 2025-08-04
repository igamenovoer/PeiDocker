"""
Network tab for PeiDocker Web GUI.

This tab handles network configuration including proxy settings,
APT repository mirrors, and port mappings.
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab
import re

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class NetworkTab(BaseTab):
    """Network configuration tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.proxy_enabled_switch: Optional[ui.switch] = None
        self.proxy_url_input: Optional[ui.input] = None
        self.apt_mirror_select: Optional[ui.select] = None
        self.port_mappings_container: Optional[ui.column] = None
        self.port_mapping_count: int = 0
        self.port_mappings_data: List[Dict[str, Any]] = []
    
    def render(self) -> ui.element:
        """Render the network tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '🌐 Network Configuration',
                'Configure proxy settings (applied globally to both stages), APT repository mirrors, and port mappings for network connectivity'
            )
            
            # Proxy Configuration
            with self.create_card('🔗 Proxy Configuration'):
                # Get proxy configuration from state
                proxy_config_state = self.app.data.config.stage_1.get('proxy', {})
                
                # Enable proxy toggle
                with ui.row().classes('items-center gap-4 mb-4'):
                    proxy_enabled = proxy_config_state.get('enable_globally', False)
                    self.proxy_enabled_switch = ui.switch('Enable HTTP Proxy', value=proxy_enabled)
                    self.proxy_enabled_switch.on('change', self._on_proxy_toggle)
                
                with ui.column().classes('ml-2') as proxy_config:
                    ui.label('Enable proxy globally for both stages').classes('text-sm text-gray-600 mb-4')
                    
                    # Proxy URL input
                    with self.create_form_group('Proxy URL', 'HTTP proxy URL for network requests'):
                        with ui.row().classes('gap-0'):
                            ui.label('http://').classes('px-3 py-2 bg-gray-100 border border-r-0 rounded-l text-sm')
                            # Combine address and port from config
                            proxy_address = proxy_config_state.get('address', 'host.docker.internal')
                            proxy_port = proxy_config_state.get('port', 7890)
                            proxy_url_value = f"{proxy_address}:{proxy_port}" if proxy_address else ''
                            self.proxy_url_input = ui.input(
                                placeholder='host.docker.internal:7890',
                                value=proxy_url_value
                            ).classes('flex-1 rounded-l-none')
                            self.proxy_url_input.on('input', self._on_proxy_url_change)
                
                proxy_config.bind_visibility_from(self.proxy_enabled_switch, 'value')
            
            # APT Configuration
            with self.create_card('📥 APT Configuration'):
                with self.create_form_group('APT Mirror', 'Choose APT repository mirror for faster package downloads'):
                    # Get APT configuration from state
                    apt_config = self.app.data.config.stage_1.get('apt', {})
                    current_mirror = apt_config.get('repo_source', 'default')
                    # Map empty string to 'default'
                    if current_mirror == '':
                        current_mirror = 'default'
                    
                    self.apt_mirror_select = ui.select(
                        options={
                            'default': 'Default Ubuntu Mirrors',
                            'tuna': 'Tsinghua University (tuna): https://mirrors.tuna.tsinghua.edu.cn/ubuntu/',
                            'aliyun': 'Alibaba Cloud (aliyun): http://mirrors.aliyun.com/ubuntu/',
                            '163': 'NetEase (163): http://mirrors.163.com/ubuntu/',
                            'ustc': 'USTC (ustc): http://mirrors.ustc.edu.cn/ubuntu/',
                            'cn': 'Ubuntu CN Mirror (cn): http://cn.archive.ubuntu.com/ubuntu/'
                        },
                        value=current_mirror
                    ).classes('w-full')
                    self.apt_mirror_select.on('change', self._on_apt_mirror_change)
            
            # Port Mappings
            with self.create_card('🔌 Port Mappings'):
                with self.create_form_group('Additional Port Mappings', 
                                         'Map container ports to host ports (SSH port is configured separately)'):
                    
                    # Warning about port mappings being applied to both stages
                    with ui.card().classes('w-full p-3 mb-4 bg-yellow-50 border-yellow-200'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('warning', color='orange')
                            with ui.column().classes('text-sm'):
                                ui.label('Port mappings will be applied to both stage-1 and stage-2 containers.') \
                                    .classes('text-yellow-800 font-medium')
                                ui.label('For more customization, edit the user_config.yml file directly.') \
                                    .classes('text-yellow-700')
                    
                    # Available port mapping formats
                    with ui.card().classes('w-full p-3 mb-4 bg-gray-50 border-gray-200'):
                        ui.label('Available formats:').classes('text-sm font-medium text-gray-700 mb-2')
                        with ui.column().classes('ml-4 text-sm font-mono'):
                            ui.label('• Single port: 8080:80')
                            ui.label('• Port range: 9090-9099:9090-9099')
                    
                    # Port mappings container
                    with ui.column().classes('w-full mb-4') as mappings_container:
                        self.port_mappings_container = mappings_container
                    
                    # Add port mapping button
                    ui.button('➕ Add Port Mapping', on_click=self._add_port_mapping) \
                        .classes('bg-blue-600 hover:bg-blue-700 text-white')
                    
                    # Info note
                    with ui.card().classes('w-full p-3 mt-4 bg-blue-50 border-blue-200'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('info', color='blue')
                            ui.label('SSH port mapping (2222:22) is configured in the SSH tab.') \
                                .classes('text-blue-800 text-sm')
            
            # Clear existing data since container was cleared
            self.port_mappings_data = []
            self.port_mapping_count = 0
            
            # Reload configuration from current state
            # set_config_data will add example port mapping if none exist
            current_ports = self.app.data.config.stage_1.get('ports', [])
            if not current_ports:
                # Add example port mapping only if no ports configured
                self._add_port_mapping('8080', '80', mark_as_modified=False)
            else:
                # Load existing port mappings
                self.set_config_data({'stage_1': self.app.data.config.stage_1})
        
        return container
    
    def _on_proxy_toggle(self, e: Any) -> None:
        """Handle proxy enable/disable toggle (applied to BOTH stages)."""
        enabled = e.value

        # Ensure proxy section exists for both stages
        for stage_dict in (self.app.data.config.stage_1, self.app.data.config.stage_2):
            if 'proxy' not in stage_dict:
                stage_dict['proxy'] = {}

        # Update both stages with correct key name
        self.app.data.config.stage_1['proxy']['enable_globally'] = enabled
        self.app.data.config.stage_2['proxy']['enable_globally'] = enabled
        self.mark_modified()
    
    def _on_proxy_url_change(self, e: Any) -> None:
        """Handle proxy URL input changes (applied to BOTH stages)."""
        proxy_url = e.value.strip()

        # Ensure proxy section exists for both stages
        for stage_dict in (self.app.data.config.stage_1, self.app.data.config.stage_2):
            if 'proxy' not in stage_dict:
                stage_dict['proxy'] = {}

        url_value = f'http://{proxy_url}' if proxy_url else ''
        self.app.data.config.stage_1['proxy']['url'] = url_value
        self.app.data.config.stage_2['proxy']['url'] = url_value
        self.mark_modified()
    
    def _on_apt_mirror_change(self, e: Any) -> None:
        """Handle APT mirror selection changes (applied to BOTH stages)."""
        mirror = e.value

        # Ensure apt section exists for both stages
        for stage_dict in (self.app.data.config.stage_1, self.app.data.config.stage_2):
            if 'apt' not in stage_dict:
                stage_dict['apt'] = {}

        self.app.data.config.stage_1['apt']['mirror'] = mirror
        self.app.data.config.stage_2['apt']['mirror'] = mirror
        self.mark_modified()
    
    def _add_port_mapping(self, host_port: str = '', container_port: str = '', mark_as_modified: bool = True) -> None:
        """Add a new port mapping configuration."""
        mapping_id = f'port-mapping-{self.port_mapping_count}'
        
        if self.port_mappings_container:
            with self.port_mappings_container:
                with ui.card().classes('w-full p-4 mb-4') as mapping_card:
                    # Mapping header
                    with ui.row().classes('items-center justify-between mb-4'):
                        ui.label(f'🔌 Port Mapping {self.port_mapping_count + 1}').classes('text-lg font-semibold')
                        ui.button('🗑️ Remove', on_click=lambda: self._remove_port_mapping(mapping_card, mapping_id)) \
                            .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                    
                    # Port configuration
                    with ui.row().classes('gap-4 mb-4'):
                        with ui.column().classes('w-full'):
                            ui.label('Host Port').classes('font-medium text-gray-700 mb-1')
                            host_input = ui.input(
                                placeholder='Host port (e.g., 8080 or 9090-9099)',
                                value=host_port
                            ).classes('w-full')
                            host_error = ui.label('').classes('text-red-600 text-sm mt-1 hidden')
                        
                        with ui.column().classes('w-full'):
                            ui.label('Container Port').classes('font-medium text-gray-700 mb-1')
                            container_input = ui.input(
                                placeholder='Container port (e.g., 80 or 9090-9099)',
                                value=container_port
                            ).classes('w-full')
                            container_error = ui.label('').classes('text-red-600 text-sm mt-1 hidden')
                    
                    # Port mapping preview (simplified)
                    preview_label = ui.label('-').classes('font-mono text-sm text-gray-900 font-bold mt-3')
                    
                    # Store mapping data
                    mapping_data = {
                        'id': mapping_id,
                        'host_input': host_input,
                        'container_input': container_input,
                        'host_error': host_error,
                        'container_error': container_error,
                        'preview_label': preview_label,
                        'card': mapping_card
                    }
                    
                    # Add event handlers
                    host_input.on('input', lambda e, data=mapping_data: self._on_port_input_change(e, data, 'host'))
                    container_input.on('input', lambda e, data=mapping_data: self._on_port_input_change(e, data, 'container'))
                    
                    self.port_mappings_data.append(mapping_data)
                    
                    # Update preview if values provided
                    if host_port or container_port:
                        self._update_port_mapping_preview(mapping_data)
        
        self.port_mapping_count += 1
        if mark_as_modified:
            self.mark_modified()
    
    def _remove_port_mapping(self, mapping_card: ui.card, mapping_id: str) -> None:
        """Remove a port mapping configuration."""
        mapping_card.delete()
        
        # Remove from data list
        self.port_mappings_data = [
            data for data in self.port_mappings_data 
            if data['id'] != mapping_id
        ]
        
        self.mark_modified()
    
    def _on_port_input_change(self, e: Any, mapping_data: Dict[str, Any], port_type: str) -> None:
        """Handle port input changes."""
        # Validate the input
        is_valid = self._validate_port_input(mapping_data, port_type)
        
        # Update preview
        self._update_port_mapping_preview(mapping_data)
        
        # Only update config and mark modified if we have valid complete mappings
        host_value = mapping_data['host_input'].value.strip()
        container_value = mapping_data['container_input'].value.strip()
        
        # Only mark as modified if both ports are provided and valid
        if host_value and container_value and is_valid:
            self._update_port_mappings_config()
    
    def _validate_port_input(self, mapping_data: Dict[str, Any], port_type: str) -> bool:
        """Validate port input and show errors."""
        input_field = mapping_data[f'{port_type}_input']
        error_field = mapping_data[f'{port_type}_error']
        value = input_field.value.strip()
        
        if not value:
            error_field.classes(replace='text-red-600 text-sm mt-1 hidden')
            input_field.classes(remove='border-red-500')
            return True
        
        # Validate port or port range
        if '-' in value:
            # Port range validation
            parts = value.split('-')
            if len(parts) != 2:
                self._show_port_error(input_field, error_field, 'Invalid range format. Use: startPort-endPort (e.g., 9090-9099)')
                return False
            
            try:
                start_port = int(parts[0].strip())
                end_port = int(parts[1].strip())
                
                if start_port < 1 or start_port > 65535 or end_port < 1 or end_port > 65535:
                    self._show_port_error(input_field, error_field, 'Port numbers must be between 1 and 65535')
                    return False
                
                if start_port >= end_port:
                    self._show_port_error(input_field, error_field, 'Start port must be less than end port')
                    return False
                
                if end_port - start_port > 1000:
                    self._show_port_error(input_field, error_field, 'Port range too large (max 1000 ports)')
                    return False
                
            except ValueError:
                self._show_port_error(input_field, error_field, 'Range must contain only numbers')
                return False
        else:
            # Single port validation
            try:
                port = int(value)
                if port < 1 or port > 65535:
                    self._show_port_error(input_field, error_field, 'Port must be between 1 and 65535')
                    return False
                
            except ValueError:
                self._show_port_error(input_field, error_field, 'Port must be a number or range (e.g., 8080 or 9090-9099)')
                return False
        
        # Valid input
        error_field.classes(replace='text-red-600 text-sm mt-1 hidden')
        input_field.classes(remove='border-red-500')
        return True
    
    def _show_port_error(self, input_field: ui.input, error_field: ui.label, message: str) -> None:
        """Show port validation error."""
        error_field.set_text(message)
        error_field.classes(replace='text-red-600 text-sm mt-1')
        input_field.classes(add='border-red-500')
    
    def _show_port_warning(self, input_field: ui.input, error_field: ui.label, message: str) -> None:
        """Show port validation warning."""
        error_field.set_text(message)
        error_field.classes(replace='text-yellow-600 text-sm mt-1')
        input_field.classes(remove='border-red-500')
    
    def _validate_matching_ranges(self, mapping_data: Dict[str, Any]) -> bool:
        """Validate that host and container port ranges have matching counts."""
        host_value = mapping_data['host_input'].value.strip()
        container_value = mapping_data['container_input'].value.strip()
        
        # Check if both are ranges
        if '-' in host_value and '-' in container_value:
            try:
                # Parse host range
                host_parts = host_value.split('-')
                host_start = int(host_parts[0].strip())
                host_end = int(host_parts[1].strip())
                host_count = host_end - host_start + 1
                
                # Parse container range
                container_parts = container_value.split('-')
                container_start = int(container_parts[0].strip())
                container_end = int(container_parts[1].strip())
                container_count = container_end - container_start + 1
                
                # Check if counts match
                if host_count != container_count:
                    self._show_port_error(
                        mapping_data['container_input'], 
                        mapping_data['container_error'], 
                        f'Port range count mismatch: host has {host_count} ports, container has {container_count} ports'
                    )
                    return False
            except (ValueError, IndexError):
                # This shouldn't happen as individual validation should catch it
                return False
        
        return True
    
    def _update_port_mapping_preview(self, mapping_data: Dict[str, Any]) -> None:
        """Update the port mapping preview display."""
        host_value = mapping_data['host_input'].value.strip()
        container_value = mapping_data['container_input'].value.strip()
        preview_label = mapping_data['preview_label']
        
        if host_value and container_value:
            # Check if both inputs are valid
            host_valid = self._validate_port_input(mapping_data, 'host')
            container_valid = self._validate_port_input(mapping_data, 'container')
            
            # Additional validation for matching range counts
            ranges_valid = self._validate_matching_ranges(mapping_data)
            
            if host_valid and container_valid and ranges_valid:
                mapping_text = f'"{host_value}:{container_value}"'
                preview_label.set_text(mapping_text)
                preview_label.classes(replace='font-mono text-sm text-green-600 font-bold mt-3')
            else:
                preview_label.set_text('Invalid mapping - check errors above')
                preview_label.classes(replace='font-mono text-sm text-red-600 font-bold mt-3')
        elif host_value or container_value:
            preview_label.set_text('Incomplete mapping - both ports required')
            preview_label.classes(replace='font-mono text-sm text-yellow-600 mt-3')
        else:
            preview_label.set_text('-')
            preview_label.classes(replace='font-mono text-sm text-gray-900 font-bold mt-3')
    
    def _update_port_mappings_config(self, mark_as_modified: bool = True) -> None:
        """Update the port mappings configuration."""
        valid_mappings = []
        
        for mapping_data in self.port_mappings_data:
            host_value = mapping_data['host_input'].value.strip()
            container_value = mapping_data['container_input'].value.strip()
            
            if host_value and container_value:
                host_valid = self._validate_port_input(mapping_data, 'host')
                container_valid = self._validate_port_input(mapping_data, 'container')
                ranges_valid = self._validate_matching_ranges(mapping_data)
                
                if host_valid and container_valid and ranges_valid:
                    valid_mappings.append(f'{host_value}:{container_value}')
        
        # Update configuration
        # Ensure ports array exists for both stages
        for stage_dict in (self.app.data.config.stage_1, self.app.data.config.stage_2):
            if 'ports' not in stage_dict:
                stage_dict['ports'] = []

        # Check if the ports actually changed
        current_ports = self.app.data.config.stage_1.get('ports', [])
        if valid_mappings != current_ports or not hasattr(self, '_ports_initialized'):
            self.app.data.config.stage_1['ports'] = valid_mappings
            self.app.data.config.stage_2['ports'] = valid_mappings
            if mark_as_modified and hasattr(self, '_ports_initialized'):
                self.mark_modified()
            self._ports_initialized = True
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate network configuration."""
        errors = []
        
        # Validate proxy configuration
        if self.proxy_enabled_switch and self.proxy_enabled_switch.value:
            if not self.proxy_url_input or not self.proxy_url_input.value.strip():
                errors.append("Proxy URL is required when proxy is enabled")
        
        # Validate port mappings
        for i, mapping_data in enumerate(self.port_mappings_data):
            host_value = mapping_data['host_input'].value.strip()
            container_value = mapping_data['container_input'].value.strip()
            
            if host_value or container_value:
                if not host_value or not container_value:
                    errors.append(f"Port mapping {i+1}: Both host and container ports are required")
                else:
                    if not self._validate_port_input(mapping_data, 'host'):
                        errors.append(f"Port mapping {i+1}: Invalid host port")
                    if not self._validate_port_input(mapping_data, 'container'):
                        errors.append(f"Port mapping {i+1}: Invalid container port")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> dict:
        """Get network configuration data from current UI state."""
        # Build proxy configuration from UI state
        proxy_config = {}
        if self.proxy_enabled_switch:
            proxy_config['enable_globally'] = self.proxy_enabled_switch.value
            if self.proxy_url_input and self.proxy_enabled_switch.value:
                url = self.proxy_url_input.value.strip()
                if url:
                    # Parse proxy URL to extract address and port
                    import re
                    match = re.match(r'(?:https?://)?([^:]+):(\d+)', url)
                    if match:
                        proxy_config['address'] = match.group(1)
                        proxy_config['port'] = int(match.group(2))
                        proxy_config['use_https'] = url.startswith('https://')
        
        # Build APT configuration
        apt_config = self.app.data.config.stage_1.get('apt', {})
        if self.apt_mirror_select:
            apt_config['mirror'] = self.apt_mirror_select.value
        
        # Build ports configuration from UI
        ports = []
        for mapping_data in self.port_mappings_data:
            host_port = mapping_data['host_input'].value.strip()
            container_port = mapping_data['container_input'].value.strip()
            if host_port and container_port:
                ports.append(f"{host_port}:{container_port}")
        
        return {
            'stage_1': {
                'proxy': proxy_config,
                'apt': apt_config,
                'ports': ports
            },
            'stage_2': {
                'proxy': proxy_config  # Same proxy config for both stages
            }
        }
    
    def set_config_data(self, data: dict) -> None:
        """Set network configuration data merging stage-1 & stage-2 (stage-2 overrides)."""
        stage_1_config = data.get('stage_1', {})
        stage_2_config = data.get('stage_2', {})

        # ---------- helpers ----------
        def _merge_dict(a: dict, b: dict) -> dict:
            """Return shallow merged dict where b overrides a."""
            merged = dict(a)
            merged.update(b)
            return merged

        # ---------- proxy ------------
        proxy_cfg = _merge_dict(stage_1_config.get('proxy', {}), stage_2_config.get('proxy', {}))
        if self.proxy_enabled_switch:
            self.proxy_enabled_switch.set_value(proxy_cfg.get('enable_globally', False))

        if self.proxy_url_input:
            proxy_url = proxy_cfg.get('url', '')
            if proxy_url.startswith('http://'):
                proxy_url = proxy_url[len('http://'):]
            self.proxy_url_input.set_value(proxy_url)

        # ---------- apt mirror -------
        apt_cfg = _merge_dict(stage_1_config.get('apt', {}), stage_2_config.get('apt', {}))
        if self.apt_mirror_select:
            self.apt_mirror_select.set_value(apt_cfg.get('mirror', 'default'))

        # ---------- ports ------------
        combined_ports: list[str] = []
        for p in stage_1_config.get('ports', []):
            if p not in combined_ports:
                combined_ports.append(p)
        for p in stage_2_config.get('ports', []):
            if p not in combined_ports:
                combined_ports.append(p)

        # Reset UI container
        if self.port_mappings_container:
            self.port_mappings_container.clear()
            self.port_mappings_data = []
            self.port_mapping_count = 0

        for port_mapping in combined_ports:
            if ':' in port_mapping:
                host_port, container_port = port_mapping.split(':', 1)
                self._add_port_mapping(host_port, container_port, mark_as_modified=False)