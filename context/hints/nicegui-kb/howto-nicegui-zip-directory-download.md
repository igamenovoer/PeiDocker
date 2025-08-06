# How to Zip a Directory and Provide Download in NiceGUI

This guide shows how to create a zip file from a local directory and trigger a browser download in NiceGUI when a user clicks a button.

## Overview

NiceGUI provides several download functions through `ui.download` that can trigger browser downloads. To zip a directory and provide it as a download, you'll typically:

1. Create a temporary zip file from the directory
2. Use `ui.download.file()` to trigger the browser download
3. Clean up temporary files

## Basic Implementation

### Method 1: In-Memory Zip (Recommended for Reliability)

```python
import os
import zipfile
import io
from nicegui import ui

def zip_directory_in_memory(source_dir: str, zip_name: str = "archive"):
    """Create zip file entirely in memory and trigger download"""
    # Create in-memory bytes buffer
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Create relative path for archive
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
    
    # Get the zip data as bytes
    zip_data = zip_buffer.getvalue()
    zip_buffer.close()
    
    # Trigger download with in-memory data
    ui.download.content(zip_data, filename=f"{zip_name}.zip", media_type="application/zip")

# Usage example
ui.button(
    'Download Project Files', 
    on_click=lambda: zip_directory_in_memory('/path/to/project', 'project_files')
)
```

### Method 2: Using `shutil.make_archive()` (Simple but has timing issues)

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

### Method 3: Using `zipfile` module for more control (File-based)

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
import zipfile
import io
import asyncio
from nicegui import ui

class DirectoryZipper:
    def __init__(self):
        self.progress = ui.linear_progress(value=0, show_value=False)
        self.progress.visible = False
        
    async def zip_and_download_async(self, source_dir: str, zip_name: str = "archive"):
        """Zip directory with progress indication using in-memory approach"""
        self.progress.visible = True
        self.progress.value = 0.1
        
        try:
            # Run the zipping in a thread to avoid blocking UI
            zip_data = await asyncio.get_event_loop().run_in_executor(
                None, self._create_zip_in_memory, source_dir
            )
            
            self.progress.value = 0.9
            
            # Trigger download with in-memory data
            ui.download.content(zip_data, filename=f"{zip_name}.zip", media_type="application/zip")
            
            self.progress.value = 1.0
            ui.notify(f'Download started: {zip_name}.zip', type='positive')
            
        except Exception as e:
            ui.notify(f'Error creating zip: {str(e)}', type='negative')
        finally:
            self.progress.visible = False
            
    def _create_zip_in_memory(self, source_dir: str) -> bytes:
        """Create zip file in memory in background thread"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        
        zip_data = zip_buffer.getvalue()
        zip_buffer.close()
        return zip_data

# Usage
zipper = DirectoryZipper()
ui.button(
    'Download with Progress', 
    on_click=lambda: zipper.zip_and_download_async('/path/to/large/directory', 'large_archive')
)
```

## Handling Different Scenarios

### Zip Multiple Directories (In-Memory)

```python
import os
import zipfile
import io
from nicegui import ui

def zip_multiple_directories_memory(dir_dict: dict, zip_name: str = "multi_archive"):
    """Zip multiple directories into one archive using in-memory approach
    
    Args:
        dir_dict: Dictionary with {folder_name: source_path}
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_name, source_path in dir_dict.items():
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create path with folder prefix
                    rel_path = os.path.relpath(file_path, source_path)
                    arc_path = os.path.join(folder_name, rel_path)
                    zipf.write(file_path, arc_path)
    
    zip_data = zip_buffer.getvalue()
    zip_buffer.close()
    
    ui.download.content(zip_data, filename=f"{zip_name}.zip", media_type="application/zip")

