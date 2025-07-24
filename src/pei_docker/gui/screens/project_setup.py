"""
Screen 1: Project Directory Selection Screen for PeiDocker GUI.

This module implements the project directory selection screen (SC-1) in the PeiDocker
GUI application. This screen allows users to select or create a project directory
and configure the project name that will be used for Docker image naming.

The screen supports both interactive mode (user selects directory) and CLI override
mode (directory pre-filled from command line arguments). It provides real-time
validation of directory paths and project names according to Docker image naming
conventions.

Key Features
------------
- Interactive directory path input with browse functionality
- Real-time project name validation with Docker image naming rules
- CLI override support (--project-dir and --here options)
- Directory existence checking and creation validation
- Docker image name preview showing resulting image names
- Navigation controls with keyboard shortcuts

Classes
-------
ProjectDirectorySelectionScreen : Main screen implementation for project setup

Notes
-----
This screen is part of the sequential navigation flow: SC-0 → SC-1 → SC-2
where SC-1 handles project directory and naming configuration before proceeding
to the main wizard (SC-2).
"""

import re
from pathlib import Path
from typing import Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import PeiDockerApp

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Label, Static, Input
from textual.validation import Function
from textual_fspicker import SelectDirectory

from ..models.config import ProjectConfig
from ..utils.file_utils import check_path_writable, ensure_dir_exists


