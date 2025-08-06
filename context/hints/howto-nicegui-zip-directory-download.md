# How to Zip a Directory and Provide Download in NiceGUI

This guide shows how to create a zip file from a local directory and trigger a browser download in NiceGUI when a user clicks a button.

## Overview

NiceGUI provides several download functions through `ui.download` that can trigger browser downloads. To zip a directory and provide it as a download, you'll typically:

1. Create a temporary zip file from the directory
2. Use `ui.download.file()` to trigger the browser download
3. Clean up temporary files

## Basic Implementation

### Method 1: Using `shutil.make_archive()` (Recommended)

```python
import os
import tempfile
import shutil
from nicegui import ui

def zip_and_download_directory(source_dir: str, zip_name: str = "archive"):
    """Create a zip file from directory and trigger download"""
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create zip file in temp directory
        zip_path = os.path.join(temp_dir, zip_name)
        zip_file = shutil.make_archive(zip_path, 'zip', source_dir)
        
        # Trigger download
        ui.download.file(zip_file, filename=f"{zip_name}.zip")

# Usage example
ui.button(
    'Download Project Files', 
    on_click=lambda: zip_and_download_directory('/path/to/project', 'project_files')
)
```

### Method 2: Using `zipfile` module for more control

```python
import os
import tempfile
import zipfile
from nicegui import ui

def zip_directory_custom(source_dir: str, zip_name: str = "archive"):
    """Create zip file with custom compression settings"""
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
        temp_zip_path = temp_file.name
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create relative path for archive
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        
        # Trigger download
        ui.download.file(temp_zip_path, filename=f"{zip_name}.zip")
        
    finally:
        # Clean up temporary file after download
        # Note: You might want to delay this or handle it differently
        # depending on your needs
        try:
            os.unlink(temp_zip_path)
        except:
            pass  # File might already be deleted

# Usage
ui.button(
    'Download Custom Archive', 
    on_click=lambda: zip_directory_custom('/path/to/directory', 'custom_archive')
)
```

## Advanced Example with Progress Indication

```python
import os
import tempfile
import shutil
import asyncio
from nicegui import ui

class DirectoryZipper:
    def __init__(self):
        self.progress = ui.linear_progress(value=0, show_value=False)
        self.progress.visible = False
        
    async def zip_and_download_async(self, source_dir: str, zip_name: str = "archive"):
        """Zip directory with progress indication"""
        self.progress.visible = True
        self.progress.value = 0.1
        
        try:
            # Run the zipping in a thread to avoid blocking UI
            await asyncio.get_event_loop().run_in_executor(
                None, self._create_zip, source_dir, zip_name
            )
            
            self.progress.value = 1.0
            ui.notify(f'Download started: {zip_name}.zip', type='positive')
            
        except Exception as e:
            ui.notify(f'Error creating zip: {str(e)}', type='negative')
        finally:
            self.progress.visible = False
            
    def _create_zip(self, source_dir: str, zip_name: str):
        """Create zip file in background thread"""
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, zip_name)
            zip_file = shutil.make_archive(zip_path, 'zip', source_dir)
            ui.download.file(zip_file, filename=f"{zip_name}.zip")

# Usage
zipper = DirectoryZipper()
ui.button(
    'Download with Progress', 
    on_click=lambda: zipper.zip_and_download_async('/path/to/large/directory', 'large_archive')
)
```

## Handling Different Scenarios

### Zip Multiple Directories

```python
def zip_multiple_directories(dir_dict: dict, zip_name: str = "multi_archive"):
    """Zip multiple directories into one archive
    
    Args:
        dir_dict: Dictionary with {folder_name: source_path}
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, f"{zip_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder_name, source_path in dir_dict.items():
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Create path with folder prefix
                        rel_path = os.path.relpath(file_path, source_path)
                        arc_path = os.path.join(folder_name, rel_path)
                        zipf.write(file_path, arc_path)
        
        ui.download.file(zip_path, filename=f"{zip_name}.zip")

# Usage
dirs_to_zip = {
    'config': '/path/to/config',
    'templates': '/path/to/templates',
    'assets': '/path/to/assets'
}
ui.button(
    'Download All Components',
    on_click=lambda: zip_multiple_directories(dirs_to_zip, 'project_components')
)
```

### Filter Files in Directory

```python
def zip_filtered_directory(source_dir: str, zip_name: str, 
                          include_patterns: list = None, 
                          exclude_patterns: list = None):
    """Zip directory with file filtering"""
    import fnmatch
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, f"{zip_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Apply include patterns
                    if include_patterns:
                        if not any(fnmatch.fnmatch(file, pattern) for pattern in include_patterns):
                            continue
                    
                    # Apply exclude patterns
                    if exclude_patterns:
                        if any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                            continue
                    
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        
        ui.download.file(zip_path, filename=f"{zip_name}.zip")

# Usage - only include Python and text files, exclude cache
ui.button(
    'Download Source Code',
    on_click=lambda: zip_filtered_directory(
        '/path/to/project',
        'source_code',
        include_patterns=['*.py', '*.txt', '*.md'],
        exclude_patterns=['*__pycache__*', '*.pyc']
    )
)
```

## Important Notes

1. **File Cleanup**: Temporary files are automatically cleaned up when using `tempfile.TemporaryDirectory()` or when the context manager exits.

2. **Large Files**: For large directories, consider using async operations to prevent UI blocking.

3. **Memory Usage**: `shutil.make_archive()` is generally more memory-efficient than manually creating zip files.

4. **Cross-Platform**: Use `os.path.join()` and `os.path.relpath()` for proper path handling across different operating systems.

5. **Error Handling**: Always wrap zip operations in try-catch blocks to handle permission errors, disk space issues, etc.

## Source Links

- [NiceGUI Download Documentation](https://nicegui.io/documentation/download)
- [Python zipfile module](https://docs.python.org/3/library/zipfile.html)
- [Python shutil.make_archive](https://docs.python.org/3/library/shutil.html#shutil.make_archive)
- [Python tempfile module](https://docs.python.org/3/library/tempfile.html)
