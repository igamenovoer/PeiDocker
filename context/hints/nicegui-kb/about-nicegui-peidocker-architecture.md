# PeiDocker Web GUI Architecture with NiceGUI

This document describes the specific architecture and implementation patterns for the PeiDocker Web GUI using NiceGUI.

## Overall Architecture

### Application Structure
```
src/pei_docker/webgui/
├── __init__.py
├── app.py                  # Main application entry
├── models/
│   ├── __init__.py
│   ├── config.py          # Configuration data models
│   └── state.py           # Application state models
├── components/
│   ├── __init__.py
│   ├── header.py          # Header component
│   ├── project_select.py  # Project selection
│   └── tabs/              # Tab components
│       ├── project.py
│       ├── ssh.py
│       ├── network.py
│       ├── environment.py
│       ├── storage.py
│       ├── scripts.py
│       └── summary.py
├── services/
│   ├── __init__.py
│   ├── config_manager.py  # Configuration management
│   ├── file_handler.py    # File operations
│   └── docker_utils.py    # Docker integration
└── utils/
    ├── __init__.py
    ├── validators.py      # Input validators
    └── converters.py      # Data converters
```

## Core Components

### Main Application (app.py)
```python
from nicegui import ui, app
from pathlib import Path
import asyncio

class PeiDockerWebGUI:
    """Main application class"""
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.state = ApplicationState()
        
    def setup_routes(self):
        """Configure application routes"""
        
        @ui.page('/')
        async def index():
            # Check if project is loaded
            if not self.state.project_loaded:
                await self.show_project_selection()
            else:
                await self.show_main_interface()
        
        # API routes
        app.add_api_route('/api/configure', self.configure_project, methods=['POST'])
        app.add_api_route('/api/download', self.download_project, methods=['GET'])
    
    def run(self):
        """Start the application"""
        self.setup_routes()
        ui.run(
            title='PeiDocker Web GUI',
            favicon='🐳',
            dark=None,  # Auto theme
            storage_secret='peidocker-secret-key',
            port=8080,
            reload=False
        )

# Entry point
def main():
    app = PeiDockerWebGUI()
    app.run()
```

### Application State Management
```python
from nicegui import app, ui
from dataclasses import dataclass
from typing import Optional

@dataclass
class ApplicationState:
    """Central application state"""
    
    project_loaded: bool = False
    project_directory: Optional[Path] = None
    configuration_dirty: bool = False
    last_configure_success: bool = False
    active_tab: str = 'project'
    
    def load_from_storage(self):
        """Load state from storage"""
        if 'app_state' in app.storage.user:
            state_dict = app.storage.user['app_state']
            self.project_directory = Path(state_dict.get('project_directory', ''))
            self.project_loaded = state_dict.get('project_loaded', False)
            self.active_tab = state_dict.get('active_tab', 'project')
    
    def save_to_storage(self):
        """Persist state to storage"""
        app.storage.user['app_state'] = {
            'project_directory': str(self.project_directory) if self.project_directory else None,
            'project_loaded': self.project_loaded,
            'active_tab': self.active_tab
        }
```

### Configuration Manager
```python
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigurationManager:
    """Manage PeiDocker configuration"""
    
    def __init__(self):
        self.config = {}
        self.original_config = {}
    
    def load_from_file(self, config_path: Path) -> bool:
        """Load configuration from user_config.yml"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
                self.original_config = self.config.copy()
            return True
        except Exception as e:
            ui.notify(f'Error loading config: {str(e)}', type='negative')
            return False
    
    def save_to_file(self, config_path: Path) -> bool:
        """Save configuration to user_config.yml"""
        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write YAML
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            
            self.original_config = self.config.copy()
            return True
        except Exception as e:
            ui.notify(f'Error saving config: {str(e)}', type='negative')
            return False
    
    def is_dirty(self) -> bool:
        """Check if configuration has unsaved changes"""
        return self.config != self.original_config
    
    def get_nested(self, path: str, default=None):
        """Get nested configuration value"""
        keys = path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default
    
    def set_nested(self, path: str, value: Any):
        """Set nested configuration value"""
        keys = path.split('.')
        target = self.config
        
        # Navigate to parent
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # Set value
        target[keys[-1]] = value
```

## UI Component Patterns

