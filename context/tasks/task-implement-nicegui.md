# Implementing the GUI via NiceGUI

implement the GUI using `nicegui` library

## Design

you can find designs here:

- design doc: `context/plans/web-gui/webgui-general-design.md`
- demo: `context/plans/web-gui/demo`
- you can find current file true structure in `context/summaries/lsfiles-src-20250731-045506.md`.
- for nicegui documentation, you should find it using `context7` or web search.

## Requirements

- create a GUI that with `nicegui` default style, but with the same structure as the demo, that is, the same layout and components, and number of pages.
- source code should be put in `src/pei_docker/webgui`
- for anything not sure, find online info via `context7` or web search.

## Testing

- you are using `pixi` python management tool, run everything use the `dev` feature like `pixi run -e dev xxxx`
- if you want to test the GUI, use `pytest-playwright`
- temporary scripts and files should be placed in `<workspace>/tmp`, create subdirs for different purposes.

I'll provide more detailed analysis with references to online examples and best practices from the NiceGUI documentation.

## Detailed Code Review with Examples and Solutions

### 1. **Two-Stage Architecture Implementation Issues**

**Current Problem**: The code treats Stage-1 and Stage-2 as parallel configurations rather than sequential builds.

**Solution with NiceGUI Pattern**:
Based on the [Modularization example](https://github.com/zauberzeug/nicegui/tree/main/examples/modularization/), create a proper model hierarchy:

````python
from dataclasses import dataclass, field
from typing import Optional
import nicegui as ui

@dataclass
class Stage1Config:
    """Foundation stage configuration"""
    base_image: str = "ubuntu:22.04"
    system_packages: list[str] = field(default_factory=list)
    build_scripts: dict[str, str] = field(default_factory=dict)
    
    def to_dockerfile(self) -> str:
        """Generate Stage-1 Dockerfile content"""
        return f"""FROM {self.base_image} AS stage1
# System packages
RUN apt-get update && apt-get install -y {' '.join(self.system_packages)}
# Build scripts
{self._format_scripts()}
"""

@dataclass
class Stage2Config:
    """Application stage configuration (inherits from Stage-1)"""
    stage1_tag: str = ""  # Reference to Stage-1 image
    dynamic_storage: dict[str, str] = field(default_factory=dict)
    app_scripts: dict[str, str] = field(default_factory=dict)
    
    def to_dockerfile(self) -> str:
        """Generate Stage-2 Dockerfile content"""
        return f"""FROM {self.stage1_tag or 'stage1'} AS stage2
# Dynamic storage setup
{self._setup_storage()}
# Application scripts
{self._format_scripts()}
"""
````

### 2. **Storage Tab Implementation with Dynamic Storage Focus**

Following the [Tab example](https://nicegui.io/documentation/tabs) and [Form validation pattern](https://nicegui.io/documentation/section_binding_properties):

````python
from nicegui import ui
from typing import Dict, List

class StorageTab:
    def __init__(self, config):
        self.config = config
        self.storage_types = ['persistent', 'ephemeral', 'shared']
        
    def render(self):
        ui.label('Dynamic Storage Configuration (Stage-2 Feature)').classes('text-h5')
        ui.markdown('''
        > **Note**: Dynamic storage is a Stage-2 specific feature that allows 
        > runtime volume management without rebuilding the image.
        ''')
        
        with ui.card().classes('w-full'):
            ui.label('Storage Volumes').classes('text-h6')
            
            # Storage list with real-time validation
            with ui.column().classes('gap-4'):
                self.render_storage_list()
                
            with ui.row().classes('gap-2 mt-4'):
                ui.button('Add Volume', on_click=self.add_volume).props('icon=add')
                ui.button('Import from YAML', on_click=self.import_yaml).props('icon=upload')
    
    def render_storage_list(self):
        """Render storage volumes with inline editing"""
        for idx, volume in enumerate(self.config.stage2_config.dynamic_storage):
            with ui.row().classes('items-center gap-2 w-full'):
                # Path input with validation
                path_input = ui.input(
                    'Mount Path',
                    value=volume.get('path', ''),
                    validation={
                        'Path must start with /': lambda x: x.startswith('/'),
                        'Path cannot contain ..': lambda x: '..' not in x
                    }
                ).classes('flex-1')
                
                # Storage type selector
                ui.select(
                    self.storage_types,
                    value=volume.get('type', 'persistent'),
                    label='Type'
                ).classes('w-32')
                
                # Size input for persistent volumes
                if volume.get('type') == 'persistent':
                    ui.input(
                        'Size',
                        value=volume.get('size', '1Gi'),
                        placeholder='e.g., 1Gi, 500Mi'
                    ).classes('w-24')
                
                # Delete button
                ui.button(
                    icon='delete',
                    on_click=lambda idx=idx: self.remove_volume(idx)
                ).props('flat color=negative')
````

### 3. **Real-time Validation Implementation**

Based on [NiceGUI's input validation](https://nicegui.io/documentation/input#input_validation) and [reactive state example](https://nicegui.io/documentation/refreshable#refreshable_ui_with_reactive_state):

````python
from nicegui import ui
from typing import Callable, Dict, Any
import re

class RealTimeValidator:
    """Real-time validation with visual feedback"""
    
    @staticmethod
    def create_validated_input(
        label: str,
        value: str = '',
        validators: Dict[str, Callable[[str], bool]] = None,
        on_valid: Callable = None
    ) -> ui.input:
        """Create input with real-time validation"""
        
        def validate(e):
            """Validate on change with visual feedback"""
            if not validators:
                return
                
            errors = []
            for msg, validator in validators.items():
                if not validator(e.value):
                    errors.append(msg)
            
            # Update visual state
            if errors:
                e.sender.props('error')
                e.sender.props(f'error-message="{"; ".join(errors)}"')
            else:
                e.sender.props(remove='error')
                if on_valid:
                    on_valid(e.value)
        
        return ui.input(
            label,
            value=value,
            on_change=validate
        ).props('clearable')

# Usage example
validator = RealTimeValidator()
docker_tag_input = validator.create_validated_input(
    'Docker Image Tag',
    validators={
        'Invalid format': lambda x: re.match(r'^[\w][\w.-]{0,127}$', x),
        'No uppercase': lambda x: x.lower() == x
    },
    on_valid=lambda x: ui.notify(f'Valid tag: {x}', type='positive')
)
````

### 4. **File Upload Security Implementation**

Following [file upload example](https://nicegui.io/documentation/upload) with security enhancements:

````python
from pathlib import Path
import hashlib
import mimetypes

class SecureFileHandler:
    """Secure file upload and download handling"""
    
    ALLOWED_EXTENSIONS = {'.yml', '.yaml', '.txt', '.sh', '.py', '.dockerfile'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_upload(self, event) -> bool:
        """Validate file upload with security checks"""
        file = event.content
        name = event.name
        
        # Check file extension
        ext = Path(name).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            ui.notify(f'File type {ext} not allowed', type='negative')
            return False
        
        # Check file size
        if len(file) > self.MAX_FILE_SIZE:
            ui.notify('File too large (max 5MB)', type='negative')
            return False
        
        # Check content type
        mime_type = mimetypes.guess_type(name)[0]
        if mime_type and not mime_type.startswith(('text/', 'application/yaml')):
            ui.notify('Invalid file content type', type='negative')
            return False
        
        return True
    
    def save_uploaded_file(self, event) -> Optional[Path]:
        """Securely save uploaded file"""
        if not self.validate_upload(event):
            return None
        
        # Generate safe filename
        name_hash = hashlib.md5(event.name.encode()).hexdigest()[:8]
        safe_name = f"{name_hash}_{Path(event.name).name}"
        
        # Ensure path is within base directory
        target_path = self.base_dir / safe_name
        if not self._is_safe_path(target_path):
            ui.notify('Invalid file path', type='negative')
            return None
        
        # Save file
        target_path.write_bytes(event.content)
        ui.notify(f'File uploaded: {safe_name}', type='positive')
        return target_path
    
    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is within base directory"""
        try:
            path.resolve().relative_to(self.base_dir.resolve())
            return True
        except ValueError:
            return False

# Usage in upload component
file_handler = SecureFileHandler(Path('./uploads'))

ui.upload(
    label='Upload Configuration',
    on_upload=file_handler.save_uploaded_file,
    max_file_size=5_000_000,
    max_files=1
).props('accept=".yml,.yaml,.txt"')
````

### 5. **Unsaved Changes Tracking**

Based on [Storage example](https://nicegui.io/documentation/storage) and JavaScript integration:

````python
from nicegui import ui, app
import json

class PeiDockerApp:
    def __init__(self):
        self.unsaved_changes = False
        self._setup_change_tracking()
    
    def _setup_change_tracking(self):
        """Setup unsaved changes tracking"""
        # Add beforeunload handler
        ui.add_head_html('''
        <script>
        window.addEventListener('beforeunload', (e) => {
            if (window.hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
        </script>
        ''')
        
        # Track changes in forms
        app.on_connect(lambda: self._setup_client_tracking())
    
    async def _setup_client_tracking(self):
        """Setup per-client change tracking"""
        await ui.run_javascript('''
        window.hasUnsavedChanges = false;
        
        // Track all input changes
        document.addEventListener('input', () => {
            window.hasUnsavedChanges = true;
            // Notify Python side
            window.pywebview.api.set_unsaved_changes(true);
        });
        ''')
    
    def mark_saved(self):
        """Mark all changes as saved"""
        self.unsaved_changes = False
        ui.run_javascript('window.hasUnsavedChanges = false;')
        ui.notify('All changes saved', type='positive')
    
    def check_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.unsaved_changes
````

### 6. **Project Management Implementation**

Following the [Single Page App example](https://github.com/zauberzeug/nicegui/tree/main/examples/single_page_app):

````python
from nicegui import ui
from pathlib import Path
import yaml

class ProjectTab:
    def __init__(self, config, app):
        self.config = config
        self.app = app
        
    def render(self):
        with ui.column().classes('gap-4'):
            ui.label('Project Management').classes('text-h5')
            
            # Project info card
            with ui.card().classes('w-full'):
                self.render_project_info()
            
            # Action buttons
            with ui.row().classes('gap-2'):
                ui.button(
                    'Create Project',
                    on_click=self.show_create_dialog
                ).props('icon=create_new_folder color=primary')
                
                ui.button(
                    'Load Project',
                    on_click=self.show_load_dialog
                ).props('icon=folder_open')
                
                ui.button(
                    'Save Project',
                    on_click=self.save_project
                ).props('icon=save').bind_enabled_from(
                    self.app, 'unsaved_changes'
                )
    
    async def show_create_dialog(self):
        """Show create project dialog"""
        with ui.dialog() as dialog, ui.card():
            ui.label('Create New Project').classes('text-h6')
            
            name_input = ui.input(
                'Project Name',
                validation={'Required': lambda x: len(x) > 0}
            )
            
            desc_input = ui.textarea('Description')
            
            with ui.row():
                ui.button('Cancel', on_click=dialog.close)
                ui.button(
                    'Create',
                    on_click=lambda: self.create_project(
                        name_input.value,
                        desc_input.value,
                        dialog
                    )
                ).props('color=primary')
        
        dialog.open()
````

### 7. **Testing Infrastructure**

Based on [pytest example](https://github.com/zauberzeug/nicegui/tree/main/examples/pytests) and [testing documentation](https://nicegui.io/documentation/section_testing):

````python
import pytest
from nicegui.testing import Screen
from playwright.sync_api import Page, expect

@pytest.fixture
def pei_docker_app(tmp_path):
    """Fixture for PeiDocker app instance"""
    from src.pei_docker.webgui.app import PeiDockerApp
    app = PeiDockerApp()
    app.config.project_dir = tmp_path
    return app

def test_stage_architecture_flow(page: Page, pei_docker_app):
    """Test two-stage architecture configuration flow"""
    # Start app
    with Screen(pei_docker_app.ui) as screen:
        # Navigate to Build tab
        screen.click('Build Configuration')
        
        # Configure Stage-1
        screen.fill('Base Image', 'ubuntu:22.04')
        screen.click('Add Package')
        screen.fill('Package Name', 'python3-pip')
        
        # Configure Stage-2
        screen.click('Stage-2 Settings')
        expect(page.locator('text=Inherits from Stage-1')).to_be_visible()
        
        # Add dynamic storage
        screen.click('Storage')
        screen.click('Add Volume')
        screen.fill('Mount Path', '/data')
        screen.select('Type', 'persistent')
        
        # Verify configuration
        screen.click('Preview Dockerfile')
        expect(page.locator('text=FROM ubuntu:22.04 AS stage1')).to_be_visible()
        expect(page.locator('text=FROM stage1 AS stage2')).to_be_visible()

def test_file_upload_security(page: Page, pei_docker_app):
    """Test file upload security measures"""
    with Screen(pei_docker_app.ui) as screen:
        # Try uploading invalid file
        screen.upload('config.exe', b'malicious content')
        expect(page.locator('text=File type .exe not allowed')).to_be_visible()
        
        # Upload valid file
        screen.upload('config.yaml', b'key: value')
        expect(page.locator('text=File uploaded')).to_be_visible()

def test_unsaved_changes_warning(page: Page, pei_docker_app):
    """Test unsaved changes tracking"""
    with Screen(pei_docker_app.ui) as screen:
        # Make changes
        screen.click('Build Configuration')
        screen.fill('Base Image', 'alpine:latest')
        
        # Try to navigate away
        screen.click('Scripts')
        
        # Check for warning
        page.on('dialog', lambda dialog: dialog.accept())
        expect(page.locator('text=Unsaved changes')).to_be_visible()
````

### 8. **WebSocket Connection Handling**

Following [NiceGUI's connection handling](https://nicegui.io/documentation/page#wait_for_client_connection):

````python
from nicegui import ui, app
import asyncio

class ConnectionManager:
    """Manage WebSocket connections with auto-reconnect"""
    
    def __init__(self):
        self.connected_clients = set()
        self.reconnect_interval = 5
        
    async def monitor_connection(self, client):
        """Monitor client connection health"""
        try:
            await client.connected()
            self.connected_clients.add(client.id)
            
            # Show connection status
            with client:
                self.status_label = ui.label('Connected').classes('text-positive')
            
            # Monitor disconnection
            await client.disconnected()
            self.connected_clients.remove(client.id)
            
            # Update UI
            with client:
                self.status_label.set_text('Disconnected')
                self.status_label.classes(remove='text-positive', add='text-negative')
                
        except Exception as e:
            print(f"Connection error: {e}")

# Usage
@ui.page('/')
async def index():
    manager = ConnectionManager()
    
    # Add connection indicator
    with ui.header():
        ui.label('PeiDocker').classes('text-h4')
        ui.space()
        manager.status_label = ui.label('Connecting...').classes('text-warning')
    
    # Start monitoring
    asyncio.create_task(manager.monitor_connection(ui.context.client))
````

### Key Implementation Patterns from Examples

1. **[Modular Structure](https://github.com/zauberzeug/nicegui/tree/main/examples/modularization/)**: Separate concerns into modules
2. **[Real-time Validation](https://nicegui.io/documentation/input#input_validation)**: Immediate feedback on user input
3. **[State Management](https://nicegui.io/documentation/storage)**: Use storage and binding for state persistence
4. **[Dialog Patterns](https://nicegui.io/documentation/dialog)**: Confirmation dialogs for destructive actions
5. **[Testing with Playwright](https://nicegui.io/documentation/section_testing#user_fixture)**: Comprehensive UI testing

### Critical Next Steps

1. **Refactor models.py** to properly represent Stage-1 → Stage-2 inheritance
2. **Implement secure file handling** using the patterns above
3. **Add comprehensive tests** following the pytest-playwright examples
4. **Complete all tab implementations** with proper validation
5. **Add WebSocket monitoring** for better UX

The examples show that NiceGUI supports all the required features, but the current implementation needs significant restructuring to properly handle PeiDocker's two-stage architecture and security requirements.