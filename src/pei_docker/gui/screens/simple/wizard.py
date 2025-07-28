"""Simple mode wizard controller."""

from typing import List, Dict, Any, Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ...app import PeiDockerApp
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Label, Button, ProgressBar
from textual.css.query import NoMatches

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
        ("b", "back", "Prev"),
        ("n", "next", "Next"),
        ("escape", "handle_escape", "Escape"),
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
        self.escape_count = 0  # Track ESC key presses for double ESC handling
        
    def _create_steps(self) -> List[WizardStep]:
        """Create the wizard steps."""
        from .project_info import ProjectInfoWidget
        from .ssh_config import SSHConfigScreen
        from .proxy_config import ProxyConfigScreen
        from .apt_config import APTConfigScreen
        from .port_mapping import PortMappingScreen
        from .env_vars import EnvironmentVariablesScreen
        from .device_config import DeviceConfigScreen
        from .mounts import MountsScreen
        from .entry_point import EntryPointScreen
        from .custom_scripts import CustomScriptsScreen
        from .summary import SummaryScreen
        
        return [
            WizardStep("project_info", "Project Information", ProjectInfoWidget),
            WizardStep("ssh_config", "SSH Configuration", SSHConfigScreen),
            WizardStep("proxy_config", "Proxy Configuration", ProxyConfigScreen),
            WizardStep("apt_config", "APT Configuration", APTConfigScreen),
            WizardStep("port_mapping", "Port Mapping", PortMappingScreen),
            WizardStep("env_vars", "Environment Variables", EnvironmentVariablesScreen),
            WizardStep("device_config", "Device Configuration", DeviceConfigScreen),
            WizardStep("mounts", "Additional Mounts", MountsScreen),
            WizardStep("entry_point", "Custom Entry Point", EntryPointScreen),
            WizardStep("custom_scripts", "Custom Scripts", CustomScriptsScreen),
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
                    classes="wizard-progress"
                )
            
            # Current step content - Create and yield the step widget directly
            with Vertical(classes="wizard-content", id="step_content"):
                # Initialize the current step widget
                step = self.steps[self.current_step]
                step_widget = step.screen_class(self.project_config)
                self.step_screens[self.current_step] = step_widget
                yield step_widget
            
            # Navigation
            with Horizontal(classes="wizard-navigation"):
                with Horizontal(classes="nav-buttons"):
                    yield Button("Prev", id="prev", variant="default", disabled=self.current_step == 0)
                    if self.current_step >= len(self.steps) - 1:
                        yield Button("Save", id="save", variant="success")
                    else:
                        yield Button("Next", id="next", variant="primary")
                    yield Button("Cancel", id="cancel", variant="default")
    
    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        # Set initial progress bar value
        self._update_step()
    
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
    
    def action_save(self) -> None:
        """Save the configuration (final step only)."""
        if self._validate_current_step():
            # The summary screen will handle saving
            summary_screen = self.step_screens[self.current_step]
            if summary_screen and hasattr(summary_screen, 'save_configuration'):
                if summary_screen.save_configuration():
                    self.notify("Configuration saved successfully!", severity="information")
                else:
                    self.notify("Failed to save configuration", severity="error")
        else:
            self.notify("Please correct the errors before saving", severity="warning")
    
    def action_handle_escape(self) -> None:
        """Handle escape key presses."""
        self.escape_count += 1
        
        # Reset escape count after 1 second if not double-pressed
        self.set_timer(1.0, self._reset_escape_count)
        
        if self.escape_count >= 2:
            # Double ESC - return to main menu (startup screen)
            self.escape_count = 0
            self.app.pop_screen()  # Return to startup screen
        else:
            # Single ESC - delegate to current step screen for input clearing
            current_screen = self.step_screens[self.current_step]
            if current_screen and hasattr(current_screen, 'handle_escape'):
                current_screen.handle_escape()
    
    def _reset_escape_count(self) -> None:
        """Reset escape count after timeout."""
        self.escape_count = 0
    
    def _update_step(self) -> None:
        """Update the current step display."""
        # Update title and progress
        title_label = self.query_one(".wizard-title", Label)
        title_label.update(f"Step {self.current_step + 1} of {len(self.steps)}: {self.steps[self.current_step].title}")
        
        progress_bar = self.query_one(".wizard-progress", ProgressBar)
        progress_bar.progress = self.current_step + 1
        
        # Update navigation buttons
        try:
            prev_btn = self.query_one("#prev", Button) 
            prev_btn.disabled = self.current_step == 0
        except NoMatches:
            pass  # Button might not exist yet
        
        # Update the step content
        self._update_step_content()
        
        # Update navigation buttons efficiently without DOM manipulation
        self._update_navigation_buttons()
    
    def _update_navigation_buttons(self) -> None:
        """Update button states without DOM manipulation."""
        # Update prev button state
        try:
            prev_btn = self.query_one("#prev", Button)
            prev_btn.disabled = self.current_step == 0
        except NoMatches:
            pass  # Button doesn't exist yet
        
        # Handle next/save button - only recreate if needed
        is_last_step = self.current_step >= len(self.steps) - 1
        
        # Try to find existing buttons
        has_next = False
        has_save = False
        try:
            self.query_one("#next", Button)
            has_next = True
        except NoMatches:
            pass
            
        try:
            self.query_one("#save", Button)
            has_save = True
        except NoMatches:
            pass
        
        # Only recreate navigation if button type mismatch
        if (is_last_step and not has_save) or (not is_last_step and not has_next):
            self._recreate_navigation_buttons()
    
    def _recreate_navigation_buttons(self) -> None:
        """Recreate navigation buttons only when button type needs to change."""
        nav_container = self.query_one(".wizard-navigation")
        nav_container.remove_children()
        
        # Create appropriate buttons for current step
        prev_button = Button("Prev", id="prev", variant="default", disabled=self.current_step == 0)
        
        if self.current_step >= len(self.steps) - 1:
            action_button = Button("Save", id="save", variant="success")
        else:
            action_button = Button("Next", id="next", variant="primary")
            
        cancel_button = Button("Cancel", id="cancel", variant="default")
        
        # Create container with buttons
        nav_buttons = Horizontal(prev_button, action_button, cancel_button, classes="nav-buttons")
        nav_container.mount(nav_buttons)
    
    def _update_step_content(self) -> None:
        """Update the step content area."""
        content_container = self.query_one("#step_content")
        content_container.remove_children()
        
        # Get new step screen content
        if self.step_screens[self.current_step] is None:
            step = self.steps[self.current_step]
            self.step_screens[self.current_step] = step.screen_class(self.project_config)
        
        # Mount the step screen widget directly
        step_screen = self.step_screens[self.current_step]
        assert step_screen is not None, "Screen should not be None after initialization"
        content_container.mount(step_screen)
    
    def _validate_current_step(self) -> bool:
        """Validate the current step before proceeding."""
        if self.step_screens[self.current_step] is None:
            return True
        
        step_screen = self.step_screens[self.current_step]
        assert step_screen is not None, "Screen should not be None after None check"
        if hasattr(step_screen, 'is_valid'):
            result = step_screen.is_valid()
            return bool(result)  # Ensure we return a bool, not Any
        
        return True
    
    @on(Button.Pressed, "#prev")
    def on_prev_pressed(self) -> None:
        """Prev button pressed."""
        self.action_back()
    
    @on(Button.Pressed, "#next")
    def on_next_pressed(self) -> None:
        """Next button pressed."""
        self.action_next()
    
    @on(Button.Pressed, "#save")
    def on_save_pressed(self) -> None:
        """Save button pressed."""
        self.action_save()
    
    @on(Button.Pressed, "#cancel")
    def on_cancel_pressed(self) -> None:
        """Cancel button pressed."""
        self.action_quit()
    
    def action_quit(self) -> None:
        """Quit the wizard."""
        cast('PeiDockerApp', self.app).action_quit_app()