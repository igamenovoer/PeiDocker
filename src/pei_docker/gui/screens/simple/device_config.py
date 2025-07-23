"""Device Configuration Screen for Simple Mode Wizard."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, RadioButton, RadioSet
from typing import cast
from textual.screen import Screen
from textual.message import Message

from ...models.config import ProjectConfig, DeviceConfig


class DeviceConfigScreen(Screen):
    """Screen for configuring hardware device access."""
    
    CSS = """
    DeviceConfigScreen {
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
    
    .gpu-info {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
    }
    
    .warning-text {
        color: $warning;
        text-style: bold;
        margin: 0 0 1 0;
    }
    
    .info-text {
        color: $text-muted;
        margin: 1 0;
    }
    
    .requirements-list {
        color: $text;
        margin: 1 0;
    }
    
    .recommendations {
        color: $success;
        margin: 1 0;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        
        # Extract current device config from project config
        self.current_config = project_config.stage_1.device or DeviceConfig()
        
    def compose(self) -> ComposeResult:
        """Create the device configuration form."""
        yield Static("Device Configuration                   Step 7 of 12", classes="header")
        
        with Container(classes="form-container"):
            yield Static("Configure hardware device access:")
            
            with Vertical(classes="form-row"):
                with RadioSet(id="gpu_enabled"):
                    gpu_enabled = self.current_config.device_type == "gpu"
                    yield RadioButton("Yes", value=gpu_enabled)
                    yield RadioButton("No", value=not gpu_enabled)
                yield Static("Enable GPU Support:")
            
            with Container(classes="gpu-info"):
                yield Static("⚠ GPU support requires:", classes="warning-text")
                
                with Vertical(classes="requirements-list"):
                    yield Static("  • NVIDIA Docker runtime")
                    yield Static("  • Compatible GPU drivers")
                    yield Static("  • CUDA-compatible base image")
                
                yield Static(
                    "We do not detect GPU availability automatically.\n"
                    "Enable this only if you have the required setup.",
                    classes="info-text"
                )
                
                yield Static("Recommended base images for GPU:", classes="recommendations")
                with Vertical(classes="requirements-list"):
                    yield Static("• nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04")
                    yield Static("• nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04")
        
        with Horizontal(classes="button-bar"):
            yield Button("Prev", id="prev", variant="default")
            yield Button("Next", id="next", variant="primary")
    
    def on_mount(self) -> None:
        """Set up initial state when screen is mounted."""
        # Set initial radio button selection
        gpu_enabled = self.query_one("#gpu_enabled", RadioSet)
        # Set initial radio button selection - already handled by value parameters in compose()
    
    def _get_config(self) -> DeviceConfig:
        """Get the current configuration from form."""
        gpu_enabled = self.query_one("#gpu_enabled", RadioSet)
        
        # Check if "Yes" button is pressed by looking at first RadioButton ("Yes")
        yes_button = cast(RadioButton, gpu_enabled.query_one("RadioButton"))  # First button is "Yes"
        gpu_value = yes_button.value if yes_button else False
        
        device_type = "gpu" if gpu_value else "cpu"
        return DeviceConfig(
            device_type=device_type
        )
    
    def save_configuration(self) -> None:
        """Save current device configuration to project config."""
        config = self._get_config()
        self.project_config.stage_1.device = config
    
    def handle_escape(self) -> None:
        """Handle escape key press - no inputs to clear in this screen."""
        pass  # Device config screen has no text inputs to clear
    
    class ConfigReady(Message):
        """Message sent when configuration is ready."""
        
        def __init__(self, config: DeviceConfig) -> None:
            super().__init__()
            self.config = config
    
    class BackPressed(Message):
        """Message sent when back button is pressed."""
        pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "prev":
            self.post_message(self.BackPressed())
        elif event.button.id == "next":
            config = self._get_config()
            self.post_message(self.ConfigReady(config))