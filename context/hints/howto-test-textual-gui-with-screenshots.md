# How to Test Textual GUI Apps with Screenshots for Visual Comparison

This guide covers testing Textual GUI applications using Claude Code CLI, capturing screenshots for visual comparison with design specifications, and best practices to avoid common pitfalls.

## Overview

Testing Textual apps involves several approaches:
1. **Interactive testing** - Running the app manually
2. **Snapshot testing** - Automated visual regression testing 
3. **Screenshot comparison** - Comparing with design specs
4. **Unit testing** - Testing individual components

## Starting Up Textual Apps

### Basic Startup Methods

```bash
# Direct Python execution
python my_textual_app.py

# Using Textual CLI (recommended)
textual run my_textual_app.py

# With development mode (live CSS reloading)
textual run my_textual_app.py --dev

# For demos and examples
python -m textual
textual demo
```

### Running in Separate Windows/Terminals (Avoiding CLI Clutter)

When using Claude Code CLI, Textual apps will take over the stdout and clutter the original terminal. Here are solutions:

#### Windows Solutions

```powershell
# Open in new Windows Terminal tab (recommended)
wt -w 0 nt powershell -Command "textual run my_app.py"

# Open in completely new terminal window
Start-Process powershell -ArgumentList "-Command", "textual run my_app.py"

# Using cmd (alternative)
start cmd /k "textual run my_app.py"

# Background process with output redirection (best for testing)
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "my_app.py" -RedirectStandardOutput "nul" -RedirectStandardError "nul"

# Using wt with specific profile (if configured)
wt -p "PowerShell" -d . powershell -Command "textual run my_app.py"
```

#### macOS/Linux Solutions

```bash
# macOS: Open in new Terminal window (best practice)
osascript -e 'tell application "Terminal" to do script "textual run my_app.py"'

# macOS: Open in new iTerm2 window
osascript -e 'tell application "iTerm2" to create window with default profile command "textual run my_app.py"'

# macOS: Using open command (elegant solution)
open -a Terminal --args -e "textual run my_app.py"

# Background process (Linux/macOS) - detached from current session
nohup textual run my_app.py > /dev/null 2>&1 &

# Using screen/tmux for detached sessions (best for long-running apps)
screen -S textual_app -d -m textual run my_app.py
tmux new-session -d -s textual_app 'textual run my_app.py'

# Linux: Open in new gnome-terminal window
gnome-terminal --window -- bash -c "textual run my_app.py; exec bash"

# Linux: Open in new tab (if gnome-terminal is already running)
gnome-terminal --tab --title="Textual App" -- bash -c "textual run my_app.py; exec bash"

# Using konsole (KDE)
konsole --new-tab -e bash -c "textual run my_app.py; exec bash"
```

#### Cross-Platform Solutions

```python
# Modern subprocess approach - best practice for Python 3.7+
import subprocess
import sys

def launch_detached_textual_app(app_path):
    """Launch Textual app detached from current process"""
    if sys.platform == "win32":
        # Windows: CREATE_NEW_CONSOLE for separate window
        subprocess.Popen(
            [sys.executable, app_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        # Unix-like: start_new_session for complete detachment
        subprocess.Popen(
            [sys.executable, app_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

# Command line alternatives
# Using textual with output redirection (cross-platform)
textual run my_app.py > textual_output.log 2>&1 &  # Unix-like
textual run my_app.py >textual_output.log 2>&1     # Windows (without &)

# Using Python to launch with proper detachment
python -c "
import subprocess
import sys
subprocess.Popen([sys.executable, 'my_app.py'], 
                 creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform=='win32' else 0,
                 stdout=subprocess.DEVNULL, 
                 stderr=subprocess.DEVNULL,
                 start_new_session=sys.platform!='win32')
"
```

### Testing Terminal Size

```bash
# Run with specific terminal dimensions
textual run my_app.py --size 80x24

# Test responsive layouts
textual run my_app.py --size 120x40
```

## Screenshot Capture Methods

### 1. Built-in Screenshot Command

```bash
# Capture after 5 seconds delay
textual run my_app.py --screenshot 5

# This generates SVG screenshots automatically
```

### 2. Pytest Snapshot Testing (Recommended)

First install the pytest plugin:

```bash
pip install pytest-textual-snapshot
```

