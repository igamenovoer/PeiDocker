# How to Test NiceGUI Applications with Playwright in Python

Testing NiceGUI applications with Playwright provides a powerful combination for end-to-end testing of Python-based web UIs. This guide covers setup, configuration, and best practices for testing NiceGUI applications using Playwright's automation capabilities.

## Overview

**NiceGUI** is a Python-based UI framework that creates web interfaces directly from Python code, running in web browsers. **Playwright** is a robust end-to-end testing framework that can automate web applications across different browsers (Chromium, Firefox, WebKit).

Combining these tools allows you to:
- Test NiceGUI applications across multiple browsers
- Automate user interactions (clicks, form inputs, navigation)
- Verify UI behavior and content
- Perform visual regression testing
- Run tests in headless or headed modes

## Installation and Setup

### 1. Install Required Packages

```bash
# Install NiceGUI
pip install nicegui

# Install Playwright for Python
pip install playwright pytest-playwright

# Install browser drivers
playwright install
```

### 2. Platform-Specific Setup

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver
```

**macOS:**
```bash
brew install chromedriver
```

**Windows (PowerShell):**
```powershell
choco install chromedriver
```

## Basic Testing Approach

### Method 1: Using NiceGUI's Built-in Testing Support

NiceGUI provides its own testing framework with the `Screen` class for simple tests:

```python
from nicegui import ui
from nicegui.testing import Screen

def test_hello_world(screen: Screen):
    ui.label('Hello, world')
    
    screen.open('/')
    screen.should_contain('Hello, world')
```

### Method 2: Using Playwright Directly

For more advanced testing, use Playwright directly with NiceGUI applications:

```python
import asyncio
import pytest
from playwright.async_api import async_playwright
from nicegui import ui, app
import threading
import time

# Sample NiceGUI application
def create_app():
    @ui.page('/')
    def index():
        ui.label('Welcome to NiceGUI').classes('text-h4')
        ui.button('Click me', on_click=lambda: ui.notify('Button clicked!'))
        ui.input('Enter text').props('outlined')
    
    return app

@pytest.fixture
async def nicegui_app():
    """Start NiceGUI app in a separate thread"""
    app = create_app()
    
    # Start the app in a separate thread
    def run_app():
        ui.run(port=8080, show=False, reload=False)
    
    thread = threading.Thread(target=run_app, daemon=True)
    thread.start()
    
    # Wait for the server to start
    time.sleep(2)
    
    yield "http://localhost:8080"

