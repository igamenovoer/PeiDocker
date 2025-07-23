"""Modal dialog components for PeiDocker GUI."""

from textual.app import ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label
from textual.message import Message


class ErrorDialog(ModalScreen[None]):
    """Modal dialog for displaying error messages."""
    
    DEFAULT_CSS = """
    ErrorDialog {
        align: center middle;
    }
    
    #error-dialog {
        grid-size: 1;
        grid-gutter: 1;
        grid-rows: auto auto auto;
        padding: 0 1;
        width: 60;
        height: auto;
        border: thick $error 80%;
        background: $surface;
    }
    
    .dialog-title {
        color: $error;
        text-style: bold;
        text-align: center;
        padding: 1 0;
    }
    
    .dialog-message {
        color: $text;
        text-align: left;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary;
    }
    
    .dialog-buttons {
        align: center middle;
        padding: 1 0;
    }
    """
    
    def __init__(self, title: str, message: str):
        super().__init__()
        self.dialog_title = title
        self.dialog_message = message
    
    def compose(self) -> ComposeResult:
        """Create the error dialog."""
        with Grid(id="error-dialog"):
            yield Label(self.dialog_title, classes="dialog-title")
            yield Static(self.dialog_message, classes="dialog-message")
            with Horizontal(classes="dialog-buttons"):
                yield Button("OK", variant="error", id="ok")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "ok":
            self.dismiss()


class ConfirmDialog(ModalScreen[bool]):
    """Modal dialog for confirmation prompts."""
    
    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }
    
    #confirm-dialog {
        grid-size: 1;
        grid-gutter: 1;
        grid-rows: auto auto auto;
        padding: 0 1;
        width: 60;
        height: auto;
        border: thick $warning 80%;
        background: $surface;
    }
    
    .dialog-title {
        color: $warning;
        text-style: bold;
        text-align: center;
        padding: 1 0;
    }
    
    .dialog-message {
        color: $text;
        text-align: left;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary;
    }
    
    .dialog-buttons {
        align: center middle;
        padding: 1 0;
    }
    """
    
    def __init__(self, title: str, message: str):
        super().__init__()
        self.dialog_title = title
        self.dialog_message = message
    
    def compose(self) -> ComposeResult:
        """Create the confirmation dialog."""
        with Grid(id="confirm-dialog"):
            yield Label(self.dialog_title, classes="dialog-title")
            yield Static(self.dialog_message, classes="dialog-message")
            with Horizontal(classes="dialog-buttons"):
                yield Button("Yes", variant="success", id="yes")
                yield Button("No", variant="default", id="no")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "yes":
            self.dismiss(True)
        elif event.button.id == "no":
            self.dismiss(False)