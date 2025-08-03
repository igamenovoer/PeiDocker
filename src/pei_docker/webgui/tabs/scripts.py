"""
Scripts tab for PeiDocker Web GUI.

This tab handles custom entry points and lifecycle hook scripts 
for Stage-1 and Stage-2 sequential image builds.
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Any, Tuple
from nicegui import ui
from .base import BaseTab
import uuid

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class ScriptsTab(BaseTab):
    """Scripts configuration tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        
        # Stage-1 Entry Point
        self.stage1_entry_mode_radio: Optional[ui.radio] = None
        self.stage1_entry_config_container: Optional[ui.column] = None
        self.stage1_entry_file_input: Optional[ui.input] = None
        self.stage1_entry_inline_name_input: Optional[ui.input] = None
        self.stage1_entry_inline_content_textarea: Optional[ui.textarea] = None
        
        # Stage-2 Entry Point
        self.stage2_entry_mode_radio: Optional[ui.radio] = None
        self.stage2_entry_config_container: Optional[ui.column] = None
        self.stage2_entry_file_input: Optional[ui.input] = None
        self.stage2_entry_inline_name_input: Optional[ui.input] = None
        self.stage2_entry_inline_content_textarea: Optional[ui.textarea] = None
        
        # Lifecycle Scripts
        self.stage1_lifecycle_containers: Dict[str, ui.column] = {}
        self.stage2_lifecycle_containers: Dict[str, ui.column] = {}
        self.stage1_lifecycle_scripts: Dict[str, List[Dict[str, Any]]] = {}
        self.stage2_lifecycle_scripts: Dict[str, List[Dict[str, Any]]] = {}
        
        # Lifecycle types
        self.lifecycle_types: List[Tuple[str, str]] = [
            ('on_build', 'Runs during image building'),
            ('on_first_run', 'Runs on first container start (respective stage)'),
            ('on_every_run', 'Runs on every container start (respective stage)'),
            ('on_user_login', 'Runs when user logs in via SSH (respective stage)')
        ]
    
    def render(self) -> ui.element:
        """Render the scripts tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '📜 Custom Scripts Configuration',
                'Configure custom entry points and lifecycle hook scripts for Stage-1 and Stage-2 sequential image builds'
            )
            
            # Important Path Access Rules
            with ui.card().classes('w-full p-3 mb-4 bg-blue-50 border-blue-200'):
                ui.label('ℹ️ Important: Script Path Access Rules').classes('text-base font-semibold text-blue-800 mb-2')
                
                with ui.column().classes('text-sm space-y-2'):
                    with ui.column():
                        ui.label('🏗️ Stage-1 Scripts:').classes('font-semibold')
                        with ui.column().classes('ml-4'):
                            ui.markdown('• Can **ONLY** reference paths starting with `stage-1/`').classes('text-sm')
                            ui.markdown('• **Cannot access** any `stage-2/` paths (stage-2 doesn\'t exist yet)').classes('text-sm')
                            ui.markdown('• Examples: `stage-1/custom/script.sh`, `stage-1/system/setup.sh`').classes('text-sm')
                    
                    with ui.column():
                        ui.label('🏗️ Stage-2 Scripts:').classes('font-semibold')
                        with ui.column().classes('ml-4'):
                            ui.markdown('• Can reference paths starting with **both** `stage-1/` and `stage-2/`').classes('text-sm')
                            ui.markdown('• Has access to all stage-1 resources plus stage-2 resources').classes('text-sm')
                            ui.markdown('• Examples: `stage-2/custom/app.sh`, `stage-1/system/base.sh`').classes('text-sm')
            
            # Stage-1 Scripts
            self._create_stage_scripts_section('stage1', '🏗️ Stage-1 Image Scripts', 'stage-1')
            
            # Stage-2 Scripts
            self._create_stage_scripts_section('stage2', '🏗️ Stage-2 Image Scripts (builds on top of Stage-1, inheriting all its resources)', 'stage-2')
        
        return container
    
    def _create_stage_scripts_section(self, stage: str, title: str, path_prefix: str) -> None:
        """Create a stage scripts section."""
        with self.create_card(title):
            # Custom Entry Point
            with self.create_form_group('Custom Entry Point', f'Override the default entry point for {stage.upper()}'):
                
                # Entry point mode selection
                with ui.column().classes('mb-4 w-full'):
                    entry_mode_radio = ui.radio(
                        options={
                            'none': 'Use default',
                            'file': 'File path',
                            'inline': 'Inline script'
                        },
                        value='none'
                    ).props('inline')
                    entry_mode_radio.on('change', lambda e, s=stage: self._on_entry_mode_change(e, s))
                
                # Entry point configuration (initially hidden)
                with ui.column().classes('w-full') as entry_config_container:
                    entry_config_container.bind_visibility_from(entry_mode_radio, 'value', lambda v: v != 'none')
                    
                    # File path mode
                    with ui.column().classes('w-full') as file_mode_container:
                        entry_file_input = ui.input(
                            placeholder=f'{path_prefix}/custom/script-{self._generate_uuid()}.bash --param=value'
                        ).classes('w-full')
                        entry_file_input.on('input', lambda e, s=stage: self._on_entry_config_change(s))
                        
                        file_mode_container.bind_visibility_from(entry_mode_radio, 'value', lambda v: v == 'file')
                    
                    # Inline script mode
                    with ui.column().classes('w-full') as inline_mode_container:
                        with ui.row().classes('items-center mb-2 gap-0 w-full'):
                            ui.label(f'{path_prefix}/custom/').classes('px-3 py-2 bg-gray-100 border border-r-0 rounded-l text-sm font-mono')
                            entry_inline_name_input = ui.input(
                                placeholder='entry-script.bash',
                                value=f'script-{self._generate_uuid()}.bash'
                            ).classes('w-full rounded-l-none')
                        
                        entry_inline_content_textarea = ui.textarea(
                            placeholder='#!/bin/bash\necho \'Custom entry point\'',
                            value='#!/bin/bash\necho \'Custom entry point\''
                        ).classes('w-full').props('rows=4')
                        entry_inline_name_input.on('input', lambda e, s=stage: self._on_entry_config_change(s))
                        entry_inline_content_textarea.on('input', lambda e, s=stage: self._on_entry_config_change(s))
                        
                        inline_mode_container.bind_visibility_from(entry_mode_radio, 'value', lambda v: v == 'inline')
                
                # Store references
                if stage == 'stage1':
                    self.stage1_entry_mode_radio = entry_mode_radio
                    self.stage1_entry_config_container = entry_config_container
                    self.stage1_entry_file_input = entry_file_input
                    self.stage1_entry_inline_name_input = entry_inline_name_input
                    self.stage1_entry_inline_content_textarea = entry_inline_content_textarea
                else:
                    self.stage2_entry_mode_radio = entry_mode_radio
                    self.stage2_entry_config_container = entry_config_container
                    self.stage2_entry_file_input = entry_file_input
                    self.stage2_entry_inline_name_input = entry_inline_name_input
                    self.stage2_entry_inline_content_textarea = entry_inline_content_textarea
            
            # Lifecycle Scripts
            with self.create_form_group('Lifecycle Scripts', 'Scripts that run at specific lifecycle events'):
                
                for lifecycle_type, description in self.lifecycle_types:
                    with ui.column().classes('mb-4 w-full'):
                        ui.label(f'{lifecycle_type} - {description}').classes('text-sm font-medium text-gray-700 mb-2')
                        
                        # Add script buttons
                        with ui.row().classes('gap-2 mb-2 w-full'):
                            ui.button('📁 Add File', 
                                    on_click=lambda lt=lifecycle_type, s=stage, pp=path_prefix: self._add_lifecycle_script(s, lt, 'file', pp)) \
                                .classes('bg-gray-600 hover:bg-gray-700 text-white text-sm')
                            ui.button('📝 Add Inline', 
                                    on_click=lambda lt=lifecycle_type, s=stage, pp=path_prefix: self._add_lifecycle_script(s, lt, 'inline', pp)) \
                                .classes('bg-gray-600 hover:bg-gray-700 text-white text-sm')
                        
                        # Scripts container
                        with ui.column().classes('w-full') as scripts_container:
                            pass
                        
                        # Store container reference
                        if stage == 'stage1':
                            self.stage1_lifecycle_containers[lifecycle_type] = scripts_container
                            if lifecycle_type not in self.stage1_lifecycle_scripts:
                                self.stage1_lifecycle_scripts[lifecycle_type] = []
                        else:
                            self.stage2_lifecycle_containers[lifecycle_type] = scripts_container
                            if lifecycle_type not in self.stage2_lifecycle_scripts:
                                self.stage2_lifecycle_scripts[lifecycle_type] = []
    
    def _generate_uuid(self) -> str:
        """Generate a short UUID for script names."""
        return str(uuid.uuid4()).replace('-', '')[:8]
    
    def _on_entry_mode_change(self, e: Any, stage: str) -> None:
        """Handle entry point mode changes."""
        mode = e.value
        
        # Generate new UUID for inline script if switching to inline mode
        if mode == 'inline':
            new_uuid = self._generate_uuid()
            if stage == 'stage1' and self.stage1_entry_inline_name_input:
                self.stage1_entry_inline_name_input.set_value(f'script-{new_uuid}.bash')
            elif stage == 'stage2' and self.stage2_entry_inline_name_input:
                self.stage2_entry_inline_name_input.set_value(f'script-{new_uuid}.bash')
        
        self._on_entry_config_change(stage)
    
    def _on_entry_config_change(self, stage: str) -> None:
        """Handle entry point configuration changes."""
        # Update configuration
        stage_key = 'stage_1' if stage == 'stage1' else 'stage_2'
        
        if 'scripts' not in self.app.data.config.__dict__[stage_key]:
            self.app.data.config.__dict__[stage_key]['scripts'] = {}
        
        scripts_config = self.app.data.config.__dict__[stage_key]['scripts']
        
        # Get current values
        if stage == 'stage1':
            mode = self.stage1_entry_mode_radio.value if self.stage1_entry_mode_radio else 'none'
            file_path = self.stage1_entry_file_input.value.strip() if self.stage1_entry_file_input else ''
            inline_name = self.stage1_entry_inline_name_input.value.strip() if self.stage1_entry_inline_name_input else ''
            inline_content = self.stage1_entry_inline_content_textarea.value.strip() if self.stage1_entry_inline_content_textarea else ''
        else:
            mode = self.stage2_entry_mode_radio.value if self.stage2_entry_mode_radio else 'none'
            file_path = self.stage2_entry_file_input.value.strip() if self.stage2_entry_file_input else ''
            inline_name = self.stage2_entry_inline_name_input.value.strip() if self.stage2_entry_inline_name_input else ''
            inline_content = self.stage2_entry_inline_content_textarea.value.strip() if self.stage2_entry_inline_content_textarea else ''
        
        # Update configuration based on mode
        if mode == 'none':
            scripts_config.pop('entry_point', None)
        elif mode == 'file':
            if file_path:
                scripts_config['entry_point'] = {'type': 'file', 'path': file_path}
            else:
                scripts_config.pop('entry_point', None)
        elif mode == 'inline':
            if inline_name and inline_content:
                scripts_config['entry_point'] = {
                    'type': 'inline',
                    'name': inline_name,
                    'content': inline_content
                }
            else:
                scripts_config.pop('entry_point', None)
        
        self.mark_modified()
    
    def _add_lifecycle_script(self, stage: str, lifecycle_type: str, script_type: str, path_prefix: str) -> None:
        """Add a lifecycle script."""
        script_id = f'{stage}-{lifecycle_type}-{script_type}-{self._generate_uuid()}'
        container = self.stage1_lifecycle_containers[lifecycle_type] if stage == 'stage1' else self.stage2_lifecycle_containers[lifecycle_type]
        
        with container:
            with ui.card().classes('w-full p-3 mb-3') as script_card:
                if script_type == 'file':
                    # File path script
                    with ui.column().classes('w-full'):
                        script_input = ui.input(
                            placeholder=f'{path_prefix}/custom/script-{self._generate_uuid()}.bash --param=value',
                            value=f'{path_prefix}/custom/script-{self._generate_uuid()}.bash'
                        ).classes('w-full mb-2')
                        
                        with ui.row().classes('gap-2 w-full'):
                            ui.button('✏️ Edit', on_click=lambda inp=script_input: self._edit_file_path(inp)) \
                                .classes('bg-yellow-600 hover:bg-yellow-700 text-white text-sm')
                            ui.button('🗑️ Remove', on_click=lambda: self._remove_script(script_card, stage, lifecycle_type, script_id)) \
                                .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                        
                        script_input.on('input', lambda e, s=stage, lt=lifecycle_type: self._on_lifecycle_script_change(s, lt))
                else:
                    # Inline script
                    script_uuid = self._generate_uuid()
                    with ui.column().classes('w-full'):
                        # Script name display
                        with ui.row().classes('items-center mb-2 gap-0 w-full'):
                            ui.label(f'{path_prefix}/custom/').classes('px-3 py-2 bg-gray-100 border border-r-0 rounded-l text-sm font-mono')
                            script_name_input = ui.input(
                                value=f'script-{script_uuid}.bash',
                                placeholder='script-name.bash'
                            ).classes('w-full rounded-l-none')
                        
                        # Script content
                        script_content_textarea = ui.textarea(
                            placeholder='#!/bin/bash\necho \'Inline script content\'',
                            value='#!/bin/bash\necho \'Inline script content\''
                        ).classes('w-full mb-2').props('rows=3')
                        
                        with ui.row().classes('gap-2 w-full'):
                            ui.button('👁️ View', on_click=lambda name=script_name_input, content=script_content_textarea: self._view_inline_script(name.value, content.value)) \
                                .classes('bg-blue-600 hover:bg-blue-700 text-white text-sm')
                            ui.button('✏️ Edit', on_click=lambda name=script_name_input, content=script_content_textarea: self._edit_inline_script(name.value, content)) \
                                .classes('bg-yellow-600 hover:bg-yellow-700 text-white text-sm')
                            ui.button('🗑️ Remove', on_click=lambda: self._remove_script(script_card, stage, lifecycle_type, script_id)) \
                                .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                        
                        script_name_input.on('input', lambda e, s=stage, lt=lifecycle_type: self._on_lifecycle_script_change(s, lt))
                        script_content_textarea.on('input', lambda e, s=stage, lt=lifecycle_type: self._on_lifecycle_script_change(s, lt))
                
                # Store script data
                script_data = {
                    'id': script_id,
                    'type': script_type,
                    'card': script_card
                }
                
                if script_type == 'file':
                    script_data['input'] = script_input
                else:
                    script_data['name_input'] = script_name_input
                    script_data['content_textarea'] = script_content_textarea
                
                # Add to scripts list
                if stage == 'stage1':
                    self.stage1_lifecycle_scripts[lifecycle_type].append(script_data)
                else:
                    self.stage2_lifecycle_scripts[lifecycle_type].append(script_data)
        
        self._on_lifecycle_script_change(stage, lifecycle_type)
    
    def _remove_script(self, script_card: Any, stage: str, lifecycle_type: str, script_id: str) -> None:
        """Remove a lifecycle script."""
        script_card.delete()
        
        # Remove from scripts list
        if stage == 'stage1':
            self.stage1_lifecycle_scripts[lifecycle_type] = [
                script for script in self.stage1_lifecycle_scripts[lifecycle_type]
                if script['id'] != script_id
            ]
        else:
            self.stage2_lifecycle_scripts[lifecycle_type] = [
                script for script in self.stage2_lifecycle_scripts[lifecycle_type]
                if script['id'] != script_id
            ]
        
        self._on_lifecycle_script_change(stage, lifecycle_type)
    
    def _on_lifecycle_script_change(self, stage: str, lifecycle_type: str) -> None:
        """Handle lifecycle script changes."""
        stage_key = 'stage_1' if stage == 'stage1' else 'stage_2'
        
        if 'scripts' not in self.app.data.config.__dict__[stage_key]:
            self.app.data.config.__dict__[stage_key]['scripts'] = {}
        
        scripts_config = self.app.data.config.__dict__[stage_key]['scripts']
        
        # Get current scripts
        scripts_list = self.stage1_lifecycle_scripts[lifecycle_type] if stage == 'stage1' else self.stage2_lifecycle_scripts[lifecycle_type]
        
        lifecycle_scripts = []
        for script_data in scripts_list:
            if script_data['type'] == 'file':
                path = script_data['input'].value.strip()
                if path:
                    lifecycle_scripts.append({'type': 'file', 'path': path})
            else:  # inline
                name = script_data['name_input'].value.strip()
                content = script_data['content_textarea'].value.strip()
                if name and content:
                    lifecycle_scripts.append({
                        'type': 'inline',
                        'name': name,
                        'content': content
                    })
        
        # Update configuration
        if lifecycle_scripts:
            scripts_config[lifecycle_type] = lifecycle_scripts
        else:
            scripts_config.pop(lifecycle_type, None)
        
        self.mark_modified()
    
    def _edit_file_path(self, input_field: Any) -> None:
        """Edit file path (simulate dialog)."""
        # In a real implementation, this would open a proper dialog
        # For now, just focus the input field
        input_field.run_method('focus')
    
    def _view_inline_script(self, name: str, content: str) -> None:
        """View inline script content."""
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label(f'Viewing: {name}').classes('text-lg font-semibold mb-3')
            ui.code(content).classes('w-full bg-gray-100 p-3 rounded text-sm')
            ui.button('Close', on_click=dialog.close).classes('mt-3')
        dialog.open()
    
    def _edit_inline_script(self, name: str, content_textarea: Any) -> None:
        """Edit inline script content."""
        # For now, just focus the textarea
        content_textarea.run_method('focus')
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate scripts configuration."""
        errors = []
        
        # Validate entry points
        for stage, stage_key in [('stage1', 'stage_1'), ('stage2', 'stage_2')]:
            scripts_config = self.app.data.config.__dict__[stage_key].get('scripts', {})
            entry_point = scripts_config.get('entry_point')
            
            if entry_point:
                if entry_point['type'] == 'file':
                    path = entry_point.get('path', '').strip()
                    if not path:
                        errors.append(f"{stage.upper()} entry point: File path is required")
                    elif not self._validate_script_path(path, stage):
                        errors.append(f"{stage.upper()} entry point: Invalid path '{path}' for {stage}")
                elif entry_point['type'] == 'inline':
                    if not entry_point.get('name', '').strip():
                        errors.append(f"{stage.upper()} entry point: Script name is required")
                    if not entry_point.get('content', '').strip():
                        errors.append(f"{stage.upper()} entry point: Script content is required")
            
            # Validate lifecycle scripts
            for lifecycle_type in ['on_build', 'on_first_run', 'on_every_run', 'on_user_login']:
                lifecycle_scripts = scripts_config.get(lifecycle_type, [])
                
                for i, script in enumerate(lifecycle_scripts):
                    if script['type'] == 'file':
                        path = script.get('path', '').strip()
                        if not path:
                            errors.append(f"{stage.upper()} {lifecycle_type} script {i+1}: File path is required")
                        elif not self._validate_script_path(path, stage):
                            errors.append(f"{stage.upper()} {lifecycle_type} script {i+1}: Invalid path '{path}' for {stage}")
                    elif script['type'] == 'inline':
                        if not script.get('name', '').strip():
                            errors.append(f"{stage.upper()} {lifecycle_type} script {i+1}: Script name is required")
                        if not script.get('content', '').strip():
                            errors.append(f"{stage.upper()} {lifecycle_type} script {i+1}: Script content is required")
        
        return len(errors) == 0, errors
    
    def _validate_script_path(self, path: str, stage: str) -> bool:
        """Validate script path based on stage rules."""
        if stage == 'stage1':
            # Stage-1 can only access stage-1/ paths
            return path.startswith('stage-1/')
        else:
            # Stage-2 can access both stage-1/ and stage-2/ paths
            return path.startswith('stage-1/') or path.startswith('stage-2/')
    
    def get_config_data(self) -> dict:
        """Get scripts configuration data.
        
        For inline scripts, we store them temporarily with metadata.
        The actual file writing will be handled by the save process.
        """
        stage_1_data: Dict[str, Any] = {}
        stage_2_data: Dict[str, Any] = {}
        
        # We need to store inline scripts data for the save process
        stage_1_inline_scripts = []
        stage_2_inline_scripts = []
        
        # Collect Stage-1 configuration
        if self.stage1_entry_mode_radio and self.stage1_entry_mode_radio.value != 'none':
            mode = self.stage1_entry_mode_radio.value
            if mode == 'file' and self.stage1_entry_file_input:
                path = self.stage1_entry_file_input.value.strip()
                if path:
                    # For file mode, use on_entry format for entry point
                    if 'custom' not in stage_1_data:
                        stage_1_data['custom'] = {}
                    stage_1_data['custom']['on_entry'] = [path]
            elif mode == 'inline' and self.stage1_entry_inline_name_input and self.stage1_entry_inline_content_textarea:
                name = self.stage1_entry_inline_name_input.value.strip()
                content = self.stage1_entry_inline_content_textarea.value.strip()
                if name and content:
                    # Store inline script data for later processing
                    script_path = f'stage-1/custom/{name}'
                    stage_1_inline_scripts.append({
                        'path': script_path,
                        'content': content,
                        'type': 'entry_point'
                    })
                    if 'custom' not in stage_1_data:
                        stage_1_data['custom'] = {}
                    stage_1_data['custom']['on_entry'] = [script_path]
        
        # Collect Stage-2 configuration
        if self.stage2_entry_mode_radio and self.stage2_entry_mode_radio.value != 'none':
            mode = self.stage2_entry_mode_radio.value
            if mode == 'file' and self.stage2_entry_file_input:
                path = self.stage2_entry_file_input.value.strip()
                if path:
                    if 'custom' not in stage_2_data:
                        stage_2_data['custom'] = {}
                    stage_2_data['custom']['on_entry'] = [path]
            elif mode == 'inline' and self.stage2_entry_inline_name_input and self.stage2_entry_inline_content_textarea:
                name = self.stage2_entry_inline_name_input.value.strip()
                content = self.stage2_entry_inline_content_textarea.value.strip()
                if name and content:
                    script_path = f'stage-2/custom/{name}'
                    stage_2_inline_scripts.append({
                        'path': script_path,
                        'content': content,
                        'type': 'entry_point'
                    })
                    if 'custom' not in stage_2_data:
                        stage_2_data['custom'] = {}
                    stage_2_data['custom']['on_entry'] = [script_path]
        
        # Collect Stage-1 lifecycle scripts
        for lifecycle_type, scripts_list in self.stage1_lifecycle_scripts.items():
            script_paths = []
            for script_data in scripts_list:
                if script_data['type'] == 'file':
                    path = script_data['input'].value.strip()
                    if path:
                        script_paths.append(path)
                else:  # inline
                    name = script_data['name_input'].value.strip()
                    content = script_data['content_textarea'].value.strip()
                    if name and content:
                        script_path = f'stage-1/custom/{name}'
                        stage_1_inline_scripts.append({
                            'path': script_path,
                            'content': content,
                            'type': lifecycle_type
                        })
                        script_paths.append(script_path)
            
            if script_paths:
                if 'custom' not in stage_1_data:
                    stage_1_data['custom'] = {}
                stage_1_data['custom'][lifecycle_type] = script_paths
        
        # Collect Stage-2 lifecycle scripts
        for lifecycle_type, scripts_list in self.stage2_lifecycle_scripts.items():
            script_paths = []
            for script_data in scripts_list:
                if script_data['type'] == 'file':
                    path = script_data['input'].value.strip()
                    if path:
                        script_paths.append(path)
                else:  # inline
                    name = script_data['name_input'].value.strip()
                    content = script_data['content_textarea'].value.strip()
                    if name and content:
                        script_path = f'stage-2/custom/{name}'
                        stage_2_inline_scripts.append({
                            'path': script_path,
                            'content': content,
                            'type': lifecycle_type
                        })
                        script_paths.append(script_path)
            
            if script_paths:
                if 'custom' not in stage_2_data:
                    stage_2_data['custom'] = {}
                stage_2_data['custom'][lifecycle_type] = script_paths
        
        # Store inline scripts metadata for the save process
        if stage_1_inline_scripts:
            if '_inline_scripts' not in stage_1_data:
                stage_1_data['_inline_scripts'] = []
            stage_1_data['_inline_scripts'] = stage_1_inline_scripts
            
        if stage_2_inline_scripts:
            if '_inline_scripts' not in stage_2_data:
                stage_2_data['_inline_scripts'] = []
            stage_2_data['_inline_scripts'] = stage_2_inline_scripts
        
        return {
            'stage_1': stage_1_data,
            'stage_2': stage_2_data
        }
    
    def set_config_data(self, data: dict) -> None:
        """Set scripts configuration data."""
        try:
            stage_1_config = data.get('stage_1', {})
            stage_2_config = data.get('stage_2', {})
            
            # Clear existing lifecycle scripts UI
            self._clear_lifecycle_scripts()
            
            # Build inline scripts lookup from persisted metadata
            inline_scripts_lookup = self._build_inline_scripts_lookup(stage_1_config, stage_2_config)
            
            # Load from 'custom' structure (not 'scripts')
            stage_1_custom = stage_1_config.get('custom', {})
            stage_2_custom = stage_2_config.get('custom', {})
            
            # Load Stage-1 entry point from 'on_entry' lifecycle type
            if 'on_entry' in stage_1_custom:
                entry_paths = stage_1_custom['on_entry']
                if entry_paths and len(entry_paths) > 0:
                    entry_path = entry_paths[0]  # Take first entry point
                    self._load_entry_point('stage1', entry_path, inline_scripts_lookup)
            
            # Load Stage-2 entry point from 'on_entry' lifecycle type  
            if 'on_entry' in stage_2_custom:
                entry_paths = stage_2_custom['on_entry']
                if entry_paths and len(entry_paths) > 0:
                    entry_path = entry_paths[0]  # Take first entry point
                    self._load_entry_point('stage2', entry_path, inline_scripts_lookup)
            
            # Load Stage-1 lifecycle scripts
            for lifecycle_type in ['on_build', 'on_first_run', 'on_every_run', 'on_user_login']:
                if lifecycle_type in stage_1_custom:
                    script_paths = stage_1_custom[lifecycle_type]
                    for script_path in script_paths:
                        self._load_lifecycle_script('stage1', lifecycle_type, script_path, inline_scripts_lookup)
            
            # Load Stage-2 lifecycle scripts
            for lifecycle_type in ['on_build', 'on_first_run', 'on_every_run', 'on_user_login']:
                if lifecycle_type in stage_2_custom:
                    script_paths = stage_2_custom[lifecycle_type]
                    for script_path in script_paths:
                        self._load_lifecycle_script('stage2', lifecycle_type, script_path, inline_scripts_lookup)
                        
        except Exception as e:
            print(f"Error loading scripts configuration: {e}")
    
    def _build_inline_scripts_lookup(self, stage_1_config: dict, stage_2_config: dict) -> Dict[str, Dict[str, str]]:
        """Build lookup table for inline scripts from persisted metadata."""
        inline_scripts_lookup: Dict[str, Dict[str, str]] = {}
        
        # Process Stage-1 inline scripts metadata
        stage_1_inline_scripts = stage_1_config.get('_inline_scripts', [])
        for script_info in stage_1_inline_scripts:
            script_path = script_info.get('path', '')
            script_content = script_info.get('content', '')
            script_type = script_info.get('type', '')
            
            if script_path:
                inline_scripts_lookup[script_path] = {
                    'content': script_content,
                    'type': script_type
                }
        
        # Process Stage-2 inline scripts metadata
        stage_2_inline_scripts = stage_2_config.get('_inline_scripts', [])
        for script_info in stage_2_inline_scripts:
            script_path = script_info.get('path', '')
            script_content = script_info.get('content', '')
            script_type = script_info.get('type', '')
            
            if script_path:
                inline_scripts_lookup[script_path] = {
                    'content': script_content,
                    'type': script_type
                }
        
        return inline_scripts_lookup
    
    def _clear_lifecycle_scripts(self) -> None:
        """Clear existing lifecycle script UI elements."""
        # Clear Stage-1 lifecycle scripts
        for lifecycle_type in self.stage1_lifecycle_scripts:
            self.stage1_lifecycle_scripts[lifecycle_type] = []
            if lifecycle_type in self.stage1_lifecycle_containers:
                self.stage1_lifecycle_containers[lifecycle_type].clear()
        
        # Clear Stage-2 lifecycle scripts
        for lifecycle_type in self.stage2_lifecycle_scripts:
            self.stage2_lifecycle_scripts[lifecycle_type] = []
            if lifecycle_type in self.stage2_lifecycle_containers:
                self.stage2_lifecycle_containers[lifecycle_type].clear()
    
    def _load_entry_point(self, stage: str, entry_path: str, inline_scripts_lookup: Dict[str, Dict[str, str]]) -> None:
        """Load entry point configuration and set UI."""
        try:
            # Check if this script is in the inline scripts lookup
            is_inline_script = entry_path in inline_scripts_lookup
            
            if stage == 'stage1':
                if self.stage1_entry_mode_radio:
                    if is_inline_script:
                        # Set as inline mode with persisted content
                        self.stage1_entry_mode_radio.set_value('inline')
                        script_name = self._extract_script_name(entry_path)
                        script_content = inline_scripts_lookup[entry_path]['content']
                        
                        if self.stage1_entry_inline_name_input:
                            self.stage1_entry_inline_name_input.set_value(script_name)
                        if self.stage1_entry_inline_content_textarea:
                            self.stage1_entry_inline_content_textarea.set_value(script_content)
                    else:
                        # Set as file mode
                        self.stage1_entry_mode_radio.set_value('file')  
                        if self.stage1_entry_file_input:
                            self.stage1_entry_file_input.set_value(entry_path)
            else:  # stage2
                if self.stage2_entry_mode_radio:
                    if is_inline_script:
                        # Set as inline mode with persisted content
                        self.stage2_entry_mode_radio.set_value('inline')
                        script_name = self._extract_script_name(entry_path)
                        script_content = inline_scripts_lookup[entry_path]['content']
                        
                        if self.stage2_entry_inline_name_input:
                            self.stage2_entry_inline_name_input.set_value(script_name)
                        if self.stage2_entry_inline_content_textarea:
                            self.stage2_entry_inline_content_textarea.set_value(script_content)
                    else:
                        # Set as file mode
                        self.stage2_entry_mode_radio.set_value('file')
                        if self.stage2_entry_file_input:
                            self.stage2_entry_file_input.set_value(entry_path)
                            
        except Exception as e:
            print(f"Error loading entry point {entry_path}: {e}")
    
    def _load_lifecycle_script(self, stage: str, lifecycle_type: str, script_path: str, inline_scripts_lookup: Dict[str, Dict[str, str]]) -> None:
        """Load a lifecycle script and create appropriate UI element."""
        try:
            # Check if this script is in the inline scripts lookup
            is_inline_script = script_path in inline_scripts_lookup
            
            # Determine path prefix for UI
            path_prefix = 'stage-1' if stage == 'stage1' else 'stage-2'
            
            if is_inline_script:
                # Create inline script UI with persisted content
                script_name = self._extract_script_name(script_path)
                script_content = inline_scripts_lookup[script_path]['content']
                self._add_lifecycle_script_from_data(stage, lifecycle_type, 'inline', path_prefix, script_name, script_content)
            else:
                # Create file-based script UI
                self._add_lifecycle_script_from_data(stage, lifecycle_type, 'file', path_prefix, script_path, '')
                
        except Exception as e:
            print(f"Error loading lifecycle script {script_path}: {e}")
    
    def _extract_script_name(self, script_path: str) -> str:
        """Extract script name from path."""
        from pathlib import Path
        return Path(script_path).name
    
    def _add_lifecycle_script_from_data(self, stage: str, lifecycle_type: str, script_type: str, 
                                       path_prefix: str, script_path_or_name: str, content: str) -> None:
        """Add a lifecycle script UI element from loaded data."""
        try:
            # This is similar to _add_lifecycle_script but for loading existing scripts
            script_id = f'{stage}-{lifecycle_type}-{script_type}-{self._generate_uuid()}'
            container = self.stage1_lifecycle_containers[lifecycle_type] if stage == 'stage1' else self.stage2_lifecycle_containers[lifecycle_type]
            
            with container:
                with ui.card().classes('w-full p-3 mb-3') as script_card:
                    if script_type == 'file':
                        # File path script
                        with ui.column().classes('w-full'):
                            script_input = ui.input(
                                placeholder=f'{path_prefix}/custom/script-{self._generate_uuid()}.bash --param=value',
                                value=script_path_or_name
                            ).classes('w-full mb-2')
                            
                            with ui.row().classes('gap-2 w-full'):
                                ui.button('✏️ Edit', on_click=lambda inp=script_input: self._edit_file_path(inp)) \
                                    .classes('bg-yellow-600 hover:bg-yellow-700 text-white text-sm')
                                ui.button('🗑️ Remove', on_click=lambda: self._remove_script(script_card, stage, lifecycle_type, script_id)) \
                                    .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                            
                            script_input.on('input', lambda e, s=stage, lt=lifecycle_type: self._on_lifecycle_script_change(s, lt))
                        
                        # Store script data
                        script_data = {
                            'id': script_id,
                            'type': script_type,
                            'card': script_card,
                            'input': script_input
                        }
                    else:
                        # Inline script
                        with ui.column().classes('w-full'):
                            # Script name display
                            with ui.row().classes('items-center mb-2 gap-0 w-full'):
                                ui.label(f'{path_prefix}/custom/').classes('px-3 py-2 bg-gray-100 border border-r-0 rounded-l text-sm font-mono')
                                script_name_input = ui.input(
                                    value=script_path_or_name,
                                    placeholder='script-name.bash'
                                ).classes('w-full rounded-l-none')
                            
                            # Script content
                            script_content_textarea = ui.textarea(
                                placeholder="#!/bin/bash\\necho 'Inline script content'",
                                value=content
                            ).classes('w-full mb-2').props('rows=3')
                            
                            with ui.row().classes('gap-2 w-full'):
                                ui.button('👁️ View', on_click=lambda name=script_name_input, content_ta=script_content_textarea: self._view_inline_script(name.value, content_ta.value)) \
                                    .classes('bg-blue-600 hover:bg-blue-700 text-white text-sm')
                                ui.button('✏️ Edit', on_click=lambda name=script_name_input, content_ta=script_content_textarea: self._edit_inline_script(name.value, content_ta)) \
                                    .classes('bg-yellow-600 hover:bg-yellow-700 text-white text-sm')
                                ui.button('🗑️ Remove', on_click=lambda: self._remove_script(script_card, stage, lifecycle_type, script_id)) \
                                    .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                            
                            script_name_input.on('input', lambda e, s=stage, lt=lifecycle_type: self._on_lifecycle_script_change(s, lt))
                            script_content_textarea.on('input', lambda e, s=stage, lt=lifecycle_type: self._on_lifecycle_script_change(s, lt))
                        
                        # Store script data
                        script_data = {
                            'id': script_id,
                            'type': script_type,
                            'card': script_card,
                            'name_input': script_name_input,
                            'content_textarea': script_content_textarea
                        }
                    
                    # Add to scripts list
                    if stage == 'stage1':
                        self.stage1_lifecycle_scripts[lifecycle_type].append(script_data)
                    else:
                        self.stage2_lifecycle_scripts[lifecycle_type].append(script_data)
                        
        except Exception as e:
            print(f"Error adding lifecycle script UI for {script_path_or_name}: {e}")