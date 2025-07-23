"""Environment Variables Configuration Screen for Simple Mode Wizard."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Input, Button, RadioButton, RadioSet, ListView, ListItem, Label
from typing import cast
from textual.screen import Screen
from textual.message import Message

from ...models.config import ProjectConfig
from ...utils.file_utils import validate_environment_variable
from ...widgets.inputs import EnvironmentVariableInput
from ...widgets.dialogs import ErrorDialog


class EnvironmentVariablesScreen(Screen):
    """Screen for configuring environment variables."""
    
    CSS = """
    EnvironmentVariablesScreen {
        layout: vertical;
        padding: 1;
    }
    
    .header {
        height: 3;
        text-align: center;
        margin-bottom: 1;
    }
    
    .form-container {
        border: solid $primary;
        padding: 1;
        margin: 1;
    }
    
    .form-row {
        height: auto;
        margin: 1 0;
    }
    
    .button-bar {
        height: 3;
        align: center middle;
    }
    
    .env-settings {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
    }
    
    .info-text {
        color: $text-muted;
        margin: 1 0;
    }
    
    .input-row {
        layout: horizontal;
        height: 3;
        align: stretch;
    }
    
    .env-input {
        width: 3fr;
    }
    
    .add-button {
        width: 1fr;
        margin-left: 1;
    }
    
    .current-vars {
        height: 8;
        border: solid $accent;
        margin: 1 0;
    }
    
    .help-text {
        color: $warning;
        margin: 1 0;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        
        # Extract current environment variables from project config
        self.current_vars = project_config.stage_1.environment or []
        
    def compose(self) -> ComposeResult:
        """Create the environment variables configuration form."""
        yield Static("Environment Variables                  Step 6 of 12", classes="header")
        
        with Container(classes="form-container"):
            yield Static("Set custom environment variables for the container:")
            
            with Vertical(classes="form-row"):
                with RadioSet(id="env_enabled"):
                    yield RadioButton("Yes", value=bool(self.current_vars))
                    yield RadioButton("No", value=not bool(self.current_vars))
                yield Static("Add Environment Variables:")
            
            with Container(classes="env-settings", id="env_settings"):
                yield Static(
                    "Enter environment variable (KEY=VALUE):",
                    classes="info-text"
                )
                
                with Horizontal(classes="input-row"):
                    yield EnvironmentVariableInput(
                        id="env_input",
                        classes="env-input"
                    )
                    yield Button("Add", id="add_env", classes="add-button")
                
                yield Static("Current variables:")
                with ScrollableContainer(classes="current-vars"):
                    yield ListView(id="env_list")
                
                yield Static(
                    "To delete a variable, set it to an empty value",
                    classes="help-text"
                )
                yield Static(
                    "Press Enter with empty input to finish",
                    classes="info-text"
                )
        
        with Horizontal(classes="button-bar"):
            yield Button("Prev", id="prev", variant="default")
            yield Button("Next", id="next", variant="primary")
    
    def on_mount(self) -> None:
        """Set up initial state when screen is mounted."""
        self._update_env_settings_visibility()
        self._update_env_list()
        
        # Set initial radio button selection - already handled by value parameters in compose()
        # RadioButton values are set during compose() based on current_vars
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button changes."""
        if event.radio_set.id == "env_enabled":
            self._update_env_settings_visibility()
            
            # If disabling environment variables, clear the list
            if event.pressed and event.pressed.label == "No":
                self.current_vars.clear()
                self._update_env_list()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "env_input":
            self._add_environment_variable()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "prev":
            self.post_message(self.BackPressed())
        elif event.button.id == "next":
            config = self._get_environment_variables()
            self.post_message(self.ConfigReady(config))
        elif event.button.id == "add_env":
            self._add_environment_variable()
    
    def _update_env_settings_visibility(self) -> None:
        """Show/hide environment settings based on enabled state."""
        env_enabled = self.query_one("#env_enabled", RadioSet)
        env_settings = self.query_one("#env_settings")
        
        # Check if "Yes" button is pressed by looking at first RadioButton ("Yes")
        yes_button = cast(RadioButton, env_enabled.query_one("RadioButton"))  # First button is "Yes"
        is_enabled = yes_button.value if yes_button else False
        env_settings.display = is_enabled
    
    def _add_environment_variable(self) -> None:
        """Add a new environment variable from the input field."""
        env_input = self.query_one("#env_input", Input)
        env_var = env_input.value.strip()
        
        if not env_var:
            # Empty input - user wants to finish
            return
        
        # Validate the environment variable format
        is_valid, error_msg = validate_environment_variable(env_var)
        if not is_valid:
            self.notify(error_msg, severity="error")
            return
        
        # Extract key and value
        if "=" not in env_var:
            self.notify("Environment variable must be in KEY=VALUE format", severity="error")
            return
        
        key, value = env_var.split("=", 1)
        key = key.strip()
        
        # Handle deletion (empty value)
        if not value.strip():
            # Remove existing variable with this key
            self.current_vars = [var for var in self.current_vars if not var.startswith(f"{key}=")]
            self._update_env_list()
            env_input.value = ""
            self.notify(f"Removed environment variable: {key}", severity="information")
            return
        
        # Check for existing variable with same key and update it
        updated = False
        for i, existing_var in enumerate(self.current_vars):
            if existing_var.startswith(f"{key}="):
                self.current_vars[i] = env_var
                updated = True
                break
        
        if not updated:
            self.current_vars.append(env_var)
        
        self._update_env_list()
        
        # Clear the input
        env_input.value = ""
        action = "Updated" if updated else "Added"
        self.notify(f"{action} environment variable: {key}", severity="information")
    
    def _update_env_list(self) -> None:
        """Update the environment variables list display."""
        env_list = self.query_one("#env_list", ListView)
        env_list.clear()
        
        # Add user-configured environment variables
        for env_var in sorted(self.current_vars):
            item = ListItem(Label(f"• {env_var}"))
            env_list.append(item)
        
        if not self.current_vars:
            item = ListItem(Label("(No environment variables configured)"))
            env_list.append(item)
    
    def _get_environment_variables(self) -> list[str]:
        """Get the current environment variables."""
        env_enabled = self.query_one("#env_enabled", RadioSet)
        
        yes_button = cast(RadioButton, env_enabled.query_one("RadioButton"))  # First button is "Yes"
        if not (yes_button and yes_button.value):
            return []
        
        return self.current_vars.copy()
    
    def save_configuration(self) -> None:
        """Save current environment variables to project configuration."""
        self.project_config.stage_1.environment = self.current_vars.copy()
    
    def handle_escape(self) -> None:
        """Handle escape key press - clear current input."""
        try:
            env_input = self.query_one("#env_input", Input)
            env_input.value = ""
        except:
            pass  # Input might not exist or be visible
    
    class ConfigReady(Message):
        """Message sent when configuration is ready."""
        
        def __init__(self, variables: list[str]) -> None:
            super().__init__()
            self.variables = variables
    
    class BackPressed(Message):
        """Message sent when back button is pressed."""
        pass