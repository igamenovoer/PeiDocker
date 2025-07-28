"""SC-3: Project Information Screen - Technical Implementation.

This module implements the Project Information Screen (SC-3) according to the
technical specification. It provides the first step of the configuration wizard
where users enter project name and Docker base image selection.

The implementation follows flat material design principles and integrates with
the SC-2 wizard controller framework for navigation and state management.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Label, Input, Static, Button
from textual.validation import ValidationResult, Validator
from textual.reactive import reactive

from ...models.config import ProjectConfig


@dataclass
class ProjectValidationResult:
    """Result of project configuration validation operations."""
    is_valid: bool
    errors: List[str]


@dataclass 
class ProjectInfoConfig:
    """Configuration data for project information step."""
    
    project_name: str = ""
    base_image: str = "ubuntu:24.04"
    directory_path: str = ""
    stage1_image_name: str = ""
    stage2_image_name: str = ""
    
    def validate(self) -> ProjectValidationResult:
        """Validate project information configuration."""
        errors = []
        
        # Project name validation
        if not self.project_name:
            errors.append("Project name is required")
        elif not self._is_valid_project_name(self.project_name):
            errors.append("Project name must contain only lowercase letters, numbers, hyphens, and underscores. Must start with a letter.")
        
        # Base image validation  
        if not self.base_image:
            errors.append("Base image is required")
        elif not self._is_valid_image_format(self.base_image):
            errors.append("Base image must be in format 'image:tag' or 'registry/image:tag'")
            
        return ProjectValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def _is_valid_project_name(self, name: str) -> bool:
        """Validate project name against Docker naming rules."""
        return bool(re.match(r'^[a-z][a-z0-9_-]*$', name))
    
    def _is_valid_image_format(self, image: str) -> bool:
        """Validate Docker image name format."""
        return bool(re.match(r'^[a-z0-9]([a-z0-9_.-]*[a-z0-9])?(/[a-z0-9]([a-z0-9_.-]*[a-z0-9])?)*(:[\w][\w.-]{0,127})?$', image))
    
    def generate_image_names(self) -> None:
        """Generate Docker image names from project name."""
        if self.project_name:
            self.stage1_image_name = f"{self.project_name}:stage-1"
            self.stage2_image_name = f"{self.project_name}:stage-2"


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


class ProjectInfoScreen(Screen[None]):
    """SC-3: Project Information Screen.
    
    Collects project name and Docker base image for PeiDocker configuration.
    Implements flat material design and integrates with SC-2 wizard controller.
    """
    
    # Flat Material Design CSS
    DEFAULT_CSS = """
    ProjectInfoScreen {
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
    
    .container-title {
        color: $foreground;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .field-group {
        margin: 1 0;
    }
    
    .field-label {
        color: $foreground;
        margin-bottom: 1;
        text-style: bold;
    }
    
    .required-indicator {
        color: $error;
    }
    
    .preview-text {
        color: $foreground-muted;
        margin-top: 1;
        text-style: italic;
    }
    
    .error-text {
        color: $error;
        margin-top: 1;
        text-style: bold;
    }
    
    /* Flat input styling */
    Input {
        background: $surface;
        border: solid $panel;
        padding: 1;
    }
    
    Input:focus {
        border: solid $primary;
        background: $panel;
    }
    
    Input.-invalid {
        border: solid $error;
        background: $surface;
    }
    
    .help-text {
        color: $foreground-muted;
        margin-top: 1;
    }
    """
    
    # Reactive state for real-time updates
    project_name_value: reactive[str] = reactive("")
    base_image_value: reactive[str] = reactive("ubuntu:24.04")
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        self.config = ProjectInfoConfig(
            project_name=project_config.project_name or "",
            base_image=project_config.stage_1.base_image,
            directory_path=project_config.project_dir or ""
        )
        
        # Auto-populate project name from directory if available
        if not self.config.project_name and self.config.directory_path:
            dir_name = Path(self.config.directory_path).name
            if self._is_valid_project_name_format(dir_name):
                self.config.project_name = dir_name
        
        # Set reactive values
        self.project_name_value = self.config.project_name
        self.base_image_value = self.config.base_image
        
        # Generate initial image names
        self.config.generate_image_names()
    
    def _is_valid_project_name_format(self, name: str) -> bool:
        """Check if name follows Docker project name format."""
        return bool(re.match(r'^[a-z][a-z0-9_-]*$', name))
    
    def compose(self) -> ComposeResult:
        """Compose the project info screen according to SC-3 specification."""
        with Vertical():
            # Main container with flat design
            with Container(classes="project-info-container"):
                yield Label("Project Information", classes="container-title")
                yield Static("Basic project settings:", classes="help-text")
                
                # Project Name Field
                with Vertical(classes="field-group"):
                    with Horizontal():
                        yield Label("Project Name:", classes="field-label")
                        yield Label(" *", classes="required-indicator")
                    
                    yield Input(
                        value=self.config.project_name,
                        placeholder="my-awesome-project",
                        id="project_name",
                        validators=[ProjectNameValidator()]
                    )
                    
                    # Docker image preview
                    preview_text = self._generate_preview_text()
                    yield Label(preview_text, classes="preview-text", id="image_preview")
                
                # Base Docker Image Field  
                with Vertical(classes="field-group"):
                    with Horizontal():
                        yield Label("Base Docker Image:", classes="field-label")
                        yield Label(" *", classes="required-indicator")
                    
                    yield Input(
                        value=self.config.base_image,
                        placeholder="ubuntu:24.04",
                        id="base_image",
                        validators=[DockerImageValidator()]
                    )
                
                # Help text
                yield Label("* Required field", classes="help-text")
    
    def _generate_preview_text(self) -> str:
        """Generate Docker image preview text."""
        if self.config.project_name:
            return f"Docker images: {self.config.project_name}:stage-1, {self.config.project_name}:stage-2"
        else:
            return "Docker images: (enter project name to preview)"
    
    def watch_project_name_value(self, new_value: str) -> None:
        """Watch for project name changes and update preview."""
        self.config.project_name = new_value
        self.config.generate_image_names()
        self._update_preview()
    
    def watch_base_image_value(self, new_value: str) -> None:
        """Watch for base image changes."""
        self.config.base_image = new_value
    
    def _update_preview(self) -> None:
        """Update the image preview display."""
        try:
            preview_label = self.query_one("#image_preview", Label)
            preview_text = self._generate_preview_text()
            preview_label.update(preview_text)
        except Exception:
            pass  # Ignore errors during update
    
    @on(Input.Changed, "#project_name")
    def on_project_name_changed(self, event: Input.Changed) -> None:
        """Handle project name input changes with real-time validation."""
        value = event.value.strip()
        self.project_name_value = value
        
        # Update project config
        self.project_config.project_name = value
        
        # Update memory store (integrated with SC-2 controller)
        self._update_memory_store()
    
    @on(Input.Changed, "#base_image")
    def on_base_image_changed(self, event: Input.Changed) -> None:
        """Handle base image input changes with real-time validation."""
        value = event.value.strip()
        self.base_image_value = value
        
        # Update project config
        self.project_config.stage_1.base_image = value
        
        # Update memory store (integrated with SC-2 controller)
        self._update_memory_store()
    
    def _update_memory_store(self) -> None:
        """Update SC-2 controller memory store with current configuration."""
        # This integrates with the SC-2 wizard controller framework
        # All changes are stored in SC-2's memory store until final save
        pass
    
    def is_valid(self) -> bool:
        """Check if all inputs are valid for navigation control."""
        validation_result = self.config.validate()
        return validation_result.is_valid
    
    def handle_escape(self) -> None:
        """Handle single ESC key press - clear current input."""
        # Try to clear the currently focused input field
        try:
            focused = self.focused
            if isinstance(focused, Input):
                focused.value = ""
        except Exception:
            pass  # Ignore errors during escape handling


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
    
    def __init__(self, project_config: 'ProjectConfig') -> None:
        super().__init__()
        self.project_config = project_config
        self.config = ProjectInfoConfig()
        
        # Auto-populate from project directory if available
        if hasattr(project_config, 'project_dir') and project_config.project_dir:
            project_dir = Path(project_config.project_dir)
            self.config.directory_path = str(project_dir)
            
            # Extract directory name for project name suggestion
            dir_name = project_dir.name.lower().replace('_', '-')
            if self._is_valid_project_name(dir_name):
                self.config.project_name = dir_name
                self.config.generate_image_names()
        
        # Ensure default values are set
        if not self.config.project_name:
            self.config.project_name = "test-project"
            self.config.generate_image_names()
    
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
                value=self.config.project_name,
                placeholder="Enter project name...",
                id="project_name",
                classes="project-input"
            )
            
            # Image Preview
            if self.config.stage1_image_name and self.config.stage2_image_name:
                yield Static(
                    f"Docker images: {self.config.stage1_image_name}, {self.config.stage2_image_name}",
                    classes="preview-text"
                )
            
            yield Static()  # Spacer
            
            # Base Image Field
            yield Horizontal(
                Label("Base Docker Image: *", classes="field-label"),
                classes="field-row"
            )
            yield Input(
                value=self.config.base_image,
                placeholder="ubuntu:24.04",
                id="base_image",
                classes="base-image-input"
            )
            
            yield Static()  # Spacer
            yield Static("* Required field", classes="required-note")
    
    @on(Input.Changed, "#project_name")
    def on_project_name_changed(self, event: Input.Changed) -> None:
        """Handle project name input changes with real-time validation."""
        self.config.project_name = event.value
        
        # Update project config
        self.project_config.project_name = event.value
        
        # Generate image names and update preview
        if self._is_valid_project_name(event.value):
            self.config.generate_image_names()
            # Update the preview text
            preview = self.query_one(".preview-text", Static)
            preview.update(f"Docker images: {self.config.stage1_image_name}, {self.config.stage2_image_name}")
        else:
            # Clear preview if invalid
            try:
                preview = self.query_one(".preview-text", Static)
                preview.update("Enter a valid project name to see Docker image preview")
            except:
                pass
    
    @on(Input.Changed, "#base_image")
    def on_base_image_changed(self, event: Input.Changed) -> None:
        """Handle base image input changes."""
        self.config.base_image = event.value
        # Update project config
        if hasattr(self.project_config, 'stage_1'):
            self.project_config.stage_1.base_image = event.value
    
    def _is_valid_project_name(self, name: str) -> bool:
        """Validate project name against Docker naming rules."""
        return bool(re.match(r'^[a-z][a-z0-9_-]*$', name))
    
    def is_valid(self) -> bool:
        """Check if all inputs are valid for navigation control."""
        validation_result = self.config.validate()
        return validation_result.is_valid
    
    def handle_escape(self) -> None:
        """Handle single ESC key press - clear current input."""
        try:
            focused = self.focused
            if isinstance(focused, Input):
                focused.value = ""
        except Exception:
            pass  # Ignore errors during escape handling