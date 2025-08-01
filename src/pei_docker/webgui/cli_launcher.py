"""
PeiDocker Web GUI CLI Launcher

This module provides the command-line interface for launching the PeiDocker NiceGUI
web application with various configuration options.
"""

import argparse
import asyncio
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, NoReturn
from contextlib import closing

from nicegui import ui, app

# Import the main app and models
from .app import create_app, PeiDockerWebGUI
from .models import TabName, AppState


def check_port_available(port: int) -> bool:
    """Check if a port is available for use.
    
    Args:
        port: Port number to check
        
    Returns:
        True if port is available, False otherwise
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        result = sock.connect_ex(('localhost', port))
        return result != 0


def create_project_with_cli(project_dir: Path) -> bool:
    """Create a new project using pei-docker-cli create command.
    
    Args:
        project_dir: Directory path for the new project
        
    Returns:
        True if project creation succeeded, False otherwise
    """
    try:
        result = subprocess.run(
            ['pei-docker-cli', 'create', '-p', str(project_dir)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error creating project: {e}", file=sys.stderr)
        return False


def validate_project_directory(project_dir: Path) -> tuple[bool, str]:
    """Validate if a project directory is legitimate for PeiDocker.
    
    Args:
        project_dir: Directory path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not project_dir.is_absolute():
        return False, "Project directory must be an absolute path"
    
    # Check if it's an existing PeiDocker project
    if project_dir.exists():
        # Check for user_config.yml as indicator of PeiDocker project
        config_file = project_dir / "user_config.yml"
        if config_file.exists():
            return True, ""
        else:
            # Directory exists but no config file
            if any(project_dir.iterdir()):
                return False, f"Directory exists but is not a PeiDocker project: {project_dir}"
            else:
                # Empty directory is okay - we can create project there
                return True, ""
    else:
        # Directory doesn't exist - check if parent is writable
        parent = project_dir.parent
        if not parent.exists():
            return False, f"Parent directory does not exist: {parent}"
        if not os.access(parent, os.W_OK):
            return False, f"No write permission for parent directory: {parent}"
        return True, ""


def validate_page_name(page_name: str) -> tuple[bool, str]:
    """Validate if page name is valid.
    
    Args:
        page_name: Page name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_pages = {tab.value for tab in TabName}
    valid_pages.add("home")  # Add home as special case
    
    if page_name not in valid_pages:
        return False, f"Invalid page name. Valid options: {', '.join(sorted(valid_pages))}"
    return True, ""


async def setup_initial_state(gui_app: PeiDockerWebGUI, project_dir: Optional[Path], 
                            jump_to_page: Optional[str]) -> None:
    """Setup initial application state based on CLI arguments.
    
    Args:
        gui_app: The PeiDockerWebGUI instance
        project_dir: Optional project directory to load/create
        jump_to_page: Optional page to navigate to
    """
    try:
        # If jump_to_page is specified but no project_dir, use the GUI's default
        if jump_to_page and not project_dir:
            # Get the default project directory from the GUI
            default_dir = gui_app._generate_default_project_dir()
            project_dir = Path(default_dir)
            print(f"No project directory specified, using default: {project_dir}")
        
        if project_dir:
            # Determine if we need to create or load project
            if project_dir.exists() and (project_dir / "user_config.yml").exists():
                # Load existing project
                print(f"Loading existing project from: {project_dir}")
                await gui_app.load_project(str(project_dir))
                # Check if project loaded successfully by checking app state
                if gui_app.data.app_state != AppState.ACTIVE:
                    print("Failed to load project")
                    return
            else:
                # Create new project
                print(f"Creating new project in: {project_dir}")
                if not project_dir.exists():
                    project_dir.mkdir(parents=True, exist_ok=True)
                
                if not create_project_with_cli(project_dir):
                    print("Failed to create project")
                    return
                
                # Load the newly created project
                await gui_app.load_project(str(project_dir))
                # Check if project loaded successfully by checking app state
                if gui_app.data.app_state != AppState.ACTIVE:
                    print("Failed to load created project")
                    return
            
            # Jump to specified page if project loaded successfully
            if gui_app.data.app_state == AppState.ACTIVE and jump_to_page:
                if jump_to_page == "home":
                    # Special case - we're already at home after load
                    pass
                else:
                    # Navigate to the specified tab
                    try:
                        tab_name = TabName(jump_to_page)
                        gui_app.switch_tab(tab_name)
                    except ValueError:
                        pass  # Invalid tab name, stay at default
    except Exception as e:
        print(f"Error in setup_initial_state: {e}")
        import traceback
        traceback.print_exc()


def start_command(args: argparse.Namespace) -> None:
    """Start the NiceGUI web application with specified options.
    
    Args:
        args: Parsed command line arguments
    """
    # Check port availability
    if not check_port_available(args.port):
        print(f"Error: Port {args.port} is already in use", file=sys.stderr)
        sys.exit(1)
    
    # Validate project directory if specified
    if args.project_dir:
        project_path = Path(args.project_dir).expanduser().resolve()
        is_valid, error_msg = validate_project_directory(project_path)
        if not is_valid:
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
    else:
        project_path = None
    
    # Validate page name if specified
    if args.jump_to_page:
        is_valid, error_msg = validate_page_name(args.jump_to_page)
        if not is_valid:
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
    
    # Create and configure the app
    @ui.page('/')
    async def index() -> None:
        gui_app = create_app()
        
        # Setup initial state if project directory or page specified
        if project_path or args.jump_to_page:
            ui.timer(0.5, lambda: asyncio.create_task(
                setup_initial_state(gui_app, project_path, args.jump_to_page)
            ), once=True)
    
    # Run the application
    print(f"Starting PeiDocker Web GUI on port {args.port}...")
    print(f"Open http://localhost:{args.port} in your browser")
    
    ui.run(
        host='0.0.0.0',
        port=args.port,
        title='PeiDocker Web GUI',
        favicon='🐳',
        dark=None,  # Auto-detect from system
        reload=False
    )


def main() -> None:
    """Main entry point for pei-docker-gui CLI."""
    parser = argparse.ArgumentParser(
        prog='pei-docker-gui',
        description='PeiDocker Web GUI - Launch the NiceGUI web application'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the NiceGUI web application')
    start_parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port to run the web application (default: 8080)'
    )
    start_parser.add_argument(
        '--project-dir',
        type=str,
        help='Project directory to load/create on startup'
    )
    start_parser.add_argument(
        '--jump-to-page',
        type=str,
        choices=['home', 'project', 'ssh', 'network', 'environment', 'storage', 'scripts', 'summary'],
        help='Page to navigate to after starting (creates default project if no --project-dir specified)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'start':
        start_command(args)
    else:
        # No command specified, show help
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()