Create a test file:

```python
def test_my_app_visual(snap_compare):
    # Basic snapshot test
    assert snap_compare("path/to/my_app.py")

def test_app_with_interactions(snap_compare):
    # Test with key presses
    assert snap_compare("path/to/my_app.py", press=["1", "2", "3", "enter"])

def test_app_custom_size(snap_compare):
    # Test with specific terminal size
    assert snap_compare("path/to/my_app.py", terminal_size=(100, 50))

def test_app_with_setup(snap_compare):
    # Run custom code before snapshot
    async def run_before(pilot) -> None:
        await pilot.hover("#my-button")
        await pilot.click("#submit")
    
    assert snap_compare("path/to/my_app.py", run_before=run_before)
```

Run the tests:

```bash
# Generate initial snapshots
pytest test_my_app.py

# Update snapshots after changes
pytest --snapshot-update test_my_app.py

# Run all snapshot tests
pytest -vv tests/snapshot_tests/
```

### 3. Manual Screenshot Tools

For terminal screenshots outside of Textual:

```bash
# Using built-in tools (varies by OS)
# Windows: Windows Terminal has screenshot features
# macOS: Command+Shift+4 for partial screen
# Linux: gnome-screenshot, scrot, or similar

# Terminal-specific screenshot tools
# Some terminals support built-in screenshot functionality
```

## Visual Comparison Workflow

### 1. Design Spec Comparison Process

1. **Prepare reference images**: Convert design specs to same format (SVG recommended)
2. **Capture app screenshots**: Use consistent terminal sizes
3. **Compare systematically**: Use diff tools or visual comparison

### 2. Automated Visual Testing

```python
# pytest-textual-snapshot automatically handles:
# - SVG generation
# - Pixel-perfect comparisons  
# - Regression detection
# - Diff visualization

def test_layout_matches_spec(snap_compare):
    # This will fail first time, requiring manual verification
    assert snap_compare("my_app.py", terminal_size=(80, 24))
    
    # After running: pytest --snapshot-update
    # Future runs will compare against this baseline
```

### 3. Diff Visualization

```css
/* CSS for highlighting differences in overlaid images */
.image-comparison-container img {
    mix-blend-mode: difference;
}
```

## Common Problems and Solutions

### 1. Claude Code CLI Output Interference

**Problem**: Textual apps take over Claude Code CLI stdout, cluttering the terminal
**Solutions**:

```bash
# Immediate solutions - run in separate window/terminal
# Windows
wt -w 0 nt powershell -Command "textual run my_app.py"
start cmd /k "textual run my_app.py"

# macOS
osascript -e 'tell application "Terminal" to do script "textual run my_app.py"'

# Linux
gnome-terminal -- bash -c "textual run my_app.py; exec bash"

# Cross-platform: Background with output redirection
textual run my_app.py > /dev/null 2>&1 &  # Unix-like
textual run my_app.py >nul 2>&1           # Windows
```

**Alternative**: Use subprocess wrapper for testing:

```python
# test_launcher.py - Production-ready wrapper following best practices
import subprocess
import sys
import time
import logging
from pathlib import Path

def launch_textual_app(app_path, duration=5, capture_output=False):
    """
    Launch Textual app in separate process for testing
    
    Args:
        app_path: Path to the Python file containing the Textual app
        duration: How long to let the app run (seconds)
        capture_output: Whether to capture stdout/stderr for analysis
    
    Returns:
        dict: Process info including return code and captured output
    """
    app_path = Path(app_path)
    if not app_path.exists():
        raise FileNotFoundError(f"App file not found: {app_path}")
    
    # Configure output handling
    if capture_output:
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
    else:
        stdout = subprocess.DEVNULL
        stderr = subprocess.DEVNULL
    
    # Platform-specific process creation
    if sys.platform == "win32":
        # Windows: Create new console window
        proc = subprocess.Popen(
            [sys.executable, str(app_path)],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=stdout,
            stderr=stderr
        )
    else:
        # Unix-like: Detached process with new session
        proc = subprocess.Popen(
            [sys.executable, str(app_path)],
            stdout=stdout,
            stderr=stderr,
            start_new_session=True
        )
    
    try:
        # Let app run for specified duration
        time.sleep(duration)
        
        # Graceful termination
        proc.terminate()
        
        # Wait for clean shutdown (with timeout)
        try:
            stdout_data, stderr_data = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if graceful termination fails
            proc.kill()
            stdout_data, stderr_data = proc.communicate()
            logging.warning("Process had to be force-killed")
        
        return {
            'returncode': proc.returncode,
            'stdout': stdout_data.decode() if capture_output and stdout_data else None,
            'stderr': stderr_data.decode() if capture_output and stderr_data else None,
            'terminated_gracefully': proc.returncode is not None
        }
        
    except Exception as e:
        # Cleanup on error
        try:
            proc.kill()
        except:
            pass
        raise e

# Usage examples
if __name__ == "__main__":
    # Basic usage
    result = launch_textual_app("my_textual_app.py")
    print(f"App finished with code: {result['returncode']}")
    
    # With output capture for debugging
    result = launch_textual_app("my_textual_app.py", duration=3, capture_output=True)
    if result['stderr']:
        print(f"Errors: {result['stderr']}")
```

