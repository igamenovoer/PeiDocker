# How to Launch NiceGUI and Save Current Page as HTML

This guide explains how to launch a NiceGUI application and save the current page state as HTML with all generated elements preserved.

## Basic NiceGUI Launch

### Simple Launch
```python
from nicegui import ui

# Create your UI elements
ui.label('Hello NiceGUI!')
ui.button('Click me!', on_click=lambda: ui.notify('Button clicked!'))

# Launch the application
ui.run()
```

### Launch with Custom Configuration
```python
from nicegui import ui

# Create UI elements
ui.label('My App')

# Launch with custom settings
ui.run(
    host='0.0.0.0',      # Allow external connections
    port=8080,           # Custom port
    title='My App',      # Page title
    show=True,           # Automatically open browser
    reload=True          # Auto-reload on file changes
)
```

## Method 1: JavaScript-based HTML Extraction

### Basic HTML Page Save
```python
from nicegui import ui

async def save_page_html():
    """Save the current page HTML to a file"""
    # Get the complete HTML including all generated elements
    html = await ui.run_javascript("document.querySelector('html').outerHTML")
    
    # Save to file
    with open("saved_page.html", "w", encoding="utf-8") as file:
        file.write(html)
    
    ui.notify("Page saved as saved_page.html")

# Create UI elements
ui.label('This is my NiceGUI page')
ui.button('Click me!', on_click=lambda: ui.notify('Hello!'))

# Add save button
ui.button('Save Page as HTML', on_click=save_page_html)

ui.run()
```

### Enhanced HTML Save with Head and Body Separation
```python
from nicegui import ui

async def save_complete_page():
    """Save page with separate head and body content"""
    # Get head and body content separately
    html_head = await ui.run_javascript("document.head.outerHTML")
    html_body = await ui.run_javascript("document.body.outerHTML")
    
    # Assemble complete HTML document
    complete_html = f"""<!DOCTYPE html>
<html>
{html_head}
{html_body}
</html>"""
    
    with open("complete_page.html", "w", encoding="utf-8") as file:
        file.write(complete_html)
    
    ui.notify("Complete page saved!")

# Your UI elements here
ui.markdown("## My NiceGUI Application")
ui.input("Enter something:", placeholder="Type here...")
ui.button('Save Complete Page', on_click=save_complete_page)

ui.run()
```

## Method 2: Browser Automation for Full Page Capture

### Using Playwright for Page Saving
```python
from nicegui import ui, app
from playwright.async_api import async_playwright
import asyncio

async def save_page_with_playwright():
    """Save page using Playwright browser automation"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to your NiceGUI app
        await page.goto(f"http://localhost:{app.config.port}")
        
        # Wait for page to load completely
        await page.wait_for_load_state('networkidle')
        
        # Save HTML content
        html_content = await page.content()
        with open("playwright_saved.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        
        # Optionally take a screenshot too
        await page.screenshot(path="page_screenshot.png", full_page=True)
        
        await browser.close()
        ui.notify("Page saved with Playwright!")

# UI setup
ui.label('NiceGUI with Playwright Save')
ui.button('Save with Playwright', on_click=save_page_with_playwright)

ui.run(port=8080)
```

### Using Selenium for Page Saving
```python
from nicegui import ui, app
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def save_page_with_selenium():
    """Save page using Selenium WebDriver"""
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless Chrome
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Create WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to your NiceGUI app
        driver.get(f"http://localhost:{app.config.port}")
        
        # Wait for page to load
        time.sleep(2)
        
        # Get page HTML
        html_content = driver.page_source
        
        # Save to file
        with open("selenium_saved.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        
        # Take screenshot
        driver.save_screenshot("selenium_screenshot.png")
        
        ui.notify("Page saved with Selenium!")
        
    finally:
        driver.quit()

# UI setup
ui.label('NiceGUI with Selenium Save')
ui.button('Save with Selenium', on_click=save_page_with_selenium)

ui.run(port=8080)
```

## Method 3: Advanced HTML Export with Static Resources

### Export with CSS and JavaScript Resources
```python
from nicegui import ui, app
import os
import shutil
from pathlib import Path

async def export_complete_application():
    """Export page with all static resources"""
    # Get the HTML content
    html = await ui.run_javascript("document.querySelector('html').outerHTML")
    
    # Create export directory
    export_dir = Path("exported_app")
    export_dir.mkdir(exist_ok=True)
    
    # Copy static files from NiceGUI
    static_dir = Path(app.config.static_files_dir) if hasattr(app.config, 'static_files_dir') else None
    if static_dir and static_dir.exists():
        shutil.copytree(static_dir, export_dir / "_static", dirs_exist_ok=True)
    
    # Modify HTML to use relative paths for static resources
    # This is a simplified approach - you might need more sophisticated URL rewriting
    modified_html = html.replace('/_static/', './_static/')
    
    # Save the modified HTML
    with open(export_dir / "index.html", "w", encoding="utf-8") as file:
        file.write(modified_html)
    
    ui.notify("Application exported to 'exported_app' directory!")

# UI setup
ui.label('Complete Application Export')
ui.button('Export App', on_click=export_complete_application)

ui.run()
```

## Limitations and Considerations

### JavaScript-based Method Limitations
- **CSS/JS Dependencies**: The saved HTML may not include NiceGUI's CSS and JavaScript files
- **Dynamic Content**: Some dynamic interactions may not work in the saved file
- **External Resources**: Links to external resources might break

### Browser Automation Benefits
- **Complete Capture**: Captures the page exactly as rendered in the browser
- **Static Resources**: Can capture and save associated static files
- **Screenshot Support**: Can also capture visual screenshots

### Best Practices
1. **Wait for Page Load**: Always ensure the page is fully loaded before capturing
2. **Handle Dynamic Content**: Consider the timing of dynamic element generation
3. **Resource Management**: Properly close browser instances to avoid memory leaks
4. **File Paths**: Use absolute paths or proper relative path handling

## Dependencies

For browser automation methods, install the required packages:

```bash
# For Playwright
pip install playwright
playwright install chromium

# For Selenium
pip install selenium
# Download ChromeDriver separately or use webdriver-manager
pip install webdriver-manager
```

## Source References

- [NiceGUI Documentation - ui.run_javascript](https://nicegui.io/documentation/run_javascript)
- [GitHub Discussion #313 - Save page as static HTML](https://github.com/zauberzeug/nicegui/discussions/313)
- [NiceGUI Documentation - ui.run](https://nicegui.io/documentation/run)
- [Playwright Screenshots Documentation](https://playwright.dev/docs/screenshots)
