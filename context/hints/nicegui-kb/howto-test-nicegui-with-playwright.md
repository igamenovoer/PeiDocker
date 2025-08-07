# How to Test NiceGUI Applications with Playwright: Complete Guide

This comprehensive guide covers testing NiceGUI applications using Playwright, including element location strategies, interaction simulation, automation best practices, and screenshot capture techniques.

## Installation & Setup

```bash
# Install Playwright with Python
pip install playwright pytest-playwright

# Install browser drivers (usually pre-installed in most environments)
playwright install
```

## Element Location Strategies

### 1. Recommended Playwright Locators (Priority Order)

**Use these locators in order of preference for stability:**

```python
# 1. Role-based locators (most stable)
page.get_by_role("button", name="Submit")
page.get_by_role("textbox", name="Username")
page.get_by_role("checkbox", name="Remember me")

# 2. Label-based locators
page.get_by_label("Email Address")
page.get_by_label("Password")

# 3. Text content locators
page.get_by_text("Sign In")
page.get_by_text("Welcome to Dashboard")

# 4. Test ID locators (requires adding data-testid)
page.get_by_test_id("submit-button")
page.get_by_test_id("user-profile")
```

### 2. Adding Test IDs to NiceGUI Elements

**For better testability, add `data-testid` attributes to your NiceGUI components:**

```python
# NiceGUI Python code
import nicegui as ui

# Button with test ID
ui.button('Submit', on_click=handle_submit).props('data-testid="submit-btn"')

# Input with test ID
ui.input('Username', placeholder='Enter username').props('data-testid="username-input"')

# Custom element with test ID
with ui.card().props('data-testid="user-card"'):
    ui.label('User Information')
    ui.input('Name').props('data-testid="name-field"')
```

**Corresponding Playwright tests:**

```python
# Playwright test code
await page.get_by_test_id("submit-btn").click()
await page.get_by_test_id("username-input").fill("john_doe")
await expect(page.get_by_test_id("user-card")).to_be_visible()
```

### 3. NiceGUI Element Mapping

**Common NiceGUI elements and their Playwright locators:**

```python
# NiceGUI: ui.button('Click Me')
# Playwright: page.get_by_role("button", name="Click Me")

# NiceGUI: ui.input('Email', placeholder='Enter email')
# Playwright: page.get_by_label("Email") or page.get_by_placeholder("Enter email")

# NiceGUI: ui.checkbox('Subscribe', value=False)
# Playwright: page.get_by_role("checkbox", name="Subscribe")

# NiceGUI: ui.select(options=['A', 'B', 'C'])
# Playwright: page.get_by_role("combobox") or page.locator("select")

# NiceGUI: ui.textarea('Description')
# Playwright: page.get_by_label("Description")
```

### 4. Advanced Element Location Techniques

```python
# For elements with dynamic IDs or classes
# Use partial matching with CSS selectors
await page.locator('[data-testid^="dynamic-button"]').click()

# Use XPath for complex navigation
await page.locator('//div[contains(@class, "card")]//button[text()="Save"]').click()

# Wait for dynamic content
await page.wait_for_selector('[data-testid="content-loaded"]')

# Element filtering
await page.get_by_role("button").filter(has_text="Submit").click()
await page.locator("input").filter(has=page.get_by_text("Required")).fill("value")
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

## Complete NiceGUI Application Example

### Sample NiceGUI App with Test IDs

```python
# app.py
from nicegui import ui, app

def create_login_form():
    with ui.card().props('data-testid="login-card"'):
        ui.label('Login').classes('text-h6')
        
        username = ui.input('Username', placeholder='Enter username').props('data-testid="username-input"')
        password = ui.input('Password', password=True).props('data-testid="password-input"')
        
        ui.button('Sign In', on_click=lambda: handle_login(username.value, password.value)).props('data-testid="login-btn"')
        
        ui.label('').props('data-testid="message"')

def handle_login(username, password):
    message_label = ui.query('[data-testid="message"]').elements[0]
    if username == "admin" and password == "secret":
        message_label.text = "Login successful!"
    else:
        message_label.text = "Invalid credentials"

@ui.page('/')
def index():
    ui.label('My App').classes('text-h4').props('data-testid="app-title"')
    create_login_form()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080)
```
```

## Complete Testing Script Template

