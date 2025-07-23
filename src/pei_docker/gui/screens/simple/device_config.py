"""Device Configuration Screen for Simple Mode Wizard."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, RadioButton, RadioSet
from textual.screen import Screen
from textual.message import Message

from ...models.config import DeviceConfig


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
    
    def __init__(self, current_config: DeviceConfig = None):
        super().__init__()
        self.current_config = current_config or DeviceConfig()
        
    def compose(self) -> ComposeResult:
        """Create the device configuration form."""
        yield Static("Device Configuration                   Step 7 of 12", classes="header")
        
        with Container(classes="form-container"):
            yield Static("Configure hardware device access:")
            
            with Vertical(classes="form-row"):
                with RadioSet(id="gpu_enabled"):
                    yield RadioButton("Yes", value=self.current_config.gpu)
                    yield RadioButton("No", value=not self.current_config.gpu)
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
            yield Button("Back", id="back", variant="default")
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
        yes_button = gpu_enabled.query_one("RadioButton")  # First button is "Yes"
        gpu_value = yes_button.value if yes_button else False
        
        return DeviceConfig(
            gpu=gpu_value
        )
    
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
        if event.button.id == "back":
            self.post_message(self.BackPressed())
        elif event.button.id == "next":
            config = self._get_config()
            self.post_message(self.ConfigReady(config))