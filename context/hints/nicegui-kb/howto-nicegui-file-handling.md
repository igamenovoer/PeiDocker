# How to Handle Files in NiceGUI

This guide covers file upload, download, and processing in NiceGUI applications, following server-side processing best practices.

## File Upload

### Basic File Upload
```python
from nicegui import ui

def handle_upload(e):
    """Handle uploaded file"""
    # e.content contains file bytes
    # e.name contains filename
    with open(f'uploads/{e.name}', 'wb') as f:
        f.write(e.content.read())
    ui.notify(f'Uploaded: {e.name}')

ui.upload(on_upload=handle_upload).classes('max-w-full')
```

### Configured Upload
```python
# Single file, specific type
ui.upload(
    on_upload=handle_upload,
    max_files=1,
    accept='.yml,.yaml'
).props('label="Upload YAML Configuration"')

# Multiple files with size limit
ui.upload(
    on_upload=handle_multiple,
    multiple=True,
    max_file_size=5_000_000  # 5MB
)
```

### Upload with Progress
```python
from nicegui import events

def handle_upload_progress(e: events.UploadEventArguments):
    ui.notify(f'Uploading {e.name}: {e.progress:.0%}')

ui.upload(
    on_upload=handle_upload,
    on_progress=handle_upload_progress
)
```

## File Download

### Direct Download
```python
from nicegui import ui
import tempfile

def generate_and_download():
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('Generated content')
        temp_path = f.name
    
    # Trigger download
    ui.download(temp_path, 'output.txt')

ui.button('Download', on_click=generate_and_download)
```

### Streaming Download
```python
from nicegui import app
from starlette.responses import StreamingResponse

@app.get('/download-zip')
async def download_zip():
    def generate():
        # Generate ZIP content in chunks
        import zipfile
        import io
        
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            zf.writestr('file1.txt', 'Content 1')
            zf.writestr('file2.txt', 'Content 2')
        
        buffer.seek(0)
        yield buffer.read()
    
    return StreamingResponse(
        generate(),
        media_type='application/zip',
        headers={'Content-Disposition': 'attachment; filename=archive.zip'}
    )

# In UI
ui.button('Download ZIP', on_click=lambda: ui.download('/download-zip'))
```

## File Processing

### Server-Side Processing Pattern
```python
import tempfile
import shutil
from pathlib import Path

class FileProcessor:
    def __init__(self):
        self.workspace = None
    
    def create_workspace(self):
        """Create temporary workspace"""
        self.workspace = Path(tempfile.mkdtemp())
        return self.workspace
    
    def process_upload(self, file_content, filename):
        """Process uploaded file"""
        if not self.workspace:
            self.create_workspace()
        
        # Save to workspace
        file_path = self.workspace / filename
        file_path.write_bytes(file_content)
        
        # Process file
        return self.validate_and_process(file_path)
    
    def cleanup(self):
        """Clean up workspace"""
        if self.workspace and self.workspace.exists():
            shutil.rmtree(self.workspace)

# Usage in UI
processor = FileProcessor()

def handle_config_upload(e):
    try:
        result = processor.process_upload(e.content.read(), e.name)
        ui.notify(f'Processed: {result}')
    except Exception as ex:
        ui.notify(f'Error: {str(ex)}', type='negative')
```

### ZIP File Creation
```python
import zipfile
from pathlib import Path

def create_project_zip(project_dir: Path) -> Path:
    """Create ZIP of project directory"""
    zip_path = project_dir.parent / f"{project_dir.name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in project_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(project_dir)
                zf.write(file_path, arcname)
    
    return zip_path

# Download project as ZIP
def download_project():
    project_dir = Path(app.storage.user.get('project_dir'))
    zip_path = create_project_zip(project_dir)
    ui.download(str(zip_path), f'{project_dir.name}.zip')
```

## File Management UI

### File Browser Component
```python
def file_browser(base_path: Path, on_select=None):
    """Simple file browser"""
    with ui.card():
        ui.label('Files').classes('text-h6')
        
        for item in sorted(base_path.iterdir()):
            with ui.row().classes('items-center'):
                icon = 'folder' if item.is_dir() else 'description'
                ui.icon(icon, size='sm')
                
                if on_select:
                    ui.link(item.name, on_click=lambda p=item: on_select(p))
                else:
                    ui.label(item.name)
```

