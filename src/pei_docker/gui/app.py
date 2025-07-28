"""
PeiDocker Terminal GUI Application.

This module provides the main entry point for the PeiDocker GUI application, which offers
a terminal-based user interface for configuring Docker containers through a wizard-style
interface.

Command Line Usage
------------------
The application is launched using the `pei-docker-gui` command with subcommands:

Start GUI (normal mode):
    pei-docker-gui start [OPTIONS]
    
    Options:
        --project-dir PATH    Project directory to use (skips directory selection)
        --here               Use current directory as the project directory

Development mode:
    pei-docker-gui dev [OPTIONS]
    
    Options:
        --project-dir PATH    Project directory to use (required for dev mode)
        --here               Use current directory as the project directory
        --screen TEXT        Screen to start with (e.g., 'sc-0', 'sc-1', etc.)

Examples:
    pei-docker-gui start
    pei-docker-gui start --project-dir ./my-project
    pei-docker-gui start --here
    pei-docker-gui dev --project-dir ./test --screen sc-1

Architecture
------------
The application uses the Textual framework for terminal UI and follows a screen-based 
navigation pattern:

- SC-0: Application Startup Screen (system validation)
- SC-1: Project Directory Selection Screen  
- SC-2: Simple Wizard Controller (orchestrates configuration steps)
- SC-3-SC-13: Individual configuration wizard screens

Notes
-----
The GUI provides only a simple mode with guided wizard-style configuration. All 
configuration changes are kept in memory until explicitly saved as user_config.yml.
"""

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
    """
    Main PeiDocker GUI application using Textual framework.
    
    This class extends Textual's App class to provide a terminal-based GUI for
    configuring Docker containers. It manages screen navigation, project configuration
    state, and system component availability checks.
    
    Attributes
    ----------
    CSS_PATH : None
        No external CSS file used, styling is embedded.
    TITLE : str
        Application title displayed in the header.
    SUB_TITLE : str  
        Application subtitle for branding.
    DEFAULT_CSS : str
        Embedded CSS styling for the application layout.
    project_config : ProjectConfig
        Central configuration object maintaining project state.
    docker_available : bool
        Whether Docker is available on the system.
    docker_version : str
        Version string of available Docker installation.
        
    Notes
    -----
    The application follows a screen-based navigation pattern where each major
    step in the configuration process has its own dedicated screen class.
    """
    
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
    
    def __init__(self, project_dir: Optional[str] = None, dev_screen: Optional[str] = None):
        """
        Initialize the PeiDocker GUI application.
        
        Parameters
        ----------
        project_dir : str, optional
            Project directory path to use. If provided, skips directory selection
            screen and pre-fills the project configuration. Default is None.
        dev_screen : str, optional
            Screen ID to start with for development mode (e.g., 'sc-0', 'sc-1', 'sc-3').
            Default is None for normal startup flow.
            
        Notes
        -----
        The constructor performs the following initialization:
        - Creates a new ProjectConfig instance
        - Sets project directory and name if provided via CLI
        - Checks Docker availability for system validation
        - Stores dev_screen for development mode navigation
        """
        super().__init__()
        self.project_config = ProjectConfig()
        self.dev_screen = dev_screen
        
        # Set project directory if provided
        if project_dir:
            self.project_config.project_dir = str(Path(project_dir).resolve())
            self.project_config.project_name = Path(project_dir).name
        
        # Check Docker availability on startup
        self.docker_available, self.docker_version = check_docker_available()
    
    def on_mount(self) -> None:
        """
        Initialize the application when mounted.
        
        This method is called by Textual when the application is first mounted.
        It sets up the initial screen based on whether dev_screen is specified.
        In normal mode, starts with startup screen. In dev mode, jumps directly
        to the specified screen for development/testing purposes.
        
        Notes
        -----
        The startup screen performs system validation and displays application
        branding before proceeding to the main workflow. Dev mode bypasses this
        for rapid development iteration.
        """
        if self.dev_screen:
            # Development mode - jump directly to specified screen
            self._jump_to_dev_screen(self.dev_screen)
        else:
            # Normal mode - start with startup screen
            self.install_screen(StartupScreen(self.project_config, self.docker_available, self.docker_version), "startup")
            self.push_screen("startup")
    
    def _jump_to_dev_screen(self, screen_id: str) -> None:
        """
        Jump directly to a specific screen for development mode.
        
        This method bypasses the normal application flow and jumps directly
        to the specified screen. It's used for development and testing to
        avoid manual navigation through multiple screens.
        
        Parameters
        ----------
        screen_id : str
            Screen identifier (e.g., 'sc-0', 'sc-1', 'sc-3', 'sc-4')
            
        Raises
        ------
        ValueError
            If the screen_id is not supported or invalid
            
        Notes
        -----
        Supported screens:
        - sc-0: StartupScreen (system validation)
        - sc-1: ProjectDirectorySelectionScreen
        - sc-3: First wizard step (Project Information)
        - sc-4: Second wizard step (SSH Configuration)
        """
        # Validate project directory is set for screens that require it
        if screen_id in ['sc-1', 'sc-3', 'sc-4'] and not self.project_config.project_dir:
            print(f"Error: dev screen '{screen_id}' requires project directory to be set")
            sys.exit(1)
        
        screen_mapping = {
            'sc-0': self._setup_startup_screen,
            'sc-1': self._setup_project_selection_screen,
            'sc-3': self._setup_wizard_first_step,
            'sc-4': self._setup_wizard_second_step,
        }
        
        if screen_id not in screen_mapping:
            print(f"Error: Unsupported dev screen '{screen_id}'. Supported: {list(screen_mapping.keys())}")
            sys.exit(1)
        
        # Call the appropriate setup method
        screen_mapping[screen_id]()
    
    def _setup_startup_screen(self) -> None:
        """Setup and display the startup screen (sc-0)."""
        startup_screen = StartupScreen(self.project_config, self.docker_available, self.docker_version)
        self.install_screen(startup_screen, "startup")
        self.push_screen("startup")
    
    def _setup_project_selection_screen(self) -> None:
        """Setup and display the project directory selection screen (sc-1)."""
        from .screens.project_setup import ProjectDirectorySelectionScreen
        project_setup_screen = ProjectDirectorySelectionScreen(
            self.project_config, 
            has_cli_project_dir=bool(self.project_config.project_dir)
        )
        self.install_screen(project_setup_screen, "project_setup")
        self.push_screen("project_setup")
    
    def _setup_wizard_first_step(self) -> None:
        """Setup and display the first wizard step (sc-3)."""
        from .screens.simple.wizard import SimpleWizardScreen
        wizard_screen = SimpleWizardScreen(self.project_config)
        # Set to first step (step 0 = sc-3)
        wizard_screen.current_step = 0
        self.install_screen(wizard_screen, "simple_wizard")
        self.push_screen("simple_wizard")
    
    def _setup_wizard_second_step(self) -> None:
        """Setup and display the second wizard step (sc-4)."""
        from .screens.simple.wizard import SimpleWizardScreen
        wizard_screen = SimpleWizardScreen(self.project_config)
        # Set to second step (step 1 = sc-4)
        wizard_screen.current_step = 1
        self.install_screen(wizard_screen, "simple_wizard")
        self.push_screen("simple_wizard")
    
    def action_goto_project_setup(self) -> None:
        """
        Navigate to the project directory selection screen (SC-1).
        
        This action method creates and displays the project setup screen where
        users can select or configure their project directory and name. The
        screen behavior adapts based on whether a project directory was
        provided via CLI arguments.
        
        Notes
        -----
        This method is typically called from the startup screen after system
        validation is complete. It handles both normal mode (user selects
        directory) and CLI override mode (directory pre-filled).
        """
        from .screens.project_setup import ProjectDirectorySelectionScreen
        project_setup_screen = ProjectDirectorySelectionScreen(
            self.project_config, 
            has_cli_project_dir=bool(self.project_config.project_dir)
        )
        self.install_screen(project_setup_screen, "project_setup")
        self.push_screen("project_setup")
    
    def action_goto_simple_wizard(self) -> None:
        """
        Navigate directly to the simple wizard controller screen (SC-2).
        
        This action method creates and displays the wizard controller that
        orchestrates the 11-step configuration process. It is called when
        the project directory setup is complete and the user is ready to
        configure their Docker container.
        
        Notes
        -----
        The simple wizard controller manages memory-based configuration
        state and provides navigation between individual configuration
        screens (SC-3 through SC-13).
        """
        from .screens.simple.wizard import SimpleWizardScreen
        wizard_screen = SimpleWizardScreen(self.project_config)
        self.install_screen(wizard_screen, "simple_wizard")
        self.push_screen("simple_wizard")
    
    def action_quit_app(self) -> None:
        """
        Quit the application gracefully.
        
        This action method terminates the application and returns control
        to the terminal. It can be called from any screen via keyboard
        shortcuts or quit buttons.
        """
        self.exit()


