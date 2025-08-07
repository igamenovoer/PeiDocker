# How to Test Textual GUI Applications in Headless Manner

This guide covers how to test Textual TUI (Terminal User Interface) applications programmatically without requiring a visible terminal or GUI display, making it ideal for automated testing, CI/CD pipelines, and unit testing.

## Overview

Textual provides excellent headless testing capabilities through its `run_test()` method and `Pilot` object, allowing you to:

- Test TUI applications without any visual display
- Simulate user interactions programmatically 
- Run tests in CI/CD environments without GUI
- Verify application state changes
- Perform automated testing of complex user workflows

## Key Testing Components

### 1. `App.run_test()` Method

The core method for headless testing that returns a `Pilot` object for interaction simulation.

```python
async with app.run_test() as pilot:
    # Test code here
    pass
```

### 2. `Pilot` Object

Provides methods to simulate user interactions:

- `pilot.press()` - Simulate key presses
- `pilot.click()` - Simulate mouse clicks
- `pilot.pause()` - Wait for pending operations
- `pilot.hover()` - Simulate mouse hover

## Basic Testing Setup

### Installation

```bash
pip install pytest pytest-asyncio textual
```

### Pytest Configuration

Create `pytest.ini`:

```ini
[tool:pytest]
asyncio_mode = auto
testpaths = tests
```

Or in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## Testing Patterns

### 1. Basic App Testing

```python
import pytest
from textual.app import App
from textual.widgets import Button, Static

class SimpleApp(App):
    def compose(self):
        yield Static("Hello", id="greeting")
        yield Button("Click me", id="btn")
    
    def on_button_pressed(self, event):
        self.query_one("#greeting").update("Clicked!")

@pytest.mark.asyncio
async def test_button_click():
    app = SimpleApp()
    async with app.run_test() as pilot:
        # Verify initial state
        greeting = app.query_one("#greeting")
        assert greeting.renderable == "Hello"
        
        # Simulate button click
        await pilot.click("#btn")
        
        # Verify state change
        assert greeting.renderable == "Clicked!"
```

### 2. Key Press Testing

```python
@pytest.mark.asyncio
async def test_key_presses():
    app = MyApp()
    async with app.run_test() as pilot:
        # Simulate individual key presses
        await pilot.press("h", "e", "l", "l", "o")
        
        # Simulate special keys
        await pilot.press("enter")
        await pilot.press("ctrl+c")
        await pilot.press("escape")
        
        # Verify results
        text_input = app.query_one("#text_input")
        assert "hello" in text_input.value
```

### 3. Testing with Custom Terminal Size

```python
@pytest.mark.asyncio
async def test_responsive_layout():
    app = ResponsiveApp()
    
    # Test with small terminal
    async with app.run_test(size=(40, 20)) as pilot:
        container = app.query_one("#main-container")
        assert container.size.width <= 40
    
    # Test with large terminal
    async with app.run_test(size=(120, 40)) as pilot:
        container = app.query_one("#main-container")
        assert container.size.width <= 120
```

### 4. Testing Async Operations

```python
@pytest.mark.asyncio
async def test_async_operations():
    app = AsyncApp()
    async with app.run_test() as pilot:
        # Trigger async operation
        await pilot.press("l")  # Load data
        
        # Wait for async operations to complete
        await pilot.pause()
        
        # Or wait with delay
        await pilot.pause(delay=0.1)
        
        # Verify async operation results
        status = app.query_one("#status")
        assert "Loaded" in status.renderable
```

### 5. Testing Mouse Interactions

```python
@pytest.mark.asyncio
async def test_mouse_interactions():
    app = MouseApp()
    async with app.run_test() as pilot:
        # Click at specific coordinates
        await pilot.click(offset=(10, 5))
        
        # Click on specific widget
        await pilot.click("#my-button")
        
        # Double click
        await pilot.click("#my-button", times=2)
        
        # Click with modifiers
        await pilot.click("#slider", control=True)
        
        # Hover over element
        await pilot.hover("#tooltip-trigger")
```

## Advanced Testing Techniques

### 1. Testing Custom Widgets

```python
from textual.widget import Widget

class CounterWidget(Widget):
    def __init__(self):
        super().__init__()
        self.count = 0
    
    def render(self):
        return f"Count: {self.count}"
    
    def action_increment(self):
        self.count += 1

@pytest.mark.asyncio
async def test_custom_widget():
    app = App()
    counter = CounterWidget()
    
    async with app.run_test() as pilot:
        await app.mount(counter)
        
        # Test initial state
        assert counter.count == 0
        
        # Trigger action
        counter.action_increment()
        assert counter.count == 1
```

### 2. Testing with Fixtures

```python
@pytest.fixture
async def app_with_data():
    app = DataApp()
    # Setup test data
    app.load_test_data()
    return app

@pytest.mark.asyncio
async def test_data_operations(app_with_data):
    async with app_with_data.run_test() as pilot:
        # Test operations on pre-loaded data
        await pilot.press("d")  # Delete item
        assert len(app_with_data.items) == 0
```

### 3. Mocking External Dependencies

