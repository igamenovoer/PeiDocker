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
            with ui.card().classes('w-full p-4 mb-6 bg-blue-50 border-blue-200'):
                ui.label('ℹ️ Important: Script Path Access Rules').classes('text-lg font-semibold text-blue-800 mb-3')
                
                with ui.column().classes('text-sm'):
                    with ui.column().classes('mb-3'):
                        ui.label('🏗️ Stage-1 Scripts:').classes('font-semibold')
                        with ui.column().classes('ml-4 mt-1'):
                            ui.markdown('• Can **ONLY** reference paths starting with `stage-1/`').classes('text-sm')
                            ui.markdown('• **Cannot access** any `stage-2/` paths (stage-2 doesn\'t exist yet)').classes('text-sm')
                            ui.markdown('• Examples: `stage-1/custom/script.sh`, `stage-1/system/setup.sh`').classes('text-sm')
                    
                    with ui.column():
                        ui.label('🏗️ Stage-2 Scripts:').classes('font-semibold')
                        with ui.column().classes('ml-4 mt-1'):
                            ui.markdown('• Can reference paths starting with **both** `stage-1/` and `stage-2/`').classes('text-sm')
                            ui.markdown('• Has access to all stage-1 resources plus stage-2 resources').classes('text-sm')
                            ui.markdown('• Examples: `stage-2/custom/app.sh`, `stage-1/system/base.sh`').classes('text-sm')
                    
                    with ui.card().classes('mt-3 p-2 bg-yellow-50 border-yellow-200'):
                        ui.label('**Why?** Stage-1 builds first and becomes the foundation. Stage-2 builds on top of Stage-1, inheriting all its resources.') \
                            .classes('text-xs font-semibold')
            
            # Stage-1 Scripts
            self._create_stage_scripts_section('stage1', '🏗️ Stage-1 Image Scripts', 'stage-1')
            
            # Stage-2 Scripts
            self._create_stage_scripts_section('stage2', '🏗️ Stage-2 Image Scripts', 'stage-2')
        
        return container
    
    def _create_stage_scripts_section(self, stage: str, title: str, path_prefix: str) -> None:
        """Create a stage scripts section."""
        with self.create_card(title):
            # Custom Entry Point
            with self.create_form_group('Custom Entry Point', f'Override the default entry point for {stage.upper()}'):
                
                # Entry point mode selection
                with ui.column().classes('mb-4'):
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
                    with ui.column() as file_mode_container:
                        entry_file_input = ui.input(
                            placeholder=f'{path_prefix}/custom/script-{self._generate_uuid()}.bash --param=value'
                        ).classes('w-full')
                        entry_file_input.on('input', lambda e, s=stage: self._on_entry_config_change(s))
                        
                        file_mode_container.bind_visibility_from(entry_mode_radio, 'value', lambda v: v == 'file')
                    
                    # Inline script mode
                    with ui.column() as inline_mode_container:
                        with ui.row().classes('items-center mb-2 gap-0'):
                            ui.label(f'{path_prefix}/custom/').classes('px-3 py-2 bg-gray-100 border border-r-0 rounded-l text-sm font-mono')
                            entry_inline_name_input = ui.input(
                                placeholder=f'script-{self._generate_uuid()}.bash',
                                value=f'script-{self._generate_uuid()}.bash'
                            ).classes('flex-1 rounded-l-none').props('readonly')
                        
                        entry_inline_content_textarea = ui.textarea(
                            placeholder='#!/bin/bash\necho \'Custom entry point\'',
                            value='#!/bin/bash\necho \'Custom entry point\''
                        ).classes('w-full').props('rows=4')
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
                    with ui.column().classes('mb-4'):
                        ui.label(f'{lifecycle_type} - {description}').classes('text-sm font-medium text-gray-700 mb-2')
                        
                        # Add script buttons
                        with ui.row().classes('gap-2 mb-2'):
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
                        
                        with ui.row().classes('gap-2'):
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
                        with ui.row().classes('items-center mb-2 gap-0'):
                            ui.label(f'{path_prefix}/custom/').classes('px-3 py-2 bg-gray-100 border border-r-0 rounded-l text-sm font-mono')
                            script_name_input = ui.input(
                                value=f'script-{script_uuid}.bash'
                            ).classes('flex-1 rounded-l-none').props('readonly')
                        
                        # Script content
                        script_content_textarea = ui.textarea(
                            placeholder='#!/bin/bash\necho \'Inline script content\'',
                            value='#!/bin/bash\necho \'Inline script content\''
                        ).classes('w-full mb-2').props('rows=3')
                        
                        with ui.row().classes('gap-2'):
                            ui.button('👁️ View', on_click=lambda name=script_name_input, content=script_content_textarea: self._view_inline_script(name.value, content.value)) \
                                .classes('bg-blue-600 hover:bg-blue-700 text-white text-sm')
                            ui.button('✏️ Edit', on_click=lambda name=script_name_input, content=script_content_textarea: self._edit_inline_script(name.value, content)) \
                                .classes('bg-yellow-600 hover:bg-yellow-700 text-white text-sm')
                            ui.button('🗑️ Remove', on_click=lambda: self._remove_script(script_card, stage, lifecycle_type, script_id)) \
                                .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                        
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
        """Get scripts configuration data."""
        return {
            'stage_1': {
                'scripts': self.app.data.config.stage_1.get('scripts', {})
            },
            'stage_2': {
                'scripts': self.app.data.config.stage_2.get('scripts', {})
            }
        }
    
    def set_config_data(self, data: dict) -> None:
        """Set scripts configuration data."""
        stage_1_config = data.get('stage_1', {})
        stage_2_config = data.get('stage_2', {})
        
        # Set entry points
        stage_1_scripts = stage_1_config.get('scripts', {})
        stage_2_scripts = stage_2_config.get('scripts', {})
        
        # Load Stage-1 entry point
        if 'entry_point' in stage_1_scripts:
            entry_point = stage_1_scripts['entry_point']
            if self.stage1_entry_mode_radio:
                self.stage1_entry_mode_radio.set_value(entry_point['type'])
                
                if entry_point['type'] == 'file' and self.stage1_entry_file_input:
                    self.stage1_entry_file_input.set_value(entry_point.get('path', ''))
                elif entry_point['type'] == 'inline':
                    if self.stage1_entry_inline_name_input:
                        self.stage1_entry_inline_name_input.set_value(entry_point.get('name', ''))
                    if self.stage1_entry_inline_content_textarea:
                        self.stage1_entry_inline_content_textarea.set_value(entry_point.get('content', ''))
        
        # Load Stage-2 entry point
        if 'entry_point' in stage_2_scripts:
            entry_point = stage_2_scripts['entry_point']
            if self.stage2_entry_mode_radio:
                self.stage2_entry_mode_radio.set_value(entry_point['type'])
                
                if entry_point['type'] == 'file' and self.stage2_entry_file_input:
                    self.stage2_entry_file_input.set_value(entry_point.get('path', ''))
                elif entry_point['type'] == 'inline':
                    if self.stage2_entry_inline_name_input:
                        self.stage2_entry_inline_name_input.set_value(entry_point.get('name', ''))
                    if self.stage2_entry_inline_content_textarea:
                        self.stage2_entry_inline_content_textarea.set_value(entry_point.get('content', ''))
        
        # Load lifecycle scripts (this would be more complex in a real implementation)
        # For now, we'll skip loading existing lifecycle scripts to avoid complexity