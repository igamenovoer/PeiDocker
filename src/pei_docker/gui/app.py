"""Main GUI application for PeiDocker."""

import sys  
from pathlib import Path
from typing import Optional

import click
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer

from .models.config import ProjectConfig
from .screens.startup import StartupScreen
from .utils.docker_utils import check_docker_available


class PeiDockerApp(App[None]):
    """Main PeiDocker GUI application."""
    
    CSS_PATH = None
    TITLE = "PeiDocker Configuration GUI"
    SUB_TITLE = "Docker Container Configuration Made Easy"
    
    DEFAULT_CSS = """
    Screen {
        background: $surface;
    }
    
    Header {
        dock: top;
        height: 3;
    }
    
    Footer {
        dock: bottom;
        height: 3;
    }
    """
    
    def __init__(self, project_dir: Optional[str] = None):
        super().__init__()
        self.project_config = ProjectConfig()
        
        # Set project directory if provided
        if project_dir:
            self.project_config.project_dir = str(Path(project_dir).resolve())
            self.project_config.project_name = Path(project_dir).name
        
        # Check Docker availability on startup
        self.docker_available, self.docker_version = check_docker_available()
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Install all screens
        self.install_screen(StartupScreen(self.project_config, self.docker_available, self.docker_version), "startup")
        
        # Start with startup screen
        self.push_screen("startup")
    
    def action_goto_project_setup(self) -> None:
        """Navigate to project directory selection screen (SC-1)."""
        from .screens.project_setup import ProjectDirectorySelectionScreen
        project_setup_screen = ProjectDirectorySelectionScreen(
            self.project_config, 
            has_cli_project_dir=bool(self.project_config.project_dir)
        )
        self.install_screen(project_setup_screen, "project_setup")
        self.push_screen("project_setup")
    
    def action_goto_simple_wizard(self) -> None:
        """Navigate directly to simple wizard screen."""
        from .screens.simple.wizard import SimpleWizardScreen
        wizard_screen = SimpleWizardScreen(self.project_config)
        self.install_screen(wizard_screen, "simple_wizard")
        self.push_screen("simple_wizard")
    
    def action_quit_app(self) -> None:
        """Quit the application."""
        self.exit()


def _validate_and_create_project_dir(project_dir: str) -> str:
    """Validate and create project directory if needed."""
    project_path = Path(project_dir)
    if not project_path.exists():
        try:
            project_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            click.echo(f"Error: Cannot create project directory '{project_dir}': {e}", err=True)
            sys.exit(1)
    return str(project_path.resolve())


def _run_app(project_dir: Optional[str] = None, dev_screen: Optional[str] = None) -> None:
    """Run the PeiDocker GUI application."""
    app = PeiDockerApp(project_dir=project_dir)
    
    # Handle development mode screen selection
    if dev_screen:
        if not project_dir:
            click.echo("Error: --screen option requires --project-dir to be specified", err=True)
            sys.exit(1)
        
        # TODO: Implement screen-specific startup for development mode
        # For now, we'll just start normally and log the intended screen
        click.echo(f"Starting in development mode with screen: {dev_screen}")
    
    try:
        app.run()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.group()
@click.version_option()
def cli() -> None:
    """PeiDocker Terminal GUI - Docker Container Configuration Made Easy."""
    pass


@cli.command()
@click.option(
    "--project-dir",
    type=click.Path(path_type=Path),
    help="Project directory to use (skips directory selection)"
)
@click.option(
    "--here",
    is_flag=True,
    help="Use current directory as the project directory"
)
def start(project_dir: Optional[Path], here: bool) -> None:
    """Start the GUI application."""
    if here and project_dir:
        click.echo("Error: Cannot specify both --here and --project-dir", err=True)
        sys.exit(1)
    
    final_project_dir: Optional[str] = None
    
    if here:
        final_project_dir = str(Path.cwd().resolve())
    elif project_dir:
        final_project_dir = _validate_and_create_project_dir(str(project_dir))
    
    _run_app(project_dir=final_project_dir)


@cli.command()
@click.option(
    "--project-dir",
    type=click.Path(path_type=Path),
    help="Project directory to use (required for dev mode)"
)
@click.option(
    "--here",
    is_flag=True,
    help="Use current directory as the project directory"
)
@click.option(
    "--screen",
    type=str,
    help="Screen to start with (e.g., 'sc-0', 'sc-1', etc.)"
)
def dev(project_dir: Optional[Path], here: bool, screen: Optional[str]) -> None:
    """Start the GUI in development mode."""
    if here and project_dir:
        click.echo("Error: Cannot specify both --here and --project-dir", err=True)
        sys.exit(1)
    
    if screen and not (here or project_dir):
        click.echo("Error: --screen option requires --project-dir or --here to be specified", err=True)
        sys.exit(1)
    
    final_project_dir: Optional[str] = None
    
    if here:
        final_project_dir = str(Path.cwd().resolve())
    elif project_dir:
        final_project_dir = _validate_and_create_project_dir(str(project_dir))
    
    _run_app(project_dir=final_project_dir, dev_screen=screen)


def main() -> None:
    """Main entry point for the GUI application."""
    cli()


if __name__ == "__main__":
    main()