# How to Handle File Operations in NiceGUI: Server-Side vs Client-Side Best Practices

## Overview

When developing file handling features in NiceGUI applications (such as creating directories for user modification and providing zip downloads), there are two main architectural approaches. This guide explains why server-side processing is preferred and provides implementation patterns.

## The Two Approaches

### Option 1: Client-Side Processing (NOT RECOMMENDED)
- Files are sent to user's browser cache
- Modification happens in the browser using JavaScript
- Zipping is done client-side using JS libraries
- Download happens directly from browser

### Option 2: Server-Side Processing (RECOMMENDED)
- Directories are created on the server filesystem
- User modifications are handled server-side
- Python code manages file operations and zipping
- Files are served to browser for download

## Why Server-Side is Preferred

### 1. Security Considerations
- **File system isolation**: Sensitive operations remain on server
- **Input validation**: Server can validate and sanitize all file operations
- **Access control**: Server enforces proper permissions and user isolation
- **No code exposure**: Business logic is not exposed to client browser

### 2. NiceGUI Architecture Alignment
- **Backend-first philosophy**: NiceGUI is designed for Python-centric development
- **FastAPI foundation**: Leverages server-side capabilities
- **Consistent with framework**: Follows NiceGUI's design principles

### 3. Technical Advantages
- **Better error handling**: Server-side exception management
- **Resource management**: Controlled memory and disk usage
- **Cross-platform compatibility**: No browser-specific limitations
- **Scalability**: Better for multi-user scenarios

## Implementation Patterns

### Basic Server-Side File Handling

```python
import tempfile
import zipfile
from pathlib import Path
from nicegui import app, ui

def create_user_workspace():
    """Create a temporary directory for user modifications"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Store workspace path in user-specific storage
    app.storage.user['workspace_dir'] = str(temp_dir)
    
    # Create some initial files/structure
    (temp_dir / 'config').mkdir()
    (temp_dir / 'data').mkdir()
    (temp_dir / 'README.txt').write_text('User workspace created')
    
    ui.notify(f'Workspace created: {temp_dir.name}', type='positive')
    return temp_dir

def zip_and_download():
    """Create zip file and trigger download"""
    workspace_dir = Path(app.storage.user.get('workspace_dir', ''))
    
    if not workspace_dir.exists():
        ui.notify('No workspace found', type='negative')
        return
    
    # Create zip file
    zip_path = workspace_dir.parent / f"{workspace_dir.name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in workspace_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(workspace_dir)
                zipf.write(file_path, arcname)
    
    # Make zip available for download
    app.add_static_file('/workspace.zip', str(zip_path))
    ui.download('/workspace.zip', f'workspace-{workspace_dir.name}.zip')
    
    ui.notify('Download started', type='positive')
```

### Advanced Pattern with File Management

```python
import shutil
from datetime import datetime, timedelta

class WorkspaceManager:
    def __init__(self):
        self.base_dir = Path(tempfile.gettempdir()) / 'nicegui_workspaces'
        self.base_dir.mkdir(exist_ok=True)
    
    def create_workspace(self, user_id: str) -> Path:
        """Create user-specific workspace"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        workspace_dir = self.base_dir / f"user_{user_id}_{timestamp}"
        workspace_dir.mkdir(parents=True)
        
        # Initialize workspace structure
        self._init_workspace_structure(workspace_dir)
        
        return workspace_dir
    
    def _init_workspace_structure(self, workspace_dir: Path):
        """Initialize workspace with default structure"""
        (workspace_dir / 'src').mkdir()
        (workspace_dir / 'config').mkdir()
        (workspace_dir / 'output').mkdir()
        
        # Create sample files
        (workspace_dir / 'README.md').write_text(
            '# User Workspace\n\nModify files as needed.'
        )
    
    def cleanup_old_workspaces(self, max_age_hours: int = 24):
        """Remove workspaces older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for workspace in self.base_dir.iterdir():
            if workspace.is_dir() and workspace.stat().st_mtime < cutoff_time.timestamp():
                shutil.rmtree(workspace)

# Usage in NiceGUI app
workspace_manager = WorkspaceManager()

def create_workspace():
    user_id = app.storage.browser.get('id', 'anonymous')
    workspace_dir = workspace_manager.create_workspace(user_id)
    app.storage.user['workspace_dir'] = str(workspace_dir)
    ui.notify('Workspace created successfully')

# Cleanup old workspaces on startup
app.on_startup(lambda: workspace_manager.cleanup_old_workspaces())
```

