# How to Programmatically Test Textual GUI Applications in Python

This guide covers comprehensive strategies for testing Textual TUI (Terminal User Interface) applications in Python, including unit testing, integration testing, mocking, and snapshot testing.

## Table of Contents

1. [Overview](#overview)
2. [Setting Up the Testing Environment](#setting-up-the-testing-environment)
3. [Basic Testing with Textual's Pilot](#basic-testing-with-textuals-pilot)
4. [Unit Testing Patterns](#unit-testing-patterns)
5. [Integration Testing](#integration-testing)
6. [Mocking External Dependencies](#mocking-external-dependencies)
7. [Snapshot Testing](#snapshot-testing)
8. [Advanced Testing Patterns](#advanced-testing-patterns)
9. [Auto-Operating Textual GUI Applications](#auto-operating-textual-gui-applications)
10. [Best Practices](#best-practices)
11. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)

## Overview

Textual is an async framework that requires special considerations when testing:
- **Async Nature**: All tests must be async and use `asyncio`
- **Headless Mode**: Tests run without displaying UI using `run_test()`
- **Pilot Object**: Simulates user interactions (clicks, key presses)
- **State Verification**: Assert changes in app state after interactions

## Setting Up the Testing Environment

### Required Dependencies

```bash
pip install pytest pytest-asyncio pytest-textual-snapshot
```

### Pytest Configuration

Create a `pytest.ini` or `pyproject.toml` configuration:

```ini
# pytest.ini
[tool:pytest]
asyncio_mode = auto
```

Or in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

This eliminates the need for `@pytest.mark.asyncio` on every async test.

## Basic Testing with Textual's Pilot

### Simple App Example

```python
# rgb_app.py
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Footer

class RGBApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    Horizontal {
        width: auto;
        height: auto;
    }
    """

    BINDINGS = [
        ("r", "switch_color('red')", "Go Red"),
        ("g", "switch_color('green')", "Go Green"),
        ("b", "switch_color('blue')", "Go Blue"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Button("Red", id="red")
            yield Button("Green", id="green")
            yield Button("Blue", id="blue")
        yield Footer()

    @on(Button.Pressed)
    def pressed_button(self, event: Button.Pressed) -> None:
        assert event.button.id is not None
        self.action_switch_color(event.button.id)

    def action_switch_color(self, color: str) -> None:
        self.screen.styles.background = color
```

### Basic Test Cases

```python
# test_rgb_app.py
from rgb_app import RGBApp
from textual.color import Color

async def test_key_presses():
    """Test pressing keys has the desired result."""
    app = RGBApp()
    async with app.run_test() as pilot:
        # Test pressing the R key
        await pilot.press("r")
        assert app.screen.styles.background == Color.parse("red")
        
        # Test pressing the G key
        await pilot.press("g")
        assert app.screen.styles.background == Color.parse("green")
        
        # Test pressing the B key
        await pilot.press("b")
        assert app.screen.styles.background == Color.parse("blue")
        
        # Test pressing unmapped key (no change)
        await pilot.press("x")
        assert app.screen.styles.background == Color.parse("blue")

async def test_button_clicks():
    """Test clicking buttons has the desired result."""
    app = RGBApp()
    async with app.run_test() as pilot:
        # Test clicking the "red" button
        await pilot.click("#red")
        assert app.screen.styles.background == Color.parse("red")
        
        # Test clicking the "green" button
        await pilot.click("#green")
        assert app.screen.styles.background == Color.parse("green")
        
        # Test clicking the "blue" button
        await pilot.click("#blue")
        assert app.screen.styles.background == Color.parse("blue")
```

## Unit Testing Patterns

### Testing Individual Components

```python
async def test_widget_initialization():
    """Test widget creates with expected initial state."""
    app = MyApp()
    async with app.run_test() as pilot:
        # Test initial state
        input_widget = app.query_one("#user-input")
        assert input_widget.value == ""
        
        # Test widget exists
        assert app.query_one("#submit-button")
        assert app.query_one("#status-label")

async def test_input_validation():
    """Test input validation logic."""
    app = MyApp()
    async with app.run_test() as pilot:
        input_widget = app.query_one("#user-input")
        
        # Test valid input
        input_widget.value = "valid@email.com"
        await pilot.click("#validate-button")
        await pilot.pause()  # Wait for message processing
        
        status = app.query_one("#status-label")
        assert "Valid" in status.renderable
```

### Testing Event Handling

```python
async def test_custom_message_handling():
    """Test custom message is handled correctly."""
    app = MyApp()
    async with app.run_test() as pilot:
        # Post custom message
        app.post_message(MyCustomMessage("test_data"))
        await pilot.pause()  # Allow message to be processed
        
        # Verify state change
        assert app.some_state_variable == "expected_value"
```

## Integration Testing

### Testing Component Interactions

```python
async def test_form_submission_flow():
    """Test complete form submission workflow."""
    app = ContactFormApp()
    async with app.run_test() as pilot:
        # Fill out form
        await pilot.click("#name-input")
        await pilot.press("J", "o", "h", "n")
        
        await pilot.click("#email-input")
        await pilot.press("j", "o", "h", "n", "@", "e", "x", "a", "m", "p", "l", "e", ".", "c", "o", "m")
        
        # Submit form
        await pilot.click("#submit-button")
        await pilot.pause()
        
        # Verify results
        success_message = app.query_one("#success-message")
        assert success_message.display
        assert "Contact saved" in str(success_message.renderable)
```

### Testing Navigation and Screen Changes

```python
async def test_screen_navigation():
    """Test navigation between screens."""
    app = MultiScreenApp()
    async with app.run_test() as pilot:
        # Start on main screen
        assert isinstance(app.screen, MainScreen)
        
        # Navigate to settings
        await pilot.press("s")  # Settings hotkey
        await pilot.pause()
        
        assert isinstance(app.screen, SettingsScreen)
        
        # Navigate back
        await pilot.press("escape")
        await pilot.pause()
        
        assert isinstance(app.screen, MainScreen)
```

## Mocking External Dependencies

### Mocking API Calls

```python
import pytest
from unittest.mock import AsyncMock, patch
from my_app import WeatherApp

async def test_weather_data_fetch(mocker):
    """Test weather data fetching with mocked API."""
    # Mock the API client
    mock_api_client = mocker.patch('my_app.weather_api_client')
    mock_api_client.get_weather = AsyncMock(return_value={
        "temperature": 25,
        "condition": "sunny"
    })
    
    app = WeatherApp()
    async with app.run_test() as pilot:
        await pilot.click("#refresh-button")
        await pilot.pause()
        
        # Verify API was called
        mock_api_client.get_weather.assert_called_once()
        
        # Verify UI updated
        temp_display = app.query_one("#temperature")
        assert "25°C" in str(temp_display.renderable)
```

### Mocking File System Operations

```python
async def test_file_save_operation(mocker):
    """Test file save with mocked file system."""
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    
    app = TextEditorApp()
    async with app.run_test() as pilot:
        # Enter some text
        await pilot.click("#text-area")
        await pilot.press("H", "e", "l", "l", "o")
        
        # Save file
        await pilot.press("ctrl+s")
        await pilot.pause()
        
        # Verify file operations
        mock_open.assert_called_once_with("untitled.txt", "w")
        mock_open().write.assert_called_with("Hello")
```

### Mocking Database Operations

```python
async def test_database_interaction(mocker):
    """Test database operations with mocked database."""
    mock_db = mocker.patch('my_app.database')
    mock_db.save_user = AsyncMock(return_value={"id": 1, "name": "John"})
    
    app = UserManagementApp()
    async with app.run_test() as pilot:
        # Fill user form
        await pilot.click("#name-input")
        await pilot.press("J", "o", "h", "n")
        
        await pilot.click("#save-button")
        await pilot.pause()
        
        # Verify database call
        mock_db.save_user.assert_called_once_with({"name": "John"})
        
        # Verify UI feedback
        status = app.query_one("#status")
        assert "User saved" in str(status.renderable)
```

## Snapshot Testing

### Installing and Setup

```bash
pip install pytest-textual-snapshot
```

### Basic Snapshot Test

```python
def test_calculator_initial_state(snap_compare):
    """Test calculator appears correctly on startup."""
    assert snap_compare("path/to/calculator.py")

def test_calculator_with_input(snap_compare):
    """Test calculator after entering numbers."""
    assert snap_compare(
        "path/to/calculator.py", 
        press=["1", "2", "3", "+", "4", "5", "6"]
    )

def test_calculator_different_size(snap_compare):
    """Test calculator with different terminal size."""
    assert snap_compare(
        "path/to/calculator.py",
        terminal_size=(100, 50)
    )
```

### Advanced Snapshot Testing

```python
def test_app_with_setup(snap_compare):
    """Test app with custom setup before snapshot."""
    async def setup_app(pilot):
        # Navigate to specific screen
        await pilot.press("s")  # Settings
        await pilot.pause()
        
        # Modify some settings
        await pilot.click("#theme-selector")
        await pilot.press("down", "enter")
        await pilot.pause()
    
    assert snap_compare(
        "path/to/app.py",
        run_before=setup_app
    )
```

## Advanced Testing Patterns

### Testing Timers and Scheduled Tasks

```python
async def test_timer_functionality():
    """Test timer updates correctly."""
    app = TimerApp()
    async with app.run_test() as pilot:
        # Start timer
        await pilot.click("#start-button")
        
        # Fast-forward time (if using textual's timer)
        app.set_timer_fast_forward(True)
        await pilot.pause(0.1)  # Allow timer to tick
        
        timer_display = app.query_one("#timer-display")
        assert "00:01" in str(timer_display.renderable)
```

### Testing Error Handling

```python
async def test_error_handling():
    """Test app handles errors gracefully."""
    app = MyApp()
    async with app.run_test() as pilot:
        # Trigger error condition
        app.some_error_prone_method()
        await pilot.pause()
        
        # Verify error is displayed
        error_message = app.query_one("#error-display")
        assert error_message.has_class("error")
        assert "Error occurred" in str(error_message.renderable)
```

### Testing Reactive Attributes

```python
async def test_reactive_updates():
    """Test reactive attributes update UI correctly."""
    app = ReactiveApp()
    async with app.run_test() as pilot:
        initial_value = app.query_one("#counter").renderable
        
        # Trigger reactive update
        app.counter += 1
        await pilot.pause()
        
        updated_value = app.query_one("#counter").renderable
        assert updated_value != initial_value
```

### Testing Data Tables and Lists

```python
async def test_data_table_operations():
    """Test data table sorting and filtering."""
    app = DataTableApp()
    async with app.run_test() as pilot:
        table = app.query_one("#data-table")
        
        # Test sorting
        await pilot.click("#name-header")
        await pilot.pause()
        
        # Verify sort order changed
        first_row = table.get_row_at(0)
        assert first_row[0] == "Alice"  # Alphabetically first
        
        # Test filtering
        await pilot.click("#filter-input")
        await pilot.press("A", "l", "i", "c", "e")
        await pilot.pause()
        
        # Verify filtered results
        assert table.row_count == 1
```

## Auto-Operating Textual GUI Applications

This section covers how to programmatically control and automate Textual GUI applications without manual interaction, enabling batch processing, scheduled operations, and unattended execution.

### Overview of Automation Approaches

There are several strategies to auto-operate Textual applications:

1. **Headless Automation with Pilot**: Use Textual's testing framework for scripted interactions
2. **Command-Line Integration**: Design apps to accept parameters and run specific workflows
3. **Configuration-Driven Automation**: Use config files to control app behavior
4. **API-Driven Automation**: Expose programmatic interfaces within your app
5. **Batch Mode Operation**: Run apps in non-interactive modes
6. **Script-Based Workflows**: Combine multiple automation techniques

### Method 1: Headless Automation with Pilot

The most straightforward approach is to use Textual's built-in `run_test()` method and Pilot class for automation.

#### Basic Headless Operation

```python
# automation_script.py
import asyncio
from my_textual_app import MyApp

async def automate_app_workflow():
    """Automate a complete workflow in the app."""
    app = MyApp()
    
    async with app.run_test() as pilot:
        # Perform automated sequence
        await pilot.click("#load-data-button")
        await pilot.pause()
        
        # Fill in form automatically
        await pilot.click("#input-field")
        await pilot.press(*"automated input data")
        
        # Process data
        await pilot.click("#process-button")
        await pilot.pause(2.0)  # Wait for processing
        
        # Save results
        await pilot.press("ctrl+s")
        await pilot.pause()
        
        # Extract results for further processing
        result_widget = app.query_one("#results")
        results = str(result_widget.renderable)
        
        return results

# Run the automation
if __name__ == "__main__":
    results = asyncio.run(automate_app_workflow())
    print(f"Automation completed. Results: {results}")
```

#### Batch Processing Multiple Items

```python
# batch_processor.py
import asyncio
import json
from pathlib import Path
from my_app import DataProcessorApp

async def batch_process_files(file_list: list[str]):
    """Process multiple files without user interaction."""
    results = []
    
    for file_path in file_list:
        app = DataProcessorApp()
        
        async with app.run_test() as pilot:
            # Load file
            await pilot.press("ctrl+o")  # Open file dialog
            await pilot.pause()
            
            # Enter file path (assuming input field is focused)
            await pilot.press(*file_path)
            await pilot.press("enter")
            await pilot.pause()
            
            # Process the file
            await pilot.click("#analyze-button")
            await pilot.pause(5.0)  # Wait for analysis
            
            # Extract results
            output_widget = app.query_one("#analysis-output")
            file_results = {
                "file": file_path,
                "analysis": str(output_widget.renderable),
                "timestamp": app.last_processed_time
            }
            results.append(file_results)
            
            # Save individual result
            await pilot.press("ctrl+s")
            await pilot.pause()
    
    return results

# Usage
async def main():
    files_to_process = [
        "/path/to/data1.csv",
        "/path/to/data2.csv",
        "/path/to/data3.csv"
    ]
    
    results = await batch_process_files(files_to_process)
    
    # Save batch results
    with open("batch_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Processed {len(results)} files successfully")

if __name__ == "__main__":
    asyncio.run(main())
```

### Method 2: Configuration-Driven Automation

Design your app to read configuration files and execute predefined workflows.

#### App with Automation Support

```python
# automated_app.py
from textual.app import App, ComposeResult
from textual.widgets import Button, Label, TextArea
import yaml
import asyncio

class AutomatedApp(App):
    """App that can run automated workflows based on config."""
    
    def __init__(self, config_path: str = None, auto_mode: bool = False):
        super().__init__()
        self.config_path = config_path
        self.auto_mode = auto_mode
        self.workflow_steps = []
        
        if config_path:
            self.load_automation_config()
    
    def load_automation_config(self):
        """Load automation configuration from YAML file."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
            self.workflow_steps = config.get("workflow", [])
    
    def compose(self) -> ComposeResult:
        yield Label("Automated Processing App")
        yield Button("Start Processing", id="start-btn")
        yield TextArea("", id="output-area")
    
    async def on_mount(self):
        """Start automation if in auto mode."""
        if self.auto_mode and self.workflow_steps:
            # Start automation after UI is ready
            self.set_timer(1.0, self.execute_automation)
    
    async def execute_automation(self):
        """Execute the predefined automation workflow."""
        output_area = self.query_one("#output-area")
        
        for step in self.workflow_steps:
            action = step.get("action")
            params = step.get("parameters", {})
            
            output_area.text += f"Executing: {action}\n"
            
            if action == "load_data":
                await self.load_data(params.get("source"))
            elif action == "process":
                await self.process_data(params)
            elif action == "save_results":
                await self.save_results(params.get("destination"))
            elif action == "wait":
                await asyncio.sleep(params.get("seconds", 1))
        
        output_area.text += "Automation completed!\n"
        
        # Exit app after automation if configured
        if self.auto_mode:
            self.exit()
    
    async def load_data(self, source: str):
        """Load data from source."""
        # Implement data loading logic
        await asyncio.sleep(1)  # Simulate loading time
    
    async def process_data(self, params: dict):
        """Process loaded data."""
        # Implement processing logic
        await asyncio.sleep(2)  # Simulate processing time
    
    async def save_results(self, destination: str):
        """Save results to destination."""
        # Implement saving logic
        await asyncio.sleep(0.5)  # Simulate saving time

# Automation config file (automation_config.yaml)
"""
workflow:
  - action: load_data
    parameters:
      source: "/path/to/input/data.csv"
  - action: process
    parameters:
      algorithm: "standard"
      output_format: "json"
  - action: wait
    parameters:
      seconds: 2
  - action: save_results
    parameters:
      destination: "/path/to/results/"
"""

# Run in automation mode
if __name__ == "__main__":
    app = AutomatedApp(
        config_path="automation_config.yaml",
        auto_mode=True
    )
    app.run()
```

### Method 3: Command Line Integration

Create apps that can be controlled via command-line arguments for batch operation.

#### CLI-Controllable App

```python
# cli_controlled_app.py
import argparse
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Label, ProgressBar

class CLIControlledApp(App):
    """App that can be controlled via command line arguments."""
    
    def __init__(self, operation: str = None, input_file: str = None, 
                 output_file: str = None, headless: bool = False):
        super().__init__()
        self.operation = operation
        self.input_file = input_file
        self.output_file = output_file
        self.headless = headless
        self.progress = 0
    
    def compose(self) -> ComposeResult:
        yield Label(f"Operation: {self.operation or 'Interactive Mode'}")
        yield Label(f"Input: {self.input_file or 'None'}")
        yield Label(f"Output: {self.output_file or 'None'}")
        yield ProgressBar(total=100, show_eta=True, id="progress")
    
    async def on_mount(self):
        """Start automated operation if specified."""
        if self.operation:
            self.set_timer(0.5, self.execute_operation)
    
    async def execute_operation(self):
        """Execute the specified operation."""
        progress_bar = self.query_one("#progress")
        
        if self.operation == "convert":
            await self.convert_data()
        elif self.operation == "analyze":
            await self.analyze_data()
        elif self.operation == "validate":
            await self.validate_data()
        
        if self.headless:
            self.exit()
    
    async def convert_data(self):
        """Convert data with progress updates."""
        progress_bar = self.query_one("#progress")
        
        # Simulate conversion with progress
        for i in range(101):
            progress_bar.progress = i
            await asyncio.sleep(0.02)  # Simulate work
        
        # Actual conversion logic would go here
        print(f"Converted {self.input_file} to {self.output_file}")
    
    async def analyze_data(self):
        """Analyze data with progress updates."""
        progress_bar = self.query_one("#progress")
        
        # Simulate analysis
        for i in range(101):
            progress_bar.progress = i
            await asyncio.sleep(0.03)
        
        print(f"Analysis of {self.input_file} completed")
    
    async def validate_data(self):
        """Validate data."""
        progress_bar = self.query_one("#progress")
        progress_bar.progress = 100
        print(f"Validation of {self.input_file} completed")

def main():
    parser = argparse.ArgumentParser(description="CLI Controlled TUI App")
    parser.add_argument("--operation", choices=["convert", "analyze", "validate"],
                       help="Operation to perform")
    parser.add_argument("--input", help="Input file path")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--headless", action="store_true",
                       help="Run without user interaction")
    
    args = parser.parse_args()
    
    app = CLIControlledApp(
        operation=args.operation,
        input_file=args.input,
        output_file=args.output,
        headless=args.headless
    )
    
    app.run()

if __name__ == "__main__":
    main()

# Usage examples:
# python cli_controlled_app.py --operation convert --input data.csv --output data.json --headless
# python cli_controlled_app.py --operation analyze --input data.csv
```

### Method 4: Scheduled Automation

Use system scheduling tools to run automated workflows.

#### Scheduled Automation Script

```python
# scheduled_automation.py
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from my_app import ReportGeneratorApp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

async def generate_daily_report():
    """Generate daily report automatically."""
    logging.info("Starting daily report generation")
    
    app = ReportGeneratorApp()
    
    try:
        async with app.run_test() as pilot:
            # Set date range for yesterday
            await pilot.click("#date-picker")
            await pilot.press("ctrl+a")  # Select all
            await pilot.press(*datetime.now().strftime("%Y-%m-%d"))
            
            # Select report type
            await pilot.click("#report-type-dropdown")
            await pilot.press("down", "down", "enter")  # Select "Daily Summary"
            
            # Generate report
            await pilot.click("#generate-button")
            await pilot.pause(10.0)  # Wait for report generation
            
            # Export report
            await pilot.press("ctrl+e")  # Export
            await pilot.pause(2.0)
            
            # Get report status
            status_widget = app.query_one("#status-label")
            status = str(status_widget.renderable)
            
            if "completed" in status.lower():
                logging.info("Daily report generated successfully")
                return True
            else:
                logging.error(f"Report generation failed: {status}")
                return False
                
    except Exception as e:
        logging.error(f"Error during report generation: {e}")
        return False

async def cleanup_old_files():
    """Clean up old report files."""
    logging.info("Starting file cleanup")
    
    reports_dir = Path("./reports")
    if reports_dir.exists():
        old_files = []
        for file in reports_dir.glob("*.pdf"):
            if file.stat().st_mtime < (datetime.now().timestamp() - 30*24*3600):  # 30 days
                old_files.append(file)
                file.unlink()
        
        logging.info(f"Cleaned up {len(old_files)} old files")

async def main():
    """Main automation routine."""
    logging.info("Starting scheduled automation")
    
    # Generate report
    success = await generate_daily_report()
    
    if success:
        # Clean up old files
        await cleanup_old_files()
        logging.info("Automation completed successfully")
    else:
        logging.error("Automation failed")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())

# Schedule with cron (Linux/Mac) or Task Scheduler (Windows)
# Cron example: 0 6 * * * /usr/bin/python3 /path/to/scheduled_automation.py
```

### Method 5: API-Driven Automation

Create apps that expose internal APIs for programmatic control.

#### App with Internal API

```python
# api_driven_app.py
from textual.app import App, ComposeResult
from textual.widgets import Label, Button
import asyncio
import json
from typing import Any, Dict

class APIControlledApp(App):
    """App that can be controlled via internal API."""
    
    def __init__(self):
        super().__init__()
        self.api_queue = asyncio.Queue()
        self.api_responses = {}
        self.request_id = 0
    
    def compose(self) -> ComposeResult:
        yield Label("API Controlled App", id="title")
        yield Label("Status: Ready", id="status")
        yield Button("Manual Operation", id="manual-btn")
    
    async def on_mount(self):
        """Start API processor."""
        self.set_timer(0.1, self.process_api_requests, repeat=True)
    
    async def process_api_requests(self):
        """Process incoming API requests."""
        try:
            while not self.api_queue.empty():
                request = await self.api_queue.get()
                await self.handle_api_request(request)
        except asyncio.QueueEmpty:
            pass
    
    async def handle_api_request(self, request: Dict[str, Any]):
        """Handle a single API request."""
        command = request.get("command")
        params = request.get("params", {})
        request_id = request.get("id")
        
        status_label = self.query_one("#status")
        
        try:
            if command == "set_title":
                title_label = self.query_one("#title")
                title_label.update(params.get("text", "Default Title"))
                response = {"success": True, "message": "Title updated"}
                
            elif command == "process_data":
                status_label.update("Status: Processing...")
                await asyncio.sleep(2)  # Simulate processing
                status_label.update("Status: Complete")
                response = {"success": True, "data": "processed_result"}
                
            elif command == "get_status":
                current_status = str(status_label.renderable)
                response = {"success": True, "status": current_status}
                
            elif command == "shutdown":
                response = {"success": True, "message": "Shutting down"}
                self.set_timer(1.0, self.exit)
                
            else:
                response = {"success": False, "error": f"Unknown command: {command}"}
        
        except Exception as e:
            response = {"success": False, "error": str(e)}
        
        # Store response for retrieval
        if request_id:
            self.api_responses[request_id] = response
    
    # API Methods for external control
    async def api_call(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make an API call to the app."""
        self.request_id += 1
        request = {
            "id": self.request_id,
            "command": command,
            "params": params or {}
        }
        
        await self.api_queue.put(request)
        
        # Wait for response
        while self.request_id not in self.api_responses:
            await asyncio.sleep(0.1)
        
        response = self.api_responses.pop(self.request_id)
        return response

# External automation script
async def automate_via_api():
    """Automate the app using its internal API."""
    app = APIControlledApp()
    
    # Run app in background
    async def run_app():
        app.run()
    
    # Start app
    app_task = asyncio.create_task(run_app())
    await asyncio.sleep(1)  # Let app initialize
    
    try:
        # Control app via API
        await app.api_call("set_title", {"text": "Automated Processing"})
        
        result = await app.api_call("process_data", {"input": "test_data"})
        print(f"Processing result: {result}")
        
        status = await app.api_call("get_status")
        print(f"Current status: {status}")
        
        # Shutdown app
        await app.api_call("shutdown")
        
    except Exception as e:
        print(f"Automation error: {e}")
    
    # Wait for app to shutdown
    await app_task

if __name__ == "__main__":
    asyncio.run(automate_via_api())
```

### Method 6: Environment Variable Control

Use environment variables to control app behavior for different automation scenarios.

```python
# env_controlled_app.py
import os
from textual.app import App, ComposeResult
from textual.widgets import Label

class EnvironmentControlledApp(App):
    """App controlled by environment variables."""
    
    def __init__(self):
        super().__init__()
        
        # Read automation settings from environment
        self.auto_mode = os.getenv("APP_AUTO_MODE", "false").lower() == "true"
        self.input_source = os.getenv("APP_INPUT_SOURCE", "manual")
        self.output_dest = os.getenv("APP_OUTPUT_DEST", "screen")
        self.operation_type = os.getenv("APP_OPERATION", "interactive")
        self.timeout = int(os.getenv("APP_TIMEOUT", "30"))
    
    def compose(self) -> ComposeResult:
        yield Label(f"Mode: {'Automatic' if self.auto_mode else 'Interactive'}")
        yield Label(f"Input: {self.input_source}")
        yield Label(f"Output: {self.output_dest}")
        yield Label(f"Operation: {self.operation_type}")
    
    async def on_mount(self):
        if self.auto_mode:
            self.set_timer(1.0, self.run_automated_operation)
            
            # Set timeout for automatic shutdown
            if self.timeout > 0:
                self.set_timer(self.timeout, self.exit)
    
    async def run_automated_operation(self):
        """Run the automated operation based on environment config."""
        if self.operation_type == "batch_process":
            await self.batch_process()
        elif self.operation_type == "data_sync":
            await self.sync_data()
        elif self.operation_type == "report_gen":
            await self.generate_report()
    
    async def batch_process(self):
        # Implementation for batch processing
        pass
    
    async def sync_data(self):
        # Implementation for data synchronization
        pass
    
    async def generate_report(self):
        # Implementation for report generation
        pass

# Usage with environment variables:
# APP_AUTO_MODE=true APP_OPERATION=batch_process python env_controlled_app.py
```

### Automation Best Practices

#### 1. Error Handling and Recovery

```python
async def robust_automation():
    """Automation with proper error handling."""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            app = MyApp()
            async with app.run_test() as pilot:
                # Your automation logic here
                await pilot.click("#process-button")
                await pilot.pause()
                
                # Verify success
                result = app.query_one("#result-status")
                if "success" in str(result.renderable).lower():
                    return True
                else:
                    raise Exception("Processing failed")
                    
        except Exception as e:
            retry_count += 1
            logging.warning(f"Attempt {retry_count} failed: {e}")
            if retry_count >= max_retries:
                logging.error("All retry attempts failed")
                return False
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
    
    return False
```

#### 2. Progress Monitoring

```python
async def monitored_automation():
    """Automation with progress monitoring."""
    app = MyApp()
    
    async with app.run_test() as pilot:
        # Start long-running operation
        await pilot.click("#start-processing")
        
        # Monitor progress
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            progress_widget = app.query_one("#progress-bar")
            progress = progress_widget.progress
            
            print(f"Progress: {progress}%")
            
            if progress >= 100:
                print("Processing completed!")
                break
                
            await pilot.pause(5.0)  # Check every 5 seconds
        else:
            raise TimeoutError("Operation timed out")
```

#### 3. Resource Management

```python
import psutil
import asyncio

async def resource_aware_automation():
    """Automation that monitors system resources."""
    
    # Check system resources before starting
    if psutil.cpu_percent(interval=1) > 80:
        print("CPU usage too high, waiting...")
        await asyncio.sleep(60)
    
    if psutil.virtual_memory().percent > 85:
        print("Memory usage too high, aborting")
        return False
    
    # Proceed with automation
    app = MyApp()
    async with app.run_test() as pilot:
        # Monitor resources during operation
        async def resource_monitor():
            while True:
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory().percent
                
                if cpu > 90 or memory > 90:
                    print("Resource usage critical, pausing...")
                    await asyncio.sleep(30)
                
                await asyncio.sleep(10)
        
        # Start resource monitoring
        monitor_task = asyncio.create_task(resource_monitor())
        
        try:
            # Your automation logic
            await pilot.click("#heavy-operation")
            await pilot.pause(60)
            
        finally:
            monitor_task.cancel()
```

### Integration with External Systems

#### Docker Container Automation

```dockerfile
# Dockerfile for automated processing
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set environment for headless operation
ENV TERM=xterm-256color
ENV APP_AUTO_MODE=true
ENV APP_TIMEOUT=600

CMD ["python", "automated_app.py"]
```

#### CI/CD Integration

```yaml
# .github/workflows/automated-processing.yml
name: Automated Data Processing

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  workflow_dispatch:

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run automated processing
      env:
        APP_AUTO_MODE: true
        APP_INPUT_SOURCE: ${{ secrets.DATA_SOURCE }}
        APP_OUTPUT_DEST: ${{ secrets.OUTPUT_LOCATION }}
      run: |
        python automated_processor.py
    
    - name: Upload results
      uses: actions/upload-artifact@v2
      with:
        name: processing-results
        path: output/
```

This comprehensive automation section provides multiple approaches for running Textual applications without manual interaction, from simple headless automation to complex scheduled workflows integrated with external systems.

## Best Practices

### 1. Test Structure and Organization

```python
# test_my_app.py
import pytest
from my_app import MyApp

class TestMyAppBasicFunctionality:
    """Group related tests together."""
    
    async def test_app_initialization(self):
        """Test app starts with correct initial state."""
        pass
    
    async def test_basic_navigation(self):
        """Test basic navigation works."""
        pass

class TestMyAppAdvancedFeatures:
    """Test complex features separately."""
    
    async def test_data_processing(self):
        """Test data processing features."""
        pass
```

### 2. Use Fixtures for Common Setup

```python
@pytest.fixture
async def app_with_data():
    """Fixture providing app with test data loaded."""
    app = MyApp()
    async with app.run_test() as pilot:
        # Load test data
        await pilot.click("#load-test-data")
        await pilot.pause()
        yield app, pilot

async def test_with_data(app_with_data):
    """Test using fixture."""
    app, pilot = app_with_data
    # Test operations on app with data
```

### 3. Test Both Happy Path and Edge Cases

```python
async def test_input_validation_valid():
    """Test valid input is accepted."""
    # Test happy path
    pass

async def test_input_validation_empty():
    """Test empty input is rejected."""
    # Test edge case
    pass

async def test_input_validation_too_long():
    """Test overly long input is handled."""
    # Test edge case
    pass
```

### 4. Use Descriptive Test Names and Documentation

```python
async def test_user_can_save_document_after_making_changes():
    """
    Test that a user can save a document after making changes.
    
    Steps:
    1. Open document
    2. Make changes
    3. Save document
    4. Verify changes are persisted
    """
    pass
```

### 5. Verify State Changes, Not Implementation Details

```python
# Good - tests behavior
async def test_button_click_changes_counter():
    app = CounterApp()
    async with app.run_test() as pilot:
        await pilot.click("#increment")
        counter_display = app.query_one("#counter")
        assert "1" in str(counter_display.renderable)

# Bad - tests implementation
async def test_button_click_calls_increment_method():
    # Don't test that specific methods are called
    pass
```

## Common Pitfalls and Solutions

### 1. Race Conditions and Timing Issues

**Problem**: Tests fail intermittently due to timing.

**Solution**: Always use `pilot.pause()` after actions that trigger async operations.

```python
async def test_async_operation():
    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.click("#async-button")
        await pilot.pause()  # Wait for async operation
        
        # Now safe to assert
        assert app.operation_completed
```

### 2. Testing Modal Dialogs and Pop-ups

**Problem**: Can't interact with modal dialogs.

**Solution**: Use screen stacking and proper selectors.

```python
async def test_modal_dialog():
    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.click("#show-modal")
        await pilot.pause()
        
        # Modal is now on top of screen stack
        modal = app.screen_stack[-1]  # Get top screen
        await pilot.click("#modal-ok-button")
        await pilot.pause()
        
        # Modal should be dismissed
        assert len(app.screen_stack) == 1
```

### 3. Screen Size Dependencies

**Problem**: Tests fail on different terminal sizes.

**Solution**: Set explicit size in tests or test multiple sizes.

```python
async def test_responsive_layout():
    app = MyApp()
    # Test with specific size
    async with app.run_test(size=(80, 24)) as pilot:
        # Test layout at standard size
        pass
    
    # Test with larger size
    async with app.run_test(size=(120, 40)) as pilot:
        # Test layout adapts correctly
        pass
```

### 4. Debugging Test Failures

**Problem**: Hard to debug why tests are failing.

**Solution**: Use logging and pilot debugging features.

```python
import logging

async def test_with_debugging():
    app = MyApp()
    async with app.run_test() as pilot:
        # Enable logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Take screenshot for debugging
        # (Available in some versions)
        if hasattr(pilot, 'screenshot'):
            screenshot = await pilot.screenshot()
            print(f"Screenshot: {screenshot}")
        
        # Log app state
        logging.debug(f"App state: {app.some_state}")
```

### 5. Testing Performance

**Problem**: Need to ensure app performs well.

**Solution**: Use timing assertions and profiling.

```python
import time

async def test_performance():
    app = MyApp()
    async with app.run_test() as pilot:
        start_time = time.time()
        
        await pilot.click("#heavy-operation")
        await pilot.pause()
        
        end_time = time.time()
        
        # Ensure operation completes within reasonable time
        assert (end_time - start_time) < 2.0  # 2 seconds max
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest test_my_app.py

# Run specific test
pytest test_my_app.py::test_button_click

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=my_app
```

### Snapshot Test Management

```bash
# Run tests and update snapshots if they look correct
pytest --snapshot-update

# Run tests without snapshot comparison (for debugging)
pytest --snapshot-no-compare
```

### Continuous Integration

Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-textual-snapshot
    - name: Run tests
      run: pytest
    - name: Upload snapshot report
      uses: actions/upload-artifact@v2
      if: failure()
      with:
        name: snapshot-report
        path: snapshot_report.html
```

This comprehensive guide should help you build robust, maintainable tests for your Textual applications. Remember to start with simple tests and gradually add more complex scenarios as your application grows.