```python
import asyncio
import subprocess
import time
import signal
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect

class TestNiceGUIApp:
    @pytest.fixture(scope="class")
    async def app_server(self):
        # Start NiceGUI app
        process = subprocess.Popen(["python", "app.py"])
        time.sleep(3)  # Wait for server to start
        yield
        process.terminate()

    @pytest.fixture
    async def page(self, app_server):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            yield page
            await browser.close()

    async def test_login_success(self, page):
        # Navigate to app
        await page.goto("http://localhost:8080")
        
        # Wait for NiceGUI to be ready
        await wait_for_nicegui_ready(page)
        
        # Verify page loaded
        await expect(page.get_by_test_id("app-title")).to_have_text("My App")
        
        # Locate and interact with form elements
        await page.get_by_test_id("username-input").fill("admin")
        await page.get_by_test_id("password-input").fill("secret")
        await page.get_by_test_id("login-btn").click()
        
        # Verify result
        await expect(page.get_by_test_id("message")).to_have_text("Login successful!")

    async def test_login_failure(self, page):
        await page.goto("http://localhost:8080")
        await wait_for_nicegui_ready(page)
        
        # Test with invalid credentials
        await page.get_by_test_id("username-input").fill("wrong")
        await page.get_by_test_id("password-input").fill("credentials")
        await page.get_by_test_id("login-btn").click()
        
        await expect(page.get_by_test_id("message")).to_have_text("Invalid credentials")

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

def cleanup_process(process):
    """Clean termination of process"""
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    except:
        process.terminate()
```
```

## Common Testing Patterns

### Testing Form Interactions
```python
# Using stable locators
await page.get_by_label("Username").fill("test_user")
await page.get_by_label("Password").fill("password123")

# Alternative: using test IDs
await page.get_by_test_id("username-input").fill("test_user")

# Click button by role and name
await page.get_by_role("button", name="Submit").click()

# Wait for notification
await page.wait_for_selector('.q-notification')
```

### Testing Tab Navigation
```python
# Click tab using role
await page.get_by_role("tab", name="Project").click()

# Alternative: using text
await page.get_by_text("Project").click()

# Wait for tab content
await page.wait_for_selector('.tab-content:visible')
```

### File Upload Testing
```python
# For NiceGUI file uploads
await page.set_input_files('input[type="file"]', 'test-file.txt')

# With test ID
await page.get_by_test_id("file-upload").set_input_files('test-file.txt')
```

### Testing Complex Interactions
```python
# Drag and drop
source = page.get_by_test_id("source-element")
target = page.get_by_test_id("target-element")
await source.drag_to(target)

# Keyboard interactions
await page.get_by_test_id("input-field").press("Enter")
await page.keyboard.press("Tab")

# Multiple element interactions
all_items = page.get_by_role("listitem")
count = await all_items.count()
for i in range(count):
    await all_items.nth(i).click()
```

## Best Practices for Automated Testing

### 1. Selector Stability

```python
# ✅ GOOD: Stable, meaningful selectors
await page.get_by_role("button", name="Save Changes")
await page.get_by_test_id("user-profile-card")
await page.get_by_label("Email Address")

# ❌ AVOID: Fragile selectors dependent on layout
await page.locator("div.container > div:nth-child(3) > button")
await page.locator(".btn-primary")  # class names can change
```

### 2. Wait Strategies

```python
# Wait for elements to be ready
await page.wait_for_selector('[data-testid="dynamic-content"]')

# Wait for network responses
async with page.expect_response("**/api/users") as response_info:
    await page.get_by_test_id("load-users-btn").click()
response = await response_info.value

# Wait for element state
await page.get_by_test_id("submit-btn").wait_for(state="enabled")
```

### 3. Error Handling and Debugging

```python
# Take screenshots on failure
try:
    await page.get_by_test_id("expected-element").click()
except Exception:
    await page.screenshot(path="debug.png")
    raise

# Debug with pause
await page.pause()  # Opens browser inspector

# Verbose locator debugging
locator = page.get_by_test_id("my-element")
print(f"Element count: {await locator.count()}")
print(f"Is visible: {await locator.is_visible()}")
```

### 4. Test Organization (Page Object Model)

```python
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.username_input = page.get_by_test_id("username-input")
        self.password_input = page.get_by_test_id("password-input")
        self.login_button = page.get_by_test_id("login-btn")
        self.message = page.get_by_test_id("message")
    
    async def login(self, username, password):
        await self.username_input.fill(username)
        await self.password_input.fill(password)
        await self.login_button.click()
    
    async def get_message(self):
        return await self.message.text_content()

# Usage in tests
async def test_with_page_object(page):
    login_page = LoginPage(page)
    await page.goto("http://localhost:8080")
    await wait_for_nicegui_ready(page)
    await login_page.login("admin", "secret")
    assert await login_page.get_message() == "Login successful!"
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