def _validate_and_create_project_dir(project_dir: str) -> str:
    """
    Validate and create a project directory if needed.
    
    This function ensures that the specified project directory exists and is
    accessible. If the directory doesn't exist, it attempts to create it
    including any necessary parent directories.
    
    Parameters
    ----------
    project_dir : str
        Path to the project directory to validate or create.
        
    Returns
    -------
    str
        Absolute path to the validated/created directory.
        
    Raises
    ------
    SystemExit
        If the directory cannot be created due to permissions or other
        filesystem errors. Error message is displayed to stderr before exit.
        
    Notes
    -----
    This function uses `mkdir(parents=True, exist_ok=True)` to create the
    directory hierarchy safely, avoiding race conditions if the directory
    is created by another process between the existence check and creation.
    """
    project_path = Path(project_dir)
    if not project_path.exists():
        try:
            project_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            click.echo(f"Error: Cannot create project directory '{project_dir}': {e}", err=True)
            sys.exit(1)
    return str(project_path.resolve())


def _run_app(project_dir: Optional[str] = None, dev_screen: Optional[str] = None) -> None:
    """
    Run the PeiDocker GUI application with specified configuration.
    
    This function creates and starts the main GUI application, handling both
    normal and development modes. It manages graceful error handling and
    user cancellation.
    
    Parameters
    ----------
    project_dir : str, optional
        Project directory path to use. If provided, the application will
        skip directory selection and pre-configure the project. Default is None.
    dev_screen : str, optional
        Screen identifier to start with in development mode (e.g., 'sc-1').
        Requires project_dir to be specified. Default is None.
        
    Raises
    ------
    SystemExit
        If invalid parameter combinations are used (e.g., dev_screen without
        project_dir) or if unhandled exceptions occur during application startup.
        
    Notes
    -----
    The function handles KeyboardInterrupt gracefully and displays appropriate
    error messages for any exceptions that occur during application execution.
    Development mode supports jumping directly to sc-0, sc-1, and sc-3 screens.
    """
    app = PeiDockerApp(project_dir=project_dir, dev_screen=dev_screen)
    
    # Handle development mode screen selection
    if dev_screen:
        if not project_dir:
            click.echo("Error: --screen option requires --project-dir to be specified", err=True)
            sys.exit(1)
        
        # Validate screen ID early
        supported_screens = ['sc-0', 'sc-1', 'sc-3', 'sc-4']
        if dev_screen not in supported_screens:
            click.echo(f"Error: Unsupported dev screen '{dev_screen}'. Supported: {supported_screens}", err=True)
            sys.exit(1)
        
        # Development mode - screen-specific startup is now implemented
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
    """
    PeiDocker Terminal GUI - Docker Container Configuration Made Easy.
    
    This is the main CLI entry point for the PeiDocker GUI application.
    Use the subcommands 'start' or 'dev' to launch the terminal-based
    interface for configuring Docker containers.
    
    The GUI provides a wizard-style interface that guides users through
    all aspects of Docker container configuration without requiring
    deep knowledge of Dockerfiles or docker-compose syntax.
    """
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
    """
    Start the GUI application in normal mode.
    
    This command launches the PeiDocker GUI with the standard user workflow.
    Without options, the user will be prompted to select a project directory.
    With --project-dir or --here, the directory selection step is skipped.
    
    Parameters
    ----------
    project_dir : Path, optional
        Specific project directory to use. The directory will be created
        if it doesn't exist. Mutually exclusive with --here.
    here : bool
        If True, use the current working directory as the project directory.
        Mutually exclusive with --project-dir.
        
    Raises
    ------
    SystemExit
        If both --project-dir and --here are specified, or if directory
        creation fails.
        
    Examples
    --------
    Start with directory selection prompt:
        pei-docker-gui start
        
    Start with specific project directory:
        pei-docker-gui start --project-dir /path/to/project
        
    Start using current directory:
        pei-docker-gui start --here
    """
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
    """
    Start the GUI in development mode.
    
    Development mode is intended for testing and debugging specific screens
    without going through the complete user workflow. A project directory
    must be specified when using development mode.
    
    Parameters
    ----------
    project_dir : Path, optional
        Project directory to use for development. The directory will be
        created if it doesn't exist. Mutually exclusive with --here.
    here : bool
        If True, use the current working directory as the project directory.
        Mutually exclusive with --project-dir.
    screen : str, optional
        Screen identifier to start with (e.g., 'sc-1' for project setup).
        Requires either --project-dir or --here to be specified.
        
    Raises
    ------
    SystemExit
        If invalid option combinations are used (both --here and --project-dir,
        or --screen without a project directory), or if directory creation fails.
        
    Examples
    --------
    Start in development mode with directory selection:
        pei-docker-gui dev --project-dir /path/to/test-project
        
    Start at specific screen for testing:
        pei-docker-gui dev --here --screen sc-1
        
    Notes
    -----
    Screen-specific startup is implemented for sc-0, sc-1, and sc-3. The
    application jumps directly to the specified screen for rapid development.
    """
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
    """
    Main entry point for the GUI application.
    
    This function serves as the primary entry point when the application
    is installed as a console script. It delegates to the Click CLI
    framework to handle command parsing and execution.
    
    Notes
    -----
    This function is typically called automatically when the user runs
    the `pei-docker-gui` command from the terminal. It should not be
    called directly in most cases.
    """
    cli()


if __name__ == "__main__":
    main()