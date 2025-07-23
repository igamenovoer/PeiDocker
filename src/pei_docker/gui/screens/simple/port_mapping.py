"""Port Mapping Configuration Screen for Simple Mode Wizard."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Input, Button, RadioButton, RadioSet, ListView, ListItem, Label
from typing import cast
from textual.screen import Screen
from textual.message import Message
import re

from ...models.config import ProjectConfig
from ...utils.file_utils import validate_port_mapping
from ...widgets.inputs import PortMappingInput
from ...widgets.dialogs import ErrorDialog


class PortMappingScreen(Screen):
    """Screen for configuring additional port mappings."""
    
    CSS = """
    PortMappingScreen {
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
    
    .port-settings {
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
    
    .port-input {
        width: 3fr;
    }
    
    .add-button {
        width: 1fr;
        margin-left: 1;
    }
    
    .current-mappings {
        height: 8;
        border: solid $accent;
        margin: 1 0;
    }
    
    .example-text {
        color: $success;
        text-style: italic;
        margin: 0 0 1 0;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        
        # Extract current mappings from project config
        self.current_mappings = project_config.stage_1.ports or []
        
        # Extract SSH port configuration
        ssh_config = project_config.stage_1.ssh
        if ssh_config.enable:
            self.ssh_port = f"{ssh_config.host_port}:{ssh_config.port}"
        else:
            self.ssh_port = "2222:22"  # Default fallback
    
    def save_configuration(self) -> None:
        """Save current port mappings to project configuration."""
        self.project_config.stage_1.ports = self.current_mappings.copy()
        
    def compose(self) -> ComposeResult:
        """Create the port mapping configuration form."""
        yield Static("Additional Port Mapping                Step 5 of 12", classes="header")
        
        with Container(classes="form-container"):
            yield Static("Map additional ports from host to container:")
            yield Static("(SSH port is already configured)", classes="info-text")
            
            with Vertical(classes="form-row"):
                with RadioSet(id="port_enabled"):
                    yield RadioButton("Yes", value=bool(self.current_mappings))
                    yield RadioButton("No", value=not bool(self.current_mappings))
                yield Static("Add Port Mappings:")
            
            with Container(classes="port-settings", id="port_settings"):
                yield Static(
                    "Enter port mapping (host:container) or range:",
                    classes="info-text"
                )
                yield Static(
                    "Examples: 8080:80, 3000:3000, 100-200:300-400",
                    classes="example-text"
                )
                
                with Horizontal(classes="input-row"):
                    yield PortMappingInput(
                        id="port_input",
                        classes="port-input"
                    )
                    yield Button("Add", id="add_port", classes="add-button")
                
                yield Static("Current mappings:")
                with ScrollableContainer(classes="current-mappings"):
                    yield ListView(id="port_list")
                
                yield Static(
                    "Press Enter with empty input to finish",
                    classes="info-text"
                )
        
        with Horizontal(classes="button-bar"):
            yield Button("Back", id="back", variant="default")
            yield Button("Next", id="next", variant="primary")
    
    def on_mount(self) -> None:
        """Set up initial state when screen is mounted."""
        self._update_port_settings_visibility()
        self._update_port_list()
        
        # Set initial radio button selection - already handled by value parameters in compose()
        # RadioButton values are set during compose() based on current_mappings
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button changes."""
        if event.radio_set.id == "port_enabled":
            self._update_port_settings_visibility()
            
            # If disabling port mappings, clear the list
            if event.pressed and event.pressed.label == "No":
                self.current_mappings.clear()
                self._update_port_list()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "port_input":
            self._add_port_mapping()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back":
            self.post_message(self.BackPressed())
        elif event.button.id == "next":
            config = self._get_port_mappings()
            self.save_configuration()
            self.post_message(self.ConfigReady(config))
        elif event.button.id == "add_port":
            self._add_port_mapping()
    
    def _update_port_settings_visibility(self) -> None:
        """Show/hide port settings based on enabled state."""
        port_enabled = self.query_one("#port_enabled", RadioSet)
        port_settings = self.query_one("#port_settings")
        
        # Check if "Yes" button is pressed by looking at first RadioButton ("Yes")
        yes_button = cast(RadioButton, port_enabled.query_one("RadioButton"))  # First button is "Yes"
        is_enabled = yes_button.value if yes_button else False
        port_settings.display = is_enabled
    
    def _add_port_mapping(self) -> None:
        """Add a new port mapping from the input field."""
        port_input = self.query_one("#port_input", Input)
        mapping = port_input.value.strip()
        
        if not mapping:
            # Empty input - user wants to finish
            return
        
        # Validate the port mapping
        is_valid, error_msg = validate_port_mapping(mapping)
        if not is_valid:
            self.notify(error_msg, severity="error")
            return
        
        # Check for duplicates
        if mapping in self.current_mappings:
            self.notify("Port mapping already exists", severity="warning")
            return
        
        # Check for conflicts with SSH port
        if mapping == self.ssh_port:
            self.notify("Port mapping conflicts with SSH port", severity="error")
            return
        
        # Add the mapping
        self.current_mappings.append(mapping)
        self._update_port_list()
        
        # Clear the input
        port_input.value = ""
        self.notify(f"Added port mapping: {mapping}", severity="information")
    
    def _update_port_list(self) -> None:
        """Update the port mappings list display."""
        port_list = self.query_one("#port_list", ListView)
        port_list.clear()
        
        # Add SSH port (read-only)
        port_list.append(ListItem(Label(f"• {self.ssh_port} (SSH)")))
        
        # Add user-configured ports
        for mapping in self.current_mappings:
            item = ListItem(Label(f"• {mapping}"))
            port_list.append(item)
    
    def _get_port_mappings(self) -> list[str]:
        """Get the current port mappings."""
        port_enabled = self.query_one("#port_enabled", RadioSet)
        
        yes_button = cast(RadioButton, port_enabled.query_one("RadioButton"))  # First button is "Yes"
        if not (yes_button and yes_button.value):
            return []
        
        return self.current_mappings.copy()
    
    class ConfigReady(Message):
        """Message sent when configuration is ready."""
        
        def __init__(self, mappings: list[str]) -> None:
            super().__init__()
            self.mappings = mappings
    
    class BackPressed(Message):
        """Message sent when back button is pressed."""
        pass