### 2. Terminal Compatibility Issues

**Problem**: Different terminals render differently
**Solutions**:
- Use consistent terminal emulator for testing
- Recommended terminals:
  - **macOS**: iTerm2, Kitty, WezTerm
  - **Windows**: Windows Terminal, ConEmu
  - **Linux**: GNOME Terminal, Alacritty, Kitty

```bash
# Test which keys work in your terminal
textual keys
```

### 2. Terminal Compatibility Issues

**Problem**: Different terminals render differently
**Solutions**:
- Use consistent terminal emulator for testing
- Recommended terminals:
  - **macOS**: iTerm2, Kitty, WezTerm
  - **Windows**: Windows Terminal, ConEmu
  - **Linux**: GNOME Terminal, Alacritty, Kitty

```bash
# Test which keys work in your terminal
textual keys
```

### 3. Size and Resolution Inconsistencies

**Problem**: Screenshots vary between environments
**Solutions**:

```python
# Always specify exact terminal size
def test_consistent_layout(snap_compare):
    assert snap_compare("my_app.py", terminal_size=(100, 30))

# Test multiple common sizes
@pytest.mark.parametrize("size", [(80, 24), (120, 40), (100, 50)])
def test_responsive_layout(snap_compare, size):
    assert snap_compare("my_app.py", terminal_size=size)
```

### 3. Size and Resolution Inconsistencies

**Problem**: Screenshots vary between environments
**Solutions**:

```python
# Always specify exact terminal size
def test_consistent_layout(snap_compare):
    assert snap_compare("my_app.py", terminal_size=(100, 30))

# Test multiple common sizes
@pytest.mark.parametrize("size", [(80, 24), (120, 40), (100, 50)])
def test_responsive_layout(snap_compare, size):
    assert snap_compare("my_app.py", terminal_size=size)
```

### 4. Timing and Animation Issues

**Problem**: Animated elements cause inconsistent screenshots
**Solutions**:

```python
# Use delays for animations to complete
def test_after_animation(snap_compare):
    assert snap_compare("my_app.py", press=["space", "wait:1000"])

# Or disable animations for testing
def test_static_layout(snap_compare):
    async def setup(pilot):
        # Disable animations programmatically
        pilot.app.animation_level = "none"
    
    assert snap_compare("my_app.py", run_before=setup)
```

### 4. Timing and Animation Issues

**Problem**: Animated elements cause inconsistent screenshots
**Solutions**:

```python
# Use delays for animations to complete
def test_after_animation(snap_compare):
    assert snap_compare("my_app.py", press=["space", "wait:1000"])

# Or disable animations for testing
def test_static_layout(snap_compare):
    async def setup(pilot):
        # Disable animations programmatically
        pilot.app.animation_level = "none"
    
    assert snap_compare("my_app.py", run_before=setup)
```

### 5. Font and Color Rendering

**Problem**: Different systems render fonts/colors differently
**Solutions**:
- Use SVG output (handles fonts better than bitmap)
- Test in containerized environments for consistency
- Focus on layout rather than pixel-perfect color matching

### 5. Font and Color Rendering

**Problem**: Different systems render fonts/colors differently
**Solutions**:
- Use SVG output (handles fonts better than bitmap)
- Test in containerized environments for consistency
- Focus on layout rather than pixel-perfect color matching

