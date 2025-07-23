"""Form widgets for PeiDocker GUI configuration."""

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button, Checkbox, Input
from textual.widget import Widget
from textual.message import Message
from typing import Dict, Any, Optional

from .inputs import DockerImageInput, PortNumberInput, UserIDInput
from ..models.config import ProjectConfig, SSHConfig, Stage1Config


class ConfigUpdated(Message):
    """Message sent when configuration is updated."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__()
        self.config = config


class ProjectConfigForm(Widget):
    """Form for basic project configuration."""
    
    DEFAULT_CSS = """
    ProjectConfigForm {
        layout: vertical;
        padding: 1;
        border: solid $primary;
    }
    
    .form-row {
        layout: vertical;
        margin: 1 0;
    }
    
    .form-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .form-buttons {
        layout: horizontal;
        align: center middle;
        margin: 1 0;
    }
    """
    
    def __init__(self, initial_config: Optional[ProjectConfig] = None):
        super().__init__()
        self.config = initial_config or ProjectConfig()
    
    def compose(self) -> ComposeResult:
        """Create the project configuration form."""
        with Vertical():
            yield Static("Project Configuration", classes="form-title")
            
            with Vertical(classes="form-row"):
                yield Static("Project Name:")
                yield Input(
                    placeholder="my-awesome-project",
                    value=self.config.project_name,
                    id="project_name"
                )
            
            with Vertical(classes="form-row"):
                yield Static("Base Docker Image:")
                yield DockerImageInput(
                    value=self.config.stage_1.base_image,
                    id="base_image"
                )
            
            with Vertical(classes="form-row"):
                yield Static("Project Directory:")
                yield Input(
                    placeholder="/path/to/project",
                    value=self.config.project_dir,
                    id="project_dir"
                )
            
            with Horizontal(classes="form-buttons"):
                yield Button("Validate", id="validate", variant="primary")
                yield Button("Reset", id="reset", variant="default")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "validate":
            self._validate_and_save()
        elif event.button.id == "reset":
            self._reset_form()
    
    def _validate_and_save(self) -> None:
        """Validate form data and save configuration."""
        try:
            # Create config with proper dataclass structure
            validated_config = ProjectConfig(
                project_name=self.query_one("#project_name", Input).value,
                project_dir=self.query_one("#project_dir", Input).value,
                stage_1=Stage1Config(
                    base_image=self.query_one("#base_image", DockerImageInput).value
                )
            )
            
            # Send message to parent
            self.post_message(ConfigUpdated(validated_config.to_user_config_dict()))
            self.notify("✓ Project configuration is valid!", severity="information")
            
        except Exception as e:
            self.notify(f"✗ Validation error: {str(e)}", severity="error")
    
    def _reset_form(self) -> None:
        """Reset form to initial values."""
        self.query_one("#project_name", Input).value = self.config.project_name
        self.query_one("#base_image", DockerImageInput).value = self.config.stage_1.base_image
        self.query_one("#project_dir", Input).value = self.config.project_dir


class SSHConfigForm(Widget):
    """Form for SSH configuration."""
    
    DEFAULT_CSS = """
    SSHConfigForm {
        layout: vertical;
        padding: 1;
        border: solid $primary;
    }
    
    .form-row {
        layout: vertical;
        margin: 1 0;
    }
    
    .form-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .ssh-options {
        border: solid $secondary;
        padding: 1;
        margin: 1 0;
    }
    
    .port-row {
        layout: horizontal;
        align: left middle;
    }
    
    .port-separator {
        margin: 0 1;
    }
    """
    
    def __init__(self, initial_config: Optional[SSHConfig] = None):
        super().__init__()
        self.config = initial_config or SSHConfig()
    
    def compose(self) -> ComposeResult:
        """Create the SSH configuration form."""
        with Vertical():
            yield Static("SSH Configuration", classes="form-title")
            
            yield Checkbox(
                "Enable SSH access",
                value=self.config.enable,
                id="ssh_enabled"
            )
            
            with Vertical(classes="ssh-options", id="ssh_options"):
                if self.config.enable:
                    with Vertical(classes="form-row"):
                        yield Static("Port Mapping:")
                        with Horizontal(classes="port-row"):
                            yield PortNumberInput(
                                value=str(self.config.host_port),
                                id="host_port"
                            )
                            yield Static(":", classes="port-separator")
                            yield PortNumberInput(
                                value=str(self.config.port),
                                id="container_port"
                            )
                    
                    with Vertical(classes="form-row"):
                        yield Static("SSH User:")
                        yield Input(
                            placeholder="username",
                            value=self.config.users[0].name if self.config.users else "",
                            id="ssh_user"
                        )
                    
                    with Vertical(classes="form-row"):
                        yield Static("SSH Password:")
                        yield Input(
                            placeholder="password",
                            password=True,
                            value=self.config.users[0].password if self.config.users else "",
                            id="ssh_password"
                        )
                    
                    with Vertical(classes="form-row"):
                        yield Static("User ID:")
                        yield UserIDInput(
                            value=str(self.config.users[0].uid) if self.config.users else "1100",
                            id="user_id"
                        )
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle SSH enable/disable checkbox."""
        if event.checkbox.id == "ssh_enabled":
            self._update_ssh_options(event.value)
    
    def _update_ssh_options(self, enabled: bool) -> None:
        """Show/hide SSH options based on enabled state."""
        options_container = self.query_one("#ssh_options")
        options_container.remove_children()
        
        if enabled:
            options_container.mount_all([
                Static("Port Mapping:"),
                Horizontal(
                    PortNumberInput(value="2222", id="host_port"),
                    Static(":", classes="port-separator"),
                    PortNumberInput(value="22", id="container_port"),
                    classes="port-row"
                ),
                Static("SSH User:"),
                Input(placeholder="username", id="ssh_user"),
                Static("SSH Password:"),
                Input(placeholder="password", password=True, id="ssh_password"),
                Static("User ID:"),
                UserIDInput(value="1100", id="user_id"),
            ])
    
    def get_config(self) -> Dict[str, Any]:
        """Get current SSH configuration."""
        enabled = self.query_one("#ssh_enabled", Checkbox).value
        
        if not enabled:
            return {"enable": False}
        
        return {
            "enable": True,
            "host_port": int(self.query_one("#host_port", PortNumberInput).value or "2222"),
            "port": int(self.query_one("#container_port", PortNumberInput).value or "22"),
            "users": [{
                "name": self.query_one("#ssh_user", Input).value or "user",
                "password": self.query_one("#ssh_password", Input).value or "password",
                "uid": int(self.query_one("#user_id", UserIDInput).value or "1100"),
            }]
        }