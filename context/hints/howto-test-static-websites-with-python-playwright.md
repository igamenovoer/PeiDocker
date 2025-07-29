# How to Test Static Websites with Python and Playwright

A comprehensive guide for testing static websites locally using Python's built-in HTTP server and Playwright for automated testing.

## Overview

Testing static websites involves two main components:
1. **Serving the static files** - Using Python's built-in HTTP server
2. **Automated testing** - Using Playwright to interact with and test the website

## Quick Start

### 1. Serve Your Static Website

Use Python's built-in HTTP server to serve your static files:

```bash
# Serve current directory on port 8000
python3 -m http.server

# Serve on specific port
python3 -m http.server 8080

# Serve specific directory
python3 -m http.server 8080 --directory /path/to/your/site
```

### 2. Basic Playwright Test Structure

```python
import asyncio
from playwright.async_api import async_playwright

async def test_static_website():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to your local server
        await page.goto("http://localhost:8000")
        
        # Your test logic here
        await expect(page.locator("h1")).to_contain_text("Welcome")
        
        await browser.close()

asyncio.run(test_static_website())
```

## Advanced Setup with Playwright Configuration

### Automatic Server Management

Configure Playwright to automatically start your development server:

```python
# playwright.config.py
from playwright.sync_api import Playwright

# Optional: Use pytest-playwright for easier setup
# pip install pytest-playwright

import pytest
from playwright.sync_api import Page

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }

# Custom fixture to start local server
@pytest.fixture(scope="session", autouse=True)
def dev_server():
    import subprocess
    import time
    import requests
    
    # Start Python HTTP server
    server = subprocess.Popen([
        "python3", "-m", "http.server", "8000"
    ], cwd="./your-static-site-directory")
    
    # Wait for server to start
    for _ in range(30):
        try:
            requests.get("http://localhost:8000")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    
    yield
    
    # Cleanup
    server.terminate()
```

### Complete Test Example

```python
import pytest
from playwright.sync_api import Page, expect

class TestStaticWebsite:
    def test_homepage_loads(self, page: Page):
        page.goto("http://localhost:8000")
        expect(page).to_have_title("Your Site Title")
        
    def test_navigation_works(self, page: Page):
        page.goto("http://localhost:8000")
        page.click("text=About")
        expect(page).to_have_url("http://localhost:8000/about.html")
        
    def test_form_submission(self, page: Page):
        page.goto("http://localhost:8000/contact")
        page.fill("#name", "Test User")
        page.fill("#email", "test@example.com")
        page.click("button[type=submit]")
        
        # Check for success message
        expect(page.locator(".success-message")).to_be_visible()
        
    def test_responsive_design(self, page: Page):
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("http://localhost:8000")
        
        # Check mobile navigation is visible
        expect(page.locator(".mobile-menu")).to_be_visible()
```

## Custom HTTP Server for Advanced Testing

For more control over your test server:

```python
import http.server
import socketserver
import threading
import time

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="./static", **kwargs)
    
    def end_headers(self):
        # Add CORS headers for testing
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        super().end_headers()

def start_test_server(port=8000):
    handler = CustomHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        return httpd

# Usage in tests
@pytest.fixture(scope="session")
def test_server():
    server = start_test_server(8000)
    time.sleep(1)  # Wait for server to start
    yield
    server.shutdown()
```

## Testing Different Scenarios

### Testing JavaScript-Heavy Sites

```python
async def test_spa_navigation(page: Page):
    # Wait for JavaScript to load
    await page.goto("http://localhost:8000")
    await page.wait_for_load_state("networkidle")
    
    # Test SPA routing
    await page.click("text=Dashboard")
    await page.wait_for_url("**/dashboard")
    await expect(page.locator("h1")).to_contain_text("Dashboard")
```

### Testing File Downloads

```python
async def test_file_download(page: Page):
    async with page.expect_download() as download_info:
        await page.click("text=Download PDF")
    
    download = await download_info.value
    assert download.suggested_filename == "document.pdf"
```

### Testing Error Pages

```python
def test_404_page(page: Page):
    page.goto("http://localhost:8000/nonexistent-page")
    expect(page).to_have_url("**/404.html")
    expect(page.locator("h1")).to_contain_text("Page Not Found")
```

## Best Practices

### 1. Use Page Object Model

```python
class HomePage:
    def __init__(self, page: Page):
        self.page = page
        self.nav_menu = page.locator("nav.main-menu")
        self.hero_title = page.locator("h1.hero-title")
    
    def navigate_to(self):
        self.page.goto("http://localhost:8000")
    
    def click_about(self):
        self.nav_menu.locator("text=About").click()

# Usage
def test_navigation_with_pom(page: Page):
    home = HomePage(page)
    home.navigate_to()
    home.click_about()
    expect(page).to_have_url("**/about.html")
```

### 2. Environment Configuration

```python
import os

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")

def test_with_env_config(page: Page):
    page.goto(BASE_URL)
    # Rest of test...
```

### 3. Screenshot on Failure

```python
@pytest.fixture(autouse=True)
def screenshot_on_failure(page: Page, request):
    yield
    if request.node.rep_call.failed:
        page.screenshot(path=f"screenshots/{request.node.name}.png")
```

## Running Tests

```bash
# Install dependencies
pip install playwright pytest pytest-playwright

# Install browser binaries
playwright install

# Run tests
pytest tests/

# Run with headed browser for debugging
pytest --headed tests/

# Run specific test
pytest tests/test_homepage.py::test_navigation

# Generate HTML report
pytest --html=report.html tests/
```

## Debugging Tips

### 1. Run in Headed Mode
```python
browser = await p.chromium.launch(headless=False, slow_mo=1000)
```

### 2. Use Playwright Inspector
```bash
PWDEBUG=1 pytest tests/test_homepage.py
```

### 3. Add Debug Prints
```python
# Take screenshot at any point
await page.screenshot(path="debug.png")

# Print page content
print(await page.content())

# Print current URL
print(page.url)
```

## Common Patterns

### Testing Forms
```python
async def test_contact_form(page: Page):
    await page.goto("http://localhost:8000/contact")
    
    # Fill form
    await page.fill("#name", "John Doe")
    await page.fill("#email", "john@example.com")
    await page.select_option("#country", "US")
    await page.check("#newsletter")
    
    # Submit and verify
    await page.click("button[type=submit]")
    await expect(page.locator(".success")).to_be_visible()
```

### Testing Accessibility
```python
def test_accessibility(page: Page):
    page.goto("http://localhost:8000")
    
    # Check for alt text on images
    images = page.locator("img")
    for i in range(images.count()):
        expect(images.nth(i)).to_have_attribute("alt")
    
    # Check for proper heading hierarchy
    expect(page.locator("h1")).to_have_count(1)
```

## Resources

- [Playwright Python Documentation](https://playwright.dev/python/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Python HTTP Server Documentation](https://docs.python.org/3/library/http.server.html)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [Playwright Configuration Options](https://playwright.dev/docs/test-configuration)

## Related Tools

- **Alternative servers**: `http-server` (Node.js), `serve` (Node.js), `caddy`
- **Testing frameworks**: `pytest`, `unittest`, `behave` (BDD)
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins with Playwright
- **Reporting**: Allure, HTML reports, JUnit XML