### Storage Options in NiceGUI

```python
# Different storage types for different use cases

# 1. User storage - persistent across sessions
app.storage.user['workspace_dir'] = str(workspace_path)
app.storage.user['user_preferences'] = {'theme': 'dark'}

# 2. Tab storage - session-specific, more secure
app.storage.tab['temp_workspace'] = str(temp_path)

# 3. Client storage - per-connection
app.storage.client['active_files'] = file_list

# 4. Browser storage - stored in browser's localStorage
app.storage.browser['user_settings'] = settings_dict
```

### Error Handling and User Feedback

```python
async def safe_file_operation():
    try:
        workspace_dir = Path(app.storage.user.get('workspace_dir'))
        
        if not workspace_dir.exists():
            raise FileNotFoundError("Workspace not found")
        
        # Perform file operations
        result = await some_file_operation(workspace_dir)
        
        ui.notify('Operation completed successfully', type='positive')
        return result
        
    except FileNotFoundError as e:
        ui.notify(f'File error: {e}', type='negative')
    except PermissionError as e:
        ui.notify('Permission denied', type='negative')
    except Exception as e:
        ui.notify(f'Unexpected error: {e}', type='negative')
        # Log the error for debugging
        print(f"Error in file operation: {e}")
```

## Security Best Practices

### 1. Path Validation
```python
def validate_file_path(user_path: str, base_dir: Path) -> bool:
    """Ensure user cannot access files outside workspace"""
    try:
        resolved_path = (base_dir / user_path).resolve()
        return base_dir.resolve() in resolved_path.parents
    except:
        return False
```

### 2. File Size Limits
```python
MAX_WORKSPACE_SIZE = 100 * 1024 * 1024  # 100MB

def check_workspace_size(workspace_dir: Path) -> bool:
    total_size = sum(f.stat().st_size for f in workspace_dir.rglob('*') if f.is_file())
    return total_size <= MAX_WORKSPACE_SIZE
```

### 3. File Type Restrictions
```python
ALLOWED_EXTENSIONS = {'.txt', '.md', '.json', '.yaml', '.yml', '.py'}

def is_allowed_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in ALLOWED_EXTENSIONS
```

## Deployment Considerations

### Local Deployment
- Files are stored in local temporary directories
- Suitable for single-user applications
- Easy cleanup and management

### Server Deployment
- Consider using persistent storage (database, cloud storage)
- Implement proper user authentication
- Add rate limiting and resource quotas
- Use container-friendly temporary storage

### Docker Deployment
```python
# Use volume mounts for persistent workspaces
WORKSPACE_BASE = Path(os.environ.get('WORKSPACE_DIR', '/app/workspaces'))
WORKSPACE_BASE.mkdir(exist_ok=True)
```

## Common Pitfalls to Avoid

1. **Don't store sensitive data in client-side storage**
2. **Always validate file paths to prevent directory traversal**
3. **Implement proper cleanup to prevent disk space issues**
4. **Use appropriate NiceGUI storage based on data lifetime needs**
5. **Handle file operation errors gracefully with user feedback**

## Resources

- [NiceGUI Documentation - Downloads](https://nicegui.io/documentation/download)
- [NiceGUI Documentation - Storage](https://nicegui.io/documentation/storage)
- [NiceGUI Documentation - Static Files](https://nicegui.io/documentation)
- [Python Tempfile Module](https://docs.python.org/3/library/tempfile.html)
- [Python Zipfile Module](https://docs.python.org/3/library/zipfile.html)
- [Web Security Best Practices](https://owasp.org/www-project-top-ten/)

## Summary

Always prefer server-side file handling in NiceGUI applications for security, reliability, and alignment with the framework's architecture. Use appropriate storage mechanisms, implement proper error handling, and follow security best practices to create robust file management features.
