# How to Start NiceGUI with OS-Selected Free Port

## Overview

When developing NiceGUI applications, you might encounter port binding errors if the default port (8080) is already in use. This guide covers several cross-platform methods to automatically find and use available ports in NiceGUI applications.

## Common Port Binding Error

```
ERROR: [Errno 13] error while attempting to bind on address ('0.0.0.0', 8080): 
[winerror 10013] an attempt was made to access a socket in a way forbidden by its access permissions
```

This error occurs when:
- Port 8080 is already in use by another application
- The port is blocked by firewall/permissions
- The port is reserved by the system

## Solutions

### Method 1: Native Mode (Automatic Port Selection)

The simplest approach is using NiceGUI's native mode, which automatically finds an open port:

```python
from nicegui import ui

@ui.page('/')
def index():
    ui.label('Hello NiceGUI!')
    ui.button('Click me!', on_click=lambda: ui.notify('Clicked!'))

# Native mode automatically finds an open port
ui.run(title='My App', native=True)
```

**Benefits:**
- Zero configuration required
- NiceGUI handles port selection automatically
- Opens in a desktop window instead of browser

**Note:** In native mode, the default host becomes `'127.0.0.1'` and `show` is automatically disabled.

### Method 2: Socket-Based Port Discovery

Use Python's socket module to find an available port and pass it to NiceGUI:

```python
import socket
from nicegui import ui

def get_free_port() -> int:
    """Get a free TCP port in a cross-platform way."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to any available port
        port = s.getsockname()[1]  # Get the assigned port number
    return port

@ui.page('/')
def index():
    ui.label('Hello NiceGUI!')

# Find and use a free port
port = get_free_port()
print(f"Starting application on port {port}")
print(f"Open http://localhost:{port} in your browser")
ui.run(title='My App', port=port)
```

### Method 3: Sequential Port Fallback

Try a preferred port first, then fallback to the next available ports:

```python
import socket
from nicegui import ui

def find_free_port(start_port: int = 8080) -> int:
    """Find the next available port starting from start_port."""
    port = start_port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError("No available ports found")

@ui.page('/')
def index():
    ui.label('Hello NiceGUI!')

# Try port 8080 first, then find next available
try:
    port = find_free_port(8080)
    print(f"Starting application on port {port}")
    ui.run(title='My App', port=port)
except RuntimeError as e:
    print(f"Error: {e}")
```

### Method 4: Hybrid Approach (Recommended)

Combines the benefits of preferred port and automatic fallback:

```python
import socket
from typing import Optional
from nicegui import ui

def get_free_port() -> int:
    """Get a free TCP port in a cross-platform way."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    return port

def try_port(port: int) -> bool:
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return True
    except OSError:
        return False

@ui.page('/')
def index():
    ui.label('Hello NiceGUI!')

def start_app(preferred_port: Optional[int] = 8080):
    """Start the app with preferred port or automatic fallback."""
    # Determine which port to use
    if preferred_port and try_port(preferred_port):
        port = preferred_port
        print(f"Starting on preferred port {port}")
    else:
        port = get_free_port()
        if preferred_port:
            print(f"Port {preferred_port} busy, using available port {port}")
        else:
            print(f"Starting on available port {port}")
    
    print(f"Open http://localhost:{port} in your browser")
    ui.run(title='My App', port=port)

# Start with fallback logic
start_app(8080)
```

## CLI Integration Example

For command-line applications, you can accept port as a parameter:

```python
import argparse
import socket
from nicegui import ui

def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

@ui.page('/')
def index():
    ui.label('My NiceGUI App')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=None, 
                       help='Port to use (default: auto-select)')
    parser.add_argument('--native', action='store_true',
                       help='Run in native mode')
    args = parser.parse_args()
    
    if args.native:
        # Native mode handles port automatically
        ui.run(title='My App', native=True)
    else:
        # Use specified port or find available one
        port = args.port if args.port else get_free_port()
        print(f"Starting on port {port}")
        ui.run(title='My App', port=port)

if __name__ == '__main__':
    main()
```

## Key Points

