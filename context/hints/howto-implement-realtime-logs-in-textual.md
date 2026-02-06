# How to Implement Real-time Logs in Textual GUI Applications

## Overview

When building Textual GUI applications that need to display real-time logs (similar to a terminal), you have several widget options and architectural patterns to choose from. This guide covers the best practices for implementing scrollable, real-time log displays.

**Important Note:** This guide is updated for Textual 4.0.0+. In version 4.0.0 and later, the `work` decorator is imported from `textual` directly (`from textual import work`), not from `textual.worker` as in earlier versions.

## Widget Options

### 1. RichLog Widget (Recommended)
The `RichLog` widget is specifically designed for displaying real-time log content with rich formatting support.

```python
from textual.app import App, ComposeResult
from textual.widgets import RichLog

class LogApp(App):
    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, wrap=False)
    
    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        log.write("Initial log message")
        log.write("Another message with [bold red]formatting[/]")
```

**Key Features:**
- Built-in scrolling
- Rich text formatting support
- Automatic highlighting
- Configurable line limits with `max_lines`
- Auto-scroll to bottom with `auto_scroll=True`

### 2. Log Widget (Simple Text)
For plain text logs without formatting:

```python
from textual.widgets import Log

class SimpleLogApp(App):
    def compose(self) -> ComposeResult:
        yield Log(auto_scroll=True, max_lines=1000)
    
    def add_log_entry(self, message: str) -> None:
        log = self.query_one(Log)
        log.write_line(f"[{datetime.now()}] {message}")
```

## Real-time Updates with Background Tasks

### Method 1: Using @work Decorator (Recommended)

```python
from textual.app import App, ComposeResult
from textual.widgets import RichLog
from textual import work  # Correct import for Textual 4.0.0+
import asyncio
import datetime

class RealTimeLogApp(App):
    def compose(self) -> ComposeResult:
        yield RichLog(auto_scroll=True, max_lines=500)
    
    def on_mount(self) -> None:
        # Start background log producer
        self.start_log_producer()
    
    @work(thread=True)
    def start_log_producer(self) -> None:
        """Background worker that generates logs"""
        import time
        counter = 0
        
        while not self.is_running:
            time.sleep(1)  # Simulate work
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] Log entry #{counter}"
            
            # Use call_from_thread to update UI safely
            self.call_from_thread(self.add_log_message, message)
            counter += 1
    
    def add_log_message(self, message: str) -> None:
        """Thread-safe method to add log messages"""
        log = self.query_one(RichLog)
        log.write(message)
```

### Method 2: Using run_worker with Async

```python
class AsyncLogApp(App):
    def compose(self) -> ComposeResult:
        yield RichLog(auto_scroll=True)
    
    def on_mount(self) -> None:
        self.run_worker(self.log_producer())
    
    async def log_producer(self) -> None:
        """Async log producer"""
        counter = 0
        while True:
            await asyncio.sleep(1)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] Async log #{counter}"
            self.query_one(RichLog).write(message)
            counter += 1
```

### Method 3: External Process Logs with Queue

For capturing logs from external processes or commands:

```python
import subprocess
import threading
from queue import Queue
from textual.message import Message

class LogMessage(Message):
    def __init__(self, content: str) -> None:
        self.content = content
        super().__init__()

class ProcessLogApp(App):
    def __init__(self):
        super().__init__()
        self.log_queue = Queue()
    
    def compose(self) -> ComposeResult:
        yield RichLog(auto_scroll=True, max_lines=1000)
    
    def on_mount(self) -> None:
        self.start_process_monitoring()
        self.set_interval(0.1, self.process_log_queue)
    
    @work(thread=True)
    def start_process_monitoring(self) -> None:
        """Monitor external process output"""
        process = subprocess.Popen(
            ["tail", "-f", "/var/log/system.log"],  # Example command
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        for line in process.stdout:
            if line.strip():
                self.call_from_thread(
                    self.post_message, 
                    LogMessage(line.strip())
                )
    
    def on_log_message(self, message: LogMessage) -> None:
        """Handle incoming log messages"""
        log = self.query_one(RichLog)
        log.write(message.content)
    
    def process_log_queue(self) -> None:
        """Process queued log messages (alternative to messages)"""
        try:
            while not self.log_queue.empty():
                message = self.log_queue.get_nowait()
                self.query_one(RichLog).write(message)
        except:
            pass
```

## Advanced Features

### Custom Log Widget with Filtering

```python
from textual.reactive import reactive

class FilterableLogWidget(RichLog):
    filter_text = reactive("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._all_logs = []
    
    def write_log(self, message: str) -> None:
        """Write log and store for filtering"""
        self._all_logs.append(message)
        if self.should_show_message(message):
            self.write(message)
    
    def should_show_message(self, message: str) -> bool:
        """Check if message matches current filter"""
        if not self.filter_text:
            return True
        return self.filter_text.lower() in message.lower()
    
    def watch_filter_text(self, old_filter: str, new_filter: str) -> None:
        """Refilter logs when filter changes"""
        self.clear()
        for message in self._all_logs:
            if self.should_show_message(message):
                self.write(message)
```

### Log Levels with Color Coding

```python
import logging
from rich.text import Text

class ColoredLogWidget(RichLog):
    def write_log(self, level: str, message: str) -> None:
        """Write log with color coding based on level"""
        colors = {
            'DEBUG': 'dim white',
            'INFO': 'blue',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold red'
        }
        
        color = colors.get(level.upper(), 'white')
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Create rich text with formatting
        text = Text()
        text.append(f"[{timestamp}] ", style="dim")
        text.append(f"{level:8}", style=color)
        text.append(f" {message}")
        
        self.write(text)
```

## Best Practices

### 1. Performance Considerations
- Set `max_lines` to prevent memory issues with long-running logs
- Use `auto_scroll=True` for real-time following
- Consider log rotation for very high-volume logs

### 2. Thread Safety
- Always use `call_from_thread()` when updating UI from worker threads
- Use `post_message()` for complex communication between threads
- Prefer `@work(thread=True)` for I/O-bound log collection

### 3. User Experience
- Provide scroll controls (Home/End keys)
- Add search/filter functionality for large logs
- Consider pause/resume for high-frequency logs
- Use different colors for different log levels

### 4. Layout Integration

```python
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Button

class LogAppWithControls(App):
    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Input(placeholder="Filter logs...", id="filter")
                yield Button("Clear", id="clear")
                yield Button("Pause", id="pause")
            yield RichLog(auto_scroll=True, id="logs")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "clear":
            self.query_one(RichLog).clear()
        elif event.button.id == "pause":
            # Toggle pause state
            pass
    
    def on_input_changed(self, event: Input.Changed) -> None:
        # Update filter
        pass
```

## CSS Styling

```css
RichLog {
    border: solid $primary;
    height: 1fr;
    scrollbar-size: 1 1;
    scrollbar-background: $surface;
    scrollbar-color: $primary;
}

RichLog:focus {
    border: solid $accent;
}
```

## References

- [Textual RichLog Documentation](https://textual.textualize.io/widgets/rich_log/)
- [Textual Log Widget Documentation](https://textual.textualize.io/widgets/log/)
- [Textual Workers Guide](https://textual.textualize.io/guide/workers/)
- [Rich Text Documentation](https://rich.readthedocs.io/en/stable/text.html)