@pytest.mark.asyncio
async def test_nicegui_with_playwright(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the NiceGUI app
        await page.goto(nicegui_app)
        
        # Test page title and content
        await page.wait_for_selector('text=Welcome to NiceGUI')
        assert await page.text_content('h4') == 'Welcome to NiceGUI'
        
        # Test button interaction
        await page.click('button:has-text("Click me")')
        
        # Verify notification appears
        await page.wait_for_selector('.q-notification')
        notification = await page.text_content('.q-notification')
        assert 'Button clicked!' in notification
        
        # Test input field
        await page.fill('input', 'Test input')
        input_value = await page.input_value('input')
        assert input_value == 'Test input'
        
        await browser.close()
```

## Advanced Testing Scenarios

### Testing Real-time Updates

NiceGUI supports real-time updates. Test these with Playwright:

```python
@pytest.mark.asyncio
async def test_realtime_updates(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto(nicegui_app)
        
        # Wait for WebSocket connection
        await page.wait_for_function(
            "window.socket && window.socket.connected"
        )
        
        # Test real-time UI updates
        await page.click('button:has-text("Update Counter")')
        
        # Wait for counter to update
        await page.wait_for_function(
            "document.querySelector('#counter').textContent !== '0'"
        )
        
        counter_text = await page.text_content('#counter')
        assert counter_text == '1'
        
        await browser.close()
```

### Testing File Uploads

```python
@pytest.mark.asyncio
async def test_file_upload(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto(nicegui_app)
        
        # Create a test file
        test_file_path = "/tmp/test.txt"
        with open(test_file_path, "w") as f:
            f.write("Test file content")
        
        # Upload file
        await page.set_input_files('input[type="file"]', test_file_path)
        
        # Verify upload success
        await page.wait_for_selector('text=Upload successful')
        
        await browser.close()
```

### Cross-Browser Testing

```python
@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
@pytest.mark.asyncio
async def test_cross_browser(nicegui_app, browser_name):
    async with async_playwright() as p:
        browser = await getattr(p, browser_name).launch()
        page = await browser.new_page()
        
        await page.goto(nicegui_app)
        
        # Perform tests across all browsers
        await page.wait_for_selector('text=Welcome to NiceGUI')
        
        await browser.close()
```

## Configuration and Best Practices

### pytest Configuration (pytest.ini)

```ini
[tool:pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --browser chromium
    --headed
    --slowmo 100
```

### Environment Configuration

```python
# conftest.py
import pytest
from playwright.async_api import async_playwright

@pytest.fixture(scope="session")
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Set to True for CI/CD
            slow_mo=50      # Slow down for debugging
        )
        yield browser
        await browser.close()

@pytest.fixture
async def page(browser):
    page = await browser.new_page()
    yield page
    await page.close()
```

## Taking Screenshots in Headless Browsers

Screenshots are essential for debugging, visual testing, and documentation. Playwright provides powerful screenshot capabilities that work seamlessly in both headless and headed modes.

### Basic Screenshot Configuration

```python
# Configure viewport for consistent screenshots
browser = await p.chromium.launch(headless=True)
context = await browser.new_context(
    viewport={"width": 1920, "height": 1080}
)
page = await context.new_page()
```

### Full Page Screenshots

Capture the entire scrollable page content:

```python
@pytest.mark.asyncio
async def test_full_page_screenshot(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        await page.goto(nicegui_app)
        await page.wait_for_load_state("networkidle")
        
        # Full page screenshot - captures entire scrollable content
        await page.screenshot(
            path="full_page_screenshot.png",
            full_page=True
        )
        
        await browser.close()
```

### Element-Specific Screenshots

Capture specific UI components:

```python
@pytest.mark.asyncio
async def test_element_screenshot(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(nicegui_app)
        
        # Screenshot of specific element
        await page.locator('.nicegui-content').screenshot(
            path="content_section.png"
        )
        
        # Screenshot of button component
        await page.locator('button').first.screenshot(
            path="button_component.png"
        )
        
        await browser.close()
```

### Screenshot with Custom Options

```python
@pytest.mark.asyncio
async def test_custom_screenshot_options(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(nicegui_app)
        
        # High-quality screenshot with custom options
        await page.screenshot(
            path="custom_screenshot.png",
            full_page=True,
            quality=95,  # For JPEG format
            type="png",  # png, jpeg
            clip={       # Capture specific area
                "x": 0,
                "y": 0,
                "width": 800,
                "height": 600
            }
        )
        
        await browser.close()
```

### Screenshots as Base64 Buffer

For in-memory processing or integration with testing frameworks:

```python
@pytest.mark.asyncio
async def test_screenshot_buffer(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(nicegui_app)
        
        # Capture screenshot as bytes buffer
        screenshot_bytes = await page.screenshot()
        
        # Convert to base64 for storage/transmission
        import base64
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        
        # Save to file if needed
        with open("screenshot_from_buffer.png", "wb") as f:
            f.write(screenshot_bytes)
        
        await browser.close()
```

### Progressive Screenshot Testing

For testing dynamic content loading:

```python
@pytest.mark.asyncio
async def test_progressive_screenshots(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(nicegui_app)
        
        # Screenshot before interaction
        await page.screenshot(path="before_interaction.png")
        
        # Trigger UI change
        await page.click('button:has-text("Load Data")')
        
        # Wait for loading to complete
        await page.wait_for_selector('.data-loaded')
        
        # Screenshot after interaction
        await page.screenshot(path="after_interaction.png")
        
        await browser.close()
```

### Visual Regression Testing

Compare screenshots over time:

```python
import filecmp
from pathlib import Path

@pytest.mark.asyncio
async def test_visual_regression(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        await page.goto(nicegui_app)
        await page.wait_for_load_state("networkidle")
        
        current_screenshot = "current_ui.png"
        baseline_screenshot = "baseline_ui.png"
        
        # Take current screenshot
        await page.screenshot(path=current_screenshot, full_page=True)
        
        # Compare with baseline (if exists)
        if Path(baseline_screenshot).exists():
            # Use image comparison library for pixel-perfect comparison
            # This is a simple file comparison - use libraries like
            # PIL (Pillow) or opencv for more sophisticated comparison
            assert filecmp.cmp(current_screenshot, baseline_screenshot), \
                "UI has changed compared to baseline"
        else:
            # First run - establish baseline
            import shutil
            shutil.copy(current_screenshot, baseline_screenshot)
            
        await browser.close()
```

### Screenshot on Test Failure

Automatically capture screenshots when tests fail:

```python
# conftest.py
import pytest
import asyncio
from playwright.async_api import async_playwright

@pytest.fixture(autouse=True)
async def screenshot_on_failure(request):
    yield
    
    if request.node.rep_call.failed:
        # Extract page from test if available
        if hasattr(request.node, '_page'):
            page = request.node._page
            screenshot_path = f"failure_{request.node.name}_{int(time.time())}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved: {screenshot_path}")

# In your test files
@pytest.mark.asyncio
async def test_with_auto_screenshot(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Make page available for screenshot on failure
        import pytest
        pytest.current_node._page = page
        
        await page.goto(nicegui_app)
        
        # Your test logic here
        assert await page.title() == "Expected Title"
        
        await browser.close()
```

### Mobile Device Screenshots

Test responsive designs:

```python
@pytest.mark.asyncio
async def test_mobile_screenshot(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Emulate mobile device
        mobile_context = await browser.new_context(
            viewport={"width": 375, "height": 667},  # iPhone SE
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X)",
            is_mobile=True,
            has_touch=True
        )
        
        page = await mobile_context.new_page()
        await page.goto(nicegui_app)
        
        # Mobile screenshot
        await page.screenshot(
            path="mobile_view.png",
            full_page=True
        )
        
        await browser.close()
```

### Best Practices for Screenshots

1. **Consistent Viewport**: Always set a fixed viewport size for consistent screenshots
2. **Wait for Content**: Use `wait_for_load_state("networkidle")` or specific selectors
3. **High DPI Support**: Consider device pixel ratio for high-resolution displays
4. **Organized Storage**: Use descriptive names and organize screenshots by test suites
5. **Cleanup**: Remove old screenshots to prevent disk space issues

```python
# Example with best practices
@pytest.mark.asyncio
async def test_screenshot_best_practices(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Fixed viewport for consistency
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            device_scale_factor=1  # Consistent DPI
        )
        
        page = await context.new_page()
        await page.goto(nicegui_app)
        
        # Wait for all content to load
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(500)  # Additional buffer
        
        # Organized screenshot naming
        timestamp = int(time.time())
        screenshot_dir = Path("screenshots") / "ui_tests"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        screenshot_path = screenshot_dir / f"nicegui_ui_{timestamp}.png"
        
        await page.screenshot(
            path=str(screenshot_path),
            full_page=True
        )
        
        await browser.close()
```

### Debugging Tips

1. **Use headed mode** for debugging:
```python
browser = await p.chromium.launch(headless=False)
```

2. **Add screenshots** on failure:
```python
@pytest.fixture(autouse=True)
async def screenshot_on_failure(page, request):
    yield
    if request.node.rep_call.failed:
        await page.screenshot(path=f"screenshot-{request.node.name}.png")
```

3. **Use page.pause()** for debugging:
```python
await page.pause()  # Opens Playwright inspector
```

## Common Challenges and Solutions

### 1. WebSocket Connection Issues

NiceGUI relies on WebSocket connections. Ensure they're established:

```python
# Wait for WebSocket connection
await page.wait_for_function(
    "window.socket && window.socket.connected"
)
```

### 2. Dynamic Content Loading

Wait for dynamic content to load:

```python
# Wait for specific element
await page.wait_for_selector('.dynamic-content')

# Wait for network idle
await page.wait_for_load_state('networkidle')
```

### 3. Vue.js Component Testing

NiceGUI uses Vue.js under the hood. Test Vue components:

```python
# Wait for Vue app to be ready
await page.wait_for_function("window.Vue && window.app")

# Test Vue reactive data
await page.evaluate("app.someReactiveProperty = 'new value'")
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test NiceGUI with Playwright

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install --with-deps
    
    - name: Run tests
      run: |
        pytest --browser chromium --browser firefox --browser webkit
```

## Performance Testing

Test application performance with Playwright:

```python
@pytest.mark.asyncio
async def test_performance(nicegui_app):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Start performance monitoring
        await page.evaluate("performance.mark('start')")
        
        await page.goto(nicegui_app)
        await page.wait_for_selector('text=Welcome')
        
        # Measure performance
        await page.evaluate("performance.mark('end')")
        duration = await page.evaluate("""
            performance.measure('test', 'start', 'end');
            performance.getEntriesByName('test')[0].duration;
        """)
        
        assert duration < 2000  # Less than 2 seconds
        
        await browser.close()
```

## Resources and References

- [Playwright Python Documentation](https://playwright.dev/python/)
- [NiceGUI Documentation](https://nicegui.io/)
- [NiceGUI Testing Guide](https://nicegui.io/documentation/section_testing)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)

## Additional Tools

Consider these complementary tools:
- **Allure** for test reporting
- **pytest-xdist** for parallel test execution  
- **pytest-html** for HTML test reports
- **Visual testing** with Playwright's screenshot comparison

This comprehensive approach enables robust testing of NiceGUI applications using Playwright's powerful automation capabilities across multiple browsers and scenarios.
