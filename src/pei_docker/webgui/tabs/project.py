"""
Project tab for PeiDocker Web GUI - Refactored with data binding.

This tab handles basic project configuration including project name,
base Docker image selection, and generated image name preview.
"""

from typing import TYPE_CHECKING, Any, Optional, List, Tuple
from pathlib import Path
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class ProjectTab(BaseTab):
    """Project configuration tab with data binding."""
    
    def __init__(self, app: 'PeiDockerWebGUI') -> None:
        super().__init__(app)
        # References to UI elements for dynamic updates
        self.stage1_image_label: Optional[ui.label] = None
        self.stage2_image_label: Optional[ui.label] = None
    
    def render(self) -> ui.element:
        """Render the project tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            # Get project UI state
            project_ui = self.app.ui_state.project
            
            # Two vertically aligned sections
            with ui.row().classes('w-full items-start gap-6'):
                # Left section - Project Information
                with ui.column().classes('flex-1'):
                    self.create_section_header(
                        '🏗️ Project Information',
                        'Configure basic project settings and Docker image information.'
                    )
                    
                    # Project name with data binding
                    with self.create_form_group('Project Name *', 'Used for Docker image naming and project identification'):
                        ui.input(
                            placeholder='Enter project name'
                        ).bind_value(project_ui, 'project_name').classes('w-full').on_value_change(self._update_image_previews) \
                            .props('data-testid="project-name-input"')
                    
                    # Base Docker image with data binding
                    with self.create_form_group('Base Docker Image', 'Docker Hub image to use as the base for your container (e.g., ubuntu:22.04, alpine:latest)'):
                        ui.input(
                            placeholder='ubuntu:22.04'
                        ).bind_value(project_ui, 'base_image').classes('w-full') \
                            .props('data-testid="base-image-input"')
                        
                        # Generated Docker Images Info (nested under base docker image)
                        with ui.column().classes('mt-3 bg-gray-50 p-3 rounded-lg border'):
                            ui.label('Generated Docker Images:').classes('text-sm font-medium text-gray-700 mb-2')
                            with ui.column().classes('gap-2 ml-2'):
                                # Stage-1 image
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('looks_one', size='sm').classes('text-blue-600')
                                    ui.label('Stage-1:').classes('text-sm font-medium text-blue-800')
                                    self.stage1_image_label = ui.label('') \
                                        .classes('font-mono text-sm text-blue-900 bg-blue-100 px-2 py-1 rounded')
                                
                                # Stage-2 image
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('looks_two', size='sm').classes('text-green-600')
                                    ui.label('Stage-2:').classes('text-sm font-medium text-green-800')
                                    self.stage2_image_label = ui.label('') \
                                        .classes('font-mono text-sm text-green-900 bg-green-100 px-2 py-1 rounded')
                
                # Right section - Two-Stage Architecture Overview
                with ui.column().classes('flex-1'):
                    self.create_section_header(
                        '🐳 Two-Stage Architecture Overview',
                        'Understanding the PeiDocker build process.'
                    )
                    
                    with ui.column().classes('p-4 bg-gray-50 rounded-lg border'):
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
    
    def _update_image_previews(self) -> None:
        """Update the generated image name previews based on project name."""
        project_name = self.app.ui_state.project.project_name or 'my-project'
        
        # Sanitize project name for Docker image naming
        sanitized_name = project_name.lower().replace('_', '-').replace(' ', '-')
        
        # Update image output names in the UI state
        self.app.ui_state.project.image_output_name = sanitized_name
        
        # Update display labels
        if self.stage1_image_label:
            self.stage1_image_label.set_text(f'{sanitized_name}:stage-1')
        
        if self.stage2_image_label:
            self.stage2_image_label.set_text(f'{sanitized_name}:stage-2')
        
        # Mark as modified when names change
        if project_name:  # Only mark modified if there's actual content
            self.app.ui_state.mark_modified()
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate project configuration."""
        errors = []
        project_ui = self.app.ui_state.project
        
        # Validate project name
        if not project_ui.project_name or not project_ui.project_name.strip():
            errors.append("❌ Project name is required")
        else:
            project_name = project_ui.project_name.strip()
            if not project_name.replace('-', '').replace('_', '').isalnum():
                errors.append("❌ Project name can only contain letters, numbers, hyphens, and underscores")
        
        # Validate base image
        if not project_ui.base_image:
            errors.append("❌ Base Docker image must be specified")
        
        # Validate project directory (if set)
        if project_ui.project_directory:
            path = Path(project_ui.project_directory)
            if not path.exists():
                errors.append("❌ Project directory does not exist")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> dict[str, Any]:
        """Get configuration data for this tab."""
        project_ui = self.app.ui_state.project
        
        # Generate sanitized project name for image outputs
        sanitized_name = (project_ui.project_name or 'my-project').lower().replace('_', '-').replace(' ', '-')
        
        return {
            'stage_1': {
                'image': {
                    'base': project_ui.base_image,
                    'output': f'{sanitized_name}:stage-1'
                }
            },
            'stage_2': {
                'image': {
                    'output': f'{sanitized_name}:stage-2'
                }
            }
        }
    
    def set_config_data(self, data: dict[str, Any]) -> None:
        """Set configuration data for this tab."""
        project_ui = self.app.ui_state.project
        
        # Extract base image from stage_1
        stage_1_image = data.get('stage_1', {}).get('image', {})
        if 'base' in stage_1_image:
            project_ui.base_image = stage_1_image['base']
        
        # Try to extract project name from image output names
        stage_1_output = stage_1_image.get('output', '')
        if stage_1_output and ':' in stage_1_output:
            image_name = stage_1_output.split(':')[0]
            # Only set if project name is not already set
            if not project_ui.project_name:
                project_ui.project_name = image_name
        
        # Update image previews after loading
        self._update_image_previews()