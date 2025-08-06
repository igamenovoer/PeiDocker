"""
Summary tab for PeiDocker Web GUI - Refactored with data binding.

This tab provides a complete configuration review, validation status,
and actions for saving and exporting the project using the UIStateBridge
to transform ui-data-model to business-data-model.
"""

from typing import TYPE_CHECKING, List, Tuple, Dict, Optional, Any
from pathlib import Path
from nicegui import ui, app
from pei_docker.webgui.tabs.base import BaseTab
import yaml
import asyncio
import tempfile
import zipfile

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class SummaryTab(BaseTab):
    """Summary and validation tab with proper data transformation."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.save_button: Optional[ui.button] = None
        self.configure_button: Optional[ui.button] = None
        self.download_button: Optional[ui.button] = None
        self.config_preview_container: Optional[ui.column] = None
        self.validation_container: Optional[ui.column] = None
    
    def render(self) -> ui.element:
        """Render the summary tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '📋 Configuration Summary',
                'Review your complete PeiDocker configuration and save your user_config.yml file'
            )
            
            # Validation Status
            self._create_validation_section()
            
            # Generated user_config.yml Preview
            self._create_config_preview()
            
            # Actions section
            self._create_actions_section()
            
            # Refresh the summary initially
            self.refresh_summary()
        
        return container
    
    def _create_validation_section(self) -> None:
        """Create the validation status section."""
        with self.create_card('✅ Validation Status'):
            with ui.column().classes('w-full') as validation_container:
                self.validation_container = validation_container
    
    def _create_actions_section(self) -> None:
        """Create the actions section with save, configure, and download buttons."""
        with self.create_card('💾 Save & Export'):
            # Save Configuration
            with ui.column().classes('mb-4'):
                self.save_button = ui.button('💾 Save Configuration', on_click=self._save_configuration) \
                    .classes('w-full bg-green-600 hover:bg-green-700 text-white')
                ui.label('Save user_config.yml and inline scripts to project directory').classes('text-center text-sm text-gray-600 mt-2')
            
            # Configure Project
            with ui.column().classes('mb-4'):
                self.configure_button = ui.button('⚙️ Configure Project', on_click=self._configure_project) \
                    .classes('w-full bg-yellow-600 hover:bg-yellow-700 text-white')
                ui.label('Save configuration and run pei-docker-cli configure').classes('text-center text-sm text-gray-600 mt-2')
            
            # Download Project
            with ui.column():
                self.download_button = ui.button('📥 Download Project', on_click=self._download_project) \
                    .classes('w-full bg-blue-600 hover:bg-blue-700 text-white')
                ui.label('Export project as ZIP file').classes('text-center text-sm text-gray-600 mt-2')
    
    def _create_config_preview(self) -> None:
        """Create the configuration preview section."""
        with self.create_card('📄 Generated user_config.yml Preview'):
            with ui.column().classes('w-full') as preview_container:
                self.config_preview_container = preview_container
    
    async def _save_configuration(self) -> None:
        """Save the configuration to user_config.yml file."""
        try:
            # Get project directory
            project_dir = self.app.ui_state.project.project_directory
            if not project_dir:
                ui.notify('Please set a project directory first', type='negative')
                return
            
            # Ensure directory exists
            project_path = Path(project_dir)
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Save configuration using UIStateBridge
            config_file = project_path / 'user_config.yml'
            success, errors = self.app.bridge.save_to_yaml(self.app.ui_state, str(config_file))
            
            if success:
                # Save inline scripts
                await self._save_inline_scripts(project_path)
                
                # Mark as saved
                self.app.ui_state.mark_saved()
                ui.notify('Configuration saved successfully!', type='positive')
                
                # Refresh preview
                self.refresh_summary()
            else:
                error_msg = '\n'.join(errors) if errors else 'Unknown error'
                ui.notify(f'Save failed: {error_msg}', type='negative', timeout=10000)
            
        except Exception as e:
            ui.notify(f'Error saving configuration: {str(e)}', type='negative', timeout=10000)
    
    async def _save_inline_scripts(self, project_path: Path) -> None:
        """Save inline scripts from the Scripts tab to files."""
        installation_dir = project_path / 'installation'
        installation_dir.mkdir(parents=True, exist_ok=True)
        
        # Process inline scripts for both stages
        for stage_num, stage_ui in [(1, self.app.ui_state.stage_1), (2, self.app.ui_state.stage_2)]:
            scripts_ui = stage_ui.scripts
            
            # Entry point inline scripts
            entry_mode = getattr(scripts_ui, f'stage{stage_num}_entry_mode')
            if entry_mode == 'inline':
                entry_name = getattr(scripts_ui, f'stage{stage_num}_entry_inline_name')
                entry_content = getattr(scripts_ui, f'stage{stage_num}_entry_inline_content')
                
                if entry_name and entry_content:
                    script_path = installation_dir / entry_name
                    script_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write script with proper shebang if missing
                    with open(script_path, 'w') as f:
                        if not entry_content.startswith('#!'):
                            f.write('#!/bin/bash\n')
                        f.write(entry_content)
                    
                    # Make executable
                    script_path.chmod(0o755)
            
            # Lifecycle inline scripts
            lifecycle_scripts = getattr(scripts_ui, f'stage{stage_num}_lifecycle_scripts', {})
            for lifecycle_type, scripts in lifecycle_scripts.items():
                for script in scripts:
                    if script.get('type') == 'inline':
                        script_name = script.get('name', '')
                        script_content = script.get('content', '')
                        
                        if script_name and script_content:
                            script_path = installation_dir / script_name
                            script_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(script_path, 'w') as f:
                                if not script_content.startswith('#!'):
                                    f.write('#!/bin/bash\n')
                                f.write(script_content)
                            
                            script_path.chmod(0o755)
    
    async def _configure_project(self) -> None:
        """Configure the project using pei-docker-cli."""
        # Show confirmation dialog
        dialog = ui.dialog()
        with dialog, ui.card().classes('w-96'):
            ui.label('Configure Project').classes('text-lg font-semibold mb-3')
            ui.label('This will:').classes('mb-2')
            ui.markdown("""
1. Save the current configuration
2. Run `pei-docker-cli configure` to generate Dockerfiles
3. This may take a few minutes

Continue?
            """).classes('mb-4 text-sm')
            
            with ui.row().classes('gap-2 justify-end'):
                ui.button('Cancel', on_click=dialog.close).classes('bg-gray-600 hover:bg-gray-700 text-white')
                ui.button('Configure', on_click=lambda: self._do_configure(dialog)) \
                    .classes('bg-yellow-600 hover:bg-yellow-700 text-white')
        
        dialog.open()
    
    async def _do_configure(self, dialog: ui.dialog) -> None:
        """Actually run the configuration after confirmation."""
        dialog.close()
        
        # First save the configuration
        await self._save_configuration()
        
        # Get project directory
        project_dir = self.app.ui_state.project.project_directory
        if not project_dir:
            ui.notify('No project directory set', type='negative')
            return
        
        try:
            # Run pei-docker-cli configure
            success = await self.app.project_manager.configure_project(Path(project_dir))
            
            if success:
                ui.notify('Project configured successfully!', type='positive')
            else:
                ui.notify('Configuration failed. Check the console for details.', type='negative')
                
        except Exception as e:
            ui.notify(f'Error configuring project: {str(e)}', type='negative', timeout=10000)
    
    async def _download_project(self) -> None:
        """Download the project as a ZIP file."""
        # Get project directory
        project_dir = self.app.ui_state.project.project_directory
        if not project_dir:
            ui.notify('Please set a project directory first', type='negative')
            return
        
        project_path = Path(project_dir)
        if not project_path.exists():
            ui.notify('Project directory does not exist', type='negative')
            return
        
        try:
            # Create ZIP file
            project_name = self.app.ui_state.project.project_name or 'peidocker-project'
            temp_dir = Path(tempfile.gettempdir())
            zip_path = temp_dir / f"{project_name}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in project_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(project_path)
                        zipf.write(file_path, arcname)
            
            # Serve the file for download
            @app.get(f'/download/{project_name}.zip')
            async def download():  # type: ignore
                return ui.download(str(zip_path), f'{project_name}.zip')
            
            # Trigger download
            ui.run_javascript(f'window.open("/download/{project_name}.zip", "_self")')
            
            ui.notify('Project exported successfully!', type='positive')
            
        except Exception as e:
            ui.notify(f'Error exporting project: {str(e)}', type='negative', timeout=10000)
    
    def refresh_summary(self) -> None:
        """Refresh the summary display with current configuration."""
        # Refresh validation status
        self._refresh_validation()
        
        # Refresh configuration preview
        self._refresh_config_preview()
    
    def _refresh_validation(self) -> None:
        """Refresh the validation status display."""
        if not self.validation_container:
            return
        
        self.validation_container.clear()
        
        with self.validation_container:
            # Validate using UIStateBridge
            is_valid, errors = self.app.bridge.validate_ui_state(self.app.ui_state)
            
            if is_valid:
                with ui.row().classes('items-center gap-2'):
                    ui.icon('check_circle', size='md').classes('text-green-600')
                    ui.label('Configuration is valid').classes('text-green-700 font-semibold')
            else:
                with ui.column().classes('gap-2'):
                    with ui.row().classes('items-center gap-2 mb-2'):
                        ui.icon('error', size='md').classes('text-red-600')
                        ui.label(f'Found {len(errors)} validation error(s)').classes('text-red-700 font-semibold')
                    
                    # List errors
                    for error in errors[:10]:  # Show max 10 errors
                        ui.label(f'• {error}').classes('text-red-600 text-sm ml-8')
                    
                    if len(errors) > 10:
                        ui.label(f'... and {len(errors) - 10} more errors').classes('text-red-600 text-sm ml-8 italic')
            
            # Show save status
            if self.app.ui_state.last_saved:
                ui.label(f'Last saved: {self.app.ui_state.last_saved}').classes('text-gray-600 text-sm mt-2')
            elif self.app.ui_state.modified:
                ui.label('Unsaved changes').classes('text-orange-600 text-sm mt-2')
    
    def _refresh_config_preview(self) -> None:
        """Refresh the configuration preview."""
        if not self.config_preview_container:
            return
        
        self.config_preview_container.clear()
        
        with self.config_preview_container:
            try:
                # Generate YAML preview using UIStateBridge internal method
                config_data = self.app.bridge._ui_to_user_config_format(self.app.ui_state)
                
                # Custom representer to ensure environment variables are quoted in the display
                def str_representer(dumper: Any, data: Any) -> Any:
                    # Force single quotes for strings that look like environment variables
                    if isinstance(data, str) and '=' in data:
                        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
                    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
                
                # Create a custom YAML dumper for display purposes
                class DisplayDumper(yaml.SafeDumper):
                    pass
                
                DisplayDumper.add_representer(str, str_representer)
                
                # Convert to YAML string with quotes for display clarity
                yaml_str = yaml.dump(config_data, Dumper=DisplayDumper, default_flow_style=False, 
                                   sort_keys=False, allow_unicode=True)
                
                # Display in a code block
                with ui.element('pre').classes('bg-gray-100 p-4 rounded overflow-x-auto text-sm'):
                    ui.html(f'<code class="language-yaml">{yaml_str}</code>')
                
            except Exception as e:
                ui.label(f'Error generating preview: {str(e)}').classes('text-red-600')
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the entire configuration."""
        # Use UIStateBridge for validation
        is_valid, errors = self.app.bridge.validate_ui_state(self.app.ui_state)
        return is_valid, errors
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get the complete configuration data."""
        # This tab doesn't contribute configuration data itself
        # It just displays and saves the combined data from all other tabs
        return {}
    
    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set configuration data for this tab."""
        # This tab doesn't have its own configuration to load
        # Just refresh the display
        self.refresh_summary()
    
    def create_card(self, title: Optional[str] = None) -> ui.element:
        """Create a consistent card container."""
        with ui.card().classes('w-full p-6 mb-6') as card:
            if title:
                ui.label(title).classes('text-xl font-bold text-gray-800 mb-4')
        return card