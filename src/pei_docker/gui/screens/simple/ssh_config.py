"""SSH configuration screen for simple mode wizard."""

from pathlib import Path
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Label, Input, Static, Button, RadioSet, RadioButton, Checkbox
from textual.validation import Function

from textual_fspicker import FileOpen

from ...models.config import ProjectConfig, SSHUser
from ...utils.file_utils import validate_ssh_public_key, get_ssh_key_from_system
from ...widgets.inputs import PortNumberInput, UserIDInput
from ...widgets.dialogs import ErrorDialog


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
        self.root_enabled = getattr(project_config.stage_1.ssh, 'root_enabled', False)
    
    def _get_or_create_first_user(self) -> 'SSHUser':
        """Get the first SSH user or create one with default values."""
        from ...models.config import SSHUser
        if self.project_config.stage_1.ssh.users:
            return self.project_config.stage_1.ssh.users[0]
        else:
            # Create default user
            default_user = SSHUser(name="me", password="123456", uid=1100)
            self.project_config.stage_1.ssh.users.append(default_user)
            return default_user
    
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
                yield from self._create_ssh_config_section()
    
    def _create_ssh_config_section(self) -> ComposeResult:
        """Create the SSH configuration section."""
        with Static(classes="section"):
            yield Label("SSH Settings", classes="section-title")
            
            # Basic SSH settings
            with Vertical(classes="field-group"):
                yield Label("SSH Container Port:", classes="field-label")
                yield PortNumberInput(
                    value=str(self.project_config.stage_1.ssh.port),
                    id="ssh_port"
                )
                
                yield Label("SSH Host Port:", classes="field-label")
                yield PortNumberInput(
                    value=str(self.project_config.stage_1.ssh.host_port),
                    id="ssh_host_port"
                )
                
                yield Label("SSH User:", classes="field-label")
                # Get first user from users list or use default
                if self.project_config.stage_1.ssh.users:
                    ssh_user = self.project_config.stage_1.ssh.users[0]
                    user_name = ssh_user.name
                else:
                    ssh_user = None
                    user_name = "me"
                yield Input(
                    value=user_name,
                    placeholder="me",
                    id="ssh_user",
                    validators=[Function(self._validate_username, "Invalid username")]
                )
                
                yield Label("User ID:", classes="field-label")
                user_uid = ssh_user.uid if ssh_user else 1100
                yield UserIDInput(
                    value=str(user_uid),
                    id="ssh_uid"
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
                        with Horizontal():
                            yield Input(
                                placeholder="Enter path to private key file or '~' for system key",
                                id="ssh_privkey",
                            )
                            yield Button("Browse...", id="browse_privkey", variant="default")
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
        return bool(value) and ' ' not in value and ',' not in value
    
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
        self.ssh_enabled = event.pressed.id == "ssh_yes" if event.pressed else False
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
        # Note: root_enabled is not part of SSHConfig data model yet
        # self.project_config.stage_1.ssh.root_enabled = self.root_enabled
        self.refresh(recompose=True)
    
    @on(Button.Pressed, "#browse_privkey")
    def on_browse_privkey_pressed(self) -> None:
        """Browse for SSH private key file."""
        # Launch file picker using async worker
        self.run_worker(self._browse_ssh_key_async())

    async def _browse_ssh_key_async(self) -> None:
        """Async worker to handle SSH key file browsing."""
        key_path = await self.app.push_screen_wait(FileOpen())
        if key_path:
            privkey_input = self.query_one("#ssh_privkey", Input)
            privkey_input.value = str(key_path)
            # Trigger input change event
            self.on_input_changed(Input.Changed(privkey_input, privkey_input.value))
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        if not self.ssh_enabled:
            return
        
        if event.input.id == "ssh_port":
            try:
                port = int(event.value.strip()) if event.value.strip() else 22
                self.project_config.stage_1.ssh.port = port
            except ValueError:
                pass  # Invalid input, ignore
        
        elif event.input.id == "ssh_host_port":
            try:
                port = int(event.value.strip()) if event.value.strip() else 2222
                self.project_config.stage_1.ssh.host_port = port
            except ValueError:
                pass  # Invalid input, ignore
        
        elif event.input.id == "ssh_uid":
            try:
                uid = int(event.value.strip()) if event.value.strip() else 1100
                # Update or create SSH user with new UID
                if not self.project_config.stage_1.ssh.users:
                    self.project_config.stage_1.ssh.users.append(SSHUser(name="me", password="123456", uid=uid))
                else:
                    user = self._get_or_create_first_user()
                    username = user.name
                    user.uid = uid
            except ValueError:
                pass  # Invalid input, ignore
        
        elif event.input.id == "ssh_user":
            if self._validate_username(event.value):
                # Update or create SSH user
                user_name = event.value.strip()
                if not self.project_config.stage_1.ssh.users:
                    self.project_config.stage_1.ssh.users.append(SSHUser(name=user_name, password="123456"))
                else:
                    # Update existing user's name by removing old entry and adding new one
                    old_user = self._get_or_create_first_user()
                    old_user.name = user_name  # Update the user's name directly
        
        elif event.input.id == "ssh_password":
            if self._validate_password(event.value):
                # Update SSH user password
                user = self._get_or_create_first_user()
                user.password = event.value
        
        elif event.input.id == "ssh_pubkey":
            if self._validate_public_key(event.value):
                key_text: Optional[str] = event.value.strip()
                if key_text == '~':
                    # Try to get system SSH key
                    system_key = get_ssh_key_from_system()
                    key_text = system_key if system_key else None
                
                # Update SSH user public key
                if self.project_config.stage_1.ssh.users:
                    user = self._get_or_create_first_user()
                    username = user.name
                    user.pubkey_text = key_text
        
        elif event.input.id == "ssh_privkey":
            privkey_path = event.value.strip()
            if privkey_path == '~':
                privkey_path = "~"  # Keep the ~ reference
            
            # Update SSH user private key
            if self.project_config.stage_1.ssh.users:
                user = self._get_or_create_first_user()
                username = user.name
                user.privkey_file = privkey_path if privkey_path else None
        
        elif event.input.id == "root_password":
            if self._validate_password(event.value):
                self.project_config.stage_1.ssh.root_password = event.value
    
    def is_valid(self) -> bool:
        """Check if all inputs are valid."""
        if not self.ssh_enabled:
            return True
        
        # Basic validation - at least SSH user and password should be set
        return bool(self.project_config.stage_1.ssh.users) or not self.ssh_enabled