class ProjectDirectorySelectionScreen(Screen[None]):
    """
    Project Directory Selection Screen (SC-1) implementation.
    
    This screen provides the user interface for configuring the project directory
    and project name. It adapts its behavior based on whether CLI override options
    were provided (--project-dir or --here), showing different UI states for
    interactive vs. pre-configured scenarios.
    
    The screen performs real-time validation of user inputs and provides immediate
    feedback through status messages and visual indicators. It ensures that the
    selected directory is writable and the project name follows Docker image
    naming conventions.
    
    Attributes
    ----------
    project_config : ProjectConfig
        Central configuration object that stores all project settings.
    has_cli_project_dir : bool
        Whether the project directory was provided via CLI arguments,
        which affects UI behavior (disables directory input and browse button).
    project_dir_valid : bool
        Current validation state of the project directory path.
    project_name_valid : bool
        Current validation state of the project name.
        
    Parameters
    ----------
    project_config : ProjectConfig
        Project configuration object to manage settings.
    has_cli_project_dir : bool, default False
        Whether project directory was provided via CLI arguments.
        
    Notes
    -----
    CLI Override Behavior:
    - When has_cli_project_dir is True, directory input is disabled and grayed out
    - Browse button is hidden when in CLI override mode
    - Project name remains editable even with CLI override
    - Status messages indicate the source of the directory path
    
    Validation Rules:
    - Directory path must be valid and writable (or parent must be writable)
    - Project name must follow Docker image naming conventions:
      * 1-50 characters in length
      * Start with a letter
      * Only letters, numbers, hyphens, and underscores
      * No spaces allowed
    """
    
    BINDINGS = [
        ("b", "back", "Back"),
        ("enter", "continue", "Continue"),
    ]
    
    DEFAULT_CSS = """
    ProjectDirectorySelectionScreen {
        background: $surface;
        color: $text;
    }
    
    .main-container {
        border: solid $primary;
        padding: 2;
        margin: 2 4;
        background: $surface-lighten-1;
    }
    
    .title {
        text-align: center;
        margin: 1 0;
        color: $primary;
        text-style: bold;
    }
    
    .subtitle {
        text-align: center;
        margin: 1 0 2 0;
        color: $text;
    }
    
    .field-group {
        margin: 2 0;
    }
    
    .field-label {
        color: $text;
        margin-bottom: 1;
        text-style: bold;
    }
    
    .field-input {
        width: 100%;
        margin-bottom: 1;
    }
    
    .field-input.-disabled {
        background: $surface-darken-1;
        color: $text-muted;
    }
    
    .browse-button {
        text-align: right;
        margin-bottom: 1;
    }
    
    .status-message {
        margin: 1 0;
        padding: 1;
        border: solid $secondary;
        background: $surface-lighten-2;
    }
    
    .status-warning {
        border: solid $warning;
        color: $warning;
    }
    
    .status-info {
        border: solid $accent;
        color: $accent;
    }
    
    .status-error {
        border: solid $error;
        color: $error;
    }
    
    .docker-preview {
        margin: 2 0;
        padding: 1;
        border: solid $primary;
        background: $surface-lighten-2;
    }
    
    .docker-preview-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .docker-image-name {
        color: $success;
        margin: 0 2;
    }
    
    .actions {
        text-align: center;
        margin: 2 0;
    }
    
    .help-text {
        text-align: center;
        margin: 1 0;
        color: $text-muted;
    }
    
    Button {
        margin: 0 1;
    }
    
    Input.-invalid {
        border: solid $error;
    }
    """
    
    def __init__(self, project_config: ProjectConfig, has_cli_project_dir: bool = False) -> None:
        """
        Initialize the project directory selection screen.
        
        Parameters
        ----------
        project_config : ProjectConfig
            Project configuration object containing current settings.
        has_cli_project_dir : bool, default False
            Whether the project directory was provided via CLI arguments,
            which affects the UI behavior and field availability.
            
        Notes
        -----
        The constructor performs the following initialization:
        1. Sets up the project configuration reference
        2. Determines UI mode based on CLI override status
        3. Initializes validation states for directory and project name
        4. Auto-populates project name from directory if not already set
        """
        super().__init__()
        self.project_config: ProjectConfig = project_config
        self.has_cli_project_dir: bool = has_cli_project_dir
        
        # Validation states
        self.project_dir_valid: bool = bool(project_config.project_dir)
        self.project_name_valid: bool = bool(project_config.project_name)
        
        # Set initial project name from directory if available
        if not self.project_config.project_name and self.project_config.project_dir:
            self.project_config.project_name = Path(self.project_config.project_dir).name
            self.project_name_valid = self._validate_project_name(self.project_config.project_name)
    
    def compose(self) -> ComposeResult:
        """Compose the project directory selection screen."""
        with Center():
            with Middle():
                with Vertical(classes="main-container"):
                    yield Label("Project Directory Setup", classes="title")
                    yield Label("Select where to create your PeiDocker project:", classes="subtitle")
                    
                    # Project Directory Section
                    with Vertical(classes="field-group"):
                        yield Label("Project Directory:", classes="field-label")
                        yield Input(
                            value=self.project_config.project_dir or "",
                            placeholder="D:\\code\\my-project",
                            id="project_dir",
                            classes="field-input",
                            disabled=self.has_cli_project_dir,
                            validators=[Function(self._validate_project_dir, "Invalid directory path")]
                        )
                        
                        if not self.has_cli_project_dir:
                            with Horizontal(classes="browse-button"):
                                yield Button("Browse...", id="browse", variant="default")
                        
                        # Directory status message
                        yield Static(self._get_directory_status_message(), 
                                   classes=f"status-message {self._get_directory_status_class()}", 
                                   id="dir_status")
                    
                    # Project Name Section
                    with Vertical(classes="field-group"):
                        yield Label("Project Name (for Docker images):", classes="field-label")
                        yield Input(
                            value=self.project_config.project_name or "",
                            placeholder="my-project",
                            id="project_name",
                            classes="field-input",
                            validators=[Function(self._validate_project_name, "Invalid project name")]
                        )
                    
                    # Docker Image Preview
                    with Vertical(classes="docker-preview"):
                        yield Label("Docker images will be named:", classes="docker-preview-title")
                        yield Static(self._get_docker_image_preview(), id="docker_preview")
                    
                    # Action Buttons
                    with Horizontal(classes="actions"):
                        yield Button("Back", id="back", variant="default")
                        yield Button("Continue", id="continue", variant="primary", 
                                   disabled=not self._is_form_valid())
                    
                    yield Label("Press 'b' for back, Enter to continue", classes="help-text")
    
    def _validate_project_dir(self, value: str) -> bool:
        """
        Validate project directory path for accessibility and writability.
        
        Checks whether the provided directory path is valid and can be used
        for creating a PeiDocker project. Handles both existing and non-existing
        directories by checking parent directory permissions.
        
        Parameters
        ----------
        value : str
            Directory path to validate.
            
        Returns
        -------
        bool
            True if the directory path is valid and writable, False otherwise.
            
        Notes
        -----
        Validation criteria:
        1. Path must not be empty after stripping whitespace
        2. Path must be a valid filesystem path format
        3. If directory exists, it must be a directory and writable
        4. If directory doesn't exist, checks parent directory writability
        5. Traverses up the directory tree until finding an existing parent
        
        The method handles various filesystem errors gracefully and returns
        False for any path that cannot be validated or accessed.
        """
        if not value.strip():
            return False
        
        try:
            path = Path(value.strip()).resolve()
            
            # Check if path is valid format
            if not path.parts:
                return False
            
            # If directory exists, check if it's accessible
            if path.exists():
                return path.is_dir() and check_path_writable(str(path))
            
            # If it doesn't exist, check if parent directory is writable
            parent = path.parent
            while not parent.exists() and parent != parent.parent:
                parent = parent.parent
            
            return parent.exists() and check_path_writable(str(parent))
            
        except (OSError, PermissionError, ValueError):
            return False
    
    def _validate_project_name(self, value: str) -> bool:
        """
        Validate project name according to Docker image naming conventions.
        
        Ensures the project name follows Docker image naming rules since it
        will be used to generate Docker image names in the format:
        {project_name}:stage-1 and {project_name}:stage-2
        
        Parameters
        ----------
        value : str
            Project name to validate.
            
        Returns
        -------
        bool
            True if the project name is valid for Docker image naming,
            False otherwise.
            
        Notes
        -----
        Docker image naming rules enforced:
        1. Must be 1-50 characters in length
        2. Must start with a letter (a-z, A-Z)
        3. Can contain letters, numbers, hyphens (-), and underscores (_)
        4. No spaces or other special characters allowed
        5. Case-sensitive but typically lowercase is recommended
        
        The validation uses a regex pattern to ensure compliance with
        Docker's image naming requirements while being permissive enough
        for practical use cases.
        """
        name = value.strip()
        if not name:
            return False
        
        # Docker image name rules:
        # - Must be 1-50 characters
        # - Only lowercase letters, numbers, hyphens, underscores
        # - Must start with letter
        # - No spaces allowed
        if len(name) > 50:
            return False
        
        # Check pattern: starts with letter, contains only valid characters, doesn't end with hyphen
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9_]$|^[a-zA-Z]$'
        return bool(re.match(pattern, name))
    
    def _get_directory_status_message(self) -> str:
        """Get status message for directory field."""
        if not self.project_config.project_dir:
            return "Please enter a project directory path"
        
        path = Path(self.project_config.project_dir)
        if path.exists():
            return "Directory already exists"
        else:
            return "Directory will be created if it doesn't exist"
    
    def _get_directory_status_class(self) -> str:
        """Get CSS class for directory status."""
        if not self.project_config.project_dir:
            return "status-error"
        
        path = Path(self.project_config.project_dir)
        if path.exists():
            return "status-info"
        else:
            return "status-warning"
    
    def _get_docker_image_preview(self) -> str:
        """Get Docker image name preview."""
        project_name = self.project_config.project_name or "project-name"
        return f"• {project_name}:stage-1\n• {project_name}:stage-2"
    
    def _is_form_valid(self) -> bool:
        """Check if the form is valid and continue button should be enabled."""
        return self.project_dir_valid and self.project_name_valid
    
    def _update_continue_button(self) -> None:
        """Update the continue button enabled state."""
        try:
            continue_btn = self.query_one("#continue", Button)
            continue_btn.disabled = not self._is_form_valid()
        except:
            pass  # Button might not exist yet
    
    def _update_docker_preview(self) -> None:
        """Update the Docker image preview."""
        try:
            preview_widget = self.query_one("#docker_preview", Static)
            preview_widget.update(self._get_docker_image_preview())
        except:
            pass  # Widget might not exist yet
    
    def _update_directory_status(self) -> None:
        """Update the directory status message."""
        try:
            status_widget = self.query_one("#dir_status", Static)
            status_widget.update(self._get_directory_status_message())
            
            # Update CSS classes
            status_widget.remove_class("status-warning")
            status_widget.remove_class("status-info")
            status_widget.remove_class("status-error")
            status_widget.add_class(self._get_directory_status_class())
        except:
            pass  # Widget might not exist yet
    
    @on(Input.Changed, "#project_dir")
    def on_project_dir_changed(self, event: Input.Changed) -> None:
        """Handle project directory input changes."""
        value = event.value.strip()
        self.project_dir_valid = self._validate_project_dir(value)
        
        if self.project_dir_valid:
            self.project_config.project_dir = str(Path(value).resolve())
            
            # Auto-update project name if it's empty or matches old directory name
            path_name = Path(value).name
            if (not self.project_config.project_name or 
                self.project_config.project_name == Path(self.project_config.project_dir or "").name):
                self.project_config.project_name = path_name
                self.project_name_valid = self._validate_project_name(path_name)
                
                # Update project name input
                try:
                    project_name_input = self.query_one("#project_name", Input)
                    project_name_input.value = path_name
                except:
                    pass
        
        self._update_directory_status()
        self._update_docker_preview()
        self._update_continue_button()
    
    @on(Input.Changed, "#project_name")
    def on_project_name_changed(self, event: Input.Changed) -> None:
        """Handle project name input changes."""
        value = event.value.strip()
        self.project_name_valid = self._validate_project_name(value)
        
        if self.project_name_valid:
            self.project_config.project_name = value
        
        self._update_docker_preview()
        self._update_continue_button()
    
    @on(Button.Pressed, "#browse")
    def on_browse_pressed(self) -> None:
        """Browse for directory using file picker."""
        if not self.has_cli_project_dir:
            self.run_worker(self._browse_directory_async())
    
    async def _browse_directory_async(self) -> None:
        """Async worker to handle directory browsing."""
        directory = await self.app.push_screen_wait(SelectDirectory())
        if directory:
            # Update project directory input
            try:
                project_dir_input = self.query_one("#project_dir", Input)
                project_dir_input.value = str(directory)
                # This will trigger the Input.Changed event
            except:
                pass
    
    @on(Button.Pressed, "#back")
    def on_back_pressed(self) -> None:
        """Back button pressed."""
        self.action_back()
    
    @on(Button.Pressed, "#continue")
    def on_continue_pressed(self) -> None:
        """Continue button pressed."""
        self.action_continue()
    
    def action_back(self) -> None:
        """Go back to startup screen (SC-0)."""
        self.app.pop_screen()  # Return to startup screen
    
    def action_continue(self) -> None:
        """Continue to next screen (SC-2 - Simple Wizard Controller)."""
        if not self._is_form_valid():
            self.notify("Please correct the errors before proceeding", severity="warning")
            return
        
        # Create project directory if it doesn't exist
        if self.project_config.project_dir and not Path(self.project_config.project_dir).exists():
            if not ensure_dir_exists(self.project_config.project_dir):
                self.notify("Failed to create project directory", severity="error")
                return
        
        # Navigate to Simple Wizard Controller (SC-2)
        cast('PeiDockerApp', self.app).action_goto_simple_wizard()
    
    def get_project_name_error_message(self) -> Optional[str]:
        """Get detailed error message for invalid project names."""
        if not self.project_config.project_name:
            return None
        
        name = self.project_config.project_name.strip()
        
        if not name:
            return "Project name cannot be empty"
        
        if len(name) > 50:
            return "Project name cannot exceed 50 characters"
        
        if ' ' in name:
            return "No spaces allowed"
        
        if not re.match(r'^[a-zA-Z]', name):
            return "Must start with letter"
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
            return "Use letters, numbers, hyphens, and underscores only"
        
        return None