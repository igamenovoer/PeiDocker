"""Startup screen for the PeiDocker GUI."""

from pathlib import Path
from typing import Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import PeiDockerApp

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Label, Static
from textual.timer import Timer

from ..models.config import ProjectConfig


class StartupScreen(Screen[None]):
    """Startup screen with system check and branding."""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("enter", "continue", "Continue"),
    ]
    
    DEFAULT_CSS = """
    StartupScreen {
        background: $surface;
        color: $text;
    }
    
    .logo {
        text-align: center;
        margin: 1 0;
        color: $accent;
    }
    
    .title {
        text-align: center;
        margin: 1 0;
        color: $primary;
    }
    
    .subtitle {
        text-align: center;
        margin: 1 0;
        color: $text-muted;
    }
    
    .system-status {
        border: solid $primary;
        padding: 1 2;
        margin: 2 4;
        background: $surface-lighten-1;
    }
    
    .status-item {
        margin: 0 1;
    }
    
    .status-ok {
        color: $success;
    }
    
    .status-warning {
        color: $warning;
    }
    
    .status-error {
        color: $error;
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
    """
    
    def __init__(self, project_config: ProjectConfig, docker_available: bool, docker_version: Optional[str]):
        super().__init__()
        self.project_config = project_config
        self.docker_available = docker_available
        self.docker_version = docker_version
        self._auto_continue_timer: Optional[Timer] = None
    
    def compose(self) -> ComposeResult:
        """Compose the startup screen."""
        with Center():
            with Middle():
                with Vertical():
                    yield Static(self._get_logo(), classes="logo")
                    yield Label("PeiDocker Configuration GUI", classes="title")
                    yield Label("Docker Container Configuration Made Easy", classes="subtitle")
                    
                    yield Static(self._get_system_status(), classes="system-status")
                    
                    with Horizontal(classes="actions"):
                        yield Button("Continue", id="continue", variant="primary")
                        yield Button("Quit", id="quit", variant="default")
                    
                    yield Label("Press 'q' to quit, Enter to continue", classes="help-text")
    
    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        # Auto-continue after 3 seconds if Docker is available
        if self.docker_available:
            self._auto_continue_timer = self.set_timer(3.0, self._auto_continue)
    
    def _auto_continue(self) -> None:
        """Auto-continue to next screen."""
        self.action_continue()
    
    def _get_logo(self) -> str:
        """Get ASCII logo for PeiDocker."""
        return """
██████╗ ███████╗██╗██████╗  ██████╗  ██████╗██╗  ██╗███████╗██████╗ 
██╔══██╗██╔════╝██║██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██████╔╝█████╗  ██║██║  ██║██║   ██║██║     █████╔╝ █████╗  ██████╔╝
██╔═══╝ ██╔══╝  ██║██║  ██║██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║     ███████╗██║██████╔╝╚██████╔╝╚██████╗██║  ██╗███████╗██║  ██║
╚═╝     ╚══════╝╚═╝╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
        """
    
    def _get_system_status(self) -> str:
        """Get system status information."""
        status_lines = ["System Status:"]
        
        # Docker status
        if self.docker_available:
            docker_info = f"✓ Docker: Available"
            if self.docker_version:
                docker_info += f" ({self.docker_version.split()[2]})"  # Extract version number only
            status_lines.append(docker_info)
        else:
            status_lines.append("⚠ Docker: Not available - some functions will not work")
        
        # Python status
        import sys
        status_lines.append(f"✓ Python: {sys.version.split()[0]}")
        
        # PeiDocker status
        try:
            from pei_docker._version import __version__
            status_lines.append(f"✓ PeiDocker: {__version__}")
        except ImportError:
            status_lines.append("✓ PeiDocker: Development version")
        
        return "\n".join(status_lines)
    
    @on(Button.Pressed, "#continue")
    def on_continue_pressed(self) -> None:
        """Continue button pressed."""
        self.action_continue()
    
    @on(Button.Pressed, "#quit")
    def on_quit_pressed(self) -> None:
        """Quit button pressed."""
        self.action_quit()
    
    def action_continue(self) -> None:
        """Continue to next screen."""
        # Cancel auto-continue timer if it exists
        if self._auto_continue_timer:
            self._auto_continue_timer.stop()
            self._auto_continue_timer = None
        
        # Check if project directory is already set
        if self.project_config.project_dir:
            # Project directory already set via --project-dir, create project and go to wizard
            if self._create_project():
                cast('PeiDockerApp', self.app).action_goto_simple_wizard()
            else:
                self.notify("Failed to create project structure", severity="error")
        else:
            # Need to get project directory first, then go to wizard
            from ..widgets.dialogs import ProjectDirectoryDialog
            project_dir_dialog = ProjectDirectoryDialog(self.project_config)
            self.app.push_screen(project_dir_dialog, self._on_project_dir_selected)
    
    def _on_project_dir_selected(self, result: Optional[str]) -> None:
        """Handle project directory selection result."""
        if result:
            self.project_config.project_dir = result
            self.project_config.project_name = Path(result).name
            if self._create_project():
                cast('PeiDockerApp', self.app).action_goto_simple_wizard()
            else:
                self.notify("Failed to create project structure", severity="error")
        # If result is None, user cancelled, so stay on startup screen
    
    def _create_project(self) -> bool:
        """Create the project directory structure."""
        try:
            import os
            import shutil
            from pei_docker.config_processor import Defaults
            from ..utils.file_utils import ensure_dir_exists
            
            project_dir = self.project_config.project_dir
            
            # Ensure project directory exists
            if not ensure_dir_exists(project_dir):
                return False
            
            # Copy all the files and folders from project_files to the output dir
            # This replicates the logic from the CLI create command
            this_dir = os.path.dirname(os.path.realpath(__file__))
            # Navigate up to the pei_docker package directory
            pei_docker_dir = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
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
        cast('PeiDockerApp', self.app).action_quit_app()