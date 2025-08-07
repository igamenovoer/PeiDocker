"""
Network tab for PeiDocker Web GUI - Refactored with data binding.

This tab handles network configuration including proxy settings,
APT repository mirrors, and port mappings using NiceGUI's data binding.
"""

from typing import TYPE_CHECKING, Optional, List, Dict, Any
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab
import re

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class NetworkTab(BaseTab):
    """Network configuration tab with data binding."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.stage1_port_mappings_container: Optional[ui.column] = None
        self.stage2_port_mappings_container: Optional[ui.column] = None
        self.stage1_port_mapping_rows: List[Dict[str, Any]] = []
        self.stage2_port_mapping_rows: List[Dict[str, Any]] = []
    
    def render(self) -> ui.element:
        """Render the network tab content with data binding."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '🌐 Network Configuration',
                'Configure proxy settings (applied globally to both stages), APT repository mirrors, and port mappings for network connectivity'
            )
            
            # Get network UI states for both stages
            network_1 = self.app.ui_state.stage_1.network
            network_2 = self.app.ui_state.stage_2.network
            
            # Proxy Configuration
            with self.create_card('🔗 Proxy Configuration'):
                # Enable proxy toggle - bound to both stages
                with ui.row().classes('items-center gap-4 mb-4'):
                    proxy_switch = ui.switch('Enable HTTP Proxy').bind_value(network_1, 'proxy_enabled')
                    # Also bind stage 2 to keep in sync
                    proxy_switch.bind_value(network_2, 'proxy_enabled')
                
                with ui.column().classes('ml-2') as proxy_config:
                    proxy_config.bind_visibility_from(network_1, 'proxy_enabled')
                    
                    ui.label('Enable proxy globally for both stages').classes('text-sm text-gray-600 mb-4')
                    
                    # HTTP Proxy URL
                    with self.create_form_group('HTTP Proxy', 'HTTP proxy URL for both HTTP and HTTPS requests'):
                        http_input = ui.input(
                            placeholder='http://host.docker.internal:7890'
                        ).classes('w-full').bind_value(network_1, 'http_proxy') \
                        .props('data-testid="http-proxy-input"')
                        # Keep stage 2 in sync
                        http_input.bind_value(network_2, 'http_proxy')
                        
                        # Info note about proxy usage
                        ui.label('This proxy will be used for both HTTP and HTTPS protocols').classes('text-sm text-gray-600 mt-2')
            
            # APT Configuration
            with self.create_card('📥 APT Configuration'):
                with self.create_form_group('APT Mirror', 'Choose APT repository mirror for faster package downloads'):
                    apt_select = ui.select(
                        options={
                            '': 'Default Ubuntu Mirrors',
                            'https://mirrors.tuna.tsinghua.edu.cn/ubuntu/': 'Tsinghua University (tuna)',
                            'http://mirrors.aliyun.com/ubuntu/': 'Alibaba Cloud (aliyun)',
                            'http://mirrors.163.com/ubuntu/': 'NetEase (163)',
                            'http://mirrors.ustc.edu.cn/ubuntu/': 'USTC',
                            'http://cn.archive.ubuntu.com/ubuntu/': 'Ubuntu CN Mirror'
                        },
                        value=''
                    ).classes('w-full').bind_value(network_1, 'apt_mirror')
                    # Keep stage 2 in sync
                    apt_select.bind_value(network_2, 'apt_mirror')
            
            # Port Mappings - Now separated by stage
            with self.create_card('🔌 Port Mappings'):
                # Info about separate port mappings
                with ui.card().classes('w-full p-3 mb-4 bg-blue-50 border-blue-200'):
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('info', color='blue')
                        with ui.column().classes('text-sm'):
                            ui.label('Port mappings can now be configured separately for each stage.') \
                                .classes('text-blue-800 font-medium')
                            ui.label('Stage-1 is for system-level services, Stage-2 is for application-level services.') \
                                .classes('text-blue-700')
                            ui.label('SSH port mapping (2222:22) is configured in the SSH tab.') \
                                .classes('text-blue-700')
                
                # Available port mapping formats
                with ui.card().classes('w-full p-3 mb-4 bg-gray-50 border-gray-200'):
                    ui.label('Available formats:').classes('text-sm font-medium text-gray-700 mb-2')
                    with ui.column().classes('ml-4 text-sm font-mono'):
                        ui.label('• Single port: 8080:80')
                        ui.label('• Port range: 9090-9099:9090-9099')
                
                # Create tabs for stage-1 and stage-2 port mappings
                with ui.tabs() as tabs:
                    stage1_tab = ui.tab('Stage-1 Ports')
                    stage2_tab = ui.tab('Stage-2 Ports')
                
                with ui.tab_panels(tabs, value=stage1_tab).classes('w-full'):
                    # Stage-1 Port Mappings
                    with ui.tab_panel(stage1_tab):
                        with self.create_form_group('Stage-1 Port Mappings', 
                                                 'Map container ports to host ports for system-level services'):
                            # Stage-1 port mappings container
                            with ui.column().classes('w-full mb-4') as stage1_mappings_container:
                                self.stage1_port_mappings_container = stage1_mappings_container
                                self._render_stage1_port_mappings()
                            
                            # Add port mapping button for stage-1
                            ui.button('➕ Add Stage-1 Port Mapping', on_click=self._add_stage1_port_mapping) \
                                .classes('bg-blue-600 hover:bg-blue-700 text-white') \
                                .props('data-testid="add-stage1-port-mapping-btn"')
                    
                    # Stage-2 Port Mappings
                    with ui.tab_panel(stage2_tab):
                        with self.create_form_group('Stage-2 Port Mappings', 
                                                 'Map container ports to host ports for application-level services'):
                            # Stage-2 port mappings container
                            with ui.column().classes('w-full mb-4') as stage2_mappings_container:
                                self.stage2_port_mappings_container = stage2_mappings_container
                                self._render_stage2_port_mappings()
                            
                            # Add port mapping button for stage-2
                            ui.button('➕ Add Stage-2 Port Mapping', on_click=self._add_stage2_port_mapping) \
                                .classes('bg-blue-600 hover:bg-blue-700 text-white') \
                                .props('data-testid="add-stage2-port-mapping-btn"')
        
        return container
    
    def _render_stage1_port_mappings(self) -> None:
        """Render port mappings for stage-1."""
        if not self.stage1_port_mappings_container:
            return
        
        # Clear existing UI elements
        self.stage1_port_mappings_container.clear()
        self.stage1_port_mapping_rows.clear()
        
        # Get the port mappings from stage-1 network state
        network = self.app.ui_state.stage_1.network
        
        # Render each port mapping
        for i, mapping in enumerate(network.port_mappings):
            self._create_port_mapping_row(i, mapping, 'stage1')
    
    def _render_stage2_port_mappings(self) -> None:
        """Render port mappings for stage-2."""
        if not self.stage2_port_mappings_container:
            return
        
        # Clear existing UI elements
        self.stage2_port_mappings_container.clear()
        self.stage2_port_mapping_rows.clear()
        
        # Get the port mappings from stage-2 network state
        network = self.app.ui_state.stage_2.network
        
        # Render each port mapping
        for i, mapping in enumerate(network.port_mappings):
            self._create_port_mapping_row(i, mapping, 'stage2')
    
    def _create_port_mapping_row(self, index: int, mapping: Dict[str, str], stage: str) -> None:
        """Create a single port mapping row with data binding.
        
        Args:
            index: Index of the mapping in the list
            mapping: Port mapping dictionary with 'host' and 'container' keys
            stage: Either 'stage1' or 'stage2' to identify which stage this mapping belongs to
        """
        container = self.stage1_port_mappings_container if stage == 'stage1' else self.stage2_port_mappings_container
        row_list = self.stage1_port_mapping_rows if stage == 'stage1' else self.stage2_port_mapping_rows
        
        if not container:
            return
        
        with container:
            with ui.card().classes('w-full p-4 mb-4') as mapping_card:
                # Mapping header
                with ui.row().classes('items-center justify-between mb-4'):
                    stage_label = 'Stage-1' if stage == 'stage1' else 'Stage-2'
                    ui.label(f'🔌 {stage_label} Port Mapping {index + 1}').classes('text-lg font-semibold')
                    ui.button('🗑️ Remove', 
                             on_click=lambda idx=index, s=stage: self._remove_port_mapping(idx, s)) \
                        .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                
                # Port configuration
                with ui.row().classes('gap-4 mb-4'):
                    with ui.column().classes('w-full'):
                        ui.label('Host Port').classes('font-medium text-gray-700 mb-1')
                        host_input = ui.input(
                            placeholder='Host port (e.g., 8080 or 9090-9099)'
                        ).classes('w-full').props(f'data-testid="port-mapping-{stage}-host-{index}"')
                        host_input.set_value(mapping.get('host', ''))
                        host_error = ui.label('').classes('text-red-600 text-sm mt-1 hidden')
                    
                    with ui.column().classes('w-full'):
                        ui.label('Container Port').classes('font-medium text-gray-700 mb-1')
                        container_input = ui.input(
                            placeholder='Container port (e.g., 80 or 9090-9099)'
                        ).classes('w-full').props(f'data-testid="port-mapping-{stage}-container-{index}"')
                        container_input.set_value(mapping.get('container', ''))
                        container_error = ui.label('').classes('text-red-600 text-sm mt-1 hidden')
                
                # Port mapping preview
                preview_label = ui.label('-').classes('font-mono text-sm text-gray-900 font-bold mt-3')
                
                # Store row data
                row_data = {
                    'index': index,
                    'stage': stage,
                    'host_input': host_input,
                    'container_input': container_input,
                    'host_error': host_error,
                    'container_error': container_error,
                    'preview_label': preview_label,
                    'card': mapping_card,
                    'mapping': mapping
                }
                row_list.append(row_data)
                
                # Update mapping on input changes
                def update_mapping(e: Any, field: str, data: Dict[str, Any] = row_data) -> None:
                    data['mapping'][field] = e.value
                    self._validate_and_update_preview(data)
                    # Mark as modified
                    self.app.ui_state.mark_modified()
                
                host_input.on_value_change(lambda e: update_mapping(e, 'host'))
                container_input.on_value_change(lambda e: update_mapping(e, 'container'))
                
                # Initial validation and preview
                self._validate_and_update_preview(row_data)
    
    def _add_stage1_port_mapping(self) -> None:
        """Add a new port mapping to stage-1."""
        new_mapping = {'host': '', 'container': ''}
        self.app.ui_state.stage_1.network.port_mappings.append(new_mapping)
        
        # Create the UI row
        index = len(self.app.ui_state.stage_1.network.port_mappings) - 1
        self._create_port_mapping_row(index, new_mapping, 'stage1')
        
        # Mark as modified
        self.app.ui_state.mark_modified()
    
    def _add_stage2_port_mapping(self) -> None:
        """Add a new port mapping to stage-2."""
        new_mapping = {'host': '', 'container': ''}
        self.app.ui_state.stage_2.network.port_mappings.append(new_mapping)
        
        # Create the UI row
        index = len(self.app.ui_state.stage_2.network.port_mappings) - 1
        self._create_port_mapping_row(index, new_mapping, 'stage2')
        
        # Mark as modified
        self.app.ui_state.mark_modified()
    
    def _remove_port_mapping(self, index: int, stage: str) -> None:
        """Remove a port mapping from the specified stage.
        
        Args:
            index: Index of the mapping to remove
            stage: Either 'stage1' or 'stage2'
        """
        if stage == 'stage1':
            if index < len(self.app.ui_state.stage_1.network.port_mappings):
                self.app.ui_state.stage_1.network.port_mappings.pop(index)
            # Re-render stage-1 mappings to update indices
            self._render_stage1_port_mappings()
        else:  # stage2
            if index < len(self.app.ui_state.stage_2.network.port_mappings):
                self.app.ui_state.stage_2.network.port_mappings.pop(index)
            # Re-render stage-2 mappings to update indices
            self._render_stage2_port_mappings()
        
        # Mark as modified
        self.app.ui_state.mark_modified()
    
    def _validate_and_update_preview(self, row_data: Dict[str, Any]) -> None:
        """Validate port mapping and update preview."""
        host_value = row_data['mapping'].get('host', '').strip()
        container_value = row_data['mapping'].get('container', '').strip()
        preview_label = row_data['preview_label']
        
        # Validate ports
        host_valid = self._validate_port(host_value, row_data['host_input'], row_data['host_error'])
        container_valid = self._validate_port(container_value, row_data['container_input'], row_data['container_error'])
        
        # Update preview
        if host_value and container_value and host_valid and container_valid:
            preview_label.set_text(f'"{host_value}:{container_value}"')
            preview_label.classes(replace='font-mono text-sm text-green-600 font-bold mt-3')
        elif host_value or container_value:
            preview_label.set_text('Incomplete mapping - both ports required')
            preview_label.classes(replace='font-mono text-sm text-yellow-600 mt-3')
        else:
            preview_label.set_text('-')
            preview_label.classes(replace='font-mono text-sm text-gray-900 font-bold mt-3')
    
    def _validate_port(self, value: str, input_field: ui.input, error_field: ui.label) -> bool:
        """Validate a port value."""
        if not value:
            error_field.classes(replace='text-red-600 text-sm mt-1 hidden')
            input_field.classes(remove='border-red-500')
            return True
        
        # Validate port or port range
        if '-' in value:
            # Port range validation
            parts = value.split('-')
            if len(parts) != 2:
                self._show_error(input_field, error_field, 'Invalid range format. Use: startPort-endPort')
                return False
            
            try:
                start_port = int(parts[0].strip())
                end_port = int(parts[1].strip())
                
                if not (1 <= start_port <= 65535) or not (1 <= end_port <= 65535):
                    self._show_error(input_field, error_field, 'Port numbers must be between 1 and 65535')
                    return False
                
                if start_port >= end_port:
                    self._show_error(input_field, error_field, 'Start port must be less than end port')
                    return False
                
            except ValueError:
                self._show_error(input_field, error_field, 'Range must contain only numbers')
                return False
        else:
            # Single port validation
            try:
                port = int(value)
                if not (1 <= port <= 65535):
                    self._show_error(input_field, error_field, 'Port must be between 1 and 65535')
                    return False
            except ValueError:
                self._show_error(input_field, error_field, 'Port must be a number')
                return False
        
        # Valid
        error_field.classes(replace='text-red-600 text-sm mt-1 hidden')
        input_field.classes(remove='border-red-500')
        return True
    
    def _show_error(self, input_field: ui.input, error_field: ui.label, message: str) -> None:
        """Show validation error."""
        error_field.set_text(message)
        error_field.classes(replace='text-red-600 text-sm mt-1')
        input_field.classes(add='border-red-500')
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate network configuration."""
        errors = []
        
        # Get network states for both stages
        network_1 = self.app.ui_state.stage_1.network
        network_2 = self.app.ui_state.stage_2.network
        
        # Validate proxy configuration (same for both stages)
        if network_1.proxy_enabled:
            if not network_1.http_proxy:
                errors.append("HTTP proxy URL is required when proxy is enabled")
            
            # Validate proxy URL
            if network_1.http_proxy and not network_1.http_proxy.startswith(('http://', 'https://', 'socks5://')):
                errors.append("HTTP proxy URL must start with http://, https://, or socks5://")
        
        # Validate stage-1 port mappings
        for i, mapping in enumerate(network_1.port_mappings):
            host = mapping.get('host', '').strip()
            container = mapping.get('container', '').strip()
            
            if host or container:
                if not host or not container:
                    errors.append(f"Stage-1 port mapping {i+1}: Both host and container ports are required")
        
        # Validate stage-2 port mappings
        for i, mapping in enumerate(network_2.port_mappings):
            host = mapping.get('host', '').strip()
            container = mapping.get('container', '').strip()
            
            if host or container:
                if not host or not container:
                    errors.append(f"Stage-2 port mapping {i+1}: Both host and container ports are required")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get network configuration data from UI state."""
        # This is now handled by the UIStateBridge
        # Keeping method for compatibility
        return {}
    
    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set network configuration data."""
        # This is now handled by the UIStateBridge during load
        # UI state is automatically bound, so we just need to refresh the view
        if self.stage1_port_mappings_container:
            self._render_stage1_port_mappings()
        if self.stage2_port_mappings_container:
            self._render_stage2_port_mappings()