# Do this task

## Prerequisites

Read these first:
- Terminololy: `context/design/terminology.md`, to understand the concepts used in this task.
- Coding guide: `context/instructions/debug-code.md`, to understand how to debug the code, and also note that python code should be strongly typed, see `context/instructions/strongly-typed.md` for details.

## The problem

change the default behavior of the `pei-docker-gui start` command, it will try to bind to port 8080, but if that port is already in use, it should try to bind to the next available port, and so until it finds an available port. Otherwise, we face the following error:

```powershell
(pei-docker) PS D:\code\PeiDocker> pei-docker-gui start                                                                                                                                                                   
Starting PeiDocker Web GUI on port 8080...
Open http://localhost:8080 in your browser
NiceGUI ready to go on http://localhost:8080, http://169.254.3.1:8080, http://169.254.81.66:8080, http://172.22.240.1:8080, http://192.168.0.95:8080, and http://198.18.0.1:8080
ERROR:    [Errno 13] error while attempting to bind on address ('0.0.0.0', 8080): [winerror 10013] an attempt was made to access a socket in a way forbidden by its access permissions
(pei-docker) PS D:\code\PeiDocker> 
```

we should change the default behavior of the `pei-docker-gui start` command to try to bind to a free port always, and let user to specify the port if they want to.

### How to bind to free port

The simplest cross-platform way to find an available TCP port in Python:

```python
import socket

def get_free_port() -> int:
    """Get a free TCP port in a cross-platform way."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to any available port
        port = s.getsockname()[1]  # Get the assigned port number
    return port

# Usage
port = get_free_port()
print(f"Available port: {port}")
```

**How it works:**
- `socket.bind(('', 0))` tells the OS to assign any available port (port 0 is special)
- The OS atomically assigns a free port, preventing race conditions
- `getsockname()[1]` returns the actual port number assigned
- This works on Windows, Linux, and macOS

**Alternative - try ports sequentially:**
```python
import socket

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
```