### Native Mode Behavior
- **Host**: Defaults to `'127.0.0.1'` (localhost only)
- **Port**: Automatically determined open port
- **Show**: Automatically disabled (doesn't open browser)
- **Window**: Opens as desktop application

### Regular Mode with Custom Port
- **Host**: Defaults to `'0.0.0.0'` (all interfaces)
- **Port**: Uses specified port (default 8080)
- **Show**: Defaults to `True` (opens browser)

### Socket Port 0 Trick
- Binding to port 0 tells the OS to assign any available port
- The OS atomically assigns the port, preventing race conditions
- Cross-platform compatible (Windows, Linux, macOS)

## Error Handling

Always handle potential errors when working with ports:

```python
import socket
from nicegui import ui

def safe_start_app():
    try:
        # Try to get a free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            port = s.getsockname()[1]
        
        print(f"Starting on port {port}")
        ui.run(title='My App', port=port)
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        # Fallback to native mode
        print("Trying native mode...")
        ui.run(title='My App', native=True)
```

## Getting the Selected Port When OS Chooses

When you let the OS choose the port (either through native mode or socket port 0), you'll need to access the actual port number for logging or other purposes.

### Method 1: Using Socket Port 0 (Recommended)

When using the socket method, you can get the port before passing it to NiceGUI:

```python
import socket
from nicegui import ui

def get_free_port() -> int:
    """Get a free TCP port and return it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    return port

@ui.page('/')
def index():
    ui.label('Hello NiceGUI!')

# Get the port and log it
port = get_free_port()
print(f"🚀 Starting NiceGUI application on port {port}")
print(f"📱 Open http://localhost:{port} in your browser")

# Start NiceGUI with the known port
ui.run(port=port, title='My App')
```

### Method 2: Accessing Server Information (Advanced)

You can access the server instance after NiceGUI starts, though this is less reliable:

```python
from nicegui import ui
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@ui.page('/')
def index():
    ui.label('Hello NiceGUI!')

# In native mode, NiceGUI will automatically find a port
def log_server_info():
    """Log server information after startup."""
    try:
        # Access the server instance (internal API - may change)
        from nicegui.server import Server
        server = Server.instance
        
        if server and hasattr(server, 'config'):
            port = server.config.port
            host = server.config.host
            logger.info(f"🚀 NiceGUI server running on {host}:{port}")
        else:
            logger.warning("Could not access server configuration")
            
    except Exception as e:
        logger.error(f"Error accessing server info: {e}")

# Register startup callback
from nicegui import app
app.on_startup(log_server_info)

# Start in native mode (auto-selects port)
ui.run(native=True, title='My App')
```

### Method 3: Environment Variable Approach

Set environment variables to capture port information:

```python
import os
from nicegui import ui

@ui.page('/')
def index():
    ui.label('Hello NiceGUI!')

def start_with_logging():
    """Start app with port logging via environment."""
    # Check if port was set by NiceGUI
    port = os.getenv('NICEGUI_PORT')
    host = os.getenv('NICEGUI_HOST', 'localhost')
    
    if port:
        print(f"🚀 NiceGUI running on {host}:{port}")
    
    ui.run(native=True, title='My App')

start_with_logging()
```

### Method 4: Custom Server Wrapper

Create a wrapper that captures the actual server configuration:

```python
import socket
from nicegui import ui
from typing import Optional

class NiceGUIWrapper:
    def __init__(self):
        self.actual_port: Optional[int] = None
        self.actual_host: Optional[str] = None
    
    def start(self, preferred_port: int = 8080, native: bool = False):
        """Start NiceGUI with port tracking."""
        
        if native:
            # Native mode - we can't easily predict the port
            print("🚀 Starting in native mode (port auto-selected)")
            
            # Register callback to try to get port info
            from nicegui import app
            app.on_startup(self._log_startup_info)
            
            ui.run(native=True, title='My App')
        else:
            # Use socket method for predictable port
            if self._is_port_available(preferred_port):
                port = preferred_port
            else:
                port = self._get_free_port()
            
            self.actual_port = port
            self.actual_host = '127.0.0.1'
            
            print(f"🚀 Starting NiceGUI on {self.actual_host}:{self.actual_port}")
            print(f"📱 Open http://{self.actual_host}:{self.actual_port}")
            
            ui.run(port=port, title='My App')
    
    def _get_free_port(self) -> int:
        """Get a free port using socket."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def _is_port_available(self, port: int) -> bool:
        """Check if port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False
    
    def _log_startup_info(self):
        """Try to log server info on startup."""
        try:
            from nicegui.server import Server
            server = Server.instance
            if server and hasattr(server, 'config'):
                port = server.config.port
                host = server.config.host
                print(f"✅ Server confirmed running on {host}:{port}")
                self.actual_port = port
                self.actual_host = host
        except Exception as e:
            print(f"⚠️ Could not determine server port: {e}")

# Usage
@ui.page('/')
def index():
    ui.label('Hello NiceGUI!')

wrapper = NiceGUIWrapper()
wrapper.start(preferred_port=8080, native=False)
```

### Important Notes

1. **Socket Method (Recommended)**: Most reliable way to know the port beforehand
2. **Native Mode Limitations**: In native mode, the port is chosen internally and harder to access
3. **Internal APIs**: Server instance access may change between NiceGUI versions
4. **Startup Callbacks**: Use `app.on_startup()` to access server info after initialization
5. **Environment Variables**: May not always be available depending on how NiceGUI is started

### Best Practice for Production

For production applications where you need to log the port, use the socket method:

```python
import socket
import logging
from nicegui import ui

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

@ui.page('/')
def index():
    ui.label('Production App')

def start_production_app():
    port = get_free_port()
    
    # Log the port for monitoring/debugging
    logger.info(f"Starting production server on port {port}")
    
    # You could also write to a file, send to monitoring, etc.
    with open('server.port', 'w') as f:
        f.write(str(port))
    
    ui.run(
        port=port,
        host='0.0.0.0',
        title='Production App',
        show=False
    )

start_production_app()
```

## Starting NiceGUI with a Specific Port

### Basic Usage

To start NiceGUI on a specific port, simply pass the `port` parameter to `ui.run()`:

```python
from nicegui import ui

@ui.page('/')
def index():
    ui.label('Hello NiceGUI!')

# Start on port 5000
ui.run(port=5000)
```

### Common Configurations

```python
# Development server
ui.run(port=3000, title='Dev Server', reload=True)

# Production server
ui.run(port=8888, host='0.0.0.0', show=False)

# Custom port with all options
ui.run(
    host='127.0.0.1',
    port=5000,
    title='My App',
    show=True,
    reload=False
)
```

### Command Line Integration

```python
import argparse
from nicegui import ui

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    
    ui.run(port=args.port)

# Usage: python app.py --port 5000
```

### Important Notes

- **Port Range**: Valid ports are 1-65535
- **Privileged Ports**: Ports < 1024 require admin privileges
- **Native Mode**: When `native=True`, port parameter is ignored
- **Default**: NiceGUI defaults to port 8080

## References

- [NiceGUI ui.run Documentation](https://nicegui.io/documentation/run)
- [NiceGUI Configuration & Deployment](https://nicegui.io/documentation/section_configuration_deployment)
- [Python Socket Documentation](https://docs.python.org/3/library/socket.html)
- [Port 0 Binding Technique](https://www.lifewire.com/port-0-in-tcp-and-udp-818145)
