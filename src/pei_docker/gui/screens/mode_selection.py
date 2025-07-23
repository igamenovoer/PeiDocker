"""Mode selection screen for the PeiDocker GUI."""

from pathlib import Path
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Label, Static, Input, DirectoryTree
from textual.validation import Function

from textual_fspicker import SelectDirectory

from ..models.config import ProjectConfig
from ..utils.file_utils import ensure_dir_exists, check_path_writable
from ..widgets.dialogs import ErrorDialog


class ModeSelectionScreen(Screen[None]):
    """Screen for selecting configuration mode and project directory."""
    
    BINDINGS = [
        ("b", "back", "Back"),
        ("q", "quit", "Quit"),
    ]
    
    DEFAULT_CSS = """
    ModeSelectionScreen {
        background: $surface;
        overflow: auto;
    }
    
    VerticalScroll {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    .section {
        border: solid $primary;
        padding: 1 2;
        margin: 1 2;
        background: $surface-lighten-1;
    }
    
    .section-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .project-info {
        margin: 1 0;
        color: $text-muted;
    }
    
    .mode-card {
        border: solid $secondary;
        padding: 1 2;
        margin: 1 0;
        background: $surface-lighten-2;
    }
    
    .mode-card:hover {
        border: solid $accent;
        background: $surface-lighten-3;
    }
    
    .mode-title {
        color: $primary;
        text-style: bold;
    }
    
    .mode-features {
        color: $text-muted;
        margin-top: 1;
    }
    
    .selected-mode {
        border: solid $success;
        background: $success 20%;
    }
    
    .actions {
        text-align: center;
        margin: 2 0;
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
        text-align: center;
        margin: 1 0;
        color: $text-muted;
    }
    
    Button {
        margin: 0 1;
    }
    
    Button:disabled {
        color: $text-muted;
        background: $surface-darken-1;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        self.selected_mode = "simple"  # Default to simple mode
        self.project_dir_valid = bool(project_config.project_dir)
    
    def compose(self) -> ComposeResult:
        """Compose the mode selection screen."""
        with VerticalScroll():
            # Project directory section (only if not already set)
            if not self.project_config.project_dir:
                with Static(classes="section"):
                    yield Label("Project Directory Setup", classes="section-title")
                    yield Label("Select where to create your PeiDocker project:", classes="project-info")
                    
                    yield Input(
                        placeholder="Enter project directory path...",
                        id="project_dir",
                        validators=[Function(self._validate_project_dir, "Invalid directory path or parent directory not writable")]
                    )
                    yield Button("Browse...", id="browse", variant="default")
                    
                    if not self.project_dir_valid:
                        yield Label("⚠ Please enter a valid project directory path", classes="warning")
            else:
                with Static(classes="section"):
                    yield Label("Project Directory", classes="section-title")
                    yield Label(f"Project: {Path(self.project_config.project_dir).name}", classes="project-info")
                    yield Label(f"Path: {self.project_config.project_dir}", classes="project-info")
            
            # Mode selection section
            with Static(classes="section"):
                yield Label("Configuration Mode", classes="section-title")
                yield Label("Choose how you'd like to configure your project:", classes="project-info")
                
                # Simple mode card
                with Button(classes="mode-card" + (" selected-mode" if self.selected_mode == "simple" else ""), id="simple_mode"):
                    yield Label("Simple Mode", classes="mode-title")
                    yield Static(
                        "✓ Guided step-by-step configuration\n"
                        "✓ Common options only\n"
                        "✓ Perfect for beginners\n"
                        "✓ Quick setup",
                        classes="mode-features"
                    )
                
                # Advanced mode card  
                with Button(classes="mode-card" + (" selected-mode" if self.selected_mode == "advanced" else ""), id="advanced_mode"):
                    yield Label("Advanced Mode", classes="mode-title")
                    yield Static(
                        "✓ Complete control over all options\n"
                        "✓ Form-based editing\n"
                        "✓ Stage-1 and Stage-2 configuration\n"
                        "✓ Expert features",
                        classes="mode-features"
                    )
            
            # Actions
            with Horizontal(classes="actions"):
                yield Button("Back", id="back", variant="default")
                yield Button("Continue", id="continue", variant="primary", disabled=not self.project_dir_valid)
            
            yield Label("Select mode and press Continue to proceed", classes="help-text")
    
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
            
            # Update project config if valid (but don't create directory yet)
            if self.project_dir_valid:
                self.project_config.project_dir = str(Path(event.value.strip()).resolve())
                self.project_config.project_name = Path(event.value.strip()).name
            
            # Enable/disable continue button
            continue_btn = self.query_one("#continue", Button)
            continue_btn.disabled = not self.project_dir_valid
            
            # Update UI to show/hide warning
            self.refresh()
    
    @on(Button.Pressed, "#simple_mode")
    def on_simple_mode_pressed(self) -> None:
        """Simple mode selected."""
        self.selected_mode = "simple"
        self._update_mode_selection()
    
    @on(Button.Pressed, "#advanced_mode")  
    def on_advanced_mode_pressed(self) -> None:
        """Advanced mode selected."""
        self.selected_mode = "advanced"
        self._update_mode_selection()
    
    def _update_mode_selection(self) -> None:
        """Update the visual selection of modes."""
        simple_card = self.query_one("#simple_mode")
        advanced_card = self.query_one("#advanced_mode")
        
        if self.selected_mode == "simple":
            simple_card.add_class("selected-mode")
            advanced_card.remove_class("selected-mode") 
        else:
            advanced_card.add_class("selected-mode")
            simple_card.remove_class("selected-mode")
    
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
    
    @on(Button.Pressed, "#back")
    def on_back_pressed(self) -> None:
        """Back button pressed."""
        self.action_back()
    
    @on(Button.Pressed, "#continue")
    def on_continue_pressed(self) -> None:
        """Continue button pressed."""
        self.action_continue()
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
    
    def action_continue(self) -> None:
        """Continue to selected mode."""
        if not self.project_dir_valid:
            self.app.push_screen(ErrorDialog(
                "Invalid Project Directory",
                "Please enter a valid project directory first."
            ))
            return
        
        # Ensure project directory exists
        if not ensure_dir_exists(self.project_config.project_dir):
            self.app.push_screen(ErrorDialog(
                "Directory Creation Failed",
                f"Cannot create project directory: {self.project_config.project_dir}"
            ))
            return
        
        # Create project using the CLI create command logic
        if not self._create_project():
            self.app.push_screen(ErrorDialog(
                "Project Creation Failed",
                "Failed to create project structure. Please check permissions and try again."
            ))
            return
        
        if self.selected_mode == "simple":
            # Navigate to simple mode wizard
            from .simple.wizard import SimpleWizardScreen
            wizard_screen = SimpleWizardScreen(self.project_config)
            self.app.install_screen(wizard_screen, "simple_wizard")
            self.app.push_screen("simple_wizard")
        else:
            # TODO: Navigate to advanced mode
            self.notify("Advanced mode not yet implemented", severity="info")
    
    def _create_project(self) -> bool:
        """Create the project directory structure."""
        try:
            import os
            import shutil
            from pei_docker.config_processor import Defaults
            
            project_dir = self.project_config.project_dir
            
            # Ensure project directory exists
            if not ensure_dir_exists(project_dir):
                return False
            
            # Copy all the files and folders from project_files to the output dir
            # This replicates the logic from the CLI create command
            this_dir = os.path.dirname(os.path.realpath(__file__))
            # Navigate up to the pei_docker package directory
            pei_docker_dir = os.path.dirname(os.path.dirname(this_dir))
            project_template_dir = os.path.join(pei_docker_dir, 'project_files')
            
            if not os.path.exists(project_template_dir):
                return False
            
            for item in os.listdir(project_template_dir):
                s = os.path.join(project_template_dir, item)
                d = os.path.join(project_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            
            # Copy config and compose template files
            templates_dir = os.path.join(pei_docker_dir, 'templates')
            
            src_config_template = os.path.join(templates_dir, 'config-template-full.yml')
            dst_config_template = os.path.join(project_dir, Defaults.OutputConfigName)
            if os.path.exists(src_config_template):
                shutil.copy2(src_config_template, dst_config_template)
            
            src_compose_template = os.path.join(templates_dir, 'base-image-gen.yml')
            dst_compose_template = os.path.join(project_dir, Defaults.OutputComposeTemplateName)
            if os.path.exists(src_compose_template):
                shutil.copy2(src_compose_template, dst_compose_template)
            
            return True
            
        except Exception as e:
            self.log.error(f"Failed to create project: {e}")
            return False
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.action_quit_app()