### Header Component
```python
def create_header(state: ApplicationState, on_save, on_configure, on_download):
    """Create application header"""
    
    with ui.header().classes('items-center justify-between'):
        with ui.row().classes('items-center'):
            ui.icon('sailing', size='lg')
            ui.label('PeiDocker Web GUI').classes('text-h6')
        
        # Action buttons
        if state.project_loaded:
            with ui.row().classes('gap-2'):
                save_btn = ui.button('Save', icon='save', on_click=on_save)
                save_btn.bind_enabled_from(
                    lambda: state.configuration_dirty
                )
                
                ui.button('Configure', icon='settings', on_click=on_configure)
                    .props('color=warning')
                
                ui.button('Download', icon='download', on_click=on_download)
                    .props('color=info')
```

### Project Selection Component
```python
async def show_project_selection(on_project_selected):
    """Show project selection interface"""
    
    with ui.column().classes('items-center justify-center h-screen gap-8'):
        ui.label('Welcome to PeiDocker Web GUI').classes('text-h4')
        
        with ui.card().classes('w-96'):
            project_dir = ui.input(
                'Project Directory',
                placeholder='/path/to/project'
            ).classes('w-full')
            
            # Directory browser
            async def browse_directory():
                # In web mode, can't use native file dialog
                ui.notify('Enter path manually or use file upload', type='info')
            
            project_dir.props('append-icon=folder')
            project_dir.on('click:append', browse_directory)
            
            with ui.row().classes('w-full gap-2 mt-4'):
                ui.button(
                    'Create Project',
                    icon='add',
                    on_click=lambda: on_project_selected(project_dir.value, create=True)
                ).classes('flex-1')
                
                ui.button(
                    'Load Project',
                    icon='folder_open',
                    on_click=lambda: on_project_selected(project_dir.value, create=False)
                ).classes('flex-1')
```

### Tab Implementation Pattern
```python
class ProjectTab:
    """Project configuration tab"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config = config_manager
    
    def render(self):
        """Render tab content"""
        with ui.column().classes('gap-4 p-4'):
            # Project name
            project_name = ui.input(
                'Project Name',
                value=self.config.get_nested('project.name', 'my-project')
            )
            project_name.on('change', 
                lambda e: self.config.set_nested('project.name', e.value)
            )
            
            # Base image
            base_images = [
                'ubuntu:22.04',
                'ubuntu:20.04', 
                'debian:11',
                'debian:10'
            ]
            
            base_image = ui.select(
                options=base_images,
                label='Base Image',
                value=self.config.get_nested('stage_1.image.base', 'ubuntu:22.04')
            )
            base_image.on('change',
                lambda e: self.config.set_nested('stage_1.image.base', e.value)
            )
            
            # Output image names
            with ui.card():
                ui.label('Output Images').classes('text-h6')
                
                stage1_output = ui.input(
                    'Stage-1 Image',
                    value=self.config.get_nested('stage_1.image.output', 'pei-image:stage-1')
                )
                stage1_output.on('change',
                    lambda e: self.config.set_nested('stage_1.image.output', e.value)
                )
                
                stage2_output = ui.input(
                    'Stage-2 Image',
                    value=self.config.get_nested('stage_2.image.output', 'pei-image:stage-2')
                )
                stage2_output.on('change',
                    lambda e: self.config.set_nested('stage_2.image.output', e.value)
                )
```

## Service Layer

### Docker Integration
```python
import asyncio
from typing import Optional

class DockerService:
    """Docker operations service"""
    
    async def run_command(self, command: str, cwd: Optional[Path] = None) -> tuple[int, str, str]:
        """Run docker command"""
        process = await asyncio.create_subprocess_exec(
            *command.split(),
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        return process.returncode, stdout.decode(), stderr.decode()
    
    async def configure_project(self, project_dir: Path) -> bool:
        """Run pei-docker-cli configure"""
        returncode, stdout, stderr = await self.run_command(
            f'pei-docker-cli configure -p {project_dir}',
            cwd=project_dir
        )
        
        if returncode == 0:
            ui.notify('Configuration successful', type='positive')
            return True
        else:
            ui.notify(f'Configuration failed: {stderr}', type='negative')
            return False
```

