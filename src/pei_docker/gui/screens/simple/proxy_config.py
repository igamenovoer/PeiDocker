"""Proxy Configuration Screen for Simple Mode Wizard."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, Button, RadioButton, RadioSet
from textual.screen import Screen
from textual.message import Message

from ...models.config import ProxyConfig


class ProxyConfigScreen(Screen):
    """Screen for configuring HTTP proxy settings."""
    
    CSS = """
    ProxyConfigScreen {
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
    
    .proxy-settings {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
    }
    
    .info-text {
        color: $text-muted;
        margin: 0 0 1 0;
    }
    
    .preview-text {
        color: $success;
        margin: 1 0;
        text-style: italic;
    }
    """
    
    def __init__(self, current_config: ProxyConfig = None):
        super().__init__()
        self.current_config = current_config or ProxyConfig()
        
    def compose(self) -> ComposeResult:
        """Create the proxy configuration form."""
        yield Static("Proxy Configuration                    Step 3 of 12", classes="header")
        
        with Container(classes="form-container"):
            yield Static("Configure HTTP proxy for container networking:")
            
            with Vertical(classes="form-row"):
                with RadioSet(id="proxy_enabled"):
                    proxy_enabled = getattr(self.current_config, 'enable_globally', False) or False
                    yield RadioButton("Yes", value=proxy_enabled)
                    yield RadioButton("No", value=not proxy_enabled)
                yield Static("Use Proxy:")
            
            with Container(classes="proxy-settings", id="proxy_settings"):
                yield Static(
                    "This will set http_proxy and https_proxy environment\n"
                    "variables in the container.",
                    classes="info-text"
                )
                
                with Vertical(classes="form-row"):
                    yield Static("Proxy Port:")
                    yield Input(
                        placeholder="8080",
                        value=str(getattr(self.current_config, 'port', None) or 8080),
                        id="proxy_port"
                    )
                
                with Vertical(classes="form-row"):
                    yield Static("Proxy Usage:")
                    with RadioSet(id="proxy_usage"):
                        yield RadioButton(
                            "Build-time only (remove after build)",
                            value=getattr(self.current_config, 'remove_after_build', False),
                            id="build_only"
                        )
                        yield RadioButton(
                            "Build and runtime (persistent)",
                            value=not getattr(self.current_config, 'remove_after_build', False),
                            id="persistent"
                        )
                
                yield Static(
                    "Proxy URL will be: http://host.docker.internal:8080",
                    classes="preview-text",
                    id="proxy_preview"
                )
        
        with Horizontal(classes="button-bar"):
            yield Button("Back", id="back", variant="default")
            yield Button("Next", id="next", variant="primary")
    
    def on_mount(self) -> None:
        """Set up initial state when screen is mounted."""
        self._update_proxy_settings_visibility()
        self._update_proxy_preview()
        
        # Set initial radio button selections
        proxy_enabled = self.query_one("#proxy_enabled", RadioSet)
        proxy_enabled_val = getattr(self.current_config, 'enable_globally', False)
        # Note: RadioSet selection should be set via RadioButton values, not pressed attribute
        
        if proxy_enabled_val:
            proxy_usage = self.query_one("#proxy_usage", RadioSet)
            build_only_val = getattr(self.current_config, 'remove_after_build', False)
            # Note: RadioSet selection should be set via RadioButton values, not pressed attribute
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button changes."""
        if event.radio_set.id == "proxy_enabled":
            self._update_proxy_settings_visibility()
        self._update_proxy_preview()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes."""
        if event.input.id == "proxy_port":
            self._update_proxy_preview()
    
    def _update_proxy_settings_visibility(self) -> None:
        """Show/hide proxy settings based on enabled state."""
        proxy_enabled = self.query_one("#proxy_enabled", RadioSet)
        proxy_settings = self.query_one("#proxy_settings")
        
        # Check which radio button is pressed by looking at their values
        yes_button = proxy_enabled.query_one("RadioButton")  # First button is "Yes"
        is_enabled = yes_button.value if yes_button else False
        proxy_settings.display = is_enabled
    
    def _update_proxy_preview(self) -> None:
        """Update the proxy URL preview."""
        proxy_enabled = self.query_one("#proxy_enabled", RadioSet)
        yes_button = proxy_enabled.query_one("RadioButton")  # First button is "Yes"
        if not (yes_button and yes_button.value):
            return
            
        port_input = self.query_one("#proxy_port", Input)
        preview = self.query_one("#proxy_preview", Static)
        
        port = port_input.value or "8080"
        preview.update(f"Proxy URL will be: http://host.docker.internal:{port}")
    
    def _validate_form(self) -> tuple[bool, str]:
        """Validate the form data."""
        proxy_enabled = self.query_one("#proxy_enabled", RadioSet)
        
        yes_button = proxy_enabled.query_one("RadioButton")  # First button is "Yes"
        if yes_button and yes_button.value:
            port_input = self.query_one("#proxy_port", Input)
            port_str = port_input.value.strip()
            
            if not port_str:
                return False, "Proxy port is required when proxy is enabled"
            
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    return False, "Proxy port must be between 1 and 65535"
            except ValueError:
                return False, "Proxy port must be a valid number"
        
        return True, ""
    
    def _get_config(self) -> ProxyConfig:
        """Get the current configuration from form."""
        proxy_enabled = self.query_one("#proxy_enabled", RadioSet)
        yes_button = proxy_enabled.query_one("RadioButton")  # First button is "Yes"
        
        if not (yes_button and yes_button.value):
            return ProxyConfig(enabled=False)
        
        port_input = self.query_one("#proxy_port", Input)
        proxy_usage = self.query_one("#proxy_usage", RadioSet)
        
        port = int(port_input.value or "8080")
        build_only_button = proxy_usage.query_one("#build_only", RadioButton)
        build_only = build_only_button.value if build_only_button else False
        
        return ProxyConfig(
            enabled=True,
            port=port,
            build_only=build_only
        )
    
    class ConfigReady(Message):
        """Message sent when configuration is ready."""
        
        def __init__(self, config: ProxyConfig) -> None:
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
            is_valid, error_msg = self._validate_form()
            if is_valid:
                config = self._get_config()
                self.post_message(self.ConfigReady(config))
            else:
                self.notify(error_msg, severity="error")