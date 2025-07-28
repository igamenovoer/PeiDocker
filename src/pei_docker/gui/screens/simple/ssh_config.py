"""SC-4: SSH Configuration Screen - Technical Implementation.

This module implements the SSH Configuration Screen (SC-4) according to the
technical specification. It provides the second step of the configuration wizard
where users configure SSH access to their containers.

The implementation follows flat material design principles and integrates with
the SC-2 wizard controller framework for navigation and state management.
"""

import re
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.widget import Widget
from textual.widgets import Label, Input, Static, RadioSet, RadioButton, Checkbox
from textual.validation import ValidationResult, Validator

from pei_docker.gui.models.config import ProjectConfig, SSHUser


class SSHPortValidator(Validator):
    """Validator for SSH port numbers."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate port number range."""
        if not value.strip():
            return self.failure("Port number is required")
        
        try:
            port = int(value.strip())
            if not (1 <= port <= 65535):
                return self.failure("Port must be between 1-65535")
            # Note: Ports < 1024 may require elevated privileges, but we allow them
            return self.success()
        except ValueError:
            return self.failure("Port must be a valid number")


class SSHUsernameValidator(Validator):
    """Validator for SSH usernames."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate SSH username format."""
        if not value.strip():
            return self.failure("SSH username is required")
        
        username = value.strip()
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
            return self.failure("Username must contain only letters, numbers, and underscores")
        
        return self.success()


class SSHPasswordValidator(Validator):
    """Validator for SSH passwords."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate SSH password constraints."""
        if not value:
            return self.failure("SSH password is required")
        
        if ' ' in value or ',' in value:
            return self.failure("Password cannot contain spaces or commas")
        
        return self.success()


class SSHUIDValidator(Validator):
    """Validator for SSH user IDs."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate SSH user UID."""
        if not value.strip():
            return self.failure("User UID is required")
        
        try:
            uid = int(value.strip())
            if uid < 1000:
                # Note: UID below 1000 may conflict with system users, but we allow it
                return self.success()
            if uid > 65535:
                return self.failure("UID must be below 65535")
            return self.success()
        except ValueError:
            return self.failure("UID must be a valid number")


class SSHKeyValidator(Validator):
    """Validator for SSH public keys."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate SSH public key format."""
        if not value.strip():
            return self.success()  # Empty is valid (optional)
        
        key_text = value.strip()
        if key_text == '~':
            return self.success()  # System key reference is valid
        
        if not any(key_text.startswith(prefix) for prefix in ['ssh-rsa', 'ssh-ed25519', 'ssh-ecdsa']):
            return self.failure("Invalid SSH public key format")
        
        return self.success()