### File Operations Service
```python
import tempfile
import zipfile
from pathlib import Path

class FileService:
    """File operations service"""
    
    def create_project_structure(self, project_dir: Path) -> bool:
        """Initialize project directory structure"""
        try:
            # Run pei-docker-cli create
            result = subprocess.run(
                ['pei-docker-cli', 'create', '-p', str(project_dir)],
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
        except Exception as e:
            ui.notify(f'Error creating project: {str(e)}', type='negative')
            return False
    
    def create_project_zip(self, project_dir: Path) -> Optional[Path]:
        """Create ZIP archive of project"""
        try:
            zip_path = Path(tempfile.mktemp(suffix='.zip'))
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in project_dir.rglob('*'):
                    if file_path.is_file() and '.git' not in str(file_path):
                        arcname = file_path.relative_to(project_dir)
                        zf.write(file_path, arcname)
            
            return zip_path
        except Exception as e:
            ui.notify(f'Error creating ZIP: {str(e)}', type='negative')
            return None
```

## State Synchronization

### Real-time Updates
```python
class RealtimeSync:
    """Synchronize UI with configuration changes"""
    
    def __init__(self, config_manager, state):
        self.config = config_manager
        self.state = state
        self.update_callbacks = []
    
    def watch_changes(self):
        """Watch for configuration changes"""
        # Create reactive wrapper
        self.dirty_state = ui.state(False)
        
        # Check periodically
        ui.timer(1.0, self.check_dirty_state)
    
    def check_dirty_state(self):
        """Check if configuration is dirty"""
        is_dirty = self.config.is_dirty()
        if is_dirty != self.dirty_state.value:
            self.dirty_state.value = is_dirty
            self.state.configuration_dirty = is_dirty
            
            # Update UI indicators
            for callback in self.update_callbacks:
                callback(is_dirty)
```

## Error Handling

### Global Error Handler
```python
from nicegui import app
from starlette.requests import Request
from starlette.responses import Response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> Response:
    """Handle uncaught exceptions"""
    import traceback
    
    # Log error
    error_details = traceback.format_exc()
    print(f"Unhandled error: {error_details}")
    
    # Show user-friendly error
    with ui.dialog() as dialog, ui.card():
        ui.label('An error occurred').classes('text-h6')
        ui.label(str(exc)).classes('text-negative')
        
        with ui.expansion('Details', icon='info'):
            ui.label(error_details).classes('font-mono text-xs')
        
        ui.button('Close', on_click=dialog.close)
    
    dialog.open()
    
    return Response(status_code=500)
```

## Performance Optimization

### Lazy Loading Tabs
```python
class LazyTabLoader:
    """Load tab content only when accessed"""
    
    def __init__(self):
        self.loaded_tabs = set()
        self.tab_loaders = {
            'project': ProjectTab,
            'ssh': SSHTab,
            'network': NetworkTab,
            # ... other tabs
        }
    
    def load_tab(self, tab_name: str, config_manager):
        """Load tab if not already loaded"""
        if tab_name not in self.loaded_tabs:
            # Create tab instance
            tab_class = self.tab_loaders.get(tab_name)
            if tab_class:
                tab_instance = tab_class(config_manager)
                tab_instance.render()
                self.loaded_tabs.add(tab_name)
```

## Testing Support

### UI Test Structure
```python
from nicegui.testing import Screen

def test_project_creation(screen: Screen):
    """Test project creation flow"""
    
    # Load main page
    screen.open('/')
    screen.should_contain('Welcome to PeiDocker Web GUI')
    
    # Enter project directory
    screen.type('/tmp/test-project', 'Project Directory')
    
    # Click create
    screen.click('Create Project')
    
    # Should show tabs
    screen.should_contain('Project')
    screen.should_contain('SSH')
    screen.should_contain('Network')
```

## Deployment Configuration

### Production Settings
```python
# For production deployment
if __name__ == '__main__':
    import os
    
    # Configuration
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    reload = os.environ.get('RELOAD', 'false').lower() == 'true'
    
    # Run application
    ui.run(
        host=host,
        port=port,
        reload=reload,
        title='PeiDocker Web GUI',
        favicon='🐳',
        storage_secret=os.environ.get('STORAGE_SECRET', 'change-me-in-production')
    )
```

## Best Practices Summary

1. **Separation of Concerns**: Keep UI, business logic, and data management separate
2. **Reactive State**: Use NiceGUI's reactive features for automatic UI updates
3. **Error Boundaries**: Handle errors gracefully at component and global levels
4. **Performance**: Lazy load components and batch updates
5. **Security**: Validate all inputs and file operations server-side
6. **Testing**: Structure code to be testable with NiceGUI's testing framework
7. **Modularity**: Create reusable components for common UI patterns

## Resources

- PeiDocker Documentation: Project README and docs
- NiceGUI Documentation: https://nicegui.io/documentation
- Design Document: context/plans/web-gui/webgui-general-design.md