# Usage
dirs_to_zip = {
    'config': '/path/to/config',
    'templates': '/path/to/templates',
    'assets': '/path/to/assets'
}
ui.button(
    'Download All Components',
    on_click=lambda: zip_multiple_directories_memory(dirs_to_zip, 'project_components')
)
```

### Filter Files in Directory (In-Memory)

```python
import os
import zipfile
import io
import fnmatch
from nicegui import ui

def zip_filtered_directory_memory(source_dir: str, zip_name: str, 
                                include_patterns: list = None, 
                                exclude_patterns: list = None):
    """Zip directory with file filtering using in-memory approach"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
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
    
    zip_data = zip_buffer.getvalue()
    zip_buffer.close()
    
    ui.download.content(zip_data, filename=f"{zip_name}.zip", media_type="application/zip")

# Usage - only include Python and text files, exclude cache
ui.button(
    'Download Source Code',
    on_click=lambda: zip_filtered_directory_memory(
        '/path/to/project',
        'source_code',
        include_patterns=['*.py', '*.txt', '*.md'],
        exclude_patterns=['*__pycache__*', '*.pyc']
    )
)
```

### Create Zip from File Contents (Pure In-Memory)

```python
import zipfile
import io
from nicegui import ui

def create_zip_from_content(file_contents: dict, zip_name: str = "content_archive"):
    """Create zip file from dictionary of file contents
    
    Args:
        file_contents: Dictionary with {filename: content} pairs
        content can be string or bytes
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename, content in file_contents.items():
            if isinstance(content, str):
                # For string content, encode to bytes
                zipf.writestr(filename, content.encode('utf-8'))
            else:
                # For binary content
                zipf.writestr(filename, content)
    
    zip_data = zip_buffer.getvalue()
    zip_buffer.close()
    
    ui.download.content(zip_data, filename=f"{zip_name}.zip", media_type="application/zip")

# Usage - create zip from generated content
file_data = {
    'readme.txt': 'This is a generated README file',
    'config.json': '{"setting": "value", "debug": true}',
    'data.csv': 'name,age,city\nJohn,30,NYC\nJane,25,LA'
}

ui.button(
    'Download Generated Files',
    on_click=lambda: create_zip_from_content(file_data, 'generated_files')
)
```

## Important Notes

1. **In-Memory vs File-Based**: **Use in-memory approach (`ui.download.content()` with `BytesIO`) for reliability**. File-based approaches using temporary files can fail if the file is deleted before the browser downloads it.

2. **Memory Usage**: In-memory zipping loads the entire zip file into RAM. For very large directories, consider:
   - Using file filtering to reduce size
   - Breaking large archives into smaller parts
   - Implementing streaming solutions for extremely large datasets

3. **Large Files**: For large directories, use async operations to prevent UI blocking.

4. **Cross-Platform**: Use `os.path.join()` and `os.path.relpath()` for proper path handling across different operating systems.

5. **Error Handling**: Always wrap zip operations in try-catch blocks to handle permission errors, disk space issues, etc.

6. **Media Type**: Specify `media_type="application/zip"` when using `ui.download.content()` for proper browser handling.

7. **File Encoding**: When using `zipf.writestr()` with string content, make sure to encode to bytes using `.encode('utf-8')`.

## Performance Comparison

- **In-Memory (`BytesIO`)**: Most reliable, no timing issues, uses more RAM
- **Temporary Files**: Can be faster for very large files, but has potential timing issues
- **`shutil.make_archive()`**: Simplest to use but has the most timing issues

## Source Links

- [NiceGUI Download Documentation](https://nicegui.io/documentation/download)
- [Python zipfile module](https://docs.python.org/3/library/zipfile.html)
- [Python io.BytesIO](https://docs.python.org/3/library/io.html#io.BytesIO)
- [Create in-memory zip files in Python - Medium](https://medium.com/@vickypalaniappan12/create-in-memory-zip-files-in-python-79193fbbc6c3)
- [Python shutil.make_archive](https://docs.python.org/3/library/shutil.html#shutil.make_archive)
- [Python tempfile module](https://docs.python.org/3/library/tempfile.html)
