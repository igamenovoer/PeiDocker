"""
Storage tab for PeiDocker Web GUI.

This tab handles Storage (Stage-2's dynamic system) and Mounts (general volume mounts) 
for both stages.
"""

from typing import TYPE_CHECKING, Dict, List, Tuple
from nicegui import ui
from .base import BaseTab

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class StorageTab(BaseTab):
    """Storage configuration tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        # Stage-2 Dynamic Storage (fixed entries)
        self.storage_configs = {}  # Will hold app, data, workspace configs
        
        # Stage-1 and Stage-2 Mounts (dynamic entries)
        self.stage1_mounts_container = None
        self.stage2_mounts_container = None
        self.stage1_mounts_data = []
        self.stage2_mounts_data = []
        self.mount_count = 0
    
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
                    with ui.column().classes('flex-1'):
                        ui.label('📋 Key Concepts:').classes('font-semibold text-blue-800')
                        ui.markdown("""**Storage** is Stage-2's unique dynamic system for predefined directories (/soft/app, /soft/data, /soft/workspace).
**Mounts** are general volume mounts that can be defined for any container path.""").classes('text-blue-700 text-sm mt-1')
            
            # Stage-2 Dynamic Storage System
            with self.create_card('🚀 Stage-2 Dynamic Storage System (Stage-2 ONLY)'):
                ui.label('Stage-2\'s unique dynamic storage for predefined directories with smart linking: /soft/xxx → /hard/volume/xxx OR /hard/image/xxx') \
                    .classes('text-gray-600 mb-4')
                
                # Create the three fixed storage entries
                self._create_storage_entry('app', '📱 App Storage (/soft/app)', 'Application files and dependencies - Fixed destination')
                self._create_storage_entry('data', '📊 Data Storage (/soft/data)', 'User data and persistent files - Fixed destination')
                self._create_storage_entry('workspace', '💼 Workspace Storage (/soft/workspace)', 'Development and workspace files - Fixed destination')
                
                # Storage note
                with ui.card().classes('w-full p-3 mt-4 bg-blue-50 border-blue-200'):
                    with ui.row().classes('items-start gap-2'):
                        ui.icon('lightbulb', color='blue')
                        with ui.column():
                            ui.label('💡 Storage Note:').classes('font-semibold text-blue-800')
                            ui.label('These 3 storage entries are always present and default to \'image\' type even when omitted from user_config.yml. They cannot be created or removed - only their storage type and related options can be configured.') \
                                .classes('text-blue-700 text-sm')
            
            # Stage-1 Mounts
            with self.create_card('🏗️ Stage-1 Mounts (General Volume Mounts)'):
                with self.create_form_group('Stage-1 Volume Mounts', 'General volume mounts for Stage-1 image (any paths, user-defined)'):
                    
                    # Mounts container
                    with ui.column().classes('w-full mb-4') as stage1_container:
                        self.stage1_mounts_container = stage1_container
                    
                    # Add mount button
                    ui.button('➕ Add mount', on_click=lambda: self._add_mount('stage1')) \
                        .classes('bg-blue-600 hover:bg-blue-700 text-white')
            
            # Stage-2 Mounts
            with self.create_card('🚀 Stage-2 Mounts (General Volume Mounts)'):
                with self.create_form_group('Stage-2 Volume Mounts', 'General volume mounts for Stage-2 image (any paths, user-defined). Stage-2 mounts don\'t inherit from Stage-1.'):
                    
                    # Mounts container
                    with ui.column().classes('w-full mb-4') as stage2_container:
                        self.stage2_mounts_container = stage2_container
                    
                    # Add mount button
                    ui.button('➕ Add mount', on_click=lambda: self._add_mount('stage2')) \
                        .classes('bg-blue-600 hover:bg-blue-700 text-white')
        
        return container
    
    def _create_storage_entry(self, storage_type: str, title: str, description: str):
        """Create a storage entry for the Stage-2 dynamic storage system."""
        with ui.card().classes('w-full p-4 mb-4'):
            ui.label(title).classes('text-lg font-semibold mb-2')
            ui.label(description).classes('text-gray-600 mb-4')
            
            # Three-column grid for storage configuration
            with ui.row().classes('gap-4 w-full'):
                # Storage Type
                with ui.column().classes('flex-1'):
                    ui.label('Storage type:').classes('font-medium text-gray-700 mb-1')
                    type_select = ui.select(
                        options={
                            'auto-volume': 'auto-volume',
                            'manual-volume': 'manual-volume', 
                            'host': 'host',
                            'image': 'image (default)'
                        },
                        value='image'
                    ).classes('w-full')
                
                # Host Path
                with ui.column().classes('flex-1'):
                    ui.label('Host path:').classes('font-medium text-gray-700 mb-1')
                    host_path_input = ui.input(
                        placeholder=f'/host/path/to/{storage_type}'
                    ).classes('w-full').props('disabled')
                    ui.label('Only editable when type is \'host\'').classes('text-xs text-gray-500 mt-1')
                
                # Volume Name
                with ui.column().classes('flex-1'):
                    ui.label('Volume name:').classes('font-medium text-gray-700 mb-1')
                    volume_name_input = ui.input(
                        placeholder=f'my-{storage_type}-volume'
                    ).classes('w-full').props('disabled')
                    ui.label('Only editable when type is \'manual-volume\'').classes('text-xs text-gray-500 mt-1')
            
            # Store configuration references
            self.storage_configs[storage_type] = {
                'type_select': type_select,
                'host_path_input': host_path_input,
                'volume_name_input': volume_name_input
            }
            
            # Add event handler
            type_select.on('change', lambda e, st=storage_type: self._on_storage_type_change(e, st))
    
    def _on_storage_type_change(self, e, storage_type: str):
        """Handle storage type changes."""
        storage_config = self.storage_configs[storage_type]
        selected_type = e.value
        
        # Update field states based on storage type
        if selected_type == 'host':
            storage_config['host_path_input'].props(remove='disabled')
            storage_config['volume_name_input'].props('disabled')
        elif selected_type == 'manual-volume':
            storage_config['host_path_input'].props('disabled')
            storage_config['volume_name_input'].props(remove='disabled')
        else:  # auto-volume or image
            storage_config['host_path_input'].props('disabled')
            storage_config['volume_name_input'].props('disabled')
        
        # Update configuration
        if 'storage' not in self.app.data.config.stage_2:
            self.app.data.config.stage_2['storage'] = {}
        if storage_type not in self.app.data.config.stage_2['storage']:
            self.app.data.config.stage_2['storage'][storage_type] = {}
        
        storage_entry = self.app.data.config.stage_2['storage'][storage_type]
        storage_entry['type'] = selected_type
        
        # Update related fields
        if selected_type == 'host':
            host_path = storage_config['host_path_input'].value.strip()
            if host_path:
                storage_entry['host_path'] = host_path
        elif selected_type == 'manual-volume':
            volume_name = storage_config['volume_name_input'].value.strip()
            if volume_name:
                storage_entry['volume_name'] = volume_name
        
        self.mark_modified()
    
    def _add_mount(self, stage: str):
        """Add a new mount configuration."""
        mount_id = f'mount-{stage}-{self.mount_count}'
        container = self.stage1_mounts_container if stage == 'stage1' else self.stage2_mounts_container
        
        with container:
            with ui.card().classes('w-full p-4 mb-4') as mount_card:
                # Mount header
                with ui.row().classes('items-center justify-between mb-4'):
                    ui.label(f'🔗 {stage.upper()} Mount {self.mount_count + 1}').classes('text-lg font-semibold')
                    ui.button('🗑️ Remove', on_click=lambda: self._remove_mount(mount_card, mount_id, stage)) \
                        .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                
                # Mount configuration - First row
                with ui.row().classes('gap-4 mb-4'):
                    # Container Path
                    with ui.column().classes('flex-1'):
                        ui.label('Container path:').classes('font-medium text-gray-700 mb-1')
                        container_path_input = ui.input(
                            placeholder='/container/path'
                        ).classes('w-full')
                    
                    # Mount Type
                    with ui.column().classes('flex-1'):
                        ui.label('Mount type:').classes('font-medium text-gray-700 mb-1')
                        mount_type_select = ui.select(
                            options={
                                'auto-volume': 'auto-volume',
                                'manual-volume': 'manual-volume',
                                'host': 'host'
                            },
                            value='auto-volume'
                        ).classes('w-full')
                
                # Mount configuration - Second row
                with ui.row().classes('gap-4'):
                    # Host Path
                    with ui.column().classes('flex-1'):
                        ui.label('Host path:').classes('font-medium text-gray-700 mb-1')
                        host_path_input = ui.input(
                            placeholder='/host/path'
                        ).classes('w-full').props('disabled')
                        ui.label('Only editable when type is \'host\'').classes('text-xs text-gray-500 mt-1')
                    
                    # Volume Name
                    with ui.column().classes('flex-1'):
                        ui.label('Volume name:').classes('font-medium text-gray-700 mb-1')
                        volume_name_input = ui.input(
                            placeholder='my-volume'
                        ).classes('w-full').props('disabled')
                        ui.label('Only editable when type is \'manual-volume\'').classes('text-xs text-gray-500 mt-1')
                
                # Store mount data
                mount_data = {
                    'id': mount_id,
                    'stage': stage,
                    'container_path_input': container_path_input,
                    'mount_type_select': mount_type_select,
                    'host_path_input': host_path_input,
                    'volume_name_input': volume_name_input,
                    'card': mount_card
                }
                
                # Add event handlers
                mount_type_select.on('change', lambda e, data=mount_data: self._on_mount_type_change(e, data))
                container_path_input.on('input', lambda e, data=mount_data: self._on_mount_change(data))
                host_path_input.on('input', lambda e, data=mount_data: self._on_mount_change(data))
                volume_name_input.on('input', lambda e, data=mount_data: self._on_mount_change(data))
                
                # Add to appropriate list
                if stage == 'stage1':
                    self.stage1_mounts_data.append(mount_data)
                else:
                    self.stage2_mounts_data.append(mount_data)
        
        self.mount_count += 1
        self.mark_modified()
    
    def _remove_mount(self, mount_card, mount_id: str, stage: str):
        """Remove a mount configuration."""
        mount_card.delete()
        
        # Remove from appropriate data list
        if stage == 'stage1':
            self.stage1_mounts_data = [
                data for data in self.stage1_mounts_data 
                if data['id'] != mount_id
            ]
        else:
            self.stage2_mounts_data = [
                data for data in self.stage2_mounts_data 
                if data['id'] != mount_id
            ]
        
        self._update_mounts_config()
        self.mark_modified()
    
    def _on_mount_type_change(self, e, mount_data):
        """Handle mount type changes."""
        selected_type = e.value
        
        # Update field states based on mount type
        if selected_type == 'host':
            mount_data['host_path_input'].props(remove='disabled')
            mount_data['volume_name_input'].props('disabled')
        elif selected_type == 'manual-volume':
            mount_data['host_path_input'].props('disabled')
            mount_data['volume_name_input'].props(remove='disabled')
        else:  # auto-volume
            mount_data['host_path_input'].props('disabled')
            mount_data['volume_name_input'].props('disabled')
        
        self._update_mounts_config()
        self.mark_modified()
    
    def _on_mount_change(self, mount_data):
        """Handle mount configuration changes."""
        self._update_mounts_config()
        self.mark_modified()
    
    def _update_mounts_config(self):
        """Update the mounts configuration."""
        # Update Stage-1 mounts
        stage1_mounts = []
        for mount_data in self.stage1_mounts_data:
            container_path = mount_data['container_path_input'].value.strip()
            mount_type = mount_data['mount_type_select'].value
            host_path = mount_data['host_path_input'].value.strip()
            volume_name = mount_data['volume_name_input'].value.strip()
            
            if container_path:  # Only add if container path is specified
                mount_entry = {
                    'container_path': container_path,
                    'type': mount_type
                }
                
                if mount_type == 'host' and host_path:
                    mount_entry['host_path'] = host_path
                elif mount_type == 'manual-volume' and volume_name:
                    mount_entry['volume_name'] = volume_name
                
                stage1_mounts.append(mount_entry)
        
        # Update Stage-2 mounts
        stage2_mounts = []
        for mount_data in self.stage2_mounts_data:
            container_path = mount_data['container_path_input'].value.strip()
            mount_type = mount_data['mount_type_select'].value
            host_path = mount_data['host_path_input'].value.strip()
            volume_name = mount_data['volume_name_input'].value.strip()
            
            if container_path:  # Only add if container path is specified
                mount_entry = {
                    'container_path': container_path,
                    'type': mount_type
                }
                
                if mount_type == 'host' and host_path:
                    mount_entry['host_path'] = host_path
                elif mount_type == 'manual-volume' and volume_name:
                    mount_entry['volume_name'] = volume_name
                
                stage2_mounts.append(mount_entry)
        
        # Update configuration
        self.app.data.config.stage_1['mounts'] = stage1_mounts
        self.app.data.config.stage_2['mounts'] = stage2_mounts
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate storage configuration."""
        errors = []
        
        # Validate storage configurations
        for storage_type, config in self.storage_configs.items():
            selected_type = config['type_select'].value
            
            if selected_type == 'host':
                host_path = config['host_path_input'].value.strip()
                if not host_path:
                    errors.append(f"{storage_type.title()} storage: Host path is required when type is 'host'")
                elif not host_path.startswith('/'):
                    errors.append(f"{storage_type.title()} storage: Host path must be an absolute path")
            
            elif selected_type == 'manual-volume':
                volume_name = config['volume_name_input'].value.strip()
                if not volume_name:
                    errors.append(f"{storage_type.title()} storage: Volume name is required when type is 'manual-volume'")
        
        # Validate mounts
        for stage, mounts_data in [('Stage-1', self.stage1_mounts_data), ('Stage-2', self.stage2_mounts_data)]:
            container_paths = set()
            
            for i, mount_data in enumerate(mounts_data):
                container_path = mount_data['container_path_input'].value.strip()
                mount_type = mount_data['mount_type_select'].value
                host_path = mount_data['host_path_input'].value.strip()
                volume_name = mount_data['volume_name_input'].value.strip()
                
                if not container_path:
                    errors.append(f"{stage} mount {i+1}: Container path is required")
                    continue
                
                if not container_path.startswith('/'):
                    errors.append(f"{stage} mount {i+1}: Container path must be an absolute path")
                
                # Check for duplicate container paths
                if container_path in container_paths:
                    errors.append(f"{stage} mount {i+1}: Duplicate container path '{container_path}'")
                else:
                    container_paths.add(container_path)
                
                if mount_type == 'host':
                    if not host_path:
                        errors.append(f"{stage} mount {i+1}: Host path is required when type is 'host'")
                    elif not host_path.startswith('/'):
                        errors.append(f"{stage} mount {i+1}: Host path must be an absolute path")
                
                elif mount_type == 'manual-volume':
                    if not volume_name:
                        errors.append(f"{stage} mount {i+1}: Volume name is required when type is 'manual-volume'")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> dict:
        """Get storage configuration data."""
        return {
            'stage_1': {
                'mounts': self.app.data.config.stage_1.get('mounts', [])
            },
            'stage_2': {
                'storage': self.app.data.config.stage_2.get('storage', {}),
                'mounts': self.app.data.config.stage_2.get('mounts', [])
            }
        }
    
    def set_config_data(self, data: dict):
        """Set storage configuration data."""
        stage_1_config = data.get('stage_1', {})
        stage_2_config = data.get('stage_2', {})
        
        # Set storage configuration
        storage_config = stage_2_config.get('storage', {})
        for storage_type in ['app', 'data', 'workspace']:
            if storage_type in storage_config and storage_type in self.storage_configs:
                storage_entry = storage_config[storage_type]
                config = self.storage_configs[storage_type]
                
                # Set storage type
                config['type_select'].set_value(storage_entry.get('type', 'image'))
                
                # Set host path if available
                if 'host_path' in storage_entry:
                    config['host_path_input'].set_value(storage_entry['host_path'])
                
                # Set volume name if available
                if 'volume_name' in storage_entry:
                    config['volume_name_input'].set_value(storage_entry['volume_name'])
                
                # Trigger field updates
                self._on_storage_type_change(
                    type('Event', (), {'value': storage_entry.get('type', 'image')})(),
                    storage_type
                )
        
        # Set mounts
        # Clear existing mounts
        if self.stage1_mounts_container:
            self.stage1_mounts_container.clear()
            self.stage1_mounts_data = []
        
        if self.stage2_mounts_container:
            self.stage2_mounts_container.clear()
            self.stage2_mounts_data = []
        
        self.mount_count = 0
        
        # Add Stage-1 mounts
        stage1_mounts = stage_1_config.get('mounts', [])
        for mount in stage1_mounts:
            self._add_mount_from_config('stage1', mount)
        
        # Add Stage-2 mounts
        stage2_mounts = stage_2_config.get('mounts', [])
        for mount in stage2_mounts:
            self._add_mount_from_config('stage2', mount)
    
    def _add_mount_from_config(self, stage: str, mount_config: dict):
        """Add a mount from configuration data."""
        # Add the mount first
        self._add_mount(stage)
        
        # Get the last added mount data
        mounts_data = self.stage1_mounts_data if stage == 'stage1' else self.stage2_mounts_data
        if mounts_data:
            mount_data = mounts_data[-1]
            
            # Set the configuration values
            mount_data['container_path_input'].set_value(mount_config.get('container_path', ''))
            mount_data['mount_type_select'].set_value(mount_config.get('type', 'auto-volume'))
            
            if 'host_path' in mount_config:
                mount_data['host_path_input'].set_value(mount_config['host_path'])
            
            if 'volume_name' in mount_config:
                mount_data['volume_name_input'].set_value(mount_config['volume_name'])
            
            # Trigger field updates
            self._on_mount_type_change(
                type('Event', (), {'value': mount_config.get('type', 'auto-volume')})(),
                mount_data
            )