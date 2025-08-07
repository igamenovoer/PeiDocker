"""
PeiDocker Web GUI CLI Launcher
==============================

This module provides the command-line interface for launching the PeiDocker NiceGUI
web application with various configuration options and debugging capabilities.

Command Line Usage
------------------
The `pei-docker-gui` command provides a NiceGUI-based web interface for PeiDocker
with advanced project management and debugging features.

Basic Usage::

    pei-docker-gui start [OPTIONS]

Available Commands
------------------

start
    Start the NiceGUI web application server

Options for 'start' Command
---------------------------

--port <port>
    Port to run the web application (default: auto-select free port)
    If not specified, automatically selects an available port.
    If specified but in use, finds the next available port.

--project-dir <path>
    Project directory to load or create on startup.
    
    - If directory exists with user_config.yml: Load existing PeiDocker project
    - If directory exists but empty: Create new project in that location  
    - If directory doesn't exist: Create directory and new project
    - If directory contains non-PeiDocker files: Show error and exit

--jump-to-page <page_name>
    Navigate to specific page after startup. Creates default project if no
    --project-dir specified. Valid page names:
    
    - home: Main welcome page
    - project: Project configuration page
    - ssh: SSH configuration page  
    - network: Network configuration page
    - environment: Environment variables page
    - storage: Volume and bind mount configuration
    - scripts: Custom scripts configuration
    - summary: Complete project configuration overview

Usage Examples
--------------

Start web GUI on default port::

    pei-docker-gui start

Start on custom port::

    pei-docker-gui start --port 9090

Load existing project::

    pei-docker-gui start --project-dir /path/to/my/project

Create new project and jump to SSH config::

    pei-docker-gui start --project-dir /tmp/new-project --jump-to-page ssh

Quick debugging - jump to network page with default project::

    pei-docker-gui start --jump-to-page network

Notes
-----
- The web interface will be available at http://localhost:<port>
- Project validation occurs before server startup to prevent runtime errors
- Jump-to-page functionality is ideal for development and debugging workflows
- Default projects are created in system temp directory with timestamp
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
from pei_docker.webgui.app import create_app, PeiDockerWebGUI, TabName, AppState


def check_port_available(port: int) -> bool:
    """Check if a port is available for use.

    Attempts to connect to the specified port on localhost to determine
    if it's already in use by another process.

    Parameters
    ----------
    port : int
        Port number to check for availability.

    Returns
    -------
    bool
        True if port is available (connection failed), False if port is in use.

    Examples
    --------
    >>> check_port_available(8080)
    True
    >>> check_port_available(80)  # Typically in use
    False
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        result = sock.connect_ex(('localhost', port))
        return result != 0


def get_free_port() -> int:
    """Get a free TCP port in a cross-platform way.
    
    Uses the OS to atomically assign a free port, preventing race conditions.
    
    Returns
    -------
    int
        An available port number.
    
    Notes
    -----
    This method is more reliable than sequentially checking ports as it lets
    the OS handle port assignment atomically.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to any available port
        port = s.getsockname()[1]  # Get the assigned port number
    return port


def find_free_port(start_port: int = 8080, max_tries: int = 100) -> Optional[int]:
    """Find the next available port starting from start_port.
    
    Sequentially checks ports starting from start_port until an available one
    is found or max_tries attempts have been made.
    
    Parameters
    ----------
    start_port : int, optional
        Port number to start checking from (default: 8080).
    max_tries : int, optional
        Maximum number of ports to try (default: 100).
    
    Returns
    -------
    int or None
        The first available port found, or None if no ports are available
        within max_tries attempts.
    
    Notes
    -----
    This method tries sequential ports starting from start_port. It's useful
    when you want a port close to a specific number (like 8080, 8081, 8082...).
    """
    port = start_port
    for _ in range(max_tries):
        if port >= 65535:
            break
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    return None


def create_project_with_cli(project_dir: Path) -> bool:
    """Create a new project using pei-docker-cli create command.

    Executes the `pei-docker-cli create` command to initialize a new PeiDocker
    project in the specified directory. Captures output and returns success status.

    Parameters
    ----------
    project_dir : Path
        Directory path where the new project will be created. Must be a valid
        filesystem path.

    Returns
    -------
    bool
        True if project creation succeeded (return code 0), False otherwise.

    Notes
    -----
    This function calls the external `pei-docker-cli` command and requires it
    to be available in the system PATH. Error messages are written to stderr
    if the command fails or raises an exception.

    Examples
    --------
    >>> from pathlib import Path
    >>> create_project_with_cli(Path("/tmp/my-project"))
    True
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

    Performs comprehensive validation of a project directory to ensure it can
    be used for PeiDocker operations. Checks path validity, existing project
    status, and write permissions.

    Parameters
    ----------
    project_dir : Path
        Directory path to validate. Must be an absolute path.

    Returns
    -------
    tuple[bool, str]
        A tuple containing:
        - bool: True if directory is valid for use, False otherwise
        - str: Error message if validation failed, empty string if valid

    Notes
    -----
    Validation criteria:
    - Path must be absolute
    - If exists: must be empty or contain user_config.yml (PeiDocker project)
    - If doesn't exist: parent directory must exist and be writable
    - Non-empty directories without user_config.yml are rejected

    Examples
    --------
    >>> from pathlib import Path
    >>> validate_project_directory(Path("/tmp/new-project"))
    (True, "")
    >>> validate_project_directory(Path("relative/path"))
    (False, "Project directory must be an absolute path")
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
    """Validate if page name is valid for jump-to-page functionality.

    Checks if the provided page name matches one of the available tab names
    in the NiceGUI web application or the special "home" page.

    Parameters
    ----------
    page_name : str
        Page name to validate against available options.

    Returns
    -------
    tuple[bool, str]
        A tuple containing:
        - bool: True if page name is valid, False otherwise
        - str: Error message listing valid options if invalid, empty string if valid

    Notes
    -----
    Valid page names are derived from the TabName enum plus "home" as a special case.
    The validation is case-sensitive and must match exactly.

    Examples
    --------
    >>> validate_page_name("project")
    (True, "")
    >>> validate_page_name("invalid")
    (False, "Invalid page name. Valid options: environment, home, network, project, scripts, ssh, storage, summary")
    """
    valid_pages = {tab.value for tab in TabName}
    valid_pages.add("home")  # Add home as special case
    
    if page_name not in valid_pages:
        return False, f"Invalid page name. Valid options: {', '.join(sorted(valid_pages))}"
    return True, ""