```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
@patch('my_app.external_api_call', new_callable=AsyncMock)
async def test_api_integration(mock_api):
    mock_api.return_value = {"status": "success"}
    
    app = ApiApp()
    async with app.run_test() as pilot:
        await pilot.press("f")  # Fetch data
        await pilot.pause()
        
        # Verify API was called
        mock_api.assert_called_once()
        
        # Verify UI updated
        status = app.query_one("#api-status")
        assert "success" in status.renderable
```

### 4. Testing Error Conditions

```python
@pytest.mark.asyncio
async def test_error_handling():
    app = ErrorApp()
    async with app.run_test() as pilot:
        # Trigger error condition
        await pilot.press("e")  # Error action
        
        # Verify error handling
        error_display = app.query_one("#error-message")
        assert error_display.has_class("error")
        assert "Error occurred" in error_display.renderable
```

## Testing Best Practices

### 1. Use Descriptive Test Names

```python
@pytest.mark.asyncio
async def test_user_can_navigate_to_settings_and_change_theme():
    # Test implementation
    pass
```

### 2. Test State Isolation

```python
@pytest.mark.asyncio
async def test_each_test_gets_fresh_app():
    app = MyApp()  # Create fresh app instance
    async with app.run_test() as pilot:
        # Test in isolation
        pass
```

### 3. Test Multiple Scenarios

```python
@pytest.mark.parametrize("input_value,expected", [
    ("valid@email.com", True),
    ("invalid-email", False),
    ("", False),
])
@pytest.mark.asyncio
async def test_email_validation(input_value, expected):
    app = EmailApp()
    async with app.run_test() as pilot:
        # Enter email
        email_input = app.query_one("#email")
        email_input.value = input_value
        
        # Trigger validation
        await pilot.press("enter")
        
        # Check result
        is_valid = app.query_one("#validation").has_class("valid")
        assert is_valid == expected
```

### 4. Use Async Context Managers Properly

```python
@pytest.mark.asyncio
async def test_proper_cleanup():
    app = ResourceApp()
    async with app.run_test() as pilot:
        # All resources automatically cleaned up
        # when exiting context manager
        pass
```

## Common Patterns and Solutions

### 1. Waiting for Async Operations

```python
@pytest.mark.asyncio
async def test_loading_data():
    app = LoadingApp()
    async with app.run_test() as pilot:
        # Start loading
        await pilot.press("l")
        
        # Wait for loading to complete
        await pilot.pause()
        
        # Alternative: wait with timeout
        import asyncio
        await asyncio.sleep(0.1)
        
        # Verify loading completed
        assert not app.is_loading
```

### 2. Testing Modal Dialogs

```python
@pytest.mark.asyncio
async def test_modal_dialog():
    app = ModalApp()
    async with app.run_test() as pilot:
        # Open modal
        await pilot.press("m")
        
        # Interact with modal
        await pilot.click("#modal-ok")
        
        # Verify modal closed
        assert not app.query("#modal")
```

### 3. Testing Navigation

```python
@pytest.mark.asyncio
async def test_screen_navigation():
    app = MultiScreenApp()
    async with app.run_test() as pilot:
        # Navigate to different screen
        await pilot.press("2")
        
        # Verify current screen
        assert app.screen.name == "settings"
        
        # Navigate back
        await pilot.press("escape")
        assert app.screen.name == "main"
```

## Continuous Integration Setup

### GitHub Actions Example

```yaml
name: Test Textual App
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    - name: Run headless tests
      run: pytest tests/
```

## Common Issues and Solutions

### 1. Race Conditions

```python
# Problem: Test fails due to timing
@pytest.mark.asyncio
async def test_with_race_condition():
    app = AsyncApp()
    async with app.run_test() as pilot:
        await pilot.press("l")
        # State might not be updated yet!
        assert app.data_loaded  # May fail

# Solution: Use pilot.pause()
@pytest.mark.asyncio
async def test_without_race_condition():
    app = AsyncApp()
    async with app.run_test() as pilot:
        await pilot.press("l")
        await pilot.pause()  # Wait for async operations
        assert app.data_loaded  # Now reliable
```

### 2. Widget Not Found

```python
# Ensure widgets exist before querying
@pytest.mark.asyncio
async def test_widget_exists():
    app = DynamicApp()
    async with app.run_test() as pilot:
        # Trigger widget creation
        await pilot.press("c")
        await pilot.pause()
        
        # Now safe to query
        widget = app.query_one("#dynamic-widget")
        assert widget is not None
```

## References

- [Textual Testing Documentation](https://textual.textualize.io/guide/testing/)
- [Textual API Reference](https://textual.textualize.io/api/)
- [Pytest Asyncio Plugin](https://pytest-asyncio.readthedocs.io/)
- [Textual GitHub Repository](https://github.com/Textualize/textual)

## Source Links

- [Textual Testing Guide](https://textual.textualize.io/guide/testing/)
- [Textual App.run_test API](https://textual.textualize.io/api/app/#textual.app.App.run_test)
- [Pilot API Documentation](https://textual.textualize.io/api/pilot/)
