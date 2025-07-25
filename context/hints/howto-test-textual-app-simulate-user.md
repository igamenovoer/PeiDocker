# How to Test Textual Apps by Simulating User Input and Taking Screenshots

This guide explains how to automate testing for your [Textual](https://textual.textualize.io/) applications by simulating user interactions and capturing snapshots of the UI. This allows for robust testing in a headless environment, which doesn't require a visible window and won't interfere with your desktop.

## Core Concepts

Testing Textual applications involves three main components:

1.  **Test Runner**: We use `pytest` with the `pytest-asyncio` plugin to handle asynchronous testing.
2.  **App Pilot**: Textual provides a `Pilot` object to programmatically interact with your app (e.g., press keys, click buttons).
3.  **Snapshot Testing**: The `pytest-textual-snapshot` plugin captures the state of your app's UI as an SVG image for visual regression testing.

This setup works seamlessly across different platforms, including Windows, without requiring a graphical display.

## Setting up the Environment

First, install the necessary packages:

```bash
pip install textual pytest pytest-asyncio pytest-textual-snapshot
```

It's recommended to configure `pytest` to automatically handle async tests. Add the following to your `pytest.ini` or `pyproject.toml` file:

**`pytest.ini`:**
```ini
[pytest]
asyncio_mode = auto
```

## Simulating User Input with `Pilot`

To test an app, you run it using `app.run_test()` instead of `app.run()`. This method is an async context manager that provides a `Pilot` object for scripting interactions.

### Example: Testing Key Presses and Clicks

Consider a simple app where pressing buttons changes the background color.

```python
# in rgb_app.py
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button

class RGBApp(App):
    BINDINGS = [
        ("r", "switch_color('red')", "Red"),
        ("g", "switch_color('green')", "Green"),
        ("b", "switch_color('blue')", "Blue"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Button("Red", id="red")
            yield Button("Green", id="green")
            yield Button("Blue", id="blue")

    def action_switch_color(self, color: str) -> None:
        self.screen.styles.background = color

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id:
            self.action_switch_color(event.button.id)
```

Here is how you would write a test for it:

```python
# in test_rgb_app.py
import pytest
from textual.color import Color
from rgb_app import RGBApp

async def test_key_presses():
    """Test that pressing keys changes the background color."""
    app = RGBApp()
    async with app.run_test() as pilot:
        await pilot.press("r")
        assert app.screen.styles.background == Color.parse("red")

        await pilot.press("g")
        assert app.screen.styles.background == Color.parse("green")

async def test_button_clicks():
    """Test that clicking buttons changes the background color."""
    app = RGBApp()
    async with app.run_test() as pilot:
        await pilot.click("#red")
        assert app.screen.styles.background == Color.parse("red")

        await pilot.click("#green")
        assert app.screen.styles.background == Color.parse("green")
```

The `app.run_test()` context manager runs the app in a **headless mode**, meaning no UI is physically rendered on your screen. The `pilot` object then simulates user actions like `press()` and `click()`. You can also use `pilot.pause()` to wait for the UI to settle or `pilot.hover()` to simulate mouse-over effects.

## Taking Screenshots with Snapshot Testing

The `pytest-textual-snapshot` plugin allows you to take "screenshots" of your terminal UI. These are not traditional image screenshots but rather SVG files that represent the terminal's state.

### Example: Snapshot Test

To create a snapshot test, use the `snap_compare` fixture provided by the plugin.

```python
# in test_snapshot.py
def test_app_initial_state(snap_compare):
    """Test the initial appearance of the app."""
    assert snap_compare("path/to/your/app_file.py")
```

**How it works:**

1.  **First Run**: The first time you run `pytest`, the test will fail because no "golden" snapshot exists. An HTML report will be generated with the captured SVG.
2.  **Approve Snapshot**: Open the report (link in the console output) and verify the UI looks correct. Then, run `pytest --snapshot-update` to approve the current look as the reference.
3.  **Subsequent Runs**: Now, `pytest` will pass as long as the UI doesn't change. If a change in your code alters the UI, the test will fail, and the report will show a diff between the old and new UI, helping you catch unintended visual regressions.

You can also simulate user input before taking the snapshot:

```python
def test_app_after_interaction(snap_compare):
    """Test the appearance after pressing a key."""
    assert snap_compare(
        "path/to/your/app_file.py",
        press=["r", "g"]  # Simulate pressing 'r' then 'g'
    )
```

## Considerations for Windows

Textual's testing tools are cross-platform and work well on Windows. Since the tests run headlessly and the "screenshots" are SVG representations of the terminal state, there are no special requirements or caveats for the Windows platform. You do not need to worry about window focus or GUI interference. The process is identical to running tests on Linux or macOS.

For more details, refer to the official [Textual documentation on testing](https://textual.textualize.io/guide/testing/).
