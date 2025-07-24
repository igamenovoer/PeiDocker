"""
Startup Screen (SC-0) for PeiDocker GUI Application.

This module implements the application startup screen that serves as the entry point
for the PeiDocker GUI. The screen displays application branding, performs system
component validation, and provides project directory analysis when CLI arguments
are provided.

The startup screen follows the philosophy of validating the environment before
proceeding to the main workflow, ensuring users are aware of any system limitations
or configuration issues early in the process.

Key Features
------------
- ASCII art branding and application information display
- Docker availability detection and version reporting  
- Python version detection and display
- PeiDocker version information
- Project directory analysis for CLI override scenarios
- System status reporting with visual indicators
- Navigation controls to proceed or exit

Classes
-------
StartupScreen : Main startup screen implementation (SC-0)

Notes
-----
This is the first screen (SC-0) in the navigation flow: SC-0 → SC-1 → SC-2.
It performs initial system validation and provides a professional entry point
to the application with clear system status information.
"""

import sys
import yaml
from pathlib import Path
from typing import Any, Optional, cast, TYPE_CHECKING, Dict, Union, List

if TYPE_CHECKING:
    from ..app import PeiDockerApp

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Label, Static

from ..models.config import ProjectConfig


class StartupScreen(Screen[None]):
    """
    Application startup screen with system validation and branding (SC-0).
    
    This screen serves as the entry point for the PeiDocker GUI application,
    providing professional branding, system component validation, and project
    directory analysis when CLI arguments are provided. It ensures users are
    aware of system requirements and configuration status before proceeding.
    
    The screen displays ASCII art branding, performs Docker availability checks,
    shows Python and PeiDocker version information, and provides clear navigation
    options to continue or exit the application.
    
    Attributes
    ----------
    project_config : ProjectConfig
        Central configuration object containing project settings and state.
    docker_available : bool
        Whether Docker is available and accessible on the system.
    docker_version : str, optional
        Version string of the available Docker installation, if detected.
    project_dir_exists : bool
        Whether the specified project directory already exists on disk.
    project_type : str
        Type of project directory detected: "none", "existing", "new", or "error".
    config_load_error : bool
        Whether there was an error loading existing user_config.yml file.
        
    Notes
    -----
    This is the first screen (SC-0) in the navigation flow: SC-0 → SC-1 → SC-2.
    It performs essential system validation and provides a professional entry
    point with clear status indicators for all system components.
    
    The screen adapts its behavior based on CLI arguments:
    - Without --project-dir: Shows standard system status
    - With --project-dir: Adds project directory analysis and status
    """
    
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
    
    def __init__(self, project_config: ProjectConfig, docker_available: bool, docker_version: Optional[str]) -> None:
        """
        Initialize the startup screen with system and project information.
        
        Parameters
        ----------
        project_config : ProjectConfig
            Project configuration object containing settings and directory information.
        docker_available : bool
            Whether Docker is available and accessible on the system.
        docker_version : str, optional
            Version string of the Docker installation, if available.
            
        Notes
        -----
        The constructor performs the following initialization:
        1. Sets up project configuration and Docker availability status
        2. Initializes project directory analysis state variables
        3. Automatically analyzes project directory if provided via CLI
        4. Prepares system status widget reference for later updates
        
        Project directory analysis determines whether the specified directory:
        - Does not exist (will be created)
        - Exists but is empty (new project)
        - Contains valid user_config.yml (existing project)
        - Contains invalid user_config.yml (error state)
        """
        super().__init__()
        self.project_config: ProjectConfig = project_config
        self.docker_available: bool = docker_available
        self.docker_version: Optional[str] = docker_version
        self._system_status_widget: Optional[Static] = None
        
        # Project directory analysis results
        self.project_dir_exists: bool = False
        self.project_type: str = "none"  # "none", "existing", "new", "error"
        self.config_load_error: bool = False
        
        # Analyze project directory if provided
        if self.project_config.project_dir:
            self._analyze_project_directory()
    
    def compose(self) -> ComposeResult:
        """
        Compose the startup screen layout with branding and system status.
        
        Creates the visual layout of the startup screen including ASCII art logo,
        application title and subtitle, system status display area, and navigation
        buttons. The layout is centered both horizontally and vertically.
        
        Returns
        -------
        ComposeResult
            Generator yielding Textual widgets in the correct layout hierarchy.
            
        Notes
        -----
        The screen layout consists of:
        1. ASCII art logo with accent color styling
        2. Application title and subtitle with branded colors
        3. System status widget showing Docker, Python, and project information
        4. Action buttons for Continue and Quit operations
        5. Help text showing keyboard shortcuts
        
        The system status widget is initially populated with a "checking" message
        and updated with actual system information in the on_mount method.
        """
        with Center():
            with Middle():
                with Vertical():
                    yield Static(self._get_logo(), classes="logo")
                    yield Label("PeiDocker Configuration GUI", classes="title")
                    yield Label("Docker Container Configuration Made Easy", classes="subtitle")
                    
                    # Create system status widget with initial "checking" message
                    self._system_status_widget = Static("Checking system components...", classes="system-status")
                    yield self._system_status_widget
                    
                    with Horizontal(classes="actions"):
                        yield Button("Continue", id="continue", variant="primary")
                        yield Button("Quit", id="quit", variant="default")
                    
                    yield Label("Press 'q' to quit, Enter to continue", classes="help-text")
    
    def on_mount(self) -> None:
        """
        Initialize the screen after mounting with real-time system information.
        
        This method is called by Textual after the screen is fully mounted and
        all widgets are available. It updates the system status widget with
        actual system information replacing the initial "checking" message.
        
        Notes
        -----
        The method performs the following updates:
        1. Retrieves current system status information
        2. Updates the system status widget with real data
        3. Ensures all status indicators reflect actual system state
        
        This approach provides immediate visual feedback while system checks
        are performed, creating a responsive user experience.
        """
        # Update system status widget with actual system information
        if self._system_status_widget:
            self._system_status_widget.update(self._get_system_status())
    
    
    def _get_logo(self) -> str:
        """
        Get ASCII art logo for PeiDocker branding.
        
        Returns
        -------
        str
            Multi-line ASCII art string representing the PeiDocker logo.
            
        Notes
        -----
        The logo uses Unicode box-drawing characters to create a professional
        branded appearance. It is displayed with accent color styling in the
        terminal interface for visual impact.
        """
        return """
██████╗ ███████╗██╗██████╗  ██████╗  ██████╗██╗  ██╗███████╗██████╗ 
██╔══██╗██╔════╝██║██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██████╔╝█████╗  ██║██║  ██║██║   ██║██║     █████╔╝ █████╗  ██████╔╝
██╔═══╝ ██╔══╝  ██║██║  ██║██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║     ███████╗██║██████╔╝╚██████╔╝╚██████╗██║  ██╗███████╗██║  ██║
╚═╝     ╚══════╝╚═╝╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
        """
    
    def _get_system_status(self) -> str:
        """
        Generate comprehensive system status information for display.
        
        Collects and formats system information including Docker availability,
        Python version, PeiDocker version, and project directory status when
        applicable. The information is formatted as a multi-line string for
        display in the system status widget.
        
        Returns
        -------
        str
            Multi-line string containing formatted system status information.
            Each line represents a different system component or status item.
            
        Notes
        -----
        Status information includes:
        1. Docker availability and version (if available)
        2. Python version from sys.version
        3. PeiDocker version (or "Development version" if not installed)
        4. Project directory status (when --project-dir provided)
        
        Docker version parsing extracts the version number from the standard
        "Docker version X.X.X" format returned by docker --version.
        """
        status_lines: List[str] = []
        
        # Docker status
        if self.docker_available:
            docker_info: str = "Docker: Available"
            if self.docker_version:
                # Extract version number from "Docker version X.X.X" format
                version_parts: List[str] = self.docker_version.split()
                if len(version_parts) >= 3:
                    docker_info += f" (version {version_parts[2]})"
            status_lines.append(docker_info)
        else:
            status_lines.append("Docker: Not found")
        
        # Python status
        status_lines.append(f"Python: {sys.version.split()[0]}")
        
        # PeiDocker status
        try:
            from pei_docker._version import __version__
            status_lines.append(f"PeiDocker: {__version__}")
        except ImportError:
            status_lines.append("PeiDocker: Development version")
        
        # Project directory status (when --project-dir provided)
        if self.project_config.project_dir:
            project_status: Optional[str] = self._get_project_directory_status()
            if project_status:
                status_lines.append(project_status)
        
        return "\n".join(status_lines)
    
    def _analyze_project_directory(self) -> None:
        """
        Analyze the specified project directory to determine its current state.
        
        Examines the project directory to classify it as new, existing, or error
        state based on directory existence and user_config.yml file validity.
        This analysis helps determine the appropriate navigation flow and user
        messaging.
        
        Notes
        -----
        Analysis classification:
        - "new": Directory doesn't exist or exists but has no user_config.yml
        - "existing": Directory exists with valid user_config.yml file
        - "error": Directory exists with invalid/corrupted user_config.yml
        - "none": No project directory specified (default state)
        
        The method updates the following instance attributes:
        - project_dir_exists: Whether the directory exists on disk
        - project_type: Classification of the directory state
        - config_load_error: Whether configuration loading failed
        
        YAML loading uses safe_load for security and logs warnings for any
        configuration file parsing errors encountered.
        """
        if not self.project_config.project_dir:
            return
            
        project_path: Path = Path(self.project_config.project_dir)
        
        # Check if directory exists
        if not project_path.exists():
            self.project_dir_exists = False
            self.project_type = "new"
            return
            
        self.project_dir_exists = True
        
        # Check for user_config.yml
        config_file: Path = project_path / "user_config.yml"
        
        if not config_file.exists():
            # No config file = new project
            self.project_type = "new"
            return
            
        # Config file exists, try to load it
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            # Successfully loaded = existing project
            self.project_type = "existing"
        except Exception as e:
            # Failed to load = config error
            self.project_type = "error"
            self.config_load_error = True
            self.log.warning(f"Failed to load user_config.yml: {e}")
    
    def _get_project_directory_status(self) -> Optional[str]:
        """
        Generate formatted project directory status message for display.
        
        Creates a human-readable status message based on the project directory
        analysis results. The message provides clear information about the
        directory state and what actions will be taken.
        
        Returns
        -------
        str, optional
            Formatted status message describing the project directory state,
            or None if no project directory is configured.
            
        Notes
        -----
        Status message formats:
        - Existing project: "Project Directory: /path (existing)"
        - New project in existing dir: "Project Directory: /path (new)"
        - New project, dir to be created: "Project Directory: /path (will be created)"
        - Config error: "Project Directory: /path (config load failed - will recreate)"
        
        The messages help users understand what will happen when they proceed
        with the configuration process.
        """
        if not self.project_config.project_dir:
            return None
            
        project_path: str = self.project_config.project_dir
        
        if self.project_type == "existing":
            return f"Project Directory: {project_path} (existing)"
        elif self.project_type == "new":
            if self.project_dir_exists:
                return f"Project Directory: {project_path} (new)"
            else:
                return f"Project Directory: {project_path} (will be created)"
        elif self.project_type == "error":
            return f"Project Directory: {project_path} (config load\n    failed - will recreate)"
        
        return f"Project Directory: {project_path}"
    
    @on(Button.Pressed, "#continue")
    def on_continue_pressed(self) -> None:
        """
        Handle continue button press event.
        
        Responds to the Continue button being pressed by delegating to the
        action_continue method. This separation allows the same continue logic
        to be triggered by both button presses and keyboard shortcuts.
        """
        self.action_continue()
    
    @on(Button.Pressed, "#quit")
    def on_quit_pressed(self) -> None:
        """
        Handle quit button press event.
        
        Responds to the Quit button being pressed by delegating to the
        action_quit method. This separation allows the same quit logic
        to be triggered by both button presses and keyboard shortcuts.
        """
        self.action_quit()
    
    def action_continue(self) -> None:
        """
        Navigate to the next screen based on project directory configuration.
        
        Determines the appropriate navigation path based on whether a project
        directory was provided via CLI arguments and the current state of that
        directory. Handles project creation, configuration loading, and error
        recovery as needed.
        
        Notes
        -----
        Navigation logic:
        - No project directory: Go to project setup screen (SC-1)
        - Existing project: Load configuration and go to wizard (SC-2)
        - New project: Create project structure and go to wizard (SC-2)
        - Config error: Recreate project and go to wizard (SC-2)
        
        The method provides user feedback through notifications for any errors
        encountered during project creation or configuration loading. Success
        cases navigate directly to the appropriate next screen.
        """
        # Check if project directory is already set via --project-dir
        if self.project_config.project_dir:
            # Handle different project states
            if self.project_type == "existing":
                # Load existing configuration and go to wizard
                if self._load_existing_config():
                    cast('PeiDockerApp', self.app).action_goto_simple_wizard()
                else:
                    self.notify("Failed to load existing configuration", severity="error")
            elif self.project_type == "new":
                # Create new project structure and go to wizard
                if self._create_project():
                    cast('PeiDockerApp', self.app).action_goto_simple_wizard()
                else:
                    self.notify("Failed to create project structure", severity="error")
            elif self.project_type == "error":
                # Config load failed, treat as new project and recreate
                if self._create_project():
                    self.notify("Configuration file was corrupted and has been recreated", severity="warning")
                    cast('PeiDockerApp', self.app).action_goto_simple_wizard()
                else:
                    self.notify("Failed to recreate project structure", severity="error")
            else:
                # Fallback: create project
                if self._create_project():
                    cast('PeiDockerApp', self.app).action_goto_simple_wizard()
                else:
                    self.notify("Failed to create project structure", severity="error")
        else:
            # No project directory provided, go to project setup screen (SC-1)
            cast('PeiDockerApp', self.app).action_goto_project_setup()
    
    def _on_project_dir_selected(self, result: Optional[str]) -> None:
        """
        Handle the result of project directory selection.
        
        Processes the result from a directory selection operation, updating
        the project configuration and creating the project structure if a
        directory was selected.
        
        Parameters
        ----------
        result : str, optional
            Selected directory path, or None if the user cancelled the selection.
            
        Notes
        -----
        Selection handling:
        - If result is provided: Updates project config, creates project, navigates to wizard
        - If result is None: User cancelled, remains on startup screen
        
        The method automatically derives the project name from the directory name
        and provides error notifications if project creation fails.
        """
        if result:
            self.project_config.project_dir = result
            self.project_config.project_name = Path(result).name
            if self._create_project():
                cast('PeiDockerApp', self.app).action_goto_simple_wizard()
            else:
                self.notify("Failed to create project structure", severity="error")
        # If result is None, user cancelled, so stay on startup screen
    
    def _load_existing_config(self) -> bool:
        """
        Load existing user_config.yml file into the project configuration.
        
        Attempts to read and parse an existing user_config.yml file from the
        project directory, validating that it can be loaded successfully.
        Currently performs validation only; full configuration mapping is
        a TODO item for future implementation.
        
        Returns
        -------
        bool
            True if the configuration file was loaded successfully,
            False if loading failed for any reason.
            
        Notes
        -----
        Current implementation:
        1. Validates that project directory and config file exist
        2. Attempts to parse the YAML file using safe_load
        3. Sets project name from directory name
        4. Logs errors for any parsing failures
        
        TODO: Map the loaded configuration data to wizard states for proper
        configuration restoration in the GUI interface.
        """
        try:
            if not self.project_config.project_dir:
                return False
                
            config_file: Path = Path(self.project_config.project_dir) / "user_config.yml"
            
            if not config_file.exists():
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data: Dict[str, Any] = yaml.safe_load(f)
            
            # TODO: Map the loaded config data to wizard states
            # This would involve updating the project_config with values from the YAML
            # For now, just validate that it loads successfully
            
            # Set project name from directory name
            self.project_config.project_name = Path(self.project_config.project_dir).name
            
            return True
            
        except Exception as e:
            self.log.error(f"Failed to load existing configuration: {e}")
            return False
    
    def _create_project(self) -> bool:
        """
        Create the complete project directory structure and template files.
        
        Sets up a new PeiDocker project by creating the directory structure
        and copying all necessary template files from the package resources.
        Uses importlib.resources for proper pip install compatibility with
        fallback to development path-based approach.
        
        Returns
        -------
        bool
            True if project creation was successful, False if any errors occurred.
            
        Notes
        -----
        Project creation process:
        1. Ensures project directory exists
        2. Copies project_files directory contents from package resources
        3. Copies configuration template (config-template-full.yml)
        4. Copies Docker Compose template (base-image-gen.yml)
        5. Uses temporary directory for safe resource extraction
        
        The method handles both installed package scenarios (using importlib.resources)
        and development scenarios (using file system paths) automatically.
        All errors are logged and result in a False return value.
        """
        try:
            import os
            import shutil
            import tempfile
            from pei_docker.config_processor import Defaults
            from ..utils.file_utils import ensure_dir_exists
            
            # Use importlib.resources for Python 3.9+ or importlib_resources for older versions
            try:
                from importlib import resources as pkg_resources
            except ImportError:
                try:
                    import importlib_resources as pkg_resources  # type: ignore
                except ImportError:
                    # Fallback to the old path-based approach with corrected path calculation
                    return self._create_project_fallback()
            
            project_dir: str = self.project_config.project_dir
            
            # Ensure project directory exists
            if not ensure_dir_exists(project_dir):
                return False
            
            # Copy all the files and folders from project_files to the output dir
            # Using importlib.resources for proper pip install compatibility
            try:
                project_files_ref: Any = pkg_resources.files('pei_docker.project_files')
                
                # Copy project_files directory contents
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Extract project_files to temporary directory first
                    temp_project_files: str = os.path.join(temp_dir, 'project_files')
                    os.makedirs(temp_project_files, exist_ok=True)
                    
                    # Recursively copy all files from the package resource
                    self._copy_resource_tree(project_files_ref, temp_project_files)
                    
                    # Now copy from temp to actual project directory
                    for item in os.listdir(temp_project_files):
                        s = os.path.join(temp_project_files, item)
                        d = os.path.join(project_dir, item)
                        if os.path.isdir(s):
                            shutil.copytree(s, d, dirs_exist_ok=True)
                        else:
                            shutil.copy2(s, d)
                
                # Copy config and compose template files
                templates_ref: Any = pkg_resources.files('pei_docker.templates')
                
                # Copy config template
                config_template_ref: Any = templates_ref / 'config-template-full.yml'
                if config_template_ref.is_file():
                    dst_config_template: str = os.path.join(project_dir, Defaults.OutputConfigName)
                    with open(dst_config_template, 'w', encoding='utf-8') as f:
                        f.write(config_template_ref.read_text(encoding='utf-8'))
                
                # Copy compose template
                compose_template_ref: Any = templates_ref / 'base-image-gen.yml'
                if compose_template_ref.is_file():
                    dst_compose_template: str = os.path.join(project_dir, Defaults.OutputComposeTemplateName)
                    with open(dst_compose_template, 'w', encoding='utf-8') as f:
                        f.write(compose_template_ref.read_text(encoding='utf-8'))
                
                return True
                
            except Exception as resource_error:
                self.log.error(f"Failed to access package resources: {resource_error}")
                # Fallback to old path-based approach with corrected path
                return self._create_project_fallback()
            
        except Exception as e:
            self.log.error(f"Failed to create project: {e}")
            return False
    
    def _copy_resource_tree(self, resource_ref: Any, dest_dir: str) -> None:
        """
        Recursively copy a package resource tree to a destination directory.
        
        Traverses a package resource hierarchy and copies all files and
        subdirectories to the specified destination, preserving the directory
        structure and file contents.
        
        Parameters
        ----------
        resource_ref : Any
            Package resource reference from importlib.resources.
        dest_dir : str
            Destination directory path where resources should be copied.
            
        Notes
        -----
        The method handles both files and directories recursively:
        - Files are copied using binary mode to preserve all file types
        - Directories are created and then recursively processed
        - Uses os.makedirs with exist_ok=True for safe directory creation
        """
        import os
        
        os.makedirs(dest_dir, exist_ok=True)
        
        for item in resource_ref.iterdir():
            dest_path: str = os.path.join(dest_dir, item.name)
            
            if item.is_file():
                with open(dest_path, 'wb') as f:
                    f.write(item.read_bytes())
            elif item.is_dir():
                self._copy_resource_tree(item, dest_path)
    
    def _create_project_fallback(self) -> bool:
        """
        Fallback project creation method for development environments.
        
        Alternative project creation approach that uses file system paths
        instead of package resources. This method is used when importlib.resources
        is not available or fails, typically in development environments.
        
        Returns
        -------
        bool
            True if project creation was successful using the fallback method,
            False if any errors occurred.
            
        Notes
        -----
        Fallback approach:
        1. Calculates paths relative to the current file location
        2. Navigates to the pei_docker package directory (2 levels up)
        3. Copies files from project_files and templates directories
        4. Uses corrected path calculation (2 levels instead of 3)
        
        This method provides compatibility for development scenarios where
        the package may not be installed through pip.
        """
        try:
            import os
            import shutil
            from pei_docker.config_processor import Defaults
            
            project_dir: str = self.project_config.project_dir
            
            # Corrected path calculation: only 2 levels up to reach pei_docker package root
            this_dir: str = os.path.dirname(os.path.realpath(__file__))
            # Navigate up to the pei_docker package directory (corrected from 3 to 2 levels)
            pei_docker_dir: str = os.path.dirname(os.path.dirname(this_dir))
            project_template_dir: str = os.path.join(pei_docker_dir, 'project_files')
            
            if not os.path.exists(project_template_dir):
                self.log.error(f"Project template directory not found: {project_template_dir}")
                return False
            
            for item in os.listdir(project_template_dir):
                s: str = os.path.join(project_template_dir, item)
                d: str = os.path.join(project_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            
            # Copy config and compose template files
            templates_dir: str = os.path.join(pei_docker_dir, 'templates')
            
            src_config_template: str = os.path.join(templates_dir, 'config-template-full.yml')
            dst_config_template: str = os.path.join(project_dir, Defaults.OutputConfigName)
            if os.path.exists(src_config_template):
                shutil.copy2(src_config_template, dst_config_template)
            
            src_compose_template: str = os.path.join(templates_dir, 'base-image-gen.yml')
            dst_compose_template: str = os.path.join(project_dir, Defaults.OutputComposeTemplateName)
            if os.path.exists(src_compose_template):
                shutil.copy2(src_compose_template, dst_compose_template)
            
            return True
            
        except Exception as e:
            self.log.error(f"Fallback project creation failed: {e}")
            return False
    
    def action_quit(self) -> None:
        """
        Terminate the application gracefully.
        
        Exits the PeiDocker GUI application and returns control to the terminal.
        This method can be called from button presses, keyboard shortcuts, or
        other quit events throughout the application.
        """
        cast('PeiDockerApp', self.app).action_quit_app()