### Upload with Preview
```python
from nicegui import ui
import base64

def handle_image_upload(e):
    """Handle image upload with preview"""
    # Read file content
    content = e.content.read()
    
    # Create base64 for preview
    b64 = base64.b64encode(content).decode()
    mime_type = e.type or 'image/png'
    
    # Show preview
    preview_container.clear()
    with preview_container:
        ui.image(f'data:{mime_type};base64,{b64}').classes('max-w-xs')

# UI
preview_container = ui.column()
ui.upload(
    on_upload=handle_image_upload,
    accept='image/*',
    max_files=1
).props('label="Upload Image"')
```

## Security Considerations

### Path Validation
```python
from pathlib import Path

def validate_file_path(user_path: str, base_dir: Path) -> bool:
    """Prevent directory traversal attacks"""
    try:
        # Resolve to absolute path
        resolved = (base_dir / user_path).resolve()
        # Check if within base directory
        return base_dir in resolved.parents or resolved == base_dir
    except:
        return False

# Usage
def safe_file_operation(filename):
    base_dir = Path('/app/uploads')
    if not validate_file_path(filename, base_dir):
        ui.notify('Invalid file path', type='negative')
        return
    # Proceed with operation
```

### File Type Validation
```python
ALLOWED_EXTENSIONS = {'.yml', '.yaml', '.json', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_upload(e):
    # Check extension
    file_ext = Path(e.name).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        ui.notify(f'Invalid file type: {file_ext}', type='negative')
        return False
    
    # Check size
    content = e.content.read()
    if len(content) > MAX_FILE_SIZE:
        ui.notify('File too large', type='negative')
        return False
    
    return True
```

## Advanced Patterns

### Chunked Upload for Large Files
```python
from nicegui import ui
import asyncio

class ChunkedUploader:
    def __init__(self):
        self.chunks = {}
    
    async def handle_chunk(self, file_id, chunk_index, chunk_data):
        """Handle individual chunk"""
        if file_id not in self.chunks:
            self.chunks[file_id] = {}
        
        self.chunks[file_id][chunk_index] = chunk_data
    
    async def assemble_file(self, file_id, total_chunks):
        """Assemble chunks into complete file"""
        if file_id not in self.chunks:
            return None
        
        # Check all chunks received
        if len(self.chunks[file_id]) != total_chunks:
            return None
        
        # Assemble in order
        data = b''
        for i in range(total_chunks):
            data += self.chunks[file_id][i]
        
        # Clean up
        del self.chunks[file_id]
        return data
```

### File Operations with Progress
```python
def process_files_with_progress(files):
    """Process multiple files with progress bar"""
    progress = ui.progress(total=len(files))
    status = ui.label('Processing...')
    
    async def process():
        for i, file in enumerate(files):
            status.text = f'Processing {file.name}...'
            # Simulate processing
            await asyncio.sleep(1)
            progress.value = i + 1
        
        status.text = 'Complete!'
        ui.notify('All files processed', type='positive')
    
    # Run async
    ui.timer(0.1, process, once=True)
```

## Integration with PeiDocker

### Configuration File Upload
```python
def handle_config_upload(e):
    """Handle user_config.yml upload"""
    try:
        import yaml
        
        # Parse YAML
        content = e.content.read().decode('utf-8')
        config = yaml.safe_load(content)
        
        # Validate structure
        if 'stage_1' not in config or 'stage_2' not in config:
            raise ValueError('Invalid configuration structure')
        
        # Store in session
        app.storage.user['config'] = config
        ui.notify('Configuration loaded successfully', type='positive')
        
        # Update UI
        populate_form_from_config(config)
        
    except Exception as ex:
        ui.notify(f'Error loading configuration: {str(ex)}', type='negative')
```

## Best Practices

1. **Always validate uploads** - Check file type, size, and content
2. **Use temporary directories** - Don't store uploads permanently without validation
3. **Clean up resources** - Remove temporary files after processing
4. **Provide feedback** - Show upload progress and processing status
5. **Handle errors gracefully** - Catch and display meaningful error messages
6. **Secure file operations** - Validate paths to prevent directory traversal

## Resources

- NiceGUI Upload Documentation: https://nicegui.io/documentation/upload
- Python tempfile module: https://docs.python.org/3/library/tempfile.html
- Python zipfile module: https://docs.python.org/3/library/zipfile.html