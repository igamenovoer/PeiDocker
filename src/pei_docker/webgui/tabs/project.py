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
        
        # Project directory UI components
        self.project_dir_input: Optional[ui.input] = None
        self.project_dir_section: Optional[ui.column] = None
        self.active_project_section: Optional[ui.column] = None
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
            
            # Project Directory Section (Always Visible)
            with ui.column().classes('mb-6'):
                ui.label('📁 Project Directory').classes('text-lg font-semibold mb-4')
                
                with self.create_form_group('Project Directory Path', 'Directory must be empty or non-existent. Leave empty to use a generated temporary directory.'):
                    self.project_dir_input = ui.input(
                        placeholder='/path/to/your/project or leave empty for temporary directory',
                        value=''
                    ).classes('w-full')
                    
                    with ui.row().classes('gap-2 mt-2'):
                        ui.button('📁 Browse', on_click=self._browse_directory) \
                            .classes('bg-gray-500 hover:bg-gray-600')
                        ui.button('🎲 Generate', on_click=self._generate_temp_directory) \
                            .classes('bg-blue-500 hover:bg-blue-600')
                
                # Action buttons
                with ui.row().classes('gap-4 mt-6'):
                    ui.button('🚀 Create Project', on_click=self._create_project) \
                        .classes('bg-green-600 hover:bg-green-700 text-white py-2 px-6')
                    ui.button('📂 Load Project', on_click=self._load_project) \
                        .classes('bg-blue-600 hover:bg-blue-700 text-white py-2 px-6')
            
            # Active Project Directory Section (Only visible when project is active)
            with ui.column().classes('mb-6') as active_project_section:
                self.active_project_section = active_project_section
                
                ui.label('📁 Active Project Directory').classes('text-lg font-semibold mb-4')
                
                with ui.row().classes('items-center justify-between'):
                    with ui.row().classes('items-center gap-3'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('circle', size='sm').classes('text-green-500')
                            ui.label().bind_text_from(self.app.data.project, 'directory', 
                                                     lambda d: str(d) if d else '') \
                                .classes('font-mono text-sm')
                    
                    ui.button('🔄 Change Project', on_click=self.app.change_project) \
                        .classes('bg-gray-500 hover:bg-gray-600 text-white text-sm px-3 py-1')
                
                # Only show this section when project is active
                active_project_section.bind_visibility_from(
                    self.app.data, 'app_state', 
                    lambda state: state == AppState.ACTIVE
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
    
    def _browse_directory(self) -> None:
        """Open directory browser (placeholder for now)."""
        ui.notify('Directory browser feature coming soon. Please enter path manually.', type='info')
    
    def _generate_temp_directory(self) -> None:
        """Generate a temporary directory path."""
        import tempfile
        from datetime import datetime
        
        temp_dir = Path(tempfile.gettempdir()) / f"peidocker-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        if self.project_dir_input:
            self.project_dir_input.set_value(str(temp_dir))
        ui.notify('Generated temporary directory path', type='info', timeout=2000)
    
    async def _create_project(self) -> None:
        """Create a new project using the specified directory."""
        if not self.project_dir_input:
            ui.notify('Project directory input not available', type='negative')
            return
            
        directory_path = self.project_dir_input.value.strip()
        
        if not directory_path:
            # Generate temporary directory if empty
            self._generate_temp_directory()
            directory_path = self.project_dir_input.value.strip()
        
        try:
            project_dir = Path(directory_path).resolve()
            
            # Check if directory exists and is not empty
            if project_dir.exists() and any(project_dir.iterdir()):
                ui.notify(f'Directory {project_dir} is not empty. Please choose an empty directory or non-existent path.', type='negative')
                return
            
            success = await self.app.project_manager.create_project(project_dir)
            
            if success:
                # Set project data
                self.app.data.project.directory = project_dir
                self.app.data.project.name = project_dir.name
                
                # Update project name input with directory name
                if self.project_name_input:
                    self.project_name_input.set_value(project_dir.name)
                
                # Update app state to active
                self.app.data.app_state = AppState.ACTIVE
                
                ui.notify(f'Project created successfully at {project_dir}', type='positive')
                
                # Load configuration into tabs
                self.app._load_config_into_tabs()
                
            else:
                ui.notify('Failed to create project. Check directory permissions and try again.', type='negative')
                
        except Exception as e:
            ui.notify(f'Error creating project: {str(e)}', type='negative')
    
    async def _load_project(self) -> None:
        """Load an existing project from the specified directory."""
        if not self.project_dir_input:
            ui.notify('Project directory input not available', type='negative')
            return
            
        directory_path = self.project_dir_input.value.strip()
        
        if not directory_path:
            ui.notify('Please enter a project directory path', type='negative')
            return
        
        try:
            project_dir = Path(directory_path).resolve()
            
            if not project_dir.exists():
                ui.notify('Project directory does not exist', type='negative')
                return
            
            # Check if this looks like a PeiDocker project
            config_file = project_dir / 'user_config.yml'
            if not config_file.exists():
                ui.notify('No user_config.yml found in directory. Not a PeiDocker project?', type='warning')
                return
            
            # Load configuration
            success = await self.app.file_ops.load_configuration(project_dir, self.app.data.config)
            
            if success:
                # Set project data
                self.app.data.project.directory = project_dir
                self.app.data.project.name = project_dir.name
                
                # Update project name input with loaded project name or directory name
                project_name = self.app.data.config.stage_1.get('image', {}).get('output', project_dir.name)
                if ':' in project_name:
                    project_name = project_name.split(':')[0]  # Remove tag if present
                
                if self.project_name_input:
                    self.project_name_input.set_value(project_name)
                    self.app.data.project.name = project_name
                
                # Update app state to active
                self.app.data.app_state = AppState.ACTIVE
                
                ui.notify(f'Project loaded successfully from {project_dir}', type='positive')
                
                # Load configuration into tabs
                self.app._load_config_into_tabs()
                
            else:
                ui.notify('Failed to load project configuration', type='negative')
                
        except Exception as e:
            ui.notify(f'Error loading project: {str(e)}', type='negative')
    
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