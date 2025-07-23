"""Project information screen for simple mode wizard."""

from pathlib import Path
from typing import List

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Label, Input, Static, Button
from textual.validation import Function

from ...models.config import ProjectConfig
from ...utils.docker_utils import check_docker_images_exist


class ProjectInfoScreen(Screen[None]):
    """Screen for collecting basic project information."""
    
    DEFAULT_CSS = """
    ProjectInfoScreen {
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
    
    .field-group {
        margin: 1 0;
    }
    
    .field-label {
        color: $text;
        margin-bottom: 1;
    }
    
    .field-help {
        color: $text-muted;
        margin-top: 1;
    }
    
    .image-info {
        color: $success;
        margin-top: 1;
    }
    
    .image-warning {
        color: $warning;
        margin-top: 1;
    }
    
    .suggestions {
        border: solid $secondary;
        padding: 1;
        margin-top: 1;
        background: $surface-lighten-2;
    }
    
    Input {
        width: 100%;
    }
    
    Input.-invalid {
        border: solid $error;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        self.project_name_valid = bool(project_config.project_name)
        self.base_image_valid = True  # Default base image is valid
    
    def compose(self) -> ComposeResult:
        """Compose the project info screen."""
        with Vertical():
            yield Label("Configure basic project settings:", classes="field-help")
            
            # Project name section
            with Static(classes="section"):
                yield Label("Project Name", classes="section-title")
                
                with Vertical(classes="field-group"):
                    yield Label("Project Name: *", classes="field-label")
                    project_name = self.project_config.project_name or Path(self.project_config.project_dir or "").name
                    yield Input(
                        value=project_name,
                        placeholder="my-awesome-project",
                        id="project_name",
                        validators=[Function(self._validate_project_name, "Project name cannot be empty")]
                    )
                    yield Label(
                        f"Images: {project_name}:stage-1, {project_name}:stage-2",
                        classes="field-help"
                    )
            
            # Base image section
            with Static(classes="section"):
                yield Label("Base Docker Image", classes="section-title")
                
                with Vertical(classes="field-group"):
                    yield Label("Base Docker Image:", classes="field-label")
                    yield Input(
                        value=self.project_config.stage_1.base_image,
                        placeholder="ubuntu:24.04",
                        id="base_image",
                        validators=[Function(self._validate_base_image, "Invalid image format")]
                    )
                    
                    yield Static(
                        "Common base images:\n"
                        "• ubuntu:24.04 (recommended)\n"
                        "• ubuntu:22.04\n"
                        "• nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04",
                        classes="suggestions"
                    )
                    
                    yield Label("✓ Image format is valid", classes="image-info", id="image_status")
    
    def _validate_project_name(self, value: str) -> bool:
        """Validate project name."""
        name = value.strip()
        if not name:
            return False
        
        # Check if it's a valid Docker image name (simplified)
        # Allow alphanumeric, hyphens, underscores
        return all(c.isalnum() or c in '-_' for c in name) and not name.startswith('-') and not name.endswith('-')
    
    def _validate_base_image(self, value: str) -> bool:
        """Validate base image format."""
        image = value.strip()
        if not image:
            return False
        
        # Basic validation for Docker image format
        # Should contain at least image:tag or just image
        parts = image.split('/')
        if len(parts) > 3:  # registry/namespace/image:tag max
            return False
        
        # Check the final part (image:tag)
        final_part = parts[-1]
        if ':' in final_part:
            image_name, tag = final_part.rsplit(':', 1)
            return bool(image_name and tag)
        else:
            return bool(final_part)
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        if event.input.id == "project_name":
            self.project_name_valid = self._validate_project_name(event.value)
            if self.project_name_valid:
                self.project_config.project_name = event.value.strip()
                # Update image names display
                self._update_image_names()
        
        elif event.input.id == "base_image":
            self.base_image_valid = self._validate_base_image(event.value)
            if self.base_image_valid:
                self.project_config.stage_1.base_image = event.value.strip()
                # Check if image exists (async)
                self._check_image_exists(event.value.strip())
    
    def _update_image_names(self) -> None:
        """Update the image names display."""
        project_name = self.project_config.project_name
        if project_name:
            # Find and update the image names label
            try:
                for widget in self.query(Label):
                    if widget.renderable and "Images:" in str(widget.renderable):
                        widget.update(f"Images: {project_name}:stage-1, {project_name}:stage-2")
                        break
            except Exception:
                pass  # Ignore errors during update
    
    def _check_image_exists(self, image_name: str) -> None:
        """Check if the base image exists locally."""
        try:
            results = check_docker_images_exist([image_name])
            if results:
                exists = results[0][1]
                status_label = self.query_one("#image_status", Label)
                if exists:
                    status_label.update("✓ Image exists locally")
                    status_label.remove_class("image-warning")
                    status_label.add_class("image-info")
                else:
                    status_label.update("⚠ Image not found locally - will be downloaded during build")
                    status_label.remove_class("image-info")
                    status_label.add_class("image-warning")
        except Exception:
            # Ignore errors during image checking
            pass
    
    def is_valid(self) -> bool:
        """Check if all inputs are valid."""
        return self.project_name_valid and self.base_image_valid