# Alternative: check for specific NiceGUI elements
await page.wait_for_selector('.nicegui-content')
```

### 2. Dynamic Content Loading
```python
# Wait for specific selectors to appear
await page.wait_for_selector('.your-dynamic-content')

# Wait for elements to be stable
await page.get_by_test_id("dynamic-element").wait_for(state="visible")
```

### 3. Element Selection Best Practices
```python
# Re-query elements instead of storing references
# ❌ BAD: element reference can become stale
element = page.get_by_test_id("dynamic-element")
await page.reload()
await element.click()  # This might fail

# ✅ GOOD: Query fresh each time
await page.reload()
await page.get_by_test_id("dynamic-element").click()
```

### 4. Screenshot Quality Issues
```python
# Don't use quality parameter with PNG
await page.screenshot(path='test.png')  # ✅ Correct
# await page.screenshot(path='test.png', quality=90)  # ❌ Error

# For JPEG screenshots with quality
await page.screenshot(path='test.jpg', quality=90, type='jpeg')
```

### 5. Process Management
```python
# Use process groups for clean termination
import os
process = subprocess.Popen(
    ['python', 'app.py'],
    preexec_fn=os.setsid
)

# Clean termination
def cleanup_process(process):
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    except:
        process.terminate()
```

### 6. Timeout and Stability Issues
```python
# Check if element exists before interaction
if await page.get_by_test_id("my-element").count() > 0:
    await page.get_by_test_id("my-element").click()

# Use explicit timeouts
try:
    await page.get_by_test_id("slow-element").click(timeout=10000)
except TimeoutError:
    print("Element not found within 10 seconds")
```

## Testing with pytest-playwright

```python
import pytest
import asyncio
from playwright.async_api import async_playwright, expect

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
        
        # Your tests here using stable locators
        await expect(page.get_by_test_id("app-title")).to_have_text("Expected Title")
        
        await browser.close()

# Configuration for custom test IDs
@pytest.fixture(scope="session")
async def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720}
    }
```

## Integration with NiceGUI Testing Framework

**You can combine Playwright with NiceGUI's built-in testing:**

```python
# Use NiceGUI's user fixture for fast unit-like tests
def test_fast_user_interaction(user):
    user.find('Username').type('admin')
    user.find('Password').type('secret')
    user.find('Sign In').click()
    user.should_see('Login successful!')

# Use Playwright for complex browser-specific scenarios
async def test_cross_browser_compatibility(page):
    # Test with different browsers, viewport sizes, etc.
    await page.set_viewport_size({"width": 1280, "height": 720})
    await page.goto("http://localhost:8080")
    await wait_for_nicegui_ready(page)
    
    # Test responsive behavior
    await page.set_viewport_size({"width": 375, "height": 667})  # Mobile
    await page.screenshot(path="mobile-view.png")
```

## Performance Considerations

- Use `headless=True` for faster execution
- Set appropriate timeouts for WebSocket connections
- Use `networkidle` wait state for dynamic content
- Clean up processes properly to avoid resource leaks
- Use stable locators to reduce test flakiness
- Implement proper wait strategies for NiceGUI's reactive updates

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Element not found | Use `wait_for_selector()` or check `count()` before interaction |
| WebSocket timeout | Ensure `window.socket.connected` before testing |
| Stale elements | Re-query elements instead of storing references |
| Process cleanup | Use `os.setsid` and `killpg` for proper termination |
| Screenshot quality | Don't use `quality` parameter with PNG format |
| Dynamic content | Wait for specific selectors or element states |

## References

- [Playwright Python Documentation](https://playwright.dev/python/)
- [Playwright Locators Guide](https://playwright.dev/python/docs/locators)
- [NiceGUI Official Testing Documentation](https://nicegui.io/documentation/section_testing)
- [NiceGUI GitHub Testing Examples](https://github.com/zauberzeug/nicegui/blob/main/tests/README.md)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-python)
- [Web Testing Best Practices](https://playwright.dev/python/docs/best-practices)

## Key Takeaways

1. **Prioritize stable locators** - Use role-based and label-based selectors over CSS classes
2. **Always wait for WebSocket connection** - This is critical for NiceGUI apps
3. **Add test IDs to NiceGUI components** - Use `.props('data-testid="name"')` for reliable targeting
4. **Use proper viewport sizing** for consistent screenshots
5. **Handle process cleanup** to avoid resource issues
6. **Test both UI interactions and server-side responses**
7. **Use appropriate wait strategies** for dynamic content loading
8. **Implement Page Object Model** for maintainable test code
9. **Combine with NiceGUI's built-in testing** for comprehensive coverage
10. **Debug with screenshots and pause()** when tests fail