"""Custom Scripts Configuration Screen for Simple Mode Wizard."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Input, Button, RadioButton, RadioSet, ListView, ListItem, Label
from textual.screen import Screen
from textual.message import Message
from typing import Dict, List, cast

from ...models.config import ProjectConfig


class CustomScriptsScreen(Screen):
    """Screen for configuring custom lifecycle scripts."""
    
    CSS = """
    CustomScriptsScreen {
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
    
    .scripts-settings {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
    }
    
    .info-text {
        color: $text-muted;
        margin: 1 0;
    }
    
    .script-type-group {
        margin: 1 0;
    }
    
    .input-row {
        layout: horizontal;
        height: 3;
        align: stretch;
    }
    
    .script-input {
        width: 3fr;
    }
    
    .add-button {
        width: 1fr;
        margin-left: 1;
    }
    
    .scripts-list {
        height: 6;
        border: solid $accent;
        margin: 1 0;
    }
    
    .script-description {
        color: $success;
        text-style: italic;
        margin: 0 0 1 0;
    }
    """
    
    SCRIPT_TYPES = {
        "on_build": "Run during Docker image build",
        "on_first_run": "Run on first container startup",
        "on_every_run": "Run on every container startup", 
        "on_user_login": "Run when user logs in via SSH"
    }
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        
        # Extract current scripts from project config
        self.stage1_scripts = project_config.stage_1.custom_scripts or {}
        self.stage2_scripts = project_config.stage_2.custom_scripts or {}
        self.current_script_type = "on_build"
        
        # Initialize empty lists for script types
        for script_type in self.SCRIPT_TYPES.keys():
            if script_type not in self.stage1_scripts:
                self.stage1_scripts[script_type] = []
            if script_type not in self.stage2_scripts:
                self.stage2_scripts[script_type] = []
    
    def compose(self) -> ComposeResult:
        """Create the custom scripts configuration form."""
        yield Static("Custom Scripts                         Step 10 of 12", classes="header")
        
        with Container(classes="form-container"):
            yield Static("Configure custom lifecycle scripts:")
            
            # Stage-1 Scripts Section
            with Vertical(classes="form-row"):
                with RadioSet(id="stage1_enabled"):
                    yield RadioButton("Yes", value=self._has_stage1_scripts())
                    yield RadioButton("No", value=not self._has_stage1_scripts())
                yield Static("Stage-1 Custom Scripts:")
            
            with Container(classes="scripts-settings", id="stage1_settings"):
                yield Static("Script Type:")
                with RadioSet(id="script_type", classes="script-type-group"):
                    for script_id, description in self.SCRIPT_TYPES.items():
                        yield RadioButton(
                            f"{script_id:15} - {description}",
                            value=self.current_script_type == script_id,
                            id=f"type_{script_id}",
                            classes="script-description"
                        )
                
                with Vertical(classes="form-row"):
                    yield Static("Script Path (with optional arguments):")
                    with Horizontal(classes="input-row"):
                        yield Input(
                            placeholder="stage-1/custom/setup.sh --verbose",
                            id="script_input",
                            classes="script-input"
                        )
                        yield Button("Add Script", id="add_script", classes="add-button")
                
                yield Static(f"Current {self.current_script_type} scripts:", id="current_scripts_label")
                with ScrollableContainer(classes="scripts-list"):
                    yield ListView(id="scripts_list")
                
                yield Static(
                    "Press Enter with empty path to switch script types",
                    classes="info-text"
                )
            
            # Stage-2 Scripts Section
            with Vertical(classes="form-row"):
                with RadioSet(id="stage2_enabled"):
                    yield RadioButton("Yes", value=self._has_stage2_scripts())
                    yield RadioButton("No", value=not self._has_stage2_scripts())
                yield Static("Stage-2 Custom Scripts:")
        
        with Horizontal(classes="button-bar"):
            yield Button("Prev", id="prev", variant="default")
            yield Button("Next", id="next", variant="primary")
    
    def on_mount(self) -> None:
        """Set up initial state when screen is mounted."""
        self._update_stage1_settings_visibility()
        self._update_scripts_list()
        
        # Set initial radio button selections - already handled by value parameters in compose()
        # RadioButton values are set during compose() based on existing scripts
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button changes."""
        if event.radio_set.id == "stage1_enabled":
            self._update_stage1_settings_visibility()
            if event.pressed and event.pressed.label == "No":
                # Clear all stage-1 scripts
                for script_type in self.stage1_scripts:
                    self.stage1_scripts[script_type].clear()
                self._update_scripts_list()
        elif event.radio_set.id == "stage2_enabled":
            if event.pressed and event.pressed.label == "No":
                # Clear all stage-2 scripts
                for script_type in self.stage2_scripts:
                    self.stage2_scripts[script_type].clear()
        elif event.radio_set.id == "script_type":
            pressed_id = event.pressed.id if event.pressed else None
            if pressed_id and pressed_id.startswith("type_"):
                self.current_script_type = pressed_id[5:]  # Remove "type_" prefix
                self._update_scripts_list()
                self._update_current_scripts_label()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "script_input":
            self._add_script()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "prev":
            self.post_message(self.BackPressed())
        elif event.button.id == "next":
            stage1_scripts, stage2_scripts = self._get_scripts_config()
            self.post_message(self.ConfigReady(stage1_scripts, stage2_scripts))
        elif event.button.id == "add_script":
            self._add_script()
    
    def _has_stage1_scripts(self) -> bool:
        """Check if there are any stage-1 scripts configured."""
        return any(scripts for scripts in self.stage1_scripts.values())
    
    def _has_stage2_scripts(self) -> bool:
        """Check if there are any stage-2 scripts configured."""
        return any(scripts for scripts in self.stage2_scripts.values())
    
    def _update_stage1_settings_visibility(self) -> None:
        """Show/hide stage-1 settings based on enabled state."""
        stage1_enabled = self.query_one("#stage1_enabled", RadioSet)
        stage1_settings = self.query_one("#stage1_settings")
        
        # Check if "Yes" button is pressed by looking at first RadioButton ("Yes")
        stage1_yes_button = cast(RadioButton, stage1_enabled.query_one("RadioButton"))  # First button is "Yes"
        is_enabled = stage1_yes_button.value if stage1_yes_button else False
        stage1_settings.display = is_enabled
    
    def _add_script(self) -> None:
        """Add a new script to the current script type."""
        script_input = self.query_one("#script_input", Input)
        script_path = script_input.value.strip()
        
        if not script_path:
            # Empty input - user wants to finish or switch types
            return
        
        # Basic validation
        if not script_path:
            self.notify("Script path is required", severity="error")
            return
        
        # Check for duplicates
        current_scripts = self.stage1_scripts[self.current_script_type]
        if script_path in current_scripts:
            self.notify("Script already exists for this type", severity="warning")
            return
        
        # Add the script
        current_scripts.append(script_path)
        self._update_scripts_list()
        
        # Clear the input
        script_input.value = ""
        self.notify(f"Added {self.current_script_type} script: {script_path}", severity="information")
    
    def _update_scripts_list(self) -> None:
        """Update the scripts list display for the current script type."""
        scripts_list = self.query_one("#scripts_list", ListView)
        scripts_list.clear()
        
        current_scripts = self.stage1_scripts[self.current_script_type]
        
        if not current_scripts:
            item = ListItem(Label(f"(No {self.current_script_type} scripts configured)"))
            scripts_list.append(item)
        else:
            for script in current_scripts:
                item = ListItem(Label(f"• {script}"))
                scripts_list.append(item)
    
    def _update_current_scripts_label(self) -> None:
        """Update the label showing current script type."""
        label = self.query_one("#current_scripts_label", Static)
        label.update(f"Current {self.current_script_type} scripts:")
    
    def _get_scripts_config(self) -> tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        """Get the current scripts configuration."""
        stage1_enabled = self.query_one("#stage1_enabled", RadioSet)
        stage2_enabled = self.query_one("#stage2_enabled", RadioSet)
        
        stage1 = {}
        stage2 = {}
        
        stage1_yes_button = cast(RadioButton, stage1_enabled.query_one("RadioButton"))  # First button is "Yes"
        if stage1_yes_button and stage1_yes_button.value:
            # Only include script types that have scripts
            for script_type, scripts in self.stage1_scripts.items():
                if scripts:
                    stage1[script_type] = scripts.copy()
        
        stage2_yes_button = cast(RadioButton, stage2_enabled.query_one("RadioButton"))  # First button is "Yes"
        if stage2_yes_button and stage2_yes_button.value:
            # Only include script types that have scripts
            for script_type, scripts in self.stage2_scripts.items():
                if scripts:
                    stage2[script_type] = scripts.copy()
        
        return stage1, stage2
    
    def save_configuration(self) -> None:
        """Save current scripts configuration to project config."""
        stage1_scripts, stage2_scripts = self._get_scripts_config()
        self.project_config.stage_1.custom_scripts = stage1_scripts
        self.project_config.stage_2.custom_scripts = stage2_scripts
    
    def handle_escape(self) -> None:
        """Handle escape key press - clear current input."""
        try:
            script_input = self.query_one("#script_input", Input)
            script_input.value = ""
        except:
            pass  # Input might not exist or be visible
    
    class ConfigReady(Message):
        """Message sent when configuration is ready."""
        
        def __init__(self, stage1_scripts: Dict[str, List[str]], stage2_scripts: Dict[str, List[str]]) -> None:
            super().__init__()
            self.stage1_scripts = stage1_scripts
            self.stage2_scripts = stage2_scripts
    
    class BackPressed(Message):
        """Message sent when back button is pressed."""
        pass