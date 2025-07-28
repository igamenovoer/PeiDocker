"""SC-3: Project Information Screen - Technical Implementation.

This module implements the Project Information Screen (SC-3) according to the
technical specification. It provides the first step of the configuration wizard
where users enter project name and Docker base image selection.

The implementation follows flat material design principles and integrates with
the SC-2 wizard controller framework for navigation and state management.
"""

import re
from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.widget import Widget
from textual.widgets import Label, Input, Static
from textual.validation import ValidationResult, Validator

from ...models.config import ProjectConfig




class ProjectNameValidator(Validator):
    """Validator for Docker-compatible project names."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate project name format."""
        if not value:
            return self.failure("Project name is required")
        
        if not re.match(r'^[a-z][a-z0-9_-]*$', value):
            return self.failure("Project name must contain only lowercase letters, numbers, hyphens, and underscores. Must start with a letter.")
        
        return self.success()


class DockerImageValidator(Validator):
    """Validator for Docker image name format."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate Docker image name format."""
        if not value:
            return self.failure("Base image is required")
        
        if not re.match(r'^[a-z0-9]([a-z0-9_.-]*[a-z0-9])?(/[a-z0-9]([a-z0-9_.-]*[a-z0-9])?)*(:[\w][\w.-]{0,127})?$', value):
            return self.failure("Base image must be in format 'image:tag' or 'registry/image:tag'")
        
        return self.success()



class ProjectInfoWidget(Widget):
    """SC-3: Project Information Widget for embedding in wizard.
    
    This is the embeddable Widget version of the Project Information screen,
    designed to be mounted within the SC-2 wizard controller framework.
    """
    
    # Flat Material Design CSS (same as Screen version)
    DEFAULT_CSS = """
    ProjectInfoWidget {
        background: $surface;
        padding: 2;
    }
    
    /* Clean container without depth effects */
    .project-info-container {
        background: $surface;
        border: none;
        padding: 2;
        margin: 1;
    }
    
    /* Flat input styling */
    Input {
        background: $surface;
        border: solid $foreground 20%;
        padding: 1;
    }
    
    Input:focus {
        border: solid $primary;
        background: $surface-lighten-1;
    }
    
    /* Image suggestions styling */
    .image-suggestions {
        background: $surface-lighten-1;
        border: none;
        padding: 1;
        color: $foreground 60%;
        text-style: italic;
    }
    
    /* Validation error styling */
    .validation-error {
        color: $error;
        background: $surface-lighten-1;
        padding: 0 1;
        text-style: italic;
    }
    
    /* Preview text styling */
    .preview-text {
        color: $foreground 60%;
        text-style: italic;
        padding: 0 1;
    }
    """
    
    def __init__(self, project_config: ProjectConfig) -> None:
        super().__init__()
        self.project_config = project_config
        
        # Auto-populate project name from directory if not set
        if not project_config.project_name and project_config.project_dir:
            project_dir = Path(project_config.project_dir)
            dir_name = project_dir.name.lower().replace('_', '-')
            if self._is_valid_project_name(dir_name):
                self.project_config.project_name = dir_name
        
        # Ensure default values are set
        if not self.project_config.project_name:
            self.project_config.project_name = "test-project"
        
        if not self.project_config.stage_1.base_image:
            self.project_config.stage_1.base_image = "ubuntu:24.04"
    
    def compose(self) -> ComposeResult:
        """Compose the project information widget."""
        with Container(classes="project-info-container"):
            yield Label("Basic project settings:", classes="section-header")
            yield Static()  # Spacer
            
            # Project Name Field
            yield Horizontal(
                Label("Project Name: *", classes="field-label"),
                classes="field-row"
            )
            yield Input(
                value=self.project_config.project_name,
                placeholder="Enter project name...",
                id="project_name",
                classes="project-input"
            )
            
            # Image Preview
            if self.project_config.project_name:
                stage1_image = f"{self.project_config.project_name}:stage-1"
                stage2_image = f"{self.project_config.project_name}:stage-2"
                yield Static(
                    f"Docker images: {stage1_image}, {stage2_image}",
                    classes="preview-text",
                    id="image_preview"
                )
            
            yield Static()  # Spacer
            
            # Base Image Field
            yield Horizontal(
                Label("Base Docker Image: *", classes="field-label"),
                classes="field-row"
            )
            yield Input(
                value=self.project_config.stage_1.base_image,
                placeholder="ubuntu:24.04",
                id="base_image",
                classes="base-image-input"
            )
            
            yield Static()  # Spacer
            yield Static("* Required field", classes="required-note")
    
    @on(Input.Changed, "#project_name")
    def on_project_name_changed(self, event: Input.Changed) -> None:
        """Handle project name input changes with real-time validation."""
        # Update project config directly
        self.project_config.project_name = event.value.strip()
        
        # Update preview with generated image names
        self._update_image_preview()
    
    @on(Input.Changed, "#base_image")
    def on_base_image_changed(self, event: Input.Changed) -> None:
        """Handle base image input changes."""
        # Update project config directly
        self.project_config.stage_1.base_image = event.value.strip()
    
    def _is_valid_project_name(self, name: str) -> bool:
        """Validate project name against Docker naming rules."""
        return bool(re.match(r'^[a-z][a-z0-9_-]*$', name))
    
    def is_valid(self) -> bool:
        """Check if all inputs are valid for navigation control."""
        return (self._is_valid_project_name(self.project_config.project_name) and 
                self._is_valid_image_format(self.project_config.stage_1.base_image))
    
    def _is_valid_image_format(self, image: str) -> bool:
        """Validate Docker image name format."""
        if not image:
            return False
        return bool(re.match(r'^[a-z0-9]([a-z0-9_.-]*[a-z0-9])?(/[a-z0-9]([a-z0-9_.-]*[a-z0-9])?)*(:[\w][\w.-]{0,127})?$', image))
    
    def _update_image_preview(self) -> None:
        """Update the Docker image preview display."""
        try:
            preview = self.query_one("#image_preview", Static)
            if self._is_valid_project_name(self.project_config.project_name):
                stage1_image = f"{self.project_config.project_name}:stage-1"
                stage2_image = f"{self.project_config.project_name}:stage-2"
                preview.update(f"Docker images: {stage1_image}, {stage2_image}")
            else:
                preview.update("Enter a valid project name to see Docker image preview")
        except Exception:
            pass  # Ignore errors during preview update
    
    def handle_escape(self) -> None:
        """Handle single ESC key press - clear current input."""
        try:
            focused_widget = self.screen.focused
            if isinstance(focused_widget, Input):
                focused_widget.value = ""
        except Exception:
            pass  # Ignore errors during escape handling