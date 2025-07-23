"""Simple mode wizard controller."""

from typing import List, Dict, Any, Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Label, Button, ProgressBar

from ...models.config import ProjectConfig


class WizardStep:
    """Represents a step in the wizard."""
    
    def __init__(self, name: str, title: str, screen_class: type):
        self.name = name
        self.title = title
        self.screen_class = screen_class


class SimpleWizardScreen(Screen[None]):
    """Main controller for the simple mode wizard."""
    
    BINDINGS = [
        ("b", "back", "Back"),
        ("n", "next", "Next"),
        ("q", "quit", "Quit"),
    ]
    
    DEFAULT_CSS = """
    SimpleWizardScreen {
        background: $surface;
    }
    
    .wizard-header {
        dock: top;
        height: 5;
        background: $primary;
        color: $text;
        padding: 1;
    }
    
    .wizard-title {
        text-style: bold;
        color: $text;
        text-align: center;
    }
    
    .wizard-progress {
        margin: 1 0;
    }
    
    .wizard-content {
        margin: 1 2;
    }
    
    .wizard-navigation {
        dock: bottom;
        height: 3;
        background: $surface-lighten-1;
        padding: 0 2;
    }
    
    .nav-buttons {
        width: 100%;
        height: 100%;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        self.current_step = 0
        self.steps = self._create_steps()
        self.step_screens = [None] * len(self.steps)  # Cache for step screens
        
    def _create_steps(self) -> List[WizardStep]:
        """Create the wizard steps."""
        from .project_info import ProjectInfoScreen
        from .ssh_config import SSHConfigScreen
        from .summary import SummaryScreen
        
        return [
            WizardStep("project_info", "Project Information", ProjectInfoScreen),
            WizardStep("ssh_config", "SSH Configuration", SSHConfigScreen),
            WizardStep("summary", "Configuration Summary", SummaryScreen),
        ]
    
    def compose(self) -> ComposeResult:
        """Compose the wizard screen."""
        with Vertical():
            # Header with progress
            with Vertical(classes="wizard-header"):
                yield Label(f"Step {self.current_step + 1} of {len(self.steps)}: {self.steps[self.current_step].title}", 
                          classes="wizard-title")
                yield ProgressBar(
                    total=len(self.steps),
                    progress=(self.current_step + 1),
                    classes="wizard-progress"
                )
            
            # Current step content
            with Vertical(classes="wizard-content", id="step_content"):
                yield self._get_current_step_screen()
            
            # Navigation
            with Horizontal(classes="wizard-navigation"):
                with Horizontal(classes="nav-buttons"):
                    yield Button("Back", id="back", variant="default", disabled=self.current_step == 0)
                    yield Button("Next", id="next", variant="primary", disabled=self.current_step >= len(self.steps) - 1)
                    yield Button("Cancel", id="cancel", variant="default")
    
    def action_back(self) -> None:
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_step()
    
    def action_next(self) -> None:
        """Go to next step."""
        # Validate current step before proceeding
        if not self._validate_current_step():
            self.notify("Please correct the errors before proceeding", severity="warning")
            return
        
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._update_step()
        elif self.current_step == len(self.steps) - 1:
            # On the last step, this should be "Finish"
            self.action_finish()
    
    def action_finish(self) -> None:
        """Finish the wizard."""
        if self._validate_current_step():
            # The summary screen will handle saving
            self.notify("Configuration completed!", severity="information")
        else:
            self.notify("Please correct the errors before finishing", severity="warning")
    
    def _update_step(self) -> None:
        """Update the current step display."""
        # Update title and progress
        title_label = self.query_one(".wizard-title", Label)
        title_label.update(f"Step {self.current_step + 1} of {len(self.steps)}: {self.steps[self.current_step].title}")
        
        progress_bar = self.query_one(".wizard-progress", ProgressBar)
        progress_bar.progress = self.current_step + 1
        
        # Update navigation buttons
        back_btn = self.query_one("#back", Button)
        back_btn.disabled = self.current_step == 0
        
        next_btn = self.query_one("#next", Button)
        if self.current_step >= len(self.steps) - 1:
            next_btn.label = "Finish"
            next_btn.variant = "success"
        else:
            next_btn.label = "Next"
            next_btn.variant = "primary"
        
        # Update the step content
        self._update_step_content()
    
    def _get_current_step_screen(self) -> ComposeResult:
        """Get the current step screen content."""
        if self.step_screens[self.current_step] is None:
            step = self.steps[self.current_step]
            self.step_screens[self.current_step] = step.screen_class(self.project_config)
        
        return self.step_screens[self.current_step].compose()
    
    def _update_step_content(self) -> None:
        """Update the step content area."""
        content_container = self.query_one("#step_content")
        content_container.remove_children()
        
        # Get new step screen content
        if self.step_screens[self.current_step] is None:
            step = self.steps[self.current_step]
            self.step_screens[self.current_step] = step.screen_class(self.project_config)
        
        # Mount the new content
        step_screen = self.step_screens[self.current_step]
        content_container.mount(*list(step_screen.compose()))
    
    def _validate_current_step(self) -> bool:
        """Validate the current step before proceeding."""
        if self.step_screens[self.current_step] is None:
            return True
        
        step_screen = self.step_screens[self.current_step]
        if hasattr(step_screen, 'is_valid'):
            return step_screen.is_valid()
        
        return True
    
    @on(Button.Pressed, "#back")
    def on_back_pressed(self) -> None:
        """Back button pressed."""
        self.action_back()
    
    @on(Button.Pressed, "#next")
    def on_next_pressed(self) -> None:
        """Next button pressed."""
        self.action_next()
    
    @on(Button.Pressed, "#cancel")
    def on_cancel_pressed(self) -> None:
        """Cancel button pressed."""
        self.action_quit()
    
    def action_quit(self) -> None:
        """Quit the wizard."""
        self.app.action_quit_app()