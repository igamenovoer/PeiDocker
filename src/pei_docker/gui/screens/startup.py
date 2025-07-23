"""Startup screen for the PeiDocker GUI."""

from pathlib import Path
from typing import Optional

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
            # Skip directory selection, go directly to mode selection
            self.app.action_goto_mode_selection()
        else:
            # Need to get project directory first
            # For now, we'll go to mode selection and handle directory selection there
            self.app.action_goto_mode_selection()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.action_quit_app()