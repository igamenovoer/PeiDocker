"""Modal dialog components for PeiDocker GUI."""

from pathlib import Path
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label, Input
from textual.validation import Function
from textual.message import Message

from textual_fspicker import SelectDirectory

from ..models.config import ProjectConfig
from ..utils.file_utils import ensure_dir_exists, check_path_writable


class ErrorDialog(ModalScreen[None]):
    """Modal dialog for displaying error messages."""
    
    DEFAULT_CSS = """
    ErrorDialog {
        align: center middle;
    }
    
    #error-dialog {
        grid-size: 1;
        grid-gutter: 1;
        grid-rows: auto auto auto;
        padding: 0 1;
        width: 60;
        height: auto;
        border: thick $error 80%;
        background: $surface;
    }
    
    .dialog-title {
        color: $error;
        text-style: bold;
        text-align: center;
        padding: 1 0;
    }
    
    .dialog-message {
        color: $text;
        text-align: left;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary;
    }
    
    .dialog-buttons {
        align: center middle;
        padding: 1 0;
    }
    """
    
    def __init__(self, title: str, message: str):
        super().__init__()
        self.dialog_title = title
        self.dialog_message = message
    
    def compose(self) -> ComposeResult:
        """Create the error dialog."""
        with Grid(id="error-dialog"):
            yield Label(self.dialog_title, classes="dialog-title")
            yield Static(self.dialog_message, classes="dialog-message")
            with Horizontal(classes="dialog-buttons"):
                yield Button("OK", variant="error", id="ok")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "ok":
            self.dismiss()


class ConfirmDialog(ModalScreen[bool]):
    """Modal dialog for confirmation prompts."""
    
    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }
    
    #confirm-dialog {
        grid-size: 1;
        grid-gutter: 1;
        grid-rows: auto auto auto;
        padding: 0 1;
        width: 60;
        height: auto;
        border: thick $warning 80%;
        background: $surface;
    }
    
    .dialog-title {
        color: $warning;
        text-style: bold;
        text-align: center;
        padding: 1 0;
    }
    
    .dialog-message {
        color: $text;
        text-align: left;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary;
    }
    
    .dialog-buttons {
        align: center middle;
        padding: 1 0;
    }
    """
    
    def __init__(self, title: str, message: str):
        super().__init__()
        self.dialog_title = title
        self.dialog_message = message
    
    def compose(self) -> ComposeResult:
        """Create the confirmation dialog."""
        with Grid(id="confirm-dialog"):
            yield Label(self.dialog_title, classes="dialog-title")
            yield Static(self.dialog_message, classes="dialog-message")
            with Horizontal(classes="dialog-buttons"):
                yield Button("Yes", variant="success", id="yes")
                yield Button("No", variant="default", id="no")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "yes":
            self.dismiss(True)
        elif event.button.id == "no":
            self.dismiss(False)


class ProjectDirectoryDialog(ModalScreen[Optional[str]]):
    """Modal dialog for selecting project directory."""
    
    DEFAULT_CSS = """
    ProjectDirectoryDialog {
        align: center middle;
    }
    
    #project-dialog {
        grid-size: 1;
        grid-gutter: 1;
        grid-rows: auto auto auto auto;
        padding: 0 1;
        width: 80;
        height: auto;
        border: thick $primary 80%;
        background: $surface;
    }
    
    .dialog-title {
        color: $primary;
        text-style: bold;
        text-align: center;
        padding: 1 0;
    }
    
    .dialog-content {
        color: $text;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $secondary;
    }
    
    .dialog-buttons {
        align: center middle;
        padding: 1 0;
    }
    
    Input {
        margin: 1 0;
    }
    
    Input.-invalid {
        border: solid $error;
    }
    
    .warning {
        color: $warning;
        margin: 1 0;
    }
    
    .help-text {
        color: $text-muted;
        margin: 1 0;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        self.project_dir_valid = False
    
    def compose(self) -> ComposeResult:
        """Create the project directory dialog."""
        with Grid(id="project-dialog"):
            yield Label("Project Directory Setup", classes="dialog-title")
            
            with Vertical(classes="dialog-content"):
                yield Label("Select where to create your PeiDocker project:", classes="help-text")
                
                yield Input(
                    placeholder="Enter project directory path...",
                    id="project_dir",
                    validators=[Function(self._validate_project_dir, "Invalid directory path or parent directory not writable")]
                )
                
                with Horizontal():
                    yield Button("Browse...", id="browse", variant="default")
                
                yield Label("Directory will be created if it doesn't exist", classes="help-text")
                
                if not self.project_dir_valid:
                    yield Label("Please enter a valid project directory path", classes="warning")
            
            with Horizontal(classes="dialog-buttons"):
                yield Button("Cancel", id="cancel", variant="default")
                yield Button("Continue", id="continue", variant="primary", disabled=True)
    
    def _validate_project_dir(self, value: str) -> bool:
        """Validate project directory path format without creating directories."""
        if not value.strip():
            return False
        
        try:
            path = Path(value.strip()).resolve()
            
            # Check if path is valid format
            if not path.parts:  # Empty path
                return False
            
            # If the directory already exists, check if it's writable
            if path.exists():
                return path.is_dir() and check_path_writable(str(path))
            
            # If it doesn't exist, check if the parent directory is writable
            # This validates we can create the directory without actually creating it
            parent = path.parent
            while not parent.exists() and parent != parent.parent:
                parent = parent.parent
            
            return parent.exists() and check_path_writable(str(parent))
            
        except (OSError, PermissionError, ValueError):
            return False
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        if event.input.id == "project_dir":
            self.project_dir_valid = self._validate_project_dir(event.value)
            
            # Enable/disable continue button
            continue_btn = self.query_one("#continue", Button)
            continue_btn.disabled = not self.project_dir_valid
            
            # Update UI to show/hide warning
            self.refresh()
    
    @on(Button.Pressed, "#browse")
    def on_browse_pressed(self) -> None:
        """Browse for directory using file picker."""
        # Launch directory picker using async worker
        self.run_worker(self._browse_directory_async())

    async def _browse_directory_async(self) -> None:
        """Async worker to handle directory browsing."""
        directory = await self.app.push_screen_wait(SelectDirectory())
        if directory:
            project_dir_input = self.query_one("#project_dir", Input)
            project_dir_input.value = str(directory)
            # Trigger validation
            self.on_input_changed(Input.Changed(project_dir_input, project_dir_input.value))
    
    @on(Button.Pressed, "#cancel")
    def on_cancel_pressed(self) -> None:
        """Cancel button pressed."""
        self.dismiss(None)
    
    @on(Button.Pressed, "#continue")
    def on_continue_pressed(self) -> None:
        """Continue button pressed."""
        if self.project_dir_valid:
            project_dir_input = self.query_one("#project_dir", Input)
            self.dismiss(str(Path(project_dir_input.value.strip()).resolve()))