class SSHConfigWidget(Widget):
    """SC-4: SSH Configuration Widget for embedding in wizard.
    
    This is the embeddable Widget version of the SSH Configuration screen,
    designed to be mounted within the SC-2 wizard controller framework.
    """
    
    # Flat Material Design CSS - Optimized Spacing
    DEFAULT_CSS = """
    SSHConfigWidget {
        padding: 0;
        layout: vertical;
    }
    
    /* Compact containers with proper vertical flow */
    .ssh-config-container {
        border: none;
        padding: 0;
        margin: 0;
        layout: vertical;
        height: auto;
    }
    
    /* SSH toggle section - tight spacing */
    .ssh-toggle-section {
        background: $surface-lighten-1;
        border: none;
        padding: 0;
        margin: 0;
        layout: vertical;
        height: auto;
    }
    
    /* SSH configuration section - tight spacing */
    .ssh-config-section {
        background: $surface-lighten-1;
        border: none;
        padding: 0;
        margin: 0;
        layout: vertical;
        height: auto;
    }
    
    /* Advanced options section - tight spacing */
    .advanced-section {
        background: $surface-lighten-2;
        border: none;
        padding: 0;
        margin: 0;
        layout: vertical;
        height: auto;
    }
    
    /* Properly sized radio buttons - no height constraint */
    RadioSet {
        background: transparent;
        border: none;
        padding: 0;
        margin: 0;
        height: auto;
    }
    
    RadioButton {
        background: transparent;
        border: none;
        margin: 0;
    }
    
    /* Compact inputs */
    Input {
        margin: 0;
        height: 1;
    }
    
    /* Compact warnings */
    .ssh-warning {
        color: $warning;
        background: $warning-muted;
        border: none;
        padding: 0;
        margin: 0;
        text-style: italic;
        height: 1;
    }
    
    /* Compact headers */
    .section-header {
        text-style: bold;
        color: $foreground;
        margin: 0;
        height: 1;
    }
    
    /* Compact labels */
    .field-label {
        color: $foreground;
        margin: 0;
        height: 1;
    }
    
    /* Compact help text */
    .preview-text {
        color: $foreground 60%;
        text-style: italic;
        padding: 0;
        margin: 0;
        height: 1;
    }
    
    /* Compact validation errors */
    .validation-error {
        color: $error;
        background: $surface-lighten-1;
        padding: 0;
        text-style: italic;
        margin: 0;
        height: 1;
    }
    
    /* Compact checkboxes */
    Checkbox {
        margin: 0;
        background: transparent;
        border: none;
        height: 1;
    }
    
    /* Compact notes */
    .required-note {
        color: $foreground 60%;
        text-style: italic;
        margin: 0;
        height: 1;
    }
    """
    
    def __init__(self, project_config: ProjectConfig) -> None:
        super().__init__()
        self.project_config = project_config
        
        # Initialize SSH configuration state
        self.ssh_enabled = project_config.stage_1.ssh.enable
        self.public_key_auth = False
        self.root_access = project_config.stage_1.ssh.root_enabled
        
        # Ensure we have at least one SSH user
        if not project_config.stage_1.ssh.users:
            default_user = SSHUser(name="me", password="123456", uid=1100)
            project_config.stage_1.ssh.users.append(default_user)
    
    def compose(self) -> ComposeResult:
        """Compose the SSH configuration widget."""
        with Container(classes="ssh-config-container"):
            yield Label("Configure SSH access to your container:", classes="section-header")
            
            # SSH Enable/Disable Section
            with Container(classes="ssh-toggle-section"):
                yield Label("Enable SSH:", classes="field-label")
                with RadioSet(id="ssh_enable"):
                    yield RadioButton("Yes", id="ssh_yes", value=self.ssh_enabled)
                    yield RadioButton("No", id="ssh_no", value=not self.ssh_enabled)
                
                if not self.ssh_enabled:
                    yield Static(
                        "WARNING: Selecting 'No' means you'll need to use docker exec commands to access the container",
                        classes="ssh-warning"
                    )
            
            # SSH Configuration Section (conditional)
            if self.ssh_enabled:
                yield from self._create_ssh_config_section()
    
    def _create_ssh_config_section(self) -> ComposeResult:
        """Create the SSH configuration section."""
        with Container(classes="ssh-config-section"):
            yield Label("SSH Settings:", classes="section-header")
            
            # SSH Container Port
            yield Label("SSH Container Port:", classes="field-label")
            yield Input(
                value=str(self.project_config.stage_1.ssh.port),
                placeholder="22",
                id="ssh_container_port",
                validators=[SSHPortValidator()]
            )
            
            # SSH Host Port
            yield Label("SSH Host Port:", classes="field-label")
            yield Input(
                value=str(self.project_config.stage_1.ssh.host_port),
                placeholder="2222",
                id="ssh_host_port",
                validators=[SSHPortValidator()]
            )
            
            # SSH User
            yield Label("SSH User:", classes="field-label")
            current_user = self._get_current_user()
            yield Input(
                value=current_user.name,
                placeholder="me",
                id="ssh_user",
                validators=[SSHUsernameValidator()]
            )
            
            # SSH Password
            yield Label("SSH Password (no spaces or commas):", classes="field-label")
            yield Input(
                value=current_user.password,
                placeholder="123456",
                password=True,
                id="ssh_password",
                validators=[SSHPasswordValidator()]
            )
            
            # SSH User UID
            yield Label("SSH User UID:", classes="field-label")
            yield Input(
                value=str(current_user.uid),
                placeholder="1100",
                id="ssh_uid",
                validators=[SSHUIDValidator()]
            )
            
            # Advanced Options Section
            yield from self._create_advanced_section()
    
    def _create_advanced_section(self) -> ComposeResult:
        """Create the advanced SSH options section."""
        with Container(classes="advanced-section"):
            yield Label("Advanced SSH Options:", classes="section-header")
            
            # SSH Public Key Authentication
            yield Checkbox(
                "SSH Public Key Authentication",
                id="public_key_auth",
                value=self.public_key_auth
            )
            
            if self.public_key_auth:
                yield Label("SSH Public Key:", classes="field-label")
                current_user = self._get_current_user()
                yield Input(
                    value=current_user.pubkey_text or "",
                    placeholder="Enter public key or type '~' to use system key",
                    id="ssh_public_key",
                    validators=[SSHKeyValidator()]
                )
                yield Static(
                    "Enter '~' to use your system's default SSH public key",
                    classes="preview-text"
                )
            
            # Root SSH Access
            yield Checkbox(
                "Root SSH Access",
                id="root_ssh_access",
                value=self.root_access
            )
            
            if self.root_access:
                yield Label("Root Password:", classes="field-label")
                yield Input(
                    value=self.project_config.stage_1.ssh.root_password,
                    placeholder="root",
                    password=True,
                    id="root_password",
                    validators=[SSHPasswordValidator()]
                )
                yield Static(
                    "WARNING: Root SSH access reduces container security",
                    classes="ssh-warning"
                )
    
    def _get_current_user(self) -> SSHUser:
        """Get the current SSH user (first in list)."""
        if not self.project_config.stage_1.ssh.users:
            default_user = SSHUser(name="me", password="123456", uid=1100)
            self.project_config.stage_1.ssh.users.append(default_user)
        return self.project_config.stage_1.ssh.users[0]
    
    @on(RadioSet.Changed, "#ssh_enable")
    def on_ssh_enable_changed(self, event: RadioSet.Changed) -> None:
        """Handle SSH enable/disable change."""
        if event.pressed:
            self.ssh_enabled = event.pressed.id == "ssh_yes"
            self.project_config.stage_1.ssh.enable = self.ssh_enabled
            # Refresh the widget to show/hide SSH configuration
            self.refresh(recompose=True)
    
    @on(Input.Changed, "#ssh_container_port")
    def on_ssh_container_port_changed(self, event: Input.Changed) -> None:
        """Handle SSH container port change."""
        try:
            port = int(event.value.strip()) if event.value.strip() else 22
            self.project_config.stage_1.ssh.port = port
        except ValueError:
            pass  # Invalid input, ignore
    
    @on(Input.Changed, "#ssh_host_port")
    def on_ssh_host_port_changed(self, event: Input.Changed) -> None:
        """Handle SSH host port change."""
        try:
            port = int(event.value.strip()) if event.value.strip() else 2222
            self.project_config.stage_1.ssh.host_port = port
        except ValueError:
            pass  # Invalid input, ignore
    
    @on(Input.Changed, "#ssh_user")
    def on_ssh_user_changed(self, event: Input.Changed) -> None:
        """Handle SSH user change."""
        if event.value.strip():
            current_user = self._get_current_user()
            current_user.name = event.value.strip()
    
    @on(Input.Changed, "#ssh_password")
    def on_ssh_password_changed(self, event: Input.Changed) -> None:
        """Handle SSH password change."""
        if event.value:
            current_user = self._get_current_user()
            current_user.password = event.value
    
    @on(Input.Changed, "#ssh_uid")
    def on_ssh_uid_changed(self, event: Input.Changed) -> None:
        """Handle SSH UID change."""
        try:
            uid = int(event.value.strip()) if event.value.strip() else 1100
            current_user = self._get_current_user()
            current_user.uid = uid
        except ValueError:
            pass  # Invalid input, ignore
    
    @on(Checkbox.Changed, "#public_key_auth")
    def on_public_key_auth_changed(self, event: Checkbox.Changed) -> None:
        """Handle public key authentication toggle."""
        self.public_key_auth = event.checkbox.value
        # Refresh to show/hide public key field
        self.refresh(recompose=True)
    
    @on(Input.Changed, "#ssh_public_key")
    def on_ssh_public_key_changed(self, event: Input.Changed) -> None:
        """Handle SSH public key change."""
        current_user = self._get_current_user()
        key_text = event.value.strip()
        
        if key_text == '~':
            # System key reference - could expand to actual key path
            current_user.pubkey_text = key_text
        elif key_text:
            current_user.pubkey_text = key_text
        else:
            current_user.pubkey_text = None
    
    @on(Checkbox.Changed, "#root_ssh_access")
    def on_root_ssh_access_changed(self, event: Checkbox.Changed) -> None:
        """Handle root SSH access toggle."""
        self.root_access = event.checkbox.value
        self.project_config.stage_1.ssh.root_enabled = self.root_access
        # Refresh to show/hide root password field
        self.refresh(recompose=True)
    
    @on(Input.Changed, "#root_password")
    def on_root_password_changed(self, event: Input.Changed) -> None:
        """Handle root password change."""
        if event.value:
            self.project_config.stage_1.ssh.root_password = event.value
    
    def is_valid(self) -> bool:
        """Check if all inputs are valid for navigation control."""
        if not self.ssh_enabled:
            return True  # If SSH is disabled, no validation needed
        
        # Check basic SSH configuration validity
        current_user = self._get_current_user()
        
        # Validate port numbers
        if not (1 <= self.project_config.stage_1.ssh.port <= 65535):
            return False
        if not (1 <= self.project_config.stage_1.ssh.host_port <= 65535):
            return False
        
        # Validate user credentials
        if not current_user.name or not self._is_valid_username(current_user.name):
            return False
        if not current_user.password or not self._is_valid_password(current_user.password):
            return False
        if not (1000 <= current_user.uid <= 65535):
            return False
        
        # If public key auth is enabled, validate the key
        if self.public_key_auth and current_user.pubkey_text:
            if not self._is_valid_ssh_key(current_user.pubkey_text):
                return False
        
        # If root access is enabled, validate root password
        if self.root_access:
            if not self.project_config.stage_1.ssh.root_password or not self._is_valid_password(self.project_config.stage_1.ssh.root_password):
                return False
        
        return True
    
    def _is_valid_username(self, username: str) -> bool:
        """Validate SSH username format."""
        return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username))
    
    def _is_valid_password(self, password: str) -> bool:
        """Validate SSH password constraints."""
        return bool(password and ' ' not in password and ',' not in password)
    
    def _is_valid_ssh_key(self, key: str) -> bool:
        """Validate SSH public key format."""
        if key == '~':
            return True  # System key reference is valid
        return any(key.startswith(prefix) for prefix in ['ssh-rsa', 'ssh-ed25519', 'ssh-ecdsa'])
    
    def handle_escape(self) -> None:
        """Handle single ESC key press - clear current input."""
        try:
            focused_widget = self.screen.focused
            if isinstance(focused_widget, Input):
                focused_widget.value = ""
        except Exception:
            pass  # Ignore errors during escape handling