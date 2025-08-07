"""
Storage tab for PeiDocker Web GUI - Refactored with data binding.

This tab handles Storage (Stage-2's dynamic system) and Mounts (general volume mounts) 
for both stages using NiceGUI's data binding.
"""

from typing import TYPE_CHECKING, Dict, List, Tuple, Optional, Any
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab
import uuid

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class StorageTab(BaseTab):
    """Storage configuration tab with data binding."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        # Containers for dynamic mount entries
        self.stage1_mounts_container: Optional[ui.column] = None
        self.stage2_mounts_container: Optional[ui.column] = None
    
    def render(self) -> ui.element:
        """Render the storage tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '💾 Storage Configuration',
                'Configure Storage (Stage-2\'s dynamic system) and Mounts (general volume mounts) for both stages'
            )
            
            # Key concepts info
            with ui.card().classes('w-full p-4 mb-6 bg-blue-50 border-blue-200'):
                with ui.row().classes('items-start gap-2'):
                    ui.icon('info', color='blue').classes('mt-1')
                    with ui.column().classes('w-full'):
                        ui.label('📋 Key Concepts:').classes('font-semibold text-blue-800 mb-2')
                        ui.markdown("""**Storage** is Stage-2's unique dynamic system for predefined directories (/soft/app, /soft/data, /soft/workspace).
**Mounts** are general volume mounts that can be defined for any container path.

These 3 storage entries are always present and default to 'image' type even when omitted from user_config.yml. They cannot be created or removed - only their storage type and related options can be configured.""").classes('text-blue-700 text-sm')
            
            # Stage-2 Dynamic Storage System
            with self.create_card('🏗️ Stage-2 Dynamic Storage System (Stage-2 ONLY)'):
                ui.label('Stage-2\'s unique dynamic storage for predefined directories with smart linking: /soft/xxx → /hard/volume/xxx OR /hard/image/xxx') \
                    .classes('text-gray-600 mb-4')
                
                # Get storage UI state for stage-2
                storage_ui = self.app.ui_state.stage_2.storage
                
                # Create the three fixed storage entries with data binding
                self._create_storage_entry(storage_ui, 'app', '📱 App Storage (/soft/app)', 'Application files and dependencies - Fixed destination')
                self._create_storage_entry(storage_ui, 'data', '💾 Data Storage (/soft/data)', 'User data and persistent files - Fixed destination')
                self._create_storage_entry(storage_ui, 'workspace', '🛠️ Workspace Storage (/soft/workspace)', 'Development and workspace files - Fixed destination')
            
            # Stage-1 Mounts
            with self.create_card('🗂️ Stage-1 Mounts (General Volume Mounts)'):
                with self.create_form_group('Stage-1 Volume Mounts', 'General volume mounts for Stage-1 image (any paths, user-defined)'):
                    
                    # Mounts container
                    with ui.column().classes('w-full mb-4') as stage1_container:
                        self.stage1_mounts_container = stage1_container
                        self._render_mounts('stage1')
                    
                    # Add mount button
                    ui.button('➕ Add mount', on_click=lambda: self._add_mount('stage1')) \
                        .classes('bg-blue-600 hover:bg-blue-700 text-white')
            
            # Stage-2 Mounts
            with self.create_card('🗂️ Stage-2 Mounts (General Volume Mounts)'):
                with self.create_form_group('Stage-2 Volume Mounts', 'General volume mounts for Stage-2 image (any paths, user-defined). Stage-2 mounts don\'t inherit from Stage-1.'):
                    
                    # Mounts container
                    with ui.column().classes('w-full mb-4') as stage2_container:
                        self.stage2_mounts_container = stage2_container
                        self._render_mounts('stage2')
                    
                    # Add mount button
                    ui.button('➕ Add mount', on_click=lambda: self._add_mount('stage2')) \
                        .classes('bg-blue-600 hover:bg-blue-700 text-white')
        
        return container
    
    def _create_storage_entry(self, storage_ui: Any, storage_type: str, title: str, description: str) -> None:
        """Create a storage entry for the Stage-2 dynamic storage system with data binding."""
        with ui.card().classes('w-full p-4 mb-4'):
            ui.label(title).classes('text-lg font-semibold mb-2')
            ui.label(description).classes('text-gray-600 mb-4')
            
            # Storage type descriptions
            type_descriptions = {
                'auto-volume': 'Docker creates a volume automatically',
                'manual-volume': 'Use an existing Docker volume',
                'host': 'Bind mount from host filesystem',
                'image': 'Store directly in the container image (not persistent)'
            }
            
            # Create reactive description label
            desc_label = ui.label('').classes('text-sm text-gray-600 italic')
            
            # Update description based on selected type
            def update_description() -> None:
                current_type = getattr(storage_ui, f'{storage_type}_storage_type')
                desc_label.set_text(f"ℹ️ {type_descriptions.get(current_type, '')}")
            
            # Three-column grid for storage configuration
            with ui.row().classes('gap-4 w-full'):
                # Storage Type
                with ui.column().classes('w-full'):
                    ui.label('Storage type:').classes('font-medium text-gray-700 mb-1')
                    ui.select(
                        options={
                            'auto-volume': 'auto-volume',
                            'manual-volume': 'manual-volume',
                            'host': 'host',
                            'image': 'image'
                        },
                        on_change=lambda: update_description()
                    ).bind_value(storage_ui, f'{storage_type}_storage_type').classes('w-full')
                
                # Volume Name (conditional)
                with ui.column().classes('w-full'):
                    ui.label('Volume name:').classes('font-medium text-gray-700 mb-1')
                    volume_input = ui.input(
                        placeholder=f'Volume name for {storage_type}'
                    ).bind_value(storage_ui, f'{storage_type}_volume_name').classes('w-full')
                    # Show only when manual-volume is selected
                    volume_input.bind_visibility_from(
                        storage_ui, 
                        f'{storage_type}_storage_type',
                        lambda t: t == 'manual-volume'
                    )
                
                # Host Path (conditional)
                with ui.column().classes('w-full'):
                    ui.label('Host path:').classes('font-medium text-gray-700 mb-1')
                    host_input = ui.input(
                        placeholder=f'Host path for {storage_type}'
                    ).bind_value(storage_ui, f'{storage_type}_host_path').classes('w-full')
                    # Show only when host is selected
                    host_input.bind_visibility_from(
                        storage_ui,
                        f'{storage_type}_storage_type', 
                        lambda t: t == 'host'
                    )
            
            # Display description below the form
            with ui.row().classes('mt-3'):
                desc_label
                
            # Initial update
            update_description()
    
    def _render_mounts(self, stage: str) -> None:
        """Render mount entries for a specific stage."""
        # Get the appropriate storage UI and container
        storage_ui = self.app.ui_state.stage_1.storage if stage == 'stage1' else self.app.ui_state.stage_2.storage
        container = self.stage1_mounts_container if stage == 'stage1' else self.stage2_mounts_container
        
        if container:
            container.clear()
            
            # Render existing mounts
            for i, mount in enumerate(storage_ui.mounts):
                self._create_mount_row(storage_ui, i, mount, container)
    
    def _create_mount_row(self, storage_ui: Any, index: int, mount: Dict[str, str], container: ui.column) -> None:
        """Create a single mount row with data binding."""
        # Ensure mount has an id (for future use if needed)
        if 'id' not in mount:
            mount['id'] = str(uuid.uuid4())
        
        with container:
            with ui.card().classes('w-full p-4 mb-3'):
                # Mount header with remove button
                with ui.row().classes('items-center justify-between mb-3'):
                    ui.label(f'Mount {index + 1}').classes('font-semibold')
                    ui.button(icon='delete', on_click=lambda idx=index, s_ui=storage_ui: self._remove_mount(s_ui, idx)) \
                        .classes('text-red-600 hover:text-red-700').props('flat')
                
                # Mount configuration
                with ui.grid(columns=3).classes('gap-4 w-full'):
                    # Mount Type
                    with ui.column():
                        ui.label('Type:').classes('font-medium text-gray-700 mb-1')
                        ui.select(
                            options={
                                'auto-volume': 'Auto Volume',
                                'manual-volume': 'Manual Volume',
                                'host': 'Host Path'
                            },
                            value=mount.get('type', 'auto-volume')
                        ).classes('w-full').on('value-change', 
                            lambda e, idx=index, s_ui=storage_ui: self._update_mount_field(s_ui, idx, 'type', e.value))
                    
                    # Container Path
                    with ui.column():
                        ui.label('Container path:').classes('font-medium text-gray-700 mb-1')
                        ui.input(
                            placeholder='/path/in/container',
                            value=mount.get('container_path', '')
                        ).classes('w-full').on('value-change',
                            lambda e, idx=index, s_ui=storage_ui: self._update_mount_field(s_ui, idx, 'container_path', e.value))
                    
                    # Source (volume name or host path)
                    with ui.column():
                        mount_type = mount.get('type', 'auto-volume')
                        label = 'Volume name:' if mount_type in ['auto-volume', 'manual-volume'] else 'Host path:'
                        placeholder = 'auto-generated' if mount_type == 'auto-volume' else 'volume-name' if mount_type == 'manual-volume' else '/host/path'
                        
                        ui.label(label).classes('font-medium text-gray-700 mb-1')
                        source_input = ui.input(
                            placeholder=placeholder,
                            value=mount.get('source', '')
                        ).classes('w-full').on('value-change',
                            lambda e, idx=index, s_ui=storage_ui: self._update_mount_field(s_ui, idx, 'source', e.value))
                        
                        # Show/hide source input based on mount type
                        if mount_type == 'auto-volume':
                            source_input.visible = False  # Auto-volume doesn't need source
                        else:
                            source_input.visible = True  # manual-volume and host need source
    
    def _add_mount(self, stage: str) -> None:
        """Add a new mount entry."""
        storage_ui = self.app.ui_state.stage_1.storage if stage == 'stage1' else self.app.ui_state.stage_2.storage
        
        # Add new mount
        new_mount = {
            'id': str(uuid.uuid4()),
            'type': 'auto-volume',
            'container_path': '',
            'source': ''
        }
        storage_ui.mounts.append(new_mount)
        
        # Mark as modified
        self.app.ui_state.mark_modified()
        
        # Re-render mounts
        self._render_mounts(stage)
    
    def _remove_mount(self, storage_ui: Any, index: int) -> None:
        """Remove a mount entry."""
        if 0 <= index < len(storage_ui.mounts):
            storage_ui.mounts.pop(index)
            self.app.ui_state.mark_modified()
            
            # Re-render mounts
            stage = 'stage1' if storage_ui == self.app.ui_state.stage_1.storage else 'stage2'
            self._render_mounts(stage)
    
    def _update_mount_field(self, storage_ui: Any, index: int, field: str, value: str) -> None:
        """Update a specific field in a mount entry."""
        if 0 <= index < len(storage_ui.mounts):
            storage_ui.mounts[index][field] = value
            self.app.ui_state.mark_modified()
            
            # If type changed, re-render to update labels
            if field == 'type':
                stage = 'stage1' if storage_ui == self.app.ui_state.stage_1.storage else 'stage2'
                self._render_mounts(stage)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate storage configuration."""
        errors = []
        
        # Validate Stage-2 dynamic storage
        storage_ui = self.app.ui_state.stage_2.storage
        
        for storage_type in ['app', 'data', 'workspace']:
            type_value = getattr(storage_ui, f'{storage_type}_storage_type')
            
            if type_value == 'manual-volume':
                volume_name = getattr(storage_ui, f'{storage_type}_volume_name')
                if not volume_name:
                    errors.append(f"❌ {storage_type.title()} storage: Volume name is required for manual-volume type")
            
            elif type_value == 'host':
                host_path = getattr(storage_ui, f'{storage_type}_host_path')
                if not host_path:
                    errors.append(f"❌ {storage_type.title()} storage: Host path is required for host type")
                elif not host_path.startswith('/'):
                    errors.append(f"❌ {storage_type.title()} storage: Host path must be absolute (start with /)")
        
        # Validate mounts for both stages
        for stage_name, stage_ui in [('Stage-1', self.app.ui_state.stage_1), ('Stage-2', self.app.ui_state.stage_2)]:
            for i, mount in enumerate(stage_ui.storage.mounts):
                mount_num = i + 1
                
                # Container path is required
                if not mount.get('container_path'):
                    errors.append(f"❌ {stage_name} Mount {mount_num}: Container path is required")
                elif not mount['container_path'].startswith('/'):
                    errors.append(f"❌ {stage_name} Mount {mount_num}: Container path must be absolute")
                
                # Source validation based on type
                mount_type = mount.get('type', 'auto-volume')
                source = mount.get('source', '')
                
                if mount_type == 'manual-volume' and not source:
                    errors.append(f"❌ {stage_name} Mount {mount_num}: Volume name is required for manual volume")
                elif mount_type == 'host' and not source:
                    errors.append(f"❌ {stage_name} Mount {mount_num}: Host path is required")
                
                if mount_type == 'host' and source and not source.startswith('/'):
                    errors.append(f"❌ {stage_name} Mount {mount_num}: Host path must be absolute")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get configuration data for this tab."""
        # Stage-2 dynamic storage
        storage_ui = self.app.ui_state.stage_2.storage
        stage2_storage = {}
        
        for storage_type in ['app', 'data', 'workspace']:
            type_value = getattr(storage_ui, f'{storage_type}_storage_type')
            config = {'type': type_value}
            
            if type_value == 'manual-volume':
                config['volume_name'] = getattr(storage_ui, f'{storage_type}_volume_name')
            elif type_value == 'host':
                config['host_path'] = getattr(storage_ui, f'{storage_type}_host_path')
            
            stage2_storage[storage_type] = config
        
        # Mounts for both stages
        stage1_mounts = []
        stage2_mounts = []
        
        for mount in self.app.ui_state.stage_1.storage.mounts:
            if mount.get('container_path'):
                mount_type = mount.get('type', 'auto-volume')
                mount_config = {
                    'type': mount_type,
                    'dst_path': mount['container_path']
                }
                
                if mount_type == 'manual-volume':
                    mount_config['volume_name'] = mount.get('source', '')
                elif mount_type == 'host':
                    mount_config['host_path'] = mount.get('source', '')
                
                stage1_mounts.append(mount_config)
        
        for mount in self.app.ui_state.stage_2.storage.mounts:
            if mount.get('container_path'):
                mount_type = mount.get('type', 'auto-volume')
                mount_config = {
                    'type': mount_type,
                    'dst_path': mount['container_path']
                }
                
                if mount_type == 'manual-volume':
                    mount_config['volume_name'] = mount.get('source', '')
                elif mount_type == 'host':
                    mount_config['host_path'] = mount.get('source', '')
                
                stage2_mounts.append(mount_config)
        
        config = {
            'stage_1': {},
            'stage_2': {'storage': stage2_storage}
        }
        
        if stage1_mounts:
            config['stage_1']['mounts'] = stage1_mounts
        
        if stage2_mounts:
            config['stage_2']['mounts'] = stage2_mounts
        
        return config
    
    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set configuration data for this tab."""
        # Stage-2 dynamic storage
        stage2_storage = data.get('stage_2', {}).get('storage', {})
        storage_ui = self.app.ui_state.stage_2.storage
        
        for storage_type in ['app', 'data', 'workspace']:
            if storage_type in stage2_storage:
                config = stage2_storage[storage_type]
                setattr(storage_ui, f'{storage_type}_storage_type', config.get('type', 'auto-volume'))
                
                if config.get('type') == 'manual-volume' and 'volume_name' in config:
                    setattr(storage_ui, f'{storage_type}_volume_name', config['volume_name'])
                elif config.get('type') == 'host' and 'host_path' in config:
                    setattr(storage_ui, f'{storage_type}_host_path', config['host_path'])
        
        # Clear existing mounts
        self.app.ui_state.stage_1.storage.mounts.clear()
        self.app.ui_state.stage_2.storage.mounts.clear()
        
        # Load Stage-1 mounts
        stage1_mounts = data.get('stage_1', {}).get('mounts', [])
        for mount in stage1_mounts:
            mount_type = mount.get('type', 'auto-volume')
            mount_data = {
                'id': str(uuid.uuid4()),
                'type': mount_type,
                'container_path': mount.get('dst_path', ''),
                'source': ''
            }
            
            if mount_type == 'manual-volume':
                mount_data['source'] = mount.get('volume_name', '')
            elif mount_type == 'host':
                mount_data['source'] = mount.get('host_path', '')
            
            self.app.ui_state.stage_1.storage.mounts.append(mount_data)
        
        # Load Stage-2 mounts
        stage2_mounts = data.get('stage_2', {}).get('mounts', [])
        for mount in stage2_mounts:
            mount_type = mount.get('type', 'auto-volume')
            mount_data = {
                'id': str(uuid.uuid4()),
                'type': mount_type,
                'container_path': mount.get('dst_path', ''),
                'source': ''
            }
            
            if mount_type == 'manual-volume':
                mount_data['source'] = mount.get('volume_name', '')
            elif mount_type == 'host':
                mount_data['source'] = mount.get('host_path', '')
            
            self.app.ui_state.stage_2.storage.mounts.append(mount_data)
        
        # Re-render mounts
        self._render_mounts('stage1')
        self._render_mounts('stage2')
    
    def create_card(self, title: Optional[str] = None) -> ui.element:
        """Create a consistent card container."""
        with ui.card().classes('w-full p-6 mb-6') as card:
            if title:
                ui.label(title).classes('text-xl font-bold text-gray-800 mb-4')
        return card