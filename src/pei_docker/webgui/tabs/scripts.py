"""
Scripts tab for PeiDocker Web GUI with proper data binding.

This tab handles custom entry points and lifecycle hook scripts 
for Stage-1 and Stage-2 sequential image builds.
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Any, Tuple
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab
from pei_docker.webgui.constants import (
    CustomScriptLifecycleTypes,
    ScriptTypes,
    EntryModes
)
import uuid

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class ScriptsTab(BaseTab):
    """Scripts configuration tab with proper data binding."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        
        # References to UI containers for lifecycle scripts
        self.stage1_lifecycle_containers: Dict[str, ui.column] = {}
        self.stage2_lifecycle_containers: Dict[str, ui.column] = {}
        
        # Lifecycle types using constants to avoid typos
        self.lifecycle_types: List[Tuple[str, str]] = CustomScriptLifecycleTypes.get_types_with_descriptions()
    
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
            self._create_stage_scripts_section('stage1', '🏗️ Stage-1 Image Scripts', 'stage-1', 
                                             self.app.ui_state.stage_1.scripts)
            
            # Stage-2 Scripts
            self._create_stage_scripts_section('stage2', '🏗️ Stage-2 Image Scripts (builds on top of Stage-1, inheriting all its resources)', 'stage-2',
                                             self.app.ui_state.stage_2.scripts)
        
        return container
    
    def _create_stage_scripts_section(self, stage: str, title: str, path_prefix: str, scripts_ui: Any) -> None:
        """Create a stage scripts section with data binding."""
        with self.create_card(title):
            # Custom Entry Point
            with self.create_form_group('Custom Entry Point', f'Override the default entry point for {stage.upper()}'):
                
                # Entry point mode selection - bind to UI state
                with ui.column().classes('mb-4 w-full'):
                    entry_mode_radio = ui.radio(
                        options={
                            EntryModes.NONE: 'Use default',
                            EntryModes.FILE: 'File path',
                            EntryModes.INLINE: 'Inline script'
                        }
                    ).bind_value(scripts_ui, 'entry_mode').props('inline')
                
                # Entry point configuration
                with ui.column().classes('w-full') as entry_config_container:
                    entry_config_container.bind_visibility_from(scripts_ui, 'entry_mode', lambda v: v != EntryModes.NONE)
                    
                    # File path mode
                    with ui.column().classes('w-full') as file_mode_container:
                        ui.input(
                            placeholder=f'{path_prefix}/custom/script-{self._generate_uuid()}.bash --param=value'
                        ).bind_value(scripts_ui, 'entry_file_path').classes('w-full').on_value_change(lambda: self.mark_modified()) \
                            .props(f'data-testid="{stage}-entry-file-path"')
                        
                        file_mode_container.bind_visibility_from(scripts_ui, 'entry_mode', lambda v: v == EntryModes.FILE)
                    
                    # Inline script mode
                    with ui.column().classes('w-full') as inline_mode_container:
                        with ui.row().classes('items-center mb-2 gap-0 w-full'):
                            ui.label(f'{path_prefix}/custom/').classes('px-3 py-2 bg-gray-100 border border-r-0 rounded-l text-sm font-mono')
                            ui.input(
                                placeholder='entry-script.bash'
                            ).bind_value(scripts_ui, 'entry_inline_name').classes('w-full rounded-l-none').on_value_change(lambda: self.mark_modified()) \
                                .props(f'data-testid="{stage}-entry-inline-name"')
                        
                        ui.textarea(
                            placeholder='#!/bin/bash\necho \'Custom entry point\''
                        ).bind_value(scripts_ui, 'entry_inline_content').classes('w-full').props('rows=4').on_value_change(lambda: self.mark_modified()) \
                            .props(f'data-testid="{stage}-entry-inline-content"')
                        
                        inline_mode_container.bind_visibility_from(scripts_ui, 'entry_mode', lambda v: v == EntryModes.INLINE)
            
            # Lifecycle Scripts
            with self.create_form_group('Lifecycle Scripts', 'Scripts that run at specific lifecycle events'):
                
                for lifecycle_type, description in self.lifecycle_types:
                    with ui.column().classes('mb-4 w-full'):
                        ui.label(f'{lifecycle_type} - {description}').classes('text-sm font-medium text-gray-700 mb-2')
                        
                        # Add script buttons
                        with ui.row().classes('gap-2 mb-2 w-full'):
                            ui.button('📁 Add File', 
                                    on_click=lambda lt=lifecycle_type, s=stage, pp=path_prefix, sui=scripts_ui: self._add_lifecycle_script(s, lt, ScriptTypes.FILE, pp, sui)) \
                                .classes('bg-gray-600 hover:bg-gray-700 text-white text-sm') \
                                .props(f'data-testid="{stage}-{lifecycle_type}-add-file-btn"')
                            ui.button('📝 Add Inline', 
                                    on_click=lambda lt=lifecycle_type, s=stage, pp=path_prefix, sui=scripts_ui: self._add_lifecycle_script(s, lt, ScriptTypes.INLINE, pp, sui)) \
                                .classes('bg-gray-600 hover:bg-gray-700 text-white text-sm') \
                                .props(f'data-testid="{stage}-{lifecycle_type}-add-inline-btn"')
                        
                        # Scripts container
                        with ui.column().classes('w-full') as scripts_container:
                            pass
                        
                        # Store container reference
                        if stage == 'stage1':
                            self.stage1_lifecycle_containers[lifecycle_type] = scripts_container
                        else:
                            self.stage2_lifecycle_containers[lifecycle_type] = scripts_container
                        
                        # Load existing scripts from model
                        self._load_lifecycle_scripts_from_model(stage, lifecycle_type, scripts_ui, path_prefix)
    
    def _generate_uuid(self) -> str:
        """Generate a short UUID for script names."""
        return str(uuid.uuid4()).replace('-', '')[:8]
    
    def _add_lifecycle_script(self, stage: str, lifecycle_type: str, script_type: str, path_prefix: str, scripts_ui: Any) -> None:
        """Add a lifecycle script with data binding."""
        script_id = f'{stage}-{lifecycle_type}-{script_type}-{self._generate_uuid()}'
        container = self.stage1_lifecycle_containers[lifecycle_type] if stage == 'stage1' else self.stage2_lifecycle_containers[lifecycle_type]
        
        # Get or initialize the lifecycle scripts list in the model
        if scripts_ui.lifecycle_scripts is None:
            scripts_ui.lifecycle_scripts = {}
        
        if lifecycle_type not in scripts_ui.lifecycle_scripts:
            scripts_ui.lifecycle_scripts[lifecycle_type] = []
        
        # Create script data
        script_data = {
            'id': script_id,
            'type': script_type,
            'path': '' if script_type == ScriptTypes.FILE else f'{path_prefix}/custom/script-{self._generate_uuid()}.bash',
            'content': '' if script_type == ScriptTypes.FILE else '#!/bin/bash\necho \'Inline script content\''
        }
        
        # Add to model
        scripts_ui.lifecycle_scripts[lifecycle_type].append(script_data)
        
        # Create UI for the script
        self._create_lifecycle_script_ui(container, stage, lifecycle_type, script_data, scripts_ui, path_prefix)
        
        self.mark_modified()
    
    def _create_lifecycle_script_ui(self, container: ui.column, stage: str, lifecycle_type: str, 
                                  script_data: Dict[str, Any], scripts_ui: Any, path_prefix: str) -> None:
        """Create UI for a lifecycle script with data binding."""
        with container:
            with ui.card().classes('w-full p-3 mb-3') as script_card:
                if script_data['type'] == ScriptTypes.FILE:
                    # File path script
                    with ui.column().classes('w-full'):
                        script_input = ui.input(
                            placeholder=f'{path_prefix}/custom/script-{self._generate_uuid()}.bash --param=value',
                            value=script_data.get('path', '')
                        ).classes('w-full mb-2').props(f'data-testid="{stage}-{lifecycle_type}-file-{script_data["id"]}"')
                        
                        # Bind input to update the model
                        script_input.on_value_change(lambda e: self._update_script_path(stage, lifecycle_type, script_data['id'], e.value, scripts_ui))
                        
                        with ui.row().classes('gap-2 w-full'):
                            ui.button('✏️ Edit', on_click=lambda inp=script_input: self._edit_file_path(inp)) \
                                .classes('bg-yellow-600 hover:bg-yellow-700 text-white text-sm')
                            ui.button('🗑️ Remove', on_click=lambda: self._remove_script(script_card, stage, lifecycle_type, script_data['id'], scripts_ui)) \
                                .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                else:
                    # Inline script
                    with ui.column().classes('w-full'):
                        # Script name display
                        script_name = script_data.get('path', '').split('/')[-1] if '/' in script_data.get('path', '') else script_data.get('path', '')
                        
                        with ui.row().classes('items-center mb-2 gap-0 w-full'):
                            ui.label(f'{path_prefix}/custom/').classes('px-3 py-2 bg-gray-100 border border-r-0 rounded-l text-sm font-mono')
                            script_name_input = ui.input(
                                value=script_name,
                                placeholder='script-name.bash'
                            ).classes('w-full rounded-l-none').props(f'data-testid="{stage}-{lifecycle_type}-inline-name-{script_data["id"]}"')
                        
                        # Script content
                        script_content_textarea = ui.textarea(
                            placeholder='#!/bin/bash\necho \'Inline script content\'',
                            value=script_data.get('content', '')
                        ).classes('w-full mb-2').props('rows=3').props(f'data-testid="{stage}-{lifecycle_type}-inline-content-{script_data["id"]}"')
                        
                        # Bind inputs to update the model
                        script_name_input.on_value_change(lambda e: self._update_inline_script(stage, lifecycle_type, script_data['id'], 
                                                                                         f'{path_prefix}/custom/{e.value}', 
                                                                                         script_content_textarea.value, scripts_ui))
                        script_content_textarea.on_value_change(lambda e: self._update_inline_script(stage, lifecycle_type, script_data['id'],
                                                                                               f'{path_prefix}/custom/{script_name_input.value}',
                                                                                               e.value, scripts_ui))
                        
                        with ui.row().classes('gap-2 w-full'):
                            ui.button('👁️ View', on_click=lambda: self._view_inline_script(script_name_input.value, script_content_textarea.value)) \
                                .classes('bg-blue-600 hover:bg-blue-700 text-white text-sm')
                            ui.button('✏️ Edit', on_click=lambda ta=script_content_textarea: self._edit_inline_script(script_name_input.value, ta)) \
                                .classes('bg-yellow-600 hover:bg-yellow-700 text-white text-sm')
                            ui.button('🗑️ Remove', on_click=lambda: self._remove_script(script_card, stage, lifecycle_type, script_data['id'], scripts_ui)) \
                                .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
    
    def _load_lifecycle_scripts_from_model(self, stage: str, lifecycle_type: str, scripts_ui: Any, path_prefix: str) -> None:
        """Load lifecycle scripts from the model and create UI elements."""
        lifecycle_scripts = scripts_ui.lifecycle_scripts
        
        if lifecycle_type in lifecycle_scripts:
            container = self.stage1_lifecycle_containers[lifecycle_type] if stage == 'stage1' else self.stage2_lifecycle_containers[lifecycle_type]
            
            for script_data in lifecycle_scripts[lifecycle_type]:
                self._create_lifecycle_script_ui(container, stage, lifecycle_type, script_data, scripts_ui, path_prefix)
    
    def _update_script_path(self, stage: str, lifecycle_type: str, script_id: str, new_path: str, scripts_ui: Any) -> None:
        """Update script path in the model."""
        lifecycle_scripts = scripts_ui.lifecycle_scripts
        
        if lifecycle_type in lifecycle_scripts:
            for script in lifecycle_scripts[lifecycle_type]:
                if script['id'] == script_id:
                    script['path'] = new_path
                    break
        
        self.mark_modified()
    
    def _update_inline_script(self, stage: str, lifecycle_type: str, script_id: str, new_path: str, new_content: str, scripts_ui: Any) -> None:
        """Update inline script in the model."""
        lifecycle_scripts = scripts_ui.lifecycle_scripts
        
        if lifecycle_type in lifecycle_scripts:
            for script in lifecycle_scripts[lifecycle_type]:
                if script['id'] == script_id:
                    script['path'] = new_path
                    script['content'] = new_content
                    break
        
        self.mark_modified()
    
    def _remove_script(self, script_card: Any, stage: str, lifecycle_type: str, script_id: str, scripts_ui: Any) -> None:
        """Remove a lifecycle script."""
        script_card.delete()
        
        # Remove from model
        lifecycle_scripts = scripts_ui.lifecycle_scripts
        
        if lifecycle_type in lifecycle_scripts:
            lifecycle_scripts[lifecycle_type] = [
                script for script in lifecycle_scripts[lifecycle_type]
                if script['id'] != script_id
            ]
        
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
        for stage, scripts_ui in [('stage1', self.app.ui_state.stage_1.scripts), ('stage2', self.app.ui_state.stage_2.scripts)]:
            entry_mode = scripts_ui.entry_mode
            
            if entry_mode == EntryModes.FILE:
                path = scripts_ui.entry_file_path.strip()
                if not path:
                    errors.append(f"{stage.upper()} entry point: File path is required")
                elif not self._validate_script_path(path, stage):
                    errors.append(f"{stage.upper()} entry point: Invalid path '{path}' for {stage}")
            elif entry_mode == EntryModes.INLINE:
                name = scripts_ui.entry_inline_name.strip()
                content = scripts_ui.entry_inline_content.strip()
                if not name:
                    errors.append(f"{stage.upper()} entry point: Script name is required")
                if not content:
                    errors.append(f"{stage.upper()} entry point: Script content is required")
            
            # Validate lifecycle scripts
            lifecycle_scripts = scripts_ui.lifecycle_scripts
            for lifecycle_type in [CustomScriptLifecycleTypes.ON_BUILD, CustomScriptLifecycleTypes.ON_FIRST_RUN, 
                                   CustomScriptLifecycleTypes.ON_EVERY_RUN, CustomScriptLifecycleTypes.ON_USER_LOGIN]:
                if lifecycle_type in lifecycle_scripts:
                    for i, script in enumerate(lifecycle_scripts[lifecycle_type]):
                        if script['type'] == ScriptTypes.FILE:
                            path = script.get('path', '').strip()
                            if not path:
                                errors.append(f"{stage.upper()} {lifecycle_type} script {i+1}: File path is required")
                            elif not self._validate_script_path(path, stage):
                                errors.append(f"{stage.upper()} {lifecycle_type} script {i+1}: Invalid path '{path}' for {stage}")
                        elif script['type'] == ScriptTypes.INLINE:
                            if not script.get('path', '').strip():
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
        """Get scripts configuration data from the UI state model."""
        stage_1_data: Dict[str, Any] = {}
        stage_2_data: Dict[str, Any] = {}
        
        # Get UI state
        stage_1_scripts = self.app.ui_state.stage_1.scripts
        stage_2_scripts = self.app.ui_state.stage_2.scripts
        
        # Collect Stage-1 configuration
        if stage_1_scripts.entry_mode != EntryModes.NONE:
            if stage_1_scripts.entry_mode == EntryModes.FILE:
                path = stage_1_scripts.entry_file_path.strip()
                if path:
                    if 'custom' not in stage_1_data:
                        stage_1_data['custom'] = {}
                    stage_1_data['custom'][CustomScriptLifecycleTypes.ON_ENTRY] = [path]
            elif stage_1_scripts.entry_mode == EntryModes.INLINE:
                name = stage_1_scripts.entry_inline_name.strip()
                content = stage_1_scripts.entry_inline_content.strip()
                if name and content:
                    script_path = f'stage-1/custom/{name}'
                    if 'custom' not in stage_1_data:
                        stage_1_data['custom'] = {}
                    stage_1_data['custom'][CustomScriptLifecycleTypes.ON_ENTRY] = [script_path]
                    # Store inline script metadata
                    if '_inline_scripts' not in stage_1_data:
                        stage_1_data['_inline_scripts'] = []
                    stage_1_data['_inline_scripts'].append({
                        'path': script_path,
                        'content': content,
                        'type': 'entry_point'
                    })
        
        # Collect Stage-2 configuration
        if stage_2_scripts.entry_mode != EntryModes.NONE:
            if stage_2_scripts.entry_mode == EntryModes.FILE:
                path = stage_2_scripts.entry_file_path.strip()
                if path:
                    if 'custom' not in stage_2_data:
                        stage_2_data['custom'] = {}
                    stage_2_data['custom'][CustomScriptLifecycleTypes.ON_ENTRY] = [path]
            elif stage_2_scripts.entry_mode == EntryModes.INLINE:
                name = stage_2_scripts.entry_inline_name.strip()
                content = stage_2_scripts.entry_inline_content.strip()
                if name and content:
                    script_path = f'stage-2/custom/{name}'
                    if 'custom' not in stage_2_data:
                        stage_2_data['custom'] = {}
                    stage_2_data['custom'][CustomScriptLifecycleTypes.ON_ENTRY] = [script_path]
                    # Store inline script metadata
                    if '_inline_scripts' not in stage_2_data:
                        stage_2_data['_inline_scripts'] = []
                    stage_2_data['_inline_scripts'].append({
                        'path': script_path,
                        'content': content,
                        'type': 'entry_point'
                    })
        
        # Collect lifecycle scripts from UI state
        for stage_scripts, stage_data, stage_prefix in [(stage_1_scripts, stage_1_data, 'stage-1'), 
                                                        (stage_2_scripts, stage_2_data, 'stage-2')]:
            lifecycle_scripts = stage_scripts.lifecycle_scripts
            
            for lifecycle_type, scripts_list in lifecycle_scripts.items():
                script_paths = []
                for script_data in scripts_list:
                    if script_data['type'] == ScriptTypes.FILE:
                        path = script_data.get('path', '').strip()
                        if path:
                            script_paths.append(path)
                    else:  # inline
                        path = script_data.get('path', '').strip()
                        content = script_data.get('content', '').strip()
                        if path and content:
                            script_paths.append(path)
                            # Store inline script metadata
                            if '_inline_scripts' not in stage_data:
                                stage_data['_inline_scripts'] = []
                            stage_data['_inline_scripts'].append({
                                'path': path,
                                'content': content,
                                'type': lifecycle_type
                            })
                
                if script_paths:
                    if 'custom' not in stage_data:
                        stage_data['custom'] = {}
                    stage_data['custom'][lifecycle_type] = script_paths
        
        return {
            'stage_1': stage_1_data,
            'stage_2': stage_2_data
        }
    
    def set_config_data(self, data: dict) -> None:
        """Set scripts configuration data to the UI state model."""
        try:
            stage_1_config = data.get('stage_1', {})
            stage_2_config = data.get('stage_2', {})
            
            # Get UI state models
            stage_1_scripts = self.app.ui_state.stage_1.scripts
            stage_2_scripts = self.app.ui_state.stage_2.scripts
            
            # Clear existing lifecycle scripts
            stage_1_scripts.lifecycle_scripts = {}
            stage_2_scripts.lifecycle_scripts = {}
            
            # Build inline scripts lookup from persisted metadata
            inline_scripts_lookup = self._build_inline_scripts_lookup(stage_1_config, stage_2_config)
            
            # Load Stage-1 configuration
            stage_1_custom = stage_1_config.get('custom', {})
            if CustomScriptLifecycleTypes.ON_ENTRY in stage_1_custom:
                entry_paths = stage_1_custom[CustomScriptLifecycleTypes.ON_ENTRY]
                if entry_paths and len(entry_paths) > 0:
                    entry_path = entry_paths[0]
                    if entry_path in inline_scripts_lookup:
                        # Inline script
                        stage_1_scripts.entry_mode = EntryModes.INLINE
                        script_name = entry_path.split('/')[-1]
                        stage_1_scripts.entry_inline_name = script_name
                        stage_1_scripts.entry_inline_content = inline_scripts_lookup[entry_path]['content']
                    else:
                        # File path
                        stage_1_scripts.entry_mode = EntryModes.FILE
                        stage_1_scripts.entry_file_path = entry_path
            else:
                stage_1_scripts.entry_mode = EntryModes.NONE
            
            # Load Stage-2 configuration
            stage_2_custom = stage_2_config.get('custom', {})
            if CustomScriptLifecycleTypes.ON_ENTRY in stage_2_custom:
                entry_paths = stage_2_custom[CustomScriptLifecycleTypes.ON_ENTRY]
                if entry_paths and len(entry_paths) > 0:
                    entry_path = entry_paths[0]
                    if entry_path in inline_scripts_lookup:
                        # Inline script
                        stage_2_scripts.entry_mode = EntryModes.INLINE
                        script_name = entry_path.split('/')[-1]
                        stage_2_scripts.entry_inline_name = script_name
                        stage_2_scripts.entry_inline_content = inline_scripts_lookup[entry_path]['content']
                    else:
                        # File path
                        stage_2_scripts.entry_mode = EntryModes.FILE
                        stage_2_scripts.entry_file_path = entry_path
            else:
                stage_2_scripts.entry_mode = EntryModes.NONE
            
            # Load lifecycle scripts
            for lifecycle_type in [CustomScriptLifecycleTypes.ON_BUILD, CustomScriptLifecycleTypes.ON_FIRST_RUN, 
                                   CustomScriptLifecycleTypes.ON_EVERY_RUN, CustomScriptLifecycleTypes.ON_USER_LOGIN]:
                # Stage-1 lifecycle scripts
                if lifecycle_type in stage_1_custom:
                    scripts_list = []
                    for script_path in stage_1_custom[lifecycle_type]:
                        if script_path in inline_scripts_lookup:
                            # Inline script
                            scripts_list.append({
                                'id': f'stage1-{lifecycle_type}-inline-{self._generate_uuid()}',
                                'type': ScriptTypes.INLINE,
                                'path': script_path,
                                'content': inline_scripts_lookup[script_path]['content']
                            })
                        else:
                            # File path
                            scripts_list.append({
                                'id': f'stage1-{lifecycle_type}-file-{self._generate_uuid()}',
                                'type': ScriptTypes.FILE,
                                'path': script_path,
                                'content': ''
                            })
                    stage_1_scripts.lifecycle_scripts[lifecycle_type] = scripts_list
                
                # Stage-2 lifecycle scripts
                if lifecycle_type in stage_2_custom:
                    scripts_list = []
                    for script_path in stage_2_custom[lifecycle_type]:
                        if script_path in inline_scripts_lookup:
                            # Inline script
                            scripts_list.append({
                                'id': f'stage2-{lifecycle_type}-inline-{self._generate_uuid()}',
                                'type': ScriptTypes.INLINE,
                                'path': script_path,
                                'content': inline_scripts_lookup[script_path]['content']
                            })
                        else:
                            # File path
                            scripts_list.append({
                                'id': f'stage2-{lifecycle_type}-file-{self._generate_uuid()}',
                                'type': ScriptTypes.FILE,
                                'path': script_path,
                                'content': ''
                            })
                    stage_2_scripts.lifecycle_scripts[lifecycle_type] = scripts_list
                        
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