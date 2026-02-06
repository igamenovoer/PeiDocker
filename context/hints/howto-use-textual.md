# Introduction to `textual`

Textual is a lean application framework for Python that allows you to build sophisticated user interfaces with a simple Python API. Your apps can run both in the terminal and in a web browser.

**Key Features:**
- Terminal and web browser support
- Rich CSS-like styling system
- Event-driven reactive programming
- Extensive widget library
- Layout management (grid, vertical, horizontal)
- Key binding support
- File delivery capabilities

## How to find docs

### Using Context7 MCP
1. **Resolve library ID**: Use `mcp_context7_resolve-library-id` with `libraryName: "textual"`
2. **Get documentation**: Use `mcp_context7_get-library-docs` with the resolved library ID `/textualize/textual`

### Official Sources
- **GitHub Repository**: https://github.com/textualize/textual
- **Official Documentation**: Available through Context7 with 1,050+ code examples
- **Trust Score**: 9.4/10 (highly reliable)

## Basic concepts and usage examples

### Installation
```bash
# Basic installation
pip install textual

# With development tools
pip install textual-dev

# With syntax highlighting support
pip install "textual[syntax]"

# Via conda-forge
micromamba install -c conda-forge textual textual-dev
```

### Quick Start
```bash
# Run the built-in demo
python -m textual

# Get CLI help
textual --help
```

### Basic Application Structure
```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class MyApp(App):
    """A simple Textual app."""
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static("Hello, Textual!")
        yield Footer()

if __name__ == "__main__":
    app = MyApp()
    app.run()
```

### Key Concepts

#### 1. App Class
- Inherit from `App` to create your application
- Override `compose()` to define the widget hierarchy
- Use `run()` to start the application

#### 2. Widgets
Common widgets available:
- `Header` / `Footer` - Application header and footer
- `Static` - Display static text or rich content
- `Button` - Interactive buttons
- `Input` - Single-line text input
- `TextArea` - Multi-line text editing
- `DataTable` - Tabular data display
- `Tree` - Hierarchical data display
- `ListView` - Scrollable lists with selection
- `Log` - Real-time text logging
- `Markdown` - Markdown content rendering

#### 3. Layout and Containers
```python
from textual.containers import Container, Vertical, Horizontal, Grid

class LayoutApp(App):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Header()
            with Horizontal():
                yield Static("Left panel")
                yield Static("Right panel")
            yield Footer()
```

#### 4. Event Handling and Key Bindings
```python
class BindingApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "add_red", "Add Red"),
        ("g", "add_green", "Add Green"),
    ]
    
    def action_quit(self) -> None:
        """Quit the app."""
        self.exit()
    
    def action_add_red(self) -> None:
        """Handle 'r' key press."""
        self.bell("Red action triggered")
```

#### 5. CSS Styling
```python
class StyledApp(App):
    CSS = """
    Screen {
        background: #222;
        color: #eee;
    }
    
    Static {
        padding: 2;
        border: thick #ffffff;
        background: $primary;
    }
    
    Button {
        width: 100%;
        height: 3;
        margin: 1 0;
    }
    
    Button:hover {
        background: $accent;
    }
    """
```

#### 6. Reactive Attributes
```python
from textual.reactive import var

class ReactiveApp(App):
    counter = var(0)  # Reactive variable
    
    def watch_counter(self, old_value: int, new_value: int) -> None:
        """Called when counter changes."""
        self.title = f"Counter: {new_value}"
```

### Advanced Features

#### Workers for Async Operations
```python
from textual.worker import work

class WeatherApp(App):
    @work(exclusive=True)
    async def fetch_weather(self) -> str:
        """Fetch weather data without blocking UI."""
        # Async operations here
        return weather_data
```

#### File Delivery (Web Mode)
```python
def save_file(self) -> None:
    """Deliver a file to the user."""
    content = "Hello, World!"
    self.deliver_text(
        content, 
        filename="output.txt",
        mime_type="text/plain"
    )
```

### Example: Complete Stopwatch App
```python
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Header, Footer, Static
from textual.reactive import var
import time

class Stopwatch(Static):
    start_time = var(None)
    time = var(0.0)
    
    def on_mount(self) -> None:
        self.update_timer = self.set_interval(1/60, self.update_time, pause=True)
    
    def update_time(self) -> None:
        if self.start_time:
            self.time = time.time() - self.start_time
    
    def watch_time(self, time: float) -> None:
        minutes, seconds = divmod(time, 60)
        self.update(f"{minutes:02.0f}:{seconds:05.2f}")
    
    def start(self) -> None:
        self.start_time = time.time()
        self.update_timer.resume()
    
    def stop(self) -> None:
        self.update_timer.pause()
    
    def reset(self) -> None:
        self.time = 0
        self.start_time = None

class StopwatchApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Stopwatch(),
            Button("Start", id="start"),
            Button("Stop", id="stop"),
            Button("Reset", id="reset"),
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        stopwatch = self.query_one(Stopwatch)
        if event.button.id == "start":
            stopwatch.start()
        elif event.button.id == "stop":
            stopwatch.stop()
        elif event.button.id == "reset":
            stopwatch.reset()

if __name__ == "__main__":
    app = StopwatchApp()
    app.run()
```