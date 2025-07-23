"""Additional Mounts Configuration Screen for Simple Mode Wizard."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Static, Input, Button, RadioButton, RadioSet, ListView, ListItem, Label
from typing import cast
from textual.screen import Screen
from textual.message import Message

from ...models.config import ProjectConfig, MountConfig


class MountsScreen(Screen):
    """Screen for configuring additional volume mounts."""
    
    CSS = """
    MountsScreen {
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
    
    .mount-settings {
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
    
    .mount-form {
        margin: 1 0;
    }
    
    .input-group {
        margin: 0 0 1 0;
    }
    
    .mount-list {
        height: 6;
        border: solid $accent;
        margin: 1 0;
    }
    """
    
    MOUNT_TYPES = {
        "auto-volume": "Automatic Docker Volume",
        "manual-volume": "Manual Docker Volume", 
        "host-dir": "Host Directory",
        "done": "Done (finish mounting)"
    }
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        
        # Extract current mounts from project config (convert dict to list for GUI)
        self.stage1_mounts = list(project_config.stage_1.mounts.values()) if project_config.stage_1.mounts else []
        self.stage2_mounts = list(project_config.stage_2.mounts.values()) if project_config.stage_2.mounts else []
        self.current_mount_type = "auto-volume"
        
    def compose(self) -> ComposeResult:
        """Create the mounts configuration form."""
        yield Static("Additional Mounts                      Step 8 of 12", classes="header")
        
        with Container(classes="form-container"):
            yield Static("Configure additional volume mounts:")
            
            # Stage-1 Mounts Section
            with Vertical(classes="form-row"):
                with RadioSet(id="stage1_enabled"):
                    yield RadioButton("Yes", value=bool(self.stage1_mounts))
                    yield RadioButton("No", value=not bool(self.stage1_mounts))
                yield Static("Stage-1 Mounts:")
            
            with Container(classes="mount-settings", id="stage1_settings"):
                yield Static("Mount Type:")
                with RadioSet(id="mount_type"):
                    for mount_id, description in self.MOUNT_TYPES.items():
                        yield RadioButton(
                            description,
                            value=self.current_mount_type == mount_id,
                            id=f"type_{mount_id}"
                        )
                
                with Vertical(classes="mount-form", id="mount_form"):
                    with Vertical(classes="input-group"):
                        yield Static("Destination Path:")
                        yield Input(
                            placeholder="/app/data",
                            id="dest_path"
                        )
                    
                    with Vertical(classes="input-group", id="source_group"):
                        yield Static("Source (for manual volume/host directory):")
                        yield Input(
                            placeholder="my-data-volume",
                            id="source_path"
                        )
                    
                    yield Button("Add Mount", id="add_mount")
                
                yield Static("Current Stage-1 mounts:")
                with ScrollableContainer(classes="mount-list"):
                    yield ListView(id="stage1_list")
            
            # Stage-2 Mounts Section
            with Vertical(classes="form-row"):
                with RadioSet(id="stage2_enabled"):
                    yield RadioButton("Yes", value=bool(self.stage2_mounts))
                    yield RadioButton("No", value=not bool(self.stage2_mounts))
                yield Static("Stage-2 Mounts:")
            
            yield Static(
                "⚠ Stage-2 mounts will completely replace Stage-1 mounts",
                classes="warning-text"
            )
        
        with Horizontal(classes="button-bar"):
            yield Button("Back", id="back", variant="default")
            yield Button("Next", id="next", variant="primary")
    
    def on_mount(self) -> None:
        """Set up initial state when screen is mounted."""
        self._update_stage1_settings_visibility()
        self._update_mount_form_visibility()
        self._update_mount_lists()
        
        # Set initial radio button selections - already handled by value parameters in compose()
        # RadioButton values are set during compose() based on existing mounts
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button changes."""
        if event.radio_set.id == "stage1_enabled":
            self._update_stage1_settings_visibility()
            if event.pressed and event.pressed.label == "No":
                self.stage1_mounts.clear()
                self._update_mount_lists()
        elif event.radio_set.id == "stage2_enabled":
            if event.pressed and event.pressed.label == "No":
                self.stage2_mounts.clear()
        elif event.radio_set.id == "mount_type":
            pressed_id = event.pressed.id if event.pressed else None
            if pressed_id and pressed_id.startswith("type_"):
                self.current_mount_type = pressed_id[5:]  # Remove "type_" prefix
                self._update_mount_form_visibility()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "back":
            self.post_message(self.BackPressed())
        elif event.button.id == "next":
            stage1_mounts, stage2_mounts = self._get_mounts_config()
            self.post_message(self.ConfigReady(stage1_mounts, stage2_mounts))
        elif event.button.id == "add_mount":
            self._add_mount()
    
    def _update_stage1_settings_visibility(self) -> None:
        """Show/hide stage-1 settings based on enabled state."""
        stage1_enabled = self.query_one("#stage1_enabled", RadioSet)
        stage1_settings = self.query_one("#stage1_settings")
        
        # Check if "Yes" button is pressed by looking at first RadioButton ("Yes")
        stage1_yes_button = cast(RadioButton, stage1_enabled.query_one("RadioButton"))  # First button is "Yes"
        is_enabled = stage1_yes_button.value if stage1_yes_button else False
        stage1_settings.display = is_enabled
    
    def _update_mount_form_visibility(self) -> None:
        """Show/hide mount form fields based on mount type."""
        mount_form = self.query_one("#mount_form")
        source_group = self.query_one("#source_group")
        
        if self.current_mount_type == "done":
            mount_form.display = False
        else:
            mount_form.display = True
            # Show source field only for manual volume and host directory
            source_group.display = self.current_mount_type in ["manual-volume", "host-dir"]
    
    def _add_mount(self) -> None:
        """Add a new mount configuration."""
        if self.current_mount_type == "done":
            return
        
        dest_input = self.query_one("#dest_path", Input)
        source_input = self.query_one("#source_path", Input)
        
        dest_path = dest_input.value.strip()
        if not dest_path:
            self.notify("Destination path is required", severity="error")
            return
        
        if not dest_path.startswith("/"):
            self.notify("Destination path must be absolute (start with /)", severity="error")
            return
        
        source = ""
        if self.current_mount_type in ["manual-volume", "host-dir"]:
            source = source_input.value.strip()
            if not source:
                self.notify("Source is required for this mount type", severity="error")
                return
        
        # Check for duplicate destination paths
        for existing_mount in self.stage1_mounts:
            if existing_mount.dst_path == dest_path:
                self.notify("Destination path already exists", severity="error")
                return
        
        # Create mount configuration
        mount_config = MountConfig(
            mount_type=self.current_mount_type,
            src_path=source if source else None,
            dst_path=dest_path
        )
        
        self.stage1_mounts.append(mount_config)
        self._update_mount_lists()
        
        # Clear inputs
        dest_input.value = ""
        source_input.value = ""
        
        self.notify(f"Added mount: {dest_path}", severity="information")
    
    def _update_mount_lists(self) -> None:
        """Update the mount lists display."""
        stage1_list = self.query_one("#stage1_list", ListView)
        stage1_list.clear()
        
        if not self.stage1_mounts:
            item = ListItem(Label("(No mounts configured)"))
            stage1_list.append(item)
        else:
            for mount in self.stage1_mounts:
                if mount.mount_type == "auto-volume":
                    description = f"• {mount.dst_path} (auto volume)"
                elif mount.mount_type == "manual-volume":
                    description = f"• {mount.src_path} → {mount.dst_path} (volume)"
                elif mount.mount_type == "host-dir":
                    description = f"• {mount.src_path} → {mount.dst_path} (host)"
                else:
                    description = f"• {mount.dst_path} ({mount.mount_type})"
                
                item = ListItem(Label(description))
                stage1_list.append(item)
    
    def _get_mounts_config(self) -> tuple[list[MountConfig], list[MountConfig]]:
        """Get the current mounts configuration."""
        stage1_enabled = self.query_one("#stage1_enabled", RadioSet)
        stage2_enabled = self.query_one("#stage2_enabled", RadioSet)
        
        stage1_yes_button = cast(RadioButton, stage1_enabled.query_one("RadioButton"))  # First button is "Yes"
        stage1 = self.stage1_mounts.copy() if (stage1_yes_button and stage1_yes_button.value) else []
        
        stage2_yes_button = cast(RadioButton, stage2_enabled.query_one("RadioButton"))  # First button is "Yes"
        stage2 = self.stage2_mounts.copy() if (stage2_yes_button and stage2_yes_button.value) else []
        
        return stage1, stage2
    
    def save_configuration(self) -> None:
        """Save current mounts configuration to project config."""
        stage1_mounts, stage2_mounts = self._get_mounts_config()
        # Convert list back to dict format for data model
        self.project_config.stage_1.mounts = {f"mount_{i}": mount for i, mount in enumerate(stage1_mounts)}
        self.project_config.stage_2.mounts = {f"mount_{i}": mount for i, mount in enumerate(stage2_mounts)}
    
    class ConfigReady(Message):
        """Message sent when configuration is ready."""
        
        def __init__(self, stage1_mounts: list[MountConfig], stage2_mounts: list[MountConfig]) -> None:
            super().__init__()
            self.stage1_mounts = stage1_mounts
            self.stage2_mounts = stage2_mounts
    
    class BackPressed(Message):
        """Message sent when back button is pressed."""
        pass