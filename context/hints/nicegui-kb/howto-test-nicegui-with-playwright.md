# How to Test NiceGUI Applications with Playwright

This guide provides essential techniques for end-to-end testing and screenshot capture of NiceGUI applications using Playwright.

## Installation & Setup

```bash
# Install Playwright with Python
pip install playwright pytest-playwright

# Install browser drivers (usually pre-installed in most environments)
playwright install
```

## Core Testing Approaches

### 1. NiceGUI Built-in Testing (Simple)

```python
from nicegui import ui
from nicegui.testing import Screen

def test_hello_world(screen: Screen):
    ui.label('Hello, world')
    
    screen.open('/')
    screen.should_contain('Hello, world')
```

### 2. Direct Playwright Testing (Advanced)

```python
import asyncio
from playwright.async_api import async_playwright

async def test_nicegui_app():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('http://localhost:8080')
        
        # Wait for NiceGUI to be ready
        await wait_for_nicegui_ready(page)
        
        # Test interactions
        await page.screenshot(path='test-screenshot.png')
        await browser.close()
```

## Essential Wait Strategies for NiceGUI

NiceGUI applications require specific wait patterns due to their architecture:

```python
async def wait_for_nicegui_ready(page, max_wait=30):
    """Wait for NiceGUI to be fully loaded"""
    # 1. Wait for basic page load
    await page.wait_for_load_state('networkidle')
    
    # 2. Wait for WebSocket connection (critical!)
    await page.wait_for_function(
        "window.socket && window.socket.connected", 
        timeout=max_wait * 1000
    )
    
    # 3. Wait for Vue.js components
    await page.wait_for_function(
        "window.Vue && window.app",
        timeout=5000
    )
    
    # 4. Additional buffer for dynamic content
    await asyncio.sleep(2)
```

## Complete Testing Script Template

```python
import asyncio
import subprocess
import time
import signal
from pathlib import Path
from playwright.async_api import async_playwright

async def test_nicegui_with_screenshot():
    """Complete example: Launch app and take screenshot"""
    app_process = None
    
    try:
        # 1. Start NiceGUI app
        app_process = start_nicegui_app()
        await asyncio.sleep(8)  # Wait for startup
        
        # 2. Launch Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            page = await browser.new_page(
                viewport={'width': 1280, 'height': 720}
            )
            
            # 3. Navigate and wait
            await page.goto('http://localhost:8080')
            await wait_for_nicegui_ready(page)
            
            # 4. Take screenshot
            await page.screenshot(
                path='nicegui-screenshot.png',
                full_page=True
            )
            
            # 5. Test interactions
            title = await page.title()
            assert "NiceGUI" in title
            
            await browser.close()
            
    finally:
        # Clean up
        if app_process:
            cleanup_process(app_process)

def start_nicegui_app():
    """Start NiceGUI app with proper Python environment"""
    # For apps that need custom runner
    runner_script = '''
import sys
sys.path.insert(0, "/path/to/your/project/src")

from nicegui import ui
from your_app import create_app

gui = create_app()
ui.run(port=8080, host='0.0.0.0', show=False, reload=False)
'''
    
    with open('/tmp/nicegui_runner.py', 'w') as f:
        f.write(runner_script)
    
    return subprocess.Popen(
        ['python', '/tmp/nicegui_runner.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
```

## Common Testing Patterns

### Testing Form Interactions
```python
# Fill input field
await page.fill('input[type="text"]', 'test value')

# Click button
await page.click('button:has-text("Submit")')

# Wait for notification
await page.wait_for_selector('.q-notification')
```

### Testing Tab Navigation
```python
# Click tab
await page.click('button:has-text("Project")')

# Wait for tab content
await page.wait_for_selector('.tab-content:visible')
```

### File Upload Testing
```python
# For NiceGUI file uploads
await page.set_input_files('input[type="file"]', 'test-file.txt')
```

## Screenshot Best Practices

### Basic Screenshot
```python
await page.screenshot(
    path='screenshot.png',
    full_page=True  # Capture entire scrollable content
)
```

### Element-Specific Screenshot
```python
# Screenshot specific component
await page.locator('.nicegui-content').screenshot(
    path='component.png'
)
```

### Viewport-Consistent Screenshots
```python
# Set consistent viewport for reproducible screenshots
page = await browser.new_page(
    viewport={'width': 1280, 'height': 720}
)
```

## Common Pitfalls & Solutions

### 1. WebSocket Connection Issues
```python
# Always wait for WebSocket before testing
await page.wait_for_function("window.socket && window.socket.connected")
```

### 2. Dynamic Content Loading
```python
# Wait for specific selectors to appear
await page.wait_for_selector('.your-dynamic-content')
```

### 3. Screenshot Quality Issues
```python
# Don't use quality parameter with PNG
await page.screenshot(path='test.png')  # ✅ Correct
# await page.screenshot(path='test.png', quality=90)  # ❌ Error
```

### 4. Process Management
```python
# Use process groups for clean termination
import os
process = subprocess.Popen(
    ['python', 'app.py'],
    preexec_fn=os.setsid
)

# Clean termination
os.killpg(os.getpgid(process.pid), signal.SIGTERM)
```

## Testing with pytest-playwright

```python
import pytest
from playwright.async_api import async_playwright

@pytest.fixture
async def nicegui_app():
    """Fixture to start NiceGUI app"""
    process = start_nicegui_app()
    await asyncio.sleep(5)
    yield "http://localhost:8080"
    cleanup_process(process)

@pytest.mark.asyncio
async def test_nicegui_interface(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(nicegui_app)
        
        await wait_for_nicegui_ready(page)
        
        # Your tests here
        assert await page.title() == "Expected Title"
        
        await browser.close()
```

## Performance Considerations

- Use `headless=True` for faster execution
- Set appropriate timeouts for WebSocket connections
- Use `networkidle` wait state for dynamic content
- Clean up processes properly to avoid resource leaks

## References

- [NiceGUI Official Testing Documentation](https://github.com/zauberzeug/nicegui/blob/main/tests/README.md)
- [Playwright Python Documentation](https://playwright.dev/python/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-python)

## Key Takeaways

1. **Always wait for WebSocket connection** - This is critical for NiceGUI apps
2. **Use proper viewport sizing** for consistent screenshots
3. **Handle process cleanup** to avoid resource issues
4. **Test both UI interactions and server-side responses**
5. **Use appropriate wait strategies** for dynamic content loading