# How to Test NiceGUI Applications with Playwright: Element Location and Automation

This guide covers best practices for testing NiceGUI applications using Playwright, focusing on element location strategies, interaction simulation, and relating these to GUI creation in Python.

## Overview

NiceGUI applications can be tested using Playwright for end-to-end testing that involves real browser automation. While NiceGUI provides its own testing framework with `user` and `screen` fixtures, Playwright offers additional capabilities for cross-browser testing and more complex scenarios.

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

## Advanced Element Location Techniques

### 1. Handling Dynamic Elements

```python
# For elements with dynamic IDs or classes
# Use partial matching with CSS selectors
await page.locator('[data-testid^="dynamic-button"]').click()

# Use XPath for complex navigation
await page.locator('//div[contains(@class, "card")]//button[text()="Save"]').click()

# Wait for dynamic content
await page.wait_for_selector('[data-testid="content-loaded"]')
```

### 2. Element Filtering

```python
# Filter by text content
await page.get_by_role("button").filter(has_text="Submit").click()

# Filter by additional attributes
await page.locator("input").filter(has=page.get_by_text("Required")).fill("value")

# Chain filters
await page.get_by_role("row").filter(has_text="John").get_by_role("button").click()
```

## Complete Test Example

### NiceGUI Application

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

### Playwright Test

```python
# test_app.py
import pytest
from playwright.async_api import async_playwright, expect
import asyncio
import subprocess
import time

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
        
        # Test with invalid credentials
        await page.get_by_test_id("username-input").fill("wrong")
        await page.get_by_test_id("password-input").fill("credentials")
        await page.get_by_test_id("login-btn").click()
        
        await expect(page.get_by_test_id("message")).to_have_text("Invalid credentials")

    async def test_form_interactions(self, page):
        await page.goto("http://localhost:8080")
        
        # Test various interaction methods
        username_input = page.get_by_test_id("username-input")
        
        # Type character by character
        await username_input.press_sequentially("test_user")
        
        # Clear and fill
        await username_input.clear()
        await username_input.fill("admin")
        
        # Test keyboard navigation
        await page.get_by_test_id("password-input").focus()
        await page.keyboard.type("secret")
        
        # Submit with Enter key
        await page.keyboard.press("Enter")
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

### 4. Test Organization

```python
# Page Object Model pattern
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
    await login_page.login("admin", "secret")
    assert await login_page.get_message() == "Login successful!"
```

### 5. Configuration and Setup

```python
# playwright.config.py
from playwright.async_api import async_playwright

# Configure test ID attribute (if using custom attributes)
async def configure_test_ids():
    async with async_playwright() as p:
        await p.selectors.set_test_id_attribute('data-qa')
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
    # ... test implementation
```

## Troubleshooting Common Issues

### 1. Element Not Found

```python
# Check if element exists
if await page.get_by_test_id("my-element").count() > 0:
    await page.get_by_test_id("my-element").click()

# Wait with timeout
try:
    await page.get_by_test_id("slow-element").click(timeout=10000)
except TimeoutError:
    print("Element not found within 10 seconds")
```

### 2. Stale Elements

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

## Resources

- [Playwright Python Documentation](https://playwright.dev/python/)
- [NiceGUI Testing Documentation](https://nicegui.io/documentation/section_testing)
- [Playwright Locators Guide](https://playwright.dev/python/docs/locators)
- [Web Testing Best Practices](https://playwright.dev/python/docs/best-practices)
