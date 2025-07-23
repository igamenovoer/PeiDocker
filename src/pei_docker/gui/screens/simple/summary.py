"""Configuration summary screen for simple mode wizard."""

import yaml
from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Label, Button, Static

from ...models.config import ProjectConfig
from ...utils.file_utils import save_user_config


class SummaryScreen(Screen[None]):
    """Screen for reviewing and saving the configuration."""
    
    DEFAULT_CSS = """
    SummaryScreen {
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
    
    .config-item {
        margin: 0 1;
        color: $text;
    }
    
    .config-group {
        margin: 1 0;
        padding: 1;
        border: solid $secondary;
        background: $surface-lighten-2;
    }
    
    .config-group-title {
        color: $primary;
        text-style: bold;
    }
    
    .actions {
        margin: 2 0;
    }
    
    .save-info {
        color: $text-muted;
        margin: 1 0;
        text-align: center;
    }
    
    .yaml-preview {
        background: $surface-darken-1;
        color: $text;
        padding: 1;
        margin: 1 0;
        border: solid $secondary;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
    
    def compose(self) -> ComposeResult:
        """Compose the summary screen."""
        with ScrollableContainer():
            with Vertical():
                yield Label("Review your configuration:", classes="section-title")
                
                # Project settings
                with Static(classes="section"):
                    yield Label("Project Settings", classes="section-title")
                    yield Label(f"Name: {self.project_config.project_name}", classes="config-item")
                    yield Label(f"Base Image: {self.project_config.stage_1.base_image}", classes="config-item")
                    yield Label(f"Output Directory: {self.project_config.project_dir}", classes="config-item")
                
                # SSH configuration
                if self.project_config.stage_1.ssh.enable:
                    with Static(classes="section"):
                        yield Label("SSH Configuration", classes="section-title")
                        ssh_config = self.project_config.stage_1.ssh
                        yield Label(f"✓ Enabled (port {ssh_config.host_port}:{ssh_config.port})", classes="config-item")
                        
                        if ssh_config.users:
                            user = ssh_config.users[0]
                            auth_methods = ["password"]
                            if user.pubkey_text:
                                auth_methods.append("public key")
                            if user.privkey_file:
                                auth_methods.append("private key")
                            yield Label(f"User: {user.name} ({', '.join(auth_methods)} auth)", classes="config-item")
                        
                        if ssh_config.root_enabled:
                            yield Label("Root access: enabled", classes="config-item")
                        else:
                            yield Label("Root access: disabled", classes="config-item")
                else:
                    with Static(classes="section"):
                        yield Label("SSH Configuration", classes="section-title")
                        yield Label("✗ Disabled", classes="config-item")
                
                # Additional configuration (placeholder for other wizard steps)
                with Static(classes="section"):
                    yield Label("Additional Configuration", classes="section-title")
                    yield Label("Proxy: disabled", classes="config-item")
                    yield Label("APT Mirror: default", classes="config-item")
                    yield Label("GPU Support: disabled", classes="config-item")
                    yield Label("Additional ports: none", classes="config-item")
                    yield Label("Environment variables: none", classes="config-item")
                
                # Configuration preview
                with Static(classes="section"):
                    yield Label("Generated Configuration Preview", classes="section-title")
                    config_yaml = self._generate_config_yaml()
                    yield Static(config_yaml, classes="yaml-preview")
                
                # Actions
                with Horizontal(classes="actions"):
                    yield Button("Back", id="back", variant="default")
                    yield Button("Save & Exit", id="save_exit", variant="success")
                    yield Button("Save & Configure More", id="save_continue", variant="primary")
                
                yield Label("Save actions will create user_config.yml in project directory", classes="save-info")
    
    def _generate_config_yaml(self) -> str:
        """Generate YAML preview of the configuration."""
        try:
            config_dict = self.project_config.to_user_config_dict()
            
            # Set the output image names if not already set
            if not self.project_config.stage_1.output_image:
                config_dict["stage_1"]["image"]["output"] = f"{self.project_config.project_name}:stage-1"
            
            return yaml.dump(config_dict, default_flow_style=False, indent=2)
        except Exception as e:
            return f"Error generating configuration: {e}"
    
    @on(Button.Pressed, "#back")
    def on_back_pressed(self) -> None:
        """Back button pressed."""
        self.action_back()
    
    @on(Button.Pressed, "#save_exit")
    def on_save_exit_pressed(self) -> None:
        """Save and exit button pressed."""
        if self._save_configuration():
            self.notify("Configuration saved successfully!", severity="information")
            self.app.action_quit_app()
        else:
            self.notify("Failed to save configuration", severity="error")
    
    @on(Button.Pressed, "#save_continue")
    def on_save_continue_pressed(self) -> None:
        """Save and configure more button pressed."""
        if self._save_configuration():
            self.notify("Configuration saved! You can now edit the config file directly.", severity="information")
            self.app.action_quit_app()
        else:
            self.notify("Failed to save configuration", severity="error")
    
    def _save_configuration(self) -> bool:
        """Save the configuration to user_config.yml."""
        try:
            # Ensure output image names are set
            if not self.project_config.stage_1.output_image:
                self.project_config.stage_1.output_image = f"{self.project_config.project_name}:stage-1"
            
            if not self.project_config.stage_2.output_image:
                self.project_config.stage_2.output_image = f"{self.project_config.project_name}:stage-2"
            
            # Generate configuration dictionary
            config_dict = self.project_config.to_user_config_dict()
            
            # Save to file
            config_path = Path(self.project_config.project_dir) / "user_config.yml"
            return save_user_config(config_dict, str(config_path))
        
        except Exception as e:
            self.log.error(f"Failed to save configuration: {e}")
            return False
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()