async def setup_initial_state(gui_app: PeiDockerWebGUI, project_dir: Optional[Path], 
                            jump_to_page: Optional[str]) -> None:
    """Setup initial application state based on CLI arguments.

    Configures the web application state by loading/creating projects and 
    navigating to specified pages. Handles both existing and new project scenarios.

    Parameters
    ----------
    gui_app : PeiDockerWebGUI
        The initialized PeiDockerWebGUI application instance.
    project_dir : Path, optional
        Project directory to load or create. If None and jump_to_page is specified,
        uses the GUI's default project directory.
    jump_to_page : str, optional
        Page name to navigate to after project setup. Must be a valid page name
        from the TabName enum or "home".

    Notes
    -----
    Project handling logic:
    - Existing project (has user_config.yml): Load project directly
    - New location: Create project using pei-docker-cli, then load
    - Navigation only occurs if project loading succeeds
    - Errors are printed to stdout with traceback for debugging

    The function uses a 0.5 second timer delay to ensure proper GUI initialization
    before applying state changes.

    Raises
    ------
    Exception
        Any exceptions during project loading or navigation are caught and logged
        with full traceback for debugging purposes.
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
                if gui_app.app_state != AppState.ACTIVE:
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
                if gui_app.app_state != AppState.ACTIVE:
                    print("Failed to load created project")
                    return
            
            # Jump to specified page if project loaded successfully
            if gui_app.app_state == AppState.ACTIVE and jump_to_page:
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

    Main entry point for the 'start' subcommand. Validates all arguments,
    configures the web application, and starts the server with proper error handling.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command line arguments containing:
        - port: Server port number (None for auto-select)
        - project_dir: Optional project directory path  
        - jump_to_page: Optional page name for navigation

    Notes
    -----
    Validation sequence:
    1. Determine port: auto-select if None, or use/find alternative for specified port
    2. Validate project directory path and permissions
    3. Validate page name if jump-to-page specified
    4. Configure NiceGUI application with timer-based state setup
    5. Start server on 0.0.0.0 with selected port

    The server runs with auto-detect dark mode, no reload, and 🐳 favicon.
    State setup is delayed by 0.5 seconds to ensure proper GUI initialization.
    
    By default (when no --port specified), uses an OS-selected free port.
    If a specific port is requested but unavailable, automatically finds an alternative.

    Raises
    ------
    SystemExit
        Exits with code 1 if project directory is invalid or page name is invalid.
    """
    # Determine which port to use
    if args.port is None:
        # No port specified - use OS-selected free port
        actual_port = get_free_port()
        print(f"No port specified, using auto-selected port {actual_port}", file=sys.stderr)
    else:
        # Port specified - try to use it, fallback if needed
        desired_port = args.port
        if check_port_available(desired_port):
            actual_port = desired_port
        else:
            print(f"Port {desired_port} is already in use, searching for an available port...", file=sys.stderr)
            # Try to find a free port starting from the desired port
            actual_port = find_free_port(desired_port)
            
            if actual_port is None:
                # If sequential search fails, try to get any free port from OS
                print("Could not find free port sequentially, requesting any available port from OS...", file=sys.stderr)
                actual_port = get_free_port()
                
            print(f"Using port {actual_port} instead", file=sys.stderr)
    
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
    gui_app = PeiDockerWebGUI()
    
    @ui.page('/')
    async def index() -> None:
        gui_app.setup_ui()
        
        # Setup initial state if project directory or page specified
        if project_path or args.jump_to_page:
            ui.timer(0.5, lambda: asyncio.create_task(
                setup_initial_state(gui_app, project_path, args.jump_to_page)
            ), once=True)
    
    # Run the application
    print(f"Starting PeiDocker Web GUI on port {actual_port}...")
    print(f"Open http://localhost:{actual_port} in your browser")
    
    ui.run(
        host='0.0.0.0',
        port=actual_port,
        title='PeiDocker Web GUI',
        favicon='🐳',
        dark=None,  # Auto-detect from system
        reload=False
    )


def main() -> None:
    """Main entry point for pei-docker-gui CLI.

    Configures argument parser with all available commands and options,
    parses command line arguments, and dispatches to appropriate handlers.

    Notes
    -----
    Command structure:
    - Main command: pei-docker-gui  
    - Subcommands: start
    - If no subcommand provided, shows help and exits with code 1

    The argument parser includes comprehensive help text and validation
    for all options. Port conflicts and invalid arguments result in
    error messages and program termination.

    Raises
    ------
    SystemExit
        Exits with code 1 if no command specified or if any validation fails.
    """
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
        default=None,
        help='Port to run the web application (default: auto-select free port)'
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