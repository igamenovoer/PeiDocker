"""Configuration summary screen for simple mode wizard."""

import yaml
from pathlib import Path
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ...app import PeiDockerApp

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
                
                # Proxy configuration
                with Static(classes="section"):
                    yield Label("Proxy Configuration", classes="section-title")
                    if hasattr(self.project_config.stage_1, 'proxy') and self.project_config.stage_1.proxy.enable:
                        proxy = self.project_config.stage_1.proxy
                        yield Label(f"✓ Enabled (port {proxy.port})", classes="config-item")
                        usage = "build-time only" if proxy.build_only else "build and runtime"
                        yield Label(f"Usage: {usage}", classes="config-item")
                    else:
                        yield Label("✗ Disabled", classes="config-item")
                
                # APT configuration  
                with Static(classes="section"):
                    yield Label("APT Configuration", classes="section-title")
                    apt_mirror = getattr(self.project_config.stage_1, 'apt_mirror', 'default')
                    yield Label(f"Mirror: {apt_mirror}", classes="config-item")
                
                # Port mappings
                with Static(classes="section"):
                    yield Label("Port Mappings", classes="section-title")
                    additional_ports = getattr(self.project_config.stage_1, 'ports', [])
                    if additional_ports:
                        for port in additional_ports:
                            yield Label(f"• {port}", classes="config-item")
                    else:
                        yield Label("No additional ports configured", classes="config-item")
                
                # Environment variables
                with Static(classes="section"):
                    yield Label("Environment Variables", classes="section-title")
                    env_vars = getattr(self.project_config.stage_1, 'environment', [])
                    if env_vars:
                        for var in env_vars:
                            yield Label(f"• {var}", classes="config-item")
                    else:
                        yield Label("No environment variables configured", classes="config-item")
                
                # Device configuration
                with Static(classes="section"):
                    yield Label("Device Configuration", classes="section-title")
                    if hasattr(self.project_config.stage_1, 'device') and self.project_config.stage_1.device.device_type == 'gpu':
                        yield Label("✓ GPU Support enabled", classes="config-item")
                    else:
                        yield Label("✗ GPU Support disabled", classes="config-item")
                
                # Mounts configuration
                with Static(classes="section"):
                    yield Label("Additional Mounts", classes="section-title")
                    stage1_mounts = getattr(self.project_config.stage_1, 'mounts', [])
                    stage2_mounts = getattr(self.project_config.stage_2, 'mounts', [])
                    
                    if stage1_mounts:
                        yield Label("Stage-1 mounts:", classes="config-item")
                        for mount in stage1_mounts:
                            if mount.type == "auto-volume":
                                yield Label(f"  • {mount.dst} (auto volume)", classes="config-item")
                            else:
                                yield Label(f"  • {mount.src} → {mount.dst} ({mount.type})", classes="config-item")
                    
                    if stage2_mounts:
                        yield Label("Stage-2 mounts:", classes="config-item")
                        for mount in stage2_mounts:
                            if mount.type == "auto-volume":
                                yield Label(f"  • {mount.dst} (auto volume)", classes="config-item")
                            else:
                                yield Label(f"  • {mount.src} → {mount.dst} ({mount.type})", classes="config-item")
                    
                    if not stage1_mounts and not stage2_mounts:
                        yield Label("No additional mounts configured", classes="config-item")
                
                # Entry point configuration
                with Static(classes="section"):
                    yield Label("Custom Entry Points", classes="section-title")
                    stage1_entrypoint = getattr(self.project_config.stage_1, 'custom_entry', '')
                    stage2_entrypoint = getattr(self.project_config.stage_2, 'custom_entry', '')
                    
                    if stage1_entrypoint:
                        yield Label(f"Stage-1: {stage1_entrypoint}", classes="config-item")
                    if stage2_entrypoint:
                        yield Label(f"Stage-2: {stage2_entrypoint}", classes="config-item")
                    if not stage1_entrypoint and not stage2_entrypoint:
                        yield Label("No custom entry points configured", classes="config-item")
                
                # Custom scripts configuration
                with Static(classes="section"):
                    yield Label("Custom Scripts", classes="section-title")
                    stage1_scripts = getattr(self.project_config.stage_1, 'custom_scripts', {})
                    stage2_scripts = getattr(self.project_config.stage_2, 'custom_scripts', {})
                    
                    has_scripts = False
                    if stage1_scripts:
                        for script_type, scripts in stage1_scripts.items():
                            if scripts:
                                yield Label(f"Stage-1 {script_type}:", classes="config-item")
                                for script in scripts:
                                    yield Label(f"  • {script}", classes="config-item")
                                has_scripts = True
                    
                    if stage2_scripts:
                        for script_type, scripts in stage2_scripts.items():
                            if scripts:
                                yield Label(f"Stage-2 {script_type}:", classes="config-item")
                                for script in scripts:
                                    yield Label(f"  • {script}", classes="config-item")
                                has_scripts = True
                    
                    if not has_scripts:
                        yield Label("No custom scripts configured", classes="config-item")
                
                # Configuration preview
                with Static(classes="section"):
                    yield Label("Generated Configuration Preview", classes="section-title")
                    config_yaml = self._generate_config_yaml()
                    yield Static(config_yaml, classes="yaml-preview")
                
                # Actions
                with Horizontal(classes="actions"):
                    yield Button("Prev", id="prev", variant="default")
                    yield Button("Save", id="save", variant="success")
                    yield Button("Cancel", id="cancel", variant="default")
                
                yield Label("Save creates user_config.yml in project directory & stays here", classes="save-info")
                yield Label("Continue navigating back/forth and save again as needed", classes="save-info")
    
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
    
    @on(Button.Pressed, "#prev")
    def on_prev_pressed(self) -> None:
        """Prev button pressed."""
        self.action_back()
    
    @on(Button.Pressed, "#save")
    def on_save_pressed(self) -> None:
        """Save button pressed - save and remain on page."""
        if self.save_configuration():
            self.notify("Configuration saved successfully! You can continue making changes.", severity="information")
        else:
            self.notify("Failed to save configuration", severity="error")
    
    @on(Button.Pressed, "#cancel")
    def on_cancel_pressed(self) -> None:
        """Cancel button pressed."""
        # Return to startup screen (main menu)
        cast('PeiDockerApp', self.app).action_quit_app()
    
    def save_configuration(self) -> bool:
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
            success = save_user_config(config_dict, str(config_path))
            
            if success:
                # Refresh the YAML preview to show saved content
                self.refresh()
            
            return success
        
        except Exception as e:
            self.log.error(f"Failed to save configuration: {e}")
            return False
    
    def handle_escape(self) -> None:
        """Handle escape key press - no special action for final screen."""
        pass  # Summary screen doesn't need special escape handling
    
    def is_valid(self) -> bool:
        """Check if the configuration is valid for saving."""
        # Summary screen is always valid if we got here
        return bool(self.project_config.project_name and self.project_config.project_dir)
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()