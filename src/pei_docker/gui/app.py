"""Main GUI application for PeiDocker."""

import argparse
import sys  
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer

from .models.config import ProjectConfig
from .screens.startup import StartupScreen
from .screens.mode_selection import ModeSelectionScreen
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
        self.install_screen(ModeSelectionScreen(self.project_config), "mode_selection")
        
        # Start with startup screen
        self.push_screen("startup")
    
    def action_goto_mode_selection(self) -> None:
        """Navigate to mode selection screen."""
        self.push_screen("mode_selection")
    
    def action_quit_app(self) -> None:
        """Quit the application."""
        self.exit()


def main():
    """Main entry point for the GUI application."""
    parser = argparse.ArgumentParser(
        description="PeiDocker Terminal GUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pei-docker-gui                           # Start with project directory selection
  pei-docker-gui --project-dir ./my-app    # Start with specific project directory
        """
    )
    
    parser.add_argument(
        "--project-dir",
        type=str,
        help="Project directory to use (skips directory selection)"
    )
    
    args = parser.parse_args()
    
    # Validate project directory if provided
    if args.project_dir:
        project_path = Path(args.project_dir)
        if not project_path.exists():
            try:
                project_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"Error: Cannot create project directory '{args.project_dir}': {e}")
                sys.exit(1)
    
    # Create and run the application
    app = PeiDockerApp(project_dir=args.project_dir)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()