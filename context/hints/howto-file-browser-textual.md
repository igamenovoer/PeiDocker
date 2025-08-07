# How to Implement "Browse for..." File/Directory Selection in Textual

This guide covers how to implement file and directory browsing dialogs in Textual GUI applications using both built-in widgets and third-party libraries.

## Method 1: Using textual-fspicker Library (Recommended)

The `textual-fspicker` library provides ready-to-use file and directory selection dialogs.

### Installation

```bash
pip install textual-fspicker
```

### Basic File Open Dialog

```python
from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Button, Label
from textual_fspicker import FileOpen

class FileOpenApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Button("Browse for file...", id="browse")
        yield Label("No file selected", id="result")

    @on(Button.Pressed, "#browse")
    @work
    async def browse_file(self) -> None:
        # Open file dialog and wait for result
        if selected_file := await self.push_screen_wait(FileOpen()):
            self.query_one("#result", Label).update(f"Selected: {selected_file}")
        else:
            self.query_one("#result", Label).update("Selection cancelled")

if __name__ == "__main__":
    FileOpenApp().run()
```

### File Save Dialog

```python
from textual_fspicker import FileSave

class FileSaveApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Button("Save file as...", id="save")
        yield Label("No file selected", id="result")

    @on(Button.Pressed, "#save")
    @work
    async def save_file(self) -> None:
        if save_path := await self.push_screen_wait(FileSave()):
            self.query_one("#result", Label).update(f"Save to: {save_path}")
        else:
            self.query_one("#result", Label).update("Save cancelled")
```

### Directory Selection Dialog

```python
from textual_fspicker import SelectDirectory

class DirectorySelectApp(App[None]):
    def compose(self) -> ComposeResult:
        yield Button("Browse for directory...", id="browse")
        yield Label("No directory selected", id="result")

    @on(Button.Pressed, "#browse")
    @work
    async def browse_directory(self) -> None:
        if selected_dir := await self.push_screen_wait(SelectDirectory()):
            self.query_one("#result", Label).update(f"Selected: {selected_dir}")
        else:
            self.query_one("#result", Label).update("Selection cancelled")
```

### Advanced Options

#### Setting Default File/Directory

```python
# File open with default file
FileOpen(default_file="config.yml")

# File save with default filename
FileSave(default_file="output.txt")
```

#### File Existence Validation

```python
# Allow opening non-existent files (default: must_exist=True)
FileOpen(must_exist=False)

# Prevent overwriting existing files (default: can_overwrite=True)
FileSave(can_overwrite=False)
```

#### File Filtering

```python
from textual_fspicker import FileOpen, Filters

# Create filters for different file types
filters = Filters(
    ("Python Files", lambda p: p.suffix.lower() == ".py"),
    ("Text Files", lambda p: p.suffix.lower() in [".txt", ".md"]),
    ("YAML Files", lambda p: p.suffix.lower() in [".yml", ".yaml"]),
    ("All Files", lambda _: True),
)

# Use filters in dialog
FileOpen(filters=filters)
```

## Method 2: Using Built-in DirectoryTree Widget

For more customized file browsing, you can create your own dialog using Textual's `DirectoryTree` widget.

### Basic Custom File Browser Dialog

```python
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Label, Static

class FileBrowserDialog(ModalScreen[Path | None]):
    """A modal file browser dialog."""
    
    def __init__(self, start_path: str | Path = ".", title: str = "Select File"):
        super().__init__()
        self.start_path = Path(start_path)
        self.title = title
        self.selected_path: Path | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self.title, id="title")
            yield DirectoryTree(str(self.start_path), id="tree")
            with Grid(id="buttons"):
                yield Button("Select", variant="primary", id="select")
                yield Button("Cancel", variant="default", id="cancel")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection in the tree."""
        self.selected_path = event.path
        self.query_one("#select", Button).disabled = False

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Handle directory selection in the tree."""
        self.selected_path = event.path
        self.query_one("#select", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "select":
            self.dismiss(self.selected_path)
        elif event.button.id == "cancel":
            self.dismiss(None)

# Usage in main app
class MainApp(App):
    def compose(self) -> ComposeResult:
        yield Button("Browse Files...", id="browse")
        yield Label("No file selected", id="result")

    @on(Button.Pressed, "#browse")
    @work
    async def browse_files(self) -> None:
        if selected := await self.push_screen_wait(FileBrowserDialog(".")):
            self.query_one("#result", Label).update(f"Selected: {selected}")
        else:
            self.query_one("#result", Label).update("No file selected")
```

