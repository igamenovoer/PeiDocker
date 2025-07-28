#!/usr/bin/env python3
"""
Direct SSH Widget Debug Test - Isolate the rendering issue

This script tests the SSH widget in complete isolation to diagnose
why the form fields aren't rendering properly.
"""

import sys
from pathlib import Path

# Add source path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from textual.app import App, ComposeResult
from textual.containers import Container

from pei_docker.gui.models.config import ProjectConfig
from pei_docker.gui.screens.simple.ssh_config import SSHConfigWidget


class SSHWidgetDebugApp(App):
    """Minimal app to test SSH widget in isolation."""
    
    def __init__(self):
        super().__init__()
        self.project_config = ProjectConfig()
        # Ensure SSH is enabled by default
        self.project_config.stage_1.ssh.enable = True
        print(f"App init: SSH enabled = {self.project_config.stage_1.ssh.enable}")
    
    def compose(self) -> ComposeResult:
        """Compose just the SSH widget with minimal container."""
        print("App compose: Creating SSH widget...")
        
        with Container():
            ssh_widget = SSHConfigWidget(self.project_config)
            print(f"App compose: SSH widget created, ssh_enabled = {ssh_widget.ssh_enabled}")
            yield ssh_widget
    
    async def on_mount(self) -> None:
        """Debug what gets mounted."""
        print("App mounted, checking widget tree...")
        
        # Query for various elements
        containers = self.query("Container")
        print(f"Found {len(containers)} Container elements")
        
        labels = self.query("Label")
        print(f"Found {len(labels)} Label elements")
        for i, label in enumerate(labels):
            print(f"  Label {i}: '{label.renderable}'")
        
        radio_sets = self.query("RadioSet")
        print(f"Found {len(radio_sets)} RadioSet elements")
        
        radio_buttons = self.query("RadioButton")
        print(f"Found {len(radio_buttons)} RadioButton elements")
        for i, radio in enumerate(radio_buttons):
            print(f"  RadioButton {i}: '{radio.label}' (value={radio.value})")
        
        inputs = self.query("Input")
        print(f"Found {len(inputs)} Input elements")
        for i, input_widget in enumerate(inputs):
            print(f"  Input {i}: id='{input_widget.id}', value='{input_widget.value}'")
        
        # Check SSH widget specifically
        ssh_widgets = self.query(SSHConfigWidget)
        if ssh_widgets:
            ssh_widget = ssh_widgets[0]
            print(f"SSH widget found: ssh_enabled = {ssh_widget.ssh_enabled}")
            print(f"SSH widget children: {len(ssh_widget.children)}")
            for i, child in enumerate(ssh_widget.children):
                print(f"  SSH Widget Child {i}: {type(child).__name__}")


if __name__ == "__main__":
    app = SSHWidgetDebugApp()
    app.run()