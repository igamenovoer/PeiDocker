"""Custom Entry Point Configuration Screen for Simple Mode Wizard."""

from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, Button, RadioButton, RadioSet
from textual.screen import Screen
from textual.message import Message
from typing import cast
import os

from textual_fspicker import FileOpen

from ...models.config import ProjectConfig
from ...utils.file_utils import validate_file_path
from ...widgets.dialogs import ErrorDialog


class EntryPointScreen(Screen):
    """Screen for configuring custom entry point scripts."""
    
    CSS = """
    EntryPointScreen {
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
    
    .entry-settings {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
    }
    
    .warning-text {
        color: $warning;
        text-style: bold;
        margin: 1 0;
    }
    
    .info-text {
        color: $text-muted;
        margin: 1 0;
    }
    
    .input-group {
        margin: 1 0;
    }
    
    .file-input-row {
        layout: horizontal;
        height: 3;
        align: stretch;
    }
    
    .file-input {
        width: 3fr;
    }
    
    .browse-button {
        width: 1fr;
        margin-left: 1;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        
        # Extract current entry points from project config
        self.stage1_entrypoint = project_config.stage_1.custom_entry or ""
        self.stage2_entrypoint = project_config.stage_2.custom_entry or ""
        
    def compose(self) -> ComposeResult:
        """Create the entry point configuration form."""
        yield Static("Custom Entry Point                     Step 9 of 12", classes="header")
        
        with Container(classes="form-container"):
            yield Static("Configure custom entry point scripts:")
            
            # Stage-1 Entry Point Section
            with Vertical(classes="form-row"):
                with RadioSet(id="stage1_enabled"):
                    yield RadioButton("Yes", value=bool(self.stage1_entrypoint))
                    yield RadioButton("No", value=not bool(self.stage1_entrypoint))
                yield Static("Stage-1 Entry Point:")
            
            with Container(classes="entry-settings", id="stage1_settings"):
                with Vertical(classes="input-group"):
                    yield Static("Entry Point Script (.sh):")
                    with Horizontal(classes="file-input-row"):
                        yield Input(
                            placeholder="/path/to/my-entrypoint.sh",
                            value=self.stage1_entrypoint,
                            id="stage1_script",
                            classes="file-input"
                        )
                        yield Button("Browse...", id="browse_stage1", classes="browse-button")
                
                yield Static(
                    "Script will be copied to project directory and\n"
                    "executed when the container starts.",
                    classes="info-text"
                )
            
            # Stage-2 Entry Point Section
            with Vertical(classes="form-row"):
                with RadioSet(id="stage2_enabled"):
                    yield RadioButton("Yes", value=bool(self.stage2_entrypoint))
                    yield RadioButton("No", value=not bool(self.stage2_entrypoint))
                yield Static("Stage-2 Entry Point:")
            
            with Container(classes="entry-settings", id="stage2_settings"):
                with Vertical(classes="input-group"):
                    yield Static("Entry Point Script (.sh):")
                    with Horizontal(classes="file-input-row"):
                        yield Input(
                            placeholder="/path/to/my-entrypoint.sh",
                            value=self.stage2_entrypoint,
                            id="stage2_script",
                            classes="file-input"
                        )
                        yield Button("Browse...", id="browse_stage2", classes="browse-button")
            
            yield Static(
                "⚠ Stage-2 entry point will override Stage-1 entry point",
                classes="warning-text"
            )
        
        with Horizontal(classes="button-bar"):
            yield Button("Back", id="back", variant="default")
            yield Button("Next", id="next", variant="primary")
    
    def on_mount(self) -> None:
        """Set up initial state when screen is mounted."""
        self._update_settings_visibility()
        
        # Set initial radio button selections - already handled by value parameters in compose()
        # RadioButton values are set during compose() based on stage entrypoints
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button changes."""
        if event.radio_set.id in ["stage1_enabled", "stage2_enabled"]:
            self._update_settings_visibility()
            
            # Clear script path if disabling
            if event.pressed and event.pressed.label == "No":
                if event.radio_set.id == "stage1_enabled":
                    stage1_script = self.query_one("#stage1_script", Input)
                    stage1_script.value = ""
                elif event.radio_set.id == "stage2_enabled":
                    stage2_script = self.query_one("#stage2_script", Input)
                    stage2_script.value = ""
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back":
            self.post_message(self.BackPressed())
        elif event.button.id == "next":
            is_valid, error_msg = self._validate_form()
            if is_valid:
                stage1_entrypoint, stage2_entrypoint = self._get_entry_point_config()
                self.post_message(self.ConfigReady(stage1_entrypoint, stage2_entrypoint))
            else:
                self.notify(error_msg, severity="error")
        elif event.button.id == "browse_stage1":
            self._browse_script_file("stage1_script")
        elif event.button.id == "browse_stage2":
            self._browse_script_file("stage2_script")
    
    def _update_settings_visibility(self) -> None:
        """Show/hide settings based on enabled state."""
        stage1_enabled = self.query_one("#stage1_enabled", RadioSet)
        stage1_settings = self.query_one("#stage1_settings")
        
        stage2_enabled = self.query_one("#stage2_enabled", RadioSet)
        stage2_settings = self.query_one("#stage2_settings")
        
        # Check if "Yes" button is pressed by looking at first RadioButton ("Yes")
        stage1_yes_button = cast(RadioButton, stage1_enabled.query_one("RadioButton"))  # First button is "Yes"
        stage1_is_enabled = stage1_yes_button.value if stage1_yes_button else False
        stage1_settings.display = stage1_is_enabled
        
        stage2_yes_button = cast(RadioButton, stage2_enabled.query_one("RadioButton"))  # First button is "Yes" 
        stage2_is_enabled = stage2_yes_button.value if stage2_yes_button else False
        stage2_settings.display = stage2_is_enabled
    
    def _browse_script_file(self, input_id: str) -> None:
        """Browse for script file using file picker."""
        # Launch file picker using async worker
        self.run_worker(self._browse_script_file_async(input_id))

    async def _browse_script_file_async(self, input_id: str) -> None:
        """Async worker to handle script file browsing."""
        file_path = await self.app.push_screen_wait(FileOpen())
        if file_path:
            script_input = self.query_one(f"#{input_id}", Input)
            script_input.value = str(file_path)
    
    def _validate_form(self) -> tuple[bool, str]:
        """Validate the form data."""
        stage1_enabled = self.query_one("#stage1_enabled", RadioSet)
        stage2_enabled = self.query_one("#stage2_enabled", RadioSet)
        
        stage1_yes_button = cast(RadioButton, stage1_enabled.query_one("RadioButton"))  # First button is "Yes"
        if stage1_yes_button and stage1_yes_button.value:
            stage1_script = self.query_one("#stage1_script", Input)
            script_path = stage1_script.value.strip()
            
            if not script_path:
                return False, "Stage-1 entry point script path is required"
            
            if not script_path.endswith('.sh'):
                return False, "Stage-1 entry point script must be a .sh file"
            
            # Validate file exists (if it's an absolute path)
            if os.path.isabs(script_path) and not os.path.exists(script_path):
                return False, f"Stage-1 entry point script not found: {script_path}"
        
        stage2_yes_button = cast(RadioButton, stage2_enabled.query_one("RadioButton"))  # First button is "Yes"
        if stage2_yes_button and stage2_yes_button.value:
            stage2_script = self.query_one("#stage2_script", Input)
            script_path = stage2_script.value.strip()
            
            if not script_path:
                return False, "Stage-2 entry point script path is required"
            
            if not script_path.endswith('.sh'):
                return False, "Stage-2 entry point script must be a .sh file"
            
            # Validate file exists (if it's an absolute path)
            if os.path.isabs(script_path) and not os.path.exists(script_path):
                return False, f"Stage-2 entry point script not found: {script_path}"
        
        return True, ""
    
    def _get_entry_point_config(self) -> tuple[str, str]:
        """Get the current entry point configuration."""
        stage1_enabled = self.query_one("#stage1_enabled", RadioSet)
        stage2_enabled = self.query_one("#stage2_enabled", RadioSet)
        
        stage1_script = ""
        stage2_script = ""
        
        stage1_yes_button = cast(RadioButton, stage1_enabled.query_one("RadioButton"))  # First button is "Yes"
        if stage1_yes_button and stage1_yes_button.value:
            stage1_input = self.query_one("#stage1_script", Input)
            stage1_script = stage1_input.value.strip()
        
        stage2_yes_button = cast(RadioButton, stage2_enabled.query_one("RadioButton"))  # First button is "Yes"
        if stage2_yes_button and stage2_yes_button.value:
            stage2_input = self.query_one("#stage2_script", Input)
            stage2_script = stage2_input.value.strip()
        
        return stage1_script, stage2_script
    
    def save_configuration(self) -> None:
        """Save current entry point configuration to project config."""
        stage1_entrypoint, stage2_entrypoint = self._get_entry_point_config()
        self.project_config.stage_1.custom_entry = stage1_entrypoint
        self.project_config.stage_2.custom_entry = stage2_entrypoint
    
    class ConfigReady(Message):
        """Message sent when configuration is ready."""
        
        def __init__(self, stage1_entrypoint: str, stage2_entrypoint: str) -> None:
            super().__init__()
            self.stage1_entrypoint = stage1_entrypoint
            self.stage2_entrypoint = stage2_entrypoint
    
    class BackPressed(Message):
        """Message sent when back button is pressed."""
        pass