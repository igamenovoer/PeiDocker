"""SSH configuration screen for simple mode wizard."""

from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Label, Input, Static, Button, RadioSet, RadioButton, Checkbox
from textual.validation import Function

from ...models.config import ProjectConfig, SSHUser
from ...utils.file_utils import validate_ssh_public_key, get_ssh_key_from_system


class SSHConfigScreen(Screen[None]):
    """Screen for configuring SSH access."""
    
    DEFAULT_CSS = """
    SSHConfigScreen {
        background: $surface;
        padding: 2;
    }
    
    .section {
        border: solid $primary;
        padding: 1 2;
        margin: 1 0;
        background: $surface-lighten-1;
    }
    
    .section-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .field-group {
        margin: 1 0;
    }
    
    .field-label {
        color: $text;
        margin-bottom: 1;
    }
    
    .field-help {
        color: $text-muted;
        margin-top: 1;
    }
    
    .warning {
        color: $warning;
        margin: 1 0;
        padding: 1;
        border: solid $warning;
        background: $warning 20%;
    }
    
    .expandable-section {
        margin-top: 1;
        padding: 1;
        border: solid $secondary;
        background: $surface-lighten-2;
    }
    
    Input {
        width: 100%;
    }
    
    Input.-invalid {
        border: solid $error;
    }
    
    RadioSet {
        margin: 1 0;
    }
    
    Checkbox {
        margin: 1 0;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        self.ssh_enabled = project_config.stage_1.ssh.enable
        self.use_public_key = False
        self.use_private_key = False
        self.root_enabled = project_config.stage_1.ssh.root_enabled
    
    def compose(self) -> ComposeResult:
        """Compose the SSH configuration screen."""
        with Vertical():
            yield Label("Configure SSH access to your container:", classes="field-help")
            
            # SSH enable/disable section
            with Static(classes="section"):
                yield Label("SSH Server", classes="section-title")
                
                with RadioSet(id="ssh_enable"):
                    yield RadioButton("Yes", id="ssh_yes", value=self.ssh_enabled)
                    yield RadioButton("No", id="ssh_no", value=not self.ssh_enabled)
                
                if not self.ssh_enabled:
                    yield Static(
                        "⚠ Selecting 'No' means you'll need to use docker exec commands to access the container",
                        classes="warning"
                    )
            
            # SSH configuration (shown when enabled)
            if self.ssh_enabled:
                yield self._create_ssh_config_section()
    
    def _create_ssh_config_section(self) -> ComposeResult:
        """Create the SSH configuration section."""
        with Static(classes="section"):
            yield Label("SSH Settings", classes="section-title")
            
            # Basic SSH settings
            with Vertical(classes="field-group"):
                yield Label("SSH Container Port:", classes="field-label")
                yield Input(
                    value=str(self.project_config.stage_1.ssh.port),
                    placeholder="22",
                    id="ssh_port",
                    validators=[Function(self._validate_port, "Invalid port number")]
                )
                
                yield Label("SSH Host Port:", classes="field-label")
                yield Input(
                    value=str(self.project_config.stage_1.ssh.host_port),
                    placeholder="2222",
                    id="ssh_host_port",
                    validators=[Function(self._validate_port, "Invalid port number")]
                )
                
                yield Label("SSH User:", classes="field-label")
                ssh_user = self.project_config.stage_1.ssh.users[0] if self.project_config.stage_1.ssh.users else None
                user_name = ssh_user.name if ssh_user else "me"
                yield Input(
                    value=user_name,
                    placeholder="me",
                    id="ssh_user",
                    validators=[Function(self._validate_username, "Invalid username")]
                )
                
                yield Label("SSH Password (no spaces or commas):", classes="field-label")
                user_password = ssh_user.password if ssh_user else "123456"
                yield Input(
                    value=user_password,
                    placeholder="123456",
                    password=True,
                    id="ssh_password",
                    validators=[Function(self._validate_password, "Password cannot contain spaces or commas")]
                )
            
            # Advanced SSH options
            with Static(classes="expandable-section"):
                yield Label("Advanced SSH Options", classes="section-title")
                
                yield Checkbox("Use SSH Public Key Authentication", id="use_pubkey", value=self.use_public_key)
                
                if self.use_public_key:
                    with Vertical(classes="field-group"):
                        yield Label("Public Key:", classes="field-label")
                        yield Input(
                            placeholder="Enter public key or type '~' to use system key",
                            id="ssh_pubkey",
                            validators=[Function(self._validate_public_key, "Invalid SSH public key")]
                        )
                        yield Label("Enter '~' to use your system's default SSH public key", classes="field-help")
                
                yield Checkbox("Use SSH Private Key", id="use_privkey", value=self.use_private_key)
                
                if self.use_private_key:
                    with Vertical(classes="field-group"):
                        yield Label("Private Key File Path:", classes="field-label")
                        yield Input(
                            placeholder="Enter path to private key file or '~' for system key",
                            id="ssh_privkey",
                        )
                        yield Label("Enter '~' to use your system's default SSH private key", classes="field-help")
                
                yield Checkbox("Enable Root SSH Access", id="root_ssh", value=self.root_enabled)
                
                if self.root_enabled:
                    with Vertical(classes="field-group"):
                        yield Label("Root Password:", classes="field-label")
                        yield Input(
                            value=self.project_config.stage_1.ssh.root_password,
                            placeholder="root",
                            password=True,
                            id="root_password",
                            validators=[Function(self._validate_password, "Password cannot contain spaces or commas")]
                        )
    
    def _validate_port(self, value: str) -> bool:
        """Validate port number."""
        try:
            port = int(value.strip())
            return 1 <= port <= 65535
        except ValueError:
            return False
    
    def _validate_username(self, value: str) -> bool:
        """Validate username."""
        username = value.strip()
        return bool(username) and username.isalnum()
    
    def _validate_password(self, value: str) -> bool:
        """Validate password (no spaces or commas)."""
        return value and ' ' not in value and ',' not in value
    
    def _validate_public_key(self, value: str) -> bool:
        """Validate SSH public key."""
        key_text = value.strip()
        if not key_text:
            return True  # Empty is valid (optional)
        
        if key_text == '~':
            return True  # System key reference is valid
        
        return validate_ssh_public_key(key_text)
    
    @on(RadioSet.Changed, "#ssh_enable")
    def on_ssh_enable_changed(self, event: RadioSet.Changed) -> None:
        """Handle SSH enable/disable change."""
        self.ssh_enabled = event.pressed.id == "ssh_yes"
        self.project_config.stage_1.ssh.enable = self.ssh_enabled
        # Refresh the screen to show/hide SSH config
        self.refresh(recompose=True)
    
    @on(Checkbox.Changed, "#use_pubkey")
    def on_use_pubkey_changed(self, event: Checkbox.Changed) -> None:
        """Handle public key checkbox change."""
        self.use_public_key = event.checkbox.value
        self.refresh(recompose=True)
    
    @on(Checkbox.Changed, "#use_privkey")
    def on_use_privkey_changed(self, event: Checkbox.Changed) -> None:
        """Handle private key checkbox change."""
        self.use_private_key = event.checkbox.value
        self.refresh(recompose=True)
    
    @on(Checkbox.Changed, "#root_ssh")
    def on_root_ssh_changed(self, event: Checkbox.Changed) -> None:
        """Handle root SSH checkbox change."""
        self.root_enabled = event.checkbox.value
        self.project_config.stage_1.ssh.root_enabled = self.root_enabled
        self.refresh(recompose=True)
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        if not self.ssh_enabled:
            return
        
        if event.input.id == "ssh_port":
            if self._validate_port(event.value):
                self.project_config.stage_1.ssh.port = int(event.value.strip())
        
        elif event.input.id == "ssh_host_port":
            if self._validate_port(event.value):
                self.project_config.stage_1.ssh.host_port = int(event.value.strip())
        
        elif event.input.id == "ssh_user":
            if self._validate_username(event.value):
                # Update or create SSH user
                user_name = event.value.strip()
                if not self.project_config.stage_1.ssh.users:
                    self.project_config.stage_1.ssh.users.append(SSHUser(name=user_name, password="123456"))
                else:
                    self.project_config.stage_1.ssh.users[0].name = user_name
        
        elif event.input.id == "ssh_password":
            if self._validate_password(event.value):
                # Update SSH user password
                if not self.project_config.stage_1.ssh.users:
                    self.project_config.stage_1.ssh.users.append(SSHUser(name="me", password=event.value))
                else:
                    self.project_config.stage_1.ssh.users[0].password = event.value
        
        elif event.input.id == "ssh_pubkey":
            if self._validate_public_key(event.value):
                key_text = event.value.strip()
                if key_text == '~':
                    # Try to get system SSH key
                    system_key = get_ssh_key_from_system()
                    key_text = system_key if system_key else None
                
                # Update SSH user public key
                if self.project_config.stage_1.ssh.users:
                    self.project_config.stage_1.ssh.users[0].pubkey_text = key_text
        
        elif event.input.id == "ssh_privkey":
            privkey_path = event.value.strip()
            if privkey_path == '~':
                privkey_path = "~"  # Keep the ~ reference
            
            # Update SSH user private key
            if self.project_config.stage_1.ssh.users:
                self.project_config.stage_1.ssh.users[0].privkey_file = privkey_path if privkey_path else None
        
        elif event.input.id == "root_password":
            if self._validate_password(event.value):
                self.project_config.stage_1.ssh.root_password = event.value
    
    def is_valid(self) -> bool:
        """Check if all inputs are valid."""
        if not self.ssh_enabled:
            return True
        
        # Basic validation - at least SSH user and password should be set
        return bool(self.project_config.stage_1.ssh.users) or not self.ssh_enabled