### 6. Interactive Element States

**Problem**: Hover states, focus, etc. affect appearance
**Solutions**:

```python
def test_interactive_states(snap_compare):
    async def test_hover_state(pilot):
        await pilot.hover("#button")
    
    assert snap_compare("my_app.py", run_before=test_hover_state)

def test_focus_states(snap_compare):
    async def test_focus(pilot):
        await pilot.press("tab")  # Focus next element
    
    assert snap_compare("my_app.py", run_before=test_focus)
```

## Best Practices

### 1. Test Environment Setup

```bash
# Create isolated test environment
python -m venv textual_test_env
source textual_test_env/bin/activate  # or textual_test_env\Scripts\activate on Windows

# Install consistent dependencies
pip install textual pytest-textual-snapshot
```

### 2. Avoiding CLI Interference During Development

```bash
# Use separate terminal for testing while keeping Claude Code CLI clean

# Method 1: Quick launch scripts (best practice)
# Windows
echo @textual run my_app.py > run_app.bat
echo @pause >> run_app.bat  # Keep window open

# Unix-like  
echo '#!/bin/bash' > run_app.sh
echo 'textual run my_app.py' >> run_app.sh
echo 'read -p "Press enter to close..."' >> run_app.sh
chmod +x run_app.sh

# Method 2: Use IDE integration (recommended)
# Most IDEs can run Python files in separate terminals
# VS Code: Right-click -> "Run Python File in Terminal"
# PyCharm: Right-click -> "Run 'filename'"

# Method 3: Automated testing without visual interference
pytest tests/test_visual.py --no-cov -q  # Quiet mode, no coverage

# Method 4: Using shell functions (advanced)
# Add to your shell profile (.bashrc, .zshrc, etc.)
function textual_dev() {
    if command -v wt &> /dev/null; then
        # Windows Terminal available
        wt -w 0 nt powershell -Command "textual run $1 --dev"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"textual run $1 --dev\""
    else
        # Linux
        gnome-terminal --window -- bash -c "textual run $1 --dev; exec bash"
    fi
}
```

### 3. Systematic Testing Approach

```python
# Organize tests by component/screen
def test_main_screen_layout(snap_compare):
    assert snap_compare("app.py", terminal_size=(80, 24))

def test_settings_dialog(snap_compare):
    async def open_settings(pilot):
        await pilot.press("ctrl+comma")
    
    assert snap_compare("app.py", run_before=open_settings)

def test_error_states(snap_compare):
    # Test error scenarios
    async def trigger_error(pilot):
        await pilot.click("#invalid-action")
    
    assert snap_compare("app.py", run_before=trigger_error)
```

### 4. CI/CD Integration

```yaml
# GitHub Actions example
name: Visual Tests
on: [push, pull_request]
jobs:
  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install textual pytest-textual-snapshot
      - run: pytest tests/visual/ -v
```

## Troubleshooting Common Issues

### CLI Output Interference
```bash
# If Claude Code CLI gets cluttered, use separate terminal
# Quick recovery: Clear terminal or restart Claude session
clear  # Unix-like
cls    # Windows

# Prevention: Always use separate terminal for GUI apps
```

### Key Detection Problems
```bash
# Debug key bindings
textual keys

# Check terminal capabilities
echo $TERM
```

### Snapshot Failures
```bash
# View detailed diff
pytest tests/test_visual.py -v --tb=short

# Update snapshots after verification
pytest --snapshot-update tests/test_visual.py
```

### Performance Issues
```bash
# Run with smaller terminal sizes for faster tests
pytest tests/ --terminal-size=40x20
```

## Source Links

- [Textual Testing Guide](https://textual.textualize.io/guide/testing/)
- [Textual CLI Documentation](https://textual.textualize.io/guide/devtools/)
- [pytest-textual-snapshot](https://github.com/textualize/pytest-textual-snapshot)
- [Textual Key Handling](https://github.com/textualize/textual/blob/main/__wiki__/Key-names-and-escape-sequences.md)
- [Python subprocess Best Practices](https://realpython.com/python-subprocess/)
- [macOS Terminal Scripting](https://scriptingosx.com/2020/03/macos-shell-command-to-create-a-new-terminal-window/)
- [iTerm2 AppleScript Documentation](https://iterm2.com/documentation-scripting.html)
