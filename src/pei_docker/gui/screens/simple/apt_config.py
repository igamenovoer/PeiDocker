"""APT Repository Configuration Screen for Simple Mode Wizard."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, RadioButton, RadioSet
from textual.screen import Screen
from textual.message import Message
from typing import cast

from ...models.config import ProjectConfig


class APTConfigScreen(Screen):
    """Screen for configuring APT repository mirrors."""
    
    CSS = """
    APTConfigScreen {
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
    
    .mirror-settings {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
    }
    
    .info-text {
        color: $text-muted;
        margin: 1 0;
    }
    
    .mirror-option {
        margin: 0 0 1 0;
    }
    """
    
    MIRROR_OPTIONS = {
        "default": "Ubuntu Default (no change)",
        "tuna": "Tsinghua University (China)",
        "aliyun": "Alibaba Cloud (China)", 
        "163": "NetEase (China)",
        "ustc": "University of Science and Technology (China)",
        "cn": "Ubuntu Official China Mirror"
    }
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        
        # Extract current APT mirror from project config
        self.current_mirror = project_config.stage_1.apt_mirror or "default"
        
    def compose(self) -> ComposeResult:
        """Create the APT configuration form."""
        yield Static("APT Repository Configuration            Step 4 of 12", classes="header")
        
        with Container(classes="form-container"):
            yield Static("Choose APT repository mirror for faster package downloads:")
            
            with Vertical(classes="form-row"):
                with RadioSet(id="mirror_enabled"):
                    yield RadioButton("Yes", value=self.current_mirror != "default")
                    yield RadioButton("No", value=self.current_mirror == "default")
                yield Static("Use Custom Mirror:")
            
            with Container(classes="mirror-settings", id="mirror_settings"):
                yield Static("Available mirrors:", classes="info-text")
                
                with RadioSet(id="mirror_selection"):
                    for mirror_id, description in self.MIRROR_OPTIONS.items():
                        yield RadioButton(
                            f"{mirror_id:8} - {description}",
                            value=self.current_mirror == mirror_id,
                            id=f"mirror_{mirror_id}",
                            classes="mirror-option"
                        )
                
                yield Static(
                    "Selected mirror provides faster downloads for users\n"
                    "in specific geographic regions.",
                    classes="info-text"
                )
        
        with Horizontal(classes="button-bar"):
            yield Button("Prev", id="prev", variant="default")
            yield Button("Next", id="next", variant="primary")
    
    def on_mount(self) -> None:
        """Set up initial state when screen is mounted."""
        self._update_mirror_settings_visibility()
        
        # Set initial radio button selections - already handled by value parameters in compose()
        # RadioButton values are set during compose() based on current_mirror
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button changes."""
        if event.radio_set.id == "mirror_enabled":
            self._update_mirror_settings_visibility()
            
            # If disabling custom mirror, reset to default
            if event.pressed and event.pressed.label == "No":
                # Reset to default mirror by setting the default radio button
                default_button = self.query_one("#mirror_default", RadioButton)
                default_button.value = True
    
    def _update_mirror_settings_visibility(self) -> None:
        """Show/hide mirror settings based on enabled state."""
        mirror_enabled = self.query_one("#mirror_enabled", RadioSet)
        mirror_settings = self.query_one("#mirror_settings")
        
        # Check if "Yes" button is pressed by looking at first RadioButton ("Yes")
        yes_button = cast(RadioButton, mirror_enabled.query_one("RadioButton"))  # First button is "Yes"
        is_enabled = yes_button.value if yes_button else False
        mirror_settings.display = is_enabled
    
    def _get_selected_mirror(self) -> str:
        """Get the currently selected mirror."""
        mirror_enabled = self.query_one("#mirror_enabled", RadioSet)
        
        yes_button = cast(RadioButton, mirror_enabled.query_one("RadioButton"))  # First button is "Yes"
        if not (yes_button and yes_button.value):
            return "default"
        
        mirror_selection = self.query_one("#mirror_selection", RadioSet)
        # Find which mirror button is selected
        pressed_id = None
        for button in mirror_selection.query("RadioButton"):
            radio_button = cast(RadioButton, button)
            if radio_button.value:
                pressed_id = radio_button.id
                break
        
        if pressed_id and pressed_id.startswith("mirror_"):
            return pressed_id[7:]  # Remove "mirror_" prefix
        
        return "default"
    
    def save_configuration(self) -> None:
        """Save current APT mirror configuration to project config."""
        selected_mirror = self._get_selected_mirror()
        self.project_config.stage_1.apt_mirror = selected_mirror
    
    def handle_escape(self) -> None:
        """Handle escape key press - no inputs to clear in this screen."""
        pass  # APT config screen has no text inputs to clear
    
    class ConfigReady(Message):
        """Message sent when configuration is ready."""
        
        def __init__(self, mirror: str) -> None:
            super().__init__()
            self.mirror = mirror
    
    class BackPressed(Message):
        """Message sent when back button is pressed."""
        pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "prev":
            self.post_message(self.BackPressed())
        elif event.button.id == "next":
            selected_mirror = self._get_selected_mirror()
            self.post_message(self.ConfigReady(selected_mirror))