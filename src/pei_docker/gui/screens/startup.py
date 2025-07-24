"""Startup screen for the PeiDocker GUI."""

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
    
    def __init__(self, project_config: ProjectConfig, docker_available: bool, docker_version: Optional[str]) -> None:
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
        """Compose the startup screen."""
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
        """Called when the screen is mounted."""
        # Update system status widget with actual system information
        if self._system_status_widget:
            self._system_status_widget.update(self._get_system_status())
    
    
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
        """Analyze the project directory to determine its state."""
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
        """Get project directory status line for display."""
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
        """Continue button pressed."""
        self.action_continue()
    
    @on(Button.Pressed, "#quit")
    def on_quit_pressed(self) -> None:
        """Quit button pressed."""
        self.action_quit()
    
    def action_continue(self) -> None:
        """Continue to next screen."""
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
        """Handle project directory selection result."""
        if result:
            self.project_config.project_dir = result
            self.project_config.project_name = Path(result).name
            if self._create_project():
                cast('PeiDockerApp', self.app).action_goto_simple_wizard()
            else:
                self.notify("Failed to create project structure", severity="error")
        # If result is None, user cancelled, so stay on startup screen
    
    def _load_existing_config(self) -> bool:
        """Load existing user_config.yml into the project config."""
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
        """Create the project directory structure."""
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
        """Recursively copy resource tree to destination directory."""
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
        """Fallback method using corrected path calculation for development."""
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
        """Quit the application."""
        cast('PeiDockerApp', self.app).action_quit_app()