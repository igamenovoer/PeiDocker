"""
Project tab for PeiDocker Web GUI.

This tab handles basic project configuration including project name,
base Docker image selection, and generated image name preview.
"""

from typing import TYPE_CHECKING
from nicegui import ui
from .base import BaseTab

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class ProjectTab(BaseTab):
    """Project configuration tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.project_name_input = None
        self.base_image_select = None
        self.stage1_image_label = None
        self.stage2_image_label = None
    
    def render(self) -> ui.element:
        """Render the project tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            # Tab header
            self.create_section_header(
                '🏗️ Project Configuration',
                'Configure basic project settings and Docker image options'
            )
            
            # Project Information Card
            with self.create_card('Project Information'):
                # Project name
                with self.create_form_group('Project Name', 'Name for your Docker project'):
                    self.project_name_input = ui.input(
                        placeholder='my-project',
                        value=self.app.data.project.name or ''
                    ).classes('max-w-md')
                    self.project_name_input.on('input', self._on_project_name_change)
                
                # Project directory (read-only display)
                with self.create_form_group('Project Directory', 'Location where project files are stored'):
                    ui.input(
                        value=str(self.app.data.project.directory) if self.app.data.project.directory else ''
                    ).classes('max-w-2xl').props('readonly')
            
            # Docker Configuration Card
            with self.create_card('Docker Configuration'):
                # Base image selection
                with self.create_form_group('Base Docker Image', 'Ubuntu base image for Stage-1 build'):
                    self.base_image_select = ui.select(
                        options={
                            'ubuntu:22.04': 'Ubuntu 22.04 LTS (Recommended)',
                            'ubuntu:20.04': 'Ubuntu 20.04 LTS',
                            'ubuntu:24.04': 'Ubuntu 24.04 LTS (Latest)',
                        },
                        value='ubuntu:22.04'
                    ).classes('max-w-md')
                    self.base_image_select.on('change', self._on_base_image_change)
                
                # Generated image names preview
                with ui.column().classes('mt-6'):
                    ui.label('Generated Image Names').classes('font-medium text-gray-700 mb-2')
                    
                    with ui.row().classes('gap-4'):
                        # Stage-1 image preview
                        with ui.column().classes('p-3 bg-blue-50 rounded border'):
                            ui.label('Stage-1 Image:').classes('text-sm font-medium text-blue-800')
                            self.stage1_image_label = ui.label('my-project:stage-1') \
                                .classes('font-mono text-sm text-blue-900')
                        
                        # Stage-2 image preview  
                        with ui.column().classes('p-3 bg-green-50 rounded border'):
                            ui.label('Stage-2 Image:').classes('text-sm font-medium text-green-800')
                            self.stage2_image_label = ui.label('my-project:stage-2') \
                                .classes('font-mono text-sm text-green-900')
            
            # Architecture Information Card
            with self.create_card('Two-Stage Architecture'):
                with ui.column().classes('space-y-3'):
                    ui.markdown("""
**Stage-1 Image Building:**
- Builds foundation image with system-level setup
- SSH server, proxy settings, APT packages, networking
- Can be used independently for basic use cases

**Stage-2 Image Building:**  
- Built on top of Stage-1 image as foundation
- Adds application-level customizations and packages
- Includes dynamic storage system (`/soft/app`, `/soft/data`, `/soft/workspace`)
- Typically the target image due to enhanced features

Both images are fully usable - you can run either with `docker compose up stage-1` or `docker compose up stage-2`.
                    """).classes('text-sm text-gray-700')
            
            # Update image previews initially
            self._update_image_previews()
        
        return container
    
    def _on_project_name_change(self, e):
        """Handle project name input changes."""
        project_name = e.value.strip()
        self.app.data.project.name = project_name
        self._update_image_previews()
        self.mark_modified()
    
    def _on_base_image_change(self, e):
        """Handle base image selection changes."""
        base_image = e.value
        # Store in configuration
        if 'stage_1' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['stage_1'] = {}
        if 'image' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['image'] = {}
        
        self.app.data.config.stage_1['image']['base'] = base_image
        self.mark_modified()
    
    def _update_image_previews(self):
        """Update the generated image name previews."""
        project_name = self.app.data.project.name or 'my-project'
        
        # Sanitize project name for Docker image naming
        sanitized_name = project_name.lower().replace('_', '-')
        
        if self.stage1_image_label:
            self.stage1_image_label.set_text(f'{sanitized_name}:stage-1')
        
        if self.stage2_image_label:
            self.stage2_image_label.set_text(f'{sanitized_name}:stage-2')
        
        # Store in configuration
        if 'image' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['image'] = {}
        if 'image' not in self.app.data.config.stage_2:
            self.app.data.config.stage_2['image'] = {}
        
        self.app.data.config.stage_1['image']['output'] = f'{sanitized_name}:stage-1'
        self.app.data.config.stage_2['image']['output'] = f'{sanitized_name}:stage-2'
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate project configuration."""
        errors = []
        
        # Validate project name
        if not self.app.data.project.name or not self.app.data.project.name.strip():
            errors.append("Project name is required")
        else:
            project_name = self.app.data.project.name.strip()
            if not project_name.replace('-', '').replace('_', '').isalnum():
                errors.append("Project name can only contain letters, numbers, hyphens, and underscores")
        
        # Validate base image is selected
        base_image = self.app.data.config.stage_1.get('image', {}).get('base')
        if not base_image:
            errors.append("Base Docker image must be selected")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> dict:
        """Get configuration data for this tab."""
        return {
            'stage_1': {
                'image': self.app.data.config.stage_1.get('image', {})
            },
            'stage_2': {
                'image': self.app.data.config.stage_2.get('image', {})
            }
        }
    
    def set_config_data(self, data: dict):
        """Set configuration data for this tab."""
        # Update UI components with loaded data
        stage_1_image = data.get('stage_1', {}).get('image', {})
        
        if 'base' in stage_1_image and self.base_image_select:
            self.base_image_select.set_value(stage_1_image['base'])
        
        # Update image previews
        self._update_image_previews()