### Custom Directory-Only Browser

```python
class DirectoryBrowserDialog(ModalScreen[Path | None]):
    """A modal directory browser dialog."""
    
    def __init__(self, start_path: str | Path = ".", title: str = "Select Directory"):
        super().__init__()
        self.start_path = Path(start_path)
        self.title = title
        self.selected_path: Path | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self.title, id="title")
            yield DirectoryTree(str(self.start_path), id="tree")
            with Grid(id="buttons"):
                yield Button("Select", variant="primary", id="select")
                yield Button("Cancel", variant="default", id="cancel")

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Only handle directory selection."""
        self.selected_path = event.path
        self.query_one("#select", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "select":
            self.dismiss(self.selected_path)
        elif event.button.id == "cancel":
            self.dismiss(None)
```

### Filtered File Browser

```python
from typing import Callable

class FilteredFileBrowser(DirectoryTree):
    """A DirectoryTree that filters files by extension."""
    
    def __init__(self, path: str, file_filter: Callable[[Path], bool] = None):
        super().__init__(path)
        self.file_filter = file_filter or (lambda _: True)

    def filter_paths(self, paths) -> list[Path]:
        """Filter paths based on the file filter."""
        filtered = []
        for path in paths:
            if path.is_dir() or self.file_filter(path):
                filtered.append(path)
        return filtered

# Usage: Only show Python files
python_filter = lambda p: p.suffix.lower() == ".py"
filtered_browser = FilteredFileBrowser(".", python_filter)
```

## Method 3: Integration with System File Dialogs (Alternative)

For system-native file dialogs, you might consider using `tkinter.filedialog` as a fallback:

```python
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

def system_file_dialog(title: str = "Select File", 
                      filetypes: list = None) -> Path | None:
    """Open system file dialog."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    filetypes = filetypes or [("All files", "*.*")]
    filename = filedialog.askopenfilename(title=title, filetypes=filetypes)
    
    root.destroy()
    return Path(filename) if filename else None

def system_directory_dialog(title: str = "Select Directory") -> Path | None:
    """Open system directory dialog."""
    root = tk.Tk()
    root.withdraw()
    
    dirname = filedialog.askdirectory(title=title)
    
    root.destroy()
    return Path(dirname) if dirname else None
```

## Best Practices

1. **Use textual-fspicker for standard dialogs** - It provides polished, ready-to-use dialogs
2. **Handle cancellation** - Always check if the result is `None` when user cancels
3. **Use `@work` decorator** - File operations should be async to avoid blocking the UI
4. **Validate paths** - Check if selected paths exist and are accessible
5. **Set appropriate defaults** - Use `default_file` or start in a meaningful directory
6. **Add file filtering** - Use filters to help users find relevant files
7. **Handle errors gracefully** - File system operations can fail, so wrap in try/except

## CSS Styling

You can style the file browser dialogs with CSS:

```css
FileBrowserDialog {
    align: center middle;
}

#title {
    text-align: center;
    padding: 1;
    background: $primary;
    color: $text;
}

#tree {
    height: 20;
    border: solid $primary;
}

#buttons {
    grid-size: 2 1;
    grid-gutter: 1;
    padding: 1;
}
```

## Summary

- **textual-fspicker** is the easiest and most feature-complete solution
- **DirectoryTree** allows for custom implementations with more control
- Both approaches return `Path` objects or `None` for cancellation
- Use modal screens (`ModalScreen`) to create dialog-like behavior
- Always handle the async nature of file dialogs with `@work` decorator
