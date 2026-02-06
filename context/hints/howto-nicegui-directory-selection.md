# How to Open a Directory Selection Dialog in NiceGUI

This guide explains how to create a "browse for directory" dialog in NiceGUI applications that allows users to select a folder and returns the selected path.

## Overview

NiceGUI provides different approaches for directory selection depending on your deployment mode:

1. **Native Mode**: Use the built-in `create_file_dialog()` with `FOLDER_DIALOG` type
2. **Web Mode**: Use the custom `local_file_picker` example from the NiceGUI repository

## Method 1: Native Mode (Recommended for Desktop Apps)

### Prerequisites
- Your app must run in native mode (`ui.run(native=True)`)
- Import the required modules

### Basic Implementation

```python
from nicegui import app, ui
import webview

async def select_directory():
    """Open a native directory selection dialog"""
    selected_folder = await app.native.main_window.create_file_dialog(
        dialog_type=webview.FOLDER_DIALOG
    )
    
    if selected_folder is None:
        ui.notify("No folder selected")
        return None
    else:
        folder_path = selected_folder[0]  # Returns a list, take first item
        ui.notify(f"Selected folder: {folder_path}")
        return folder_path

# Create a button to trigger folder selection
ui.button("Browse for Folder", on_click=select_directory)

# Run in native mode
ui.run(native=True)
```

### Complete Example with Path Display

```python
from nicegui import app, ui
import webview
from pathlib import Path

class FolderSelector:
    def __init__(self):
        self.selected_path = None
        self.path_label = ui.label("No folder selected")
        
    async def browse_folder(self):
        """Open folder selection dialog and update display"""
        try:
            result = await app.native.main_window.create_file_dialog(
                dialog_type=webview.FOLDER_DIALOG
            )
            
            if result and len(result) > 0:
                self.selected_path = Path(result[0])
                self.path_label.text = f"Selected: {self.selected_path}"
                ui.notify(f"Folder selected: {self.selected_path.name}")
            else:
                ui.notify("Folder selection cancelled")
                
        except Exception as e:
            ui.notify(f"Error selecting folder: {str(e)}")

# Usage
selector = FolderSelector()
ui.button("📁 Browse for Folder", on_click=selector.browse_folder)

ui.run(native=True)
```

### Available Dialog Types

The `create_file_dialog()` function supports these dialog types:

- `webview.OPEN_DIALOG` - File selection dialog
- `webview.FOLDER_DIALOG` - Directory selection dialog  
- `webview.SAVE_DIALOG` - Save file dialog

### Additional Parameters

```python
# For file dialogs with specific file types
await app.native.main_window.create_file_dialog(
    dialog_type=webview.OPEN_DIALOG,
    allow_multiple=True,  # Allow multiple file selection
    file_types=("Text files (*.txt)", "All files (*.*)")
)

# For save dialogs
await app.native.main_window.create_file_dialog(
    dialog_type=webview.SAVE_DIALOG,
    save_filename="default_name.txt",
    file_types=("Text files (*.txt)",)
)
```

## Method 2: Web Mode (Custom File Browser)

For web deployment where native dialogs aren't available, use the custom file picker implementation.

### Basic Implementation

```python
from nicegui import ui
from pathlib import Path

async def web_directory_picker(start_path: str = "."):
    """Custom directory picker for web mode"""
    # This would use the local_file_picker example from NiceGUI
    # See: https://github.com/zauberzeug/nicegui/tree/main/examples/local_file_picker
    
    # Simplified version - you would implement the full AG Grid-based picker
    with ui.dialog() as dialog:
        with ui.card():
            ui.label("Select a directory:")
            # Add your custom directory browser implementation here
            
            with ui.row():
                ui.button("Cancel", on_click=dialog.close)
                ui.button("Select", on_click=lambda: dialog.submit(str(Path.cwd())))
    
    result = await dialog
    return result

# Usage
ui.button("Browse Directory", on_click=lambda: web_directory_picker())
ui.run()
```

## Important Considerations

### Security Limitations
- **Web Mode**: Browser security prevents direct file system access
- **Remote Access**: Native dialogs only work on the server machine, not client browsers
- **Permissions**: Ensure your application has proper file system permissions

### Browser vs Desktop Behavior
- **Native Mode**: Uses OS-native file dialogs (Windows Explorer, macOS Finder, etc.)
- **Web Mode**: Requires custom implementation using web technologies

### Error Handling
Always implement proper error handling for file operations:

```python
async def safe_directory_selection():
    try:
        result = await app.native.main_window.create_file_dialog(
            dialog_type=webview.FOLDER_DIALOG
        )
        if result:
            path = Path(result[0])
            if path.exists() and path.is_dir():
                return str(path)
            else:
                ui.notify("Selected path is not a valid directory")
    except Exception as e:
        ui.notify(f"Error: {str(e)}")
    return None
```

## Source References

- [NiceGUI File Picker Discussion #283](https://github.com/zauberzeug/nicegui/discussions/283)
- [NiceGUI Local File Picker Example](https://github.com/zauberzeug/nicegui/tree/main/examples/local_file_picker)
- [PyWebView API Documentation](https://pywebview.flowrl.com/guide/api.html)
- [NiceGUI Native Apps Tips (Japanese)](https://qiita.com/masushin/items/3cc7e941b7eebb26c4b5)

## Troubleshooting

**"Connection Lost" Error**: Ensure you're running in native mode and have the required dependencies installed.

**No Dialog Appears**: Check that your app is running in native mode (`ui.run(native=True)`).

**Permission Denied**: Verify that your application has the necessary file system permissions.

**Remote Access Issues**: Native dialogs only work locally. For remote access, implement the web-based file picker.
