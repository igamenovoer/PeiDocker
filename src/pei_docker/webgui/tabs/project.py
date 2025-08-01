"""
Project tab for PeiDocker Web GUI.

This tab handles basic project configuration including project name,
base Docker image selection, and generated image name preview.
"""

from typing import TYPE_CHECKING, Any, Optional
from pathlib import Path
from nicegui import ui
from .base import BaseTab
from ..models import AppState

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class ProjectTab(BaseTab):
    """Project configuration tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI') -> None:
        super().__init__(app)
        self.project_name_input: Optional[ui.input] = None
        self.base_image_select: Optional[ui.select] = None
        self.stage1_image_label: Optional[ui.label] = None
        self.stage2_image_label: Optional[ui.label] = None
        
        # Project configuration UI components
        self.project_config_section: Optional[ui.column] = None
    
    def render(self) -> ui.element:
        """Render the project tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container: ui.column = container
            
            # Tab header
            self.create_section_header(
                '🏗️ Project Information',
                'Configure basic project settings and Docker image information. This forms the foundation of your containerized development environment.'
            )
            
            # Project Configuration (Always Available)
            with ui.column() as project_config_section:
                self.project_config_section = project_config_section
                
                # Two-column grid layout matching static demo
                with ui.row().classes('w-full gap-6'):
                    # Left Column - Basic Settings
                    with ui.column().classes('flex-1'):
                        ui.label('Basic Settings').classes('text-lg font-semibold mb-4')
                        
                        # Project name
                        with self.create_form_group('Project Name *', 'Used for Docker image naming and project identification'):
                            self.project_name_input = ui.input(
                                placeholder='Enter project name',
                                value=self.app.data.project.name or 'demo-project'
                            ).classes('w-full max-w-md')
                            self.project_name_input.on('input', self._on_project_name_change)
                        
                        # Base Docker image
                        with self.create_form_group('Base Docker Image', 'Docker Hub image to use as the base for your container'):
                            self.base_image_select = ui.select(
                                options={
                                    'ubuntu:22.04': '🐧 Ubuntu 22.04 LTS (Recommended)',
                                    'ubuntu:20.04': '🐧 Ubuntu 20.04 LTS',
                                    'ubuntu:24.04': '🐧 Ubuntu 24.04 LTS (Latest)',
                                },
                                value='ubuntu:22.04'
                            ).classes('w-full max-w-md')
                            self.base_image_select.on('change', self._on_base_image_change)
                    
                    # Right Column - Generated Docker Images
                    with ui.column().classes('flex-1'):
                        ui.label('Generated Docker Images').classes('text-lg font-semibold mb-4')
                        
                        # Preview panel with stage images
                        with ui.column().classes('bg-gray-50 p-4 rounded-lg border'):
                            with ui.column().classes('gap-3'):
                                # Stage-1 image
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('looks_one', size='sm').classes('text-blue-600')
                                    ui.label('Stage-1:').classes('text-sm font-medium text-blue-800')
                                    self.stage1_image_label = ui.label('demo-project:stage-1') \
                                        .classes('font-mono text-sm text-blue-900 bg-blue-100 px-2 py-1 rounded')
                                
                                # Stage-2 image
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('looks_two', size='sm').classes('text-green-600')
                                    ui.label('Stage-2:').classes('text-sm font-medium text-green-800')
                                    self.stage2_image_label = ui.label('demo-project:stage-2') \
                                        .classes('font-mono text-sm text-green-900 bg-green-100 px-2 py-1 rounded')
                
                # Architecture Information Section (moved to bottom, more compact)
                with ui.column().classes('mt-8'):
                    with ui.expansion('🏗️ Two-Stage Architecture Overview', icon='info').classes('w-full'):
                        with ui.column().classes('p-4 space-y-3'):
                            ui.markdown("""
**🔱 Stage-1 Image Building:**
- 🏗️ Builds foundation image with system-level setup
- 🔐 SSH server, proxy settings, APT packages, networking
- ✅ Can be used independently for basic use cases

**🔲 Stage-2 Image Building:**  
- 📁 Built on top of Stage-1 image as foundation
- ⚙️ Adds application-level customizations and packages
- 💾 Includes dynamic storage system (`/soft/app`, `/soft/data`, `/soft/workspace`)
- ⭐ Typically the target image due to enhanced features

🚀 Both images are fully usable - you can run either with `docker compose up stage-1` or `docker compose up stage-2`.
                            """).classes('text-sm text-gray-700')
            
            # Update image previews initially
            self._update_image_previews()
        
        return container
    
    def _on_project_name_change(self, e: Any) -> None:
        """Handle project name input changes."""
        project_name = e.value.strip()
        self.app.data.project.name = project_name
        self._update_image_previews()
        self.mark_modified()
    
    def _on_base_image_change(self, e: Any) -> None:
        """Handle base image selection changes."""
        base_image = e.value
        # Store in configuration
        if 'stage_1' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['stage_1'] = {}
        if 'image' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['image'] = {}
        
        self.app.data.config.stage_1['image']['base'] = base_image
        self.mark_modified()
    
    def _update_image_previews(self) -> None:
        """Update the generated image name previews."""
        project_name = self.app.data.project.name or 'demo-project'
        
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
            errors.append("❌ Project name is required")
        else:
            project_name = self.app.data.project.name.strip()
            if not project_name.replace('-', '').replace('_', '').isalnum():
                errors.append("❌ Project name can only contain letters, numbers, hyphens, and underscores")
        
        # Validate base image is selected
        base_image = self.app.data.config.stage_1.get('image', {}).get('base')
        if not base_image:
            errors.append("❌ Base Docker image must be selected")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> dict[str, Any]:
        """Get configuration data for this tab."""
        return {
            'stage_1': {
                'image': self.app.data.config.stage_1.get('image', {})
            },
            'stage_2': {
                'image': self.app.data.config.stage_2.get('image', {})
            }
        }
    
    def set_config_data(self, data: dict[str, Any]) -> None:
        """Set configuration data for this tab."""
        # Update UI components with loaded data
        stage_1_image = data.get('stage_1', {}).get('image', {})
        
        if 'base' in stage_1_image and self.base_image_select:
            self.base_image_select.set_value(stage_1_image['base'])
        
        # Update image previews
        self._update_image_previews()