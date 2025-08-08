# CLI Reference

PeiDocker provides two command-line tools:
- `pei-docker-cli` - Main CLI for project management
- `pei-docker-gui` - Web GUI launcher

## `pei-docker-cli`

**Usage:** `pei-docker-cli [OPTIONS] COMMAND [ARGS]...`

### Options

| Option | Description |
| --- | --- |
| `--help` | Show this message and exit. |

### Commands

| Command | Description |
| --- | --- |
| `create` | Creates a new PeiDocker project. |
| `configure` | Configures a PeiDocker project. |
| `remove` | Removes Docker images and containers created by this project. |

---

## `create`

**Usage:** `pei-docker-cli create [OPTIONS]`

### Options

| Option | Description |
| --- | --- |
| `-p`, `--project-dir DIRECTORY` | project directory (required) |
| `-e`, `--with-examples` | copy example files to the project dir |
| `--with-contrib` | copy contrib directory to the project dir |
| `--help` | Show this message and exit. |

---

## `configure`

**Usage:** `pei-docker-cli configure [OPTIONS]`

### Options

| Option | Description |
| --- | --- |
| `-p`, `--project-dir DIRECTORY` | project directory (default: current working directory) |
| `-c`, `--config FILE` | config file name, relative to the project dir |
| `-f`, `--full-compose` | generate full compose file with x-??? sections |
| `--help` | Show this message and exit. |

---

## `remove`

**Usage:** `pei-docker-cli remove [OPTIONS]`

### Options

| Option | Description |
| --- | --- |
| `-p`, `--project-dir DIRECTORY` | project directory (required) |
| `-y`, `--yes` | skip confirmation prompts |
| `--help` | Show this message and exit. |

---

## `pei-docker-gui`

Modern web-based graphical interface for managing PeiDocker projects, built with NiceGUI framework.

**Usage:** `pei-docker-gui [OPTIONS] COMMAND [ARGS]...`

### Commands

| Command | Description |
| --- | --- |
| `start` | Start the NiceGUI web application server |

---

## `start` (GUI)

**Usage:** `pei-docker-gui start [OPTIONS]`

Starts the web interface for visual project configuration. The GUI provides a comprehensive wizard-style interface for creating and managing PeiDocker projects.

### Options

| Option | Description | Default |
| --- | --- | --- |
| `--port PORT` | Port to run the web application | Auto-select free port |
| `--project-dir PATH` | Project directory to load/create on startup | None |
| `--jump-to-page PAGE` | Navigate to specific page after startup | `home` |
| `--native` | Run in native desktop mode with OS window (requires pywebview) | False |
| `--help` | Show this message and exit. | - |

### Page Options for `--jump-to-page`

| Page | Description | Key Features |
| --- | --- | --- |
| `home` | Main welcome page | Project creation, loading, recent projects |
| `project` | Project configuration page | Docker image settings, base image selection |
| `ssh` | SSH configuration page | User management, authentication methods, key generation |
| `network` | Network and port configuration | Port mappings (stage-1/2), proxy settings |
| `environment` | Environment variables page | Docker Compose-style substitution, stage-specific vars |
| `storage` | Volume and mount configuration | Storage strategies, volume management, bind mounts |
| `scripts` | Custom scripts configuration | Build/runtime scripts, parameter support |
| `summary` | Complete project overview | Configuration review, export, docker-compose generation |

### Project Directory Behavior

The `--project-dir` option determines the startup behavior:

| Scenario | Behavior |
| --- | --- |
| Directory exists with `user_config.yml` | Load existing PeiDocker project |
| Directory exists but empty | Create new project in that location |
| Directory doesn't exist | Create directory and new project |
| Directory contains non-PeiDocker files | Show error and exit |
| No `--project-dir` specified | Start with project management screen |

### Examples

```sh
# Start GUI on auto-selected port
pei-docker-gui start

# Start on specific port
pei-docker-gui start --port 8080

# Load existing project
pei-docker-gui start --project-dir /path/to/project

# Create new project and jump to SSH config
pei-docker-gui start --project-dir /tmp/new-project --jump-to-page ssh

# Quick debugging - jump to network page
pei-docker-gui start --jump-to-page network

# Run in native desktop mode
pei-docker-gui start --native

# Full example with all options
pei-docker-gui start --port 9090 --project-dir ./my-project --jump-to-page storage --native
```

### GUI Features

**Visual Configuration:**
- Tab-based navigation with progress indicators
- Real-time validation with error highlighting
- Contextual help and tooltips
- Configuration templates for quick setup

**Project Management:**
- Create new projects with wizard interface
- Load and modify existing projects
- Import/export projects as ZIP files
- Recent projects list with quick access

**SSH Configuration:**
- Multiple user management
- Password authentication
- SSH key file references
- Inline public/private key input
- Automatic public key generation from private keys
- Custom UID assignment

**Network Configuration:**
- Separate port mappings for stage-1 and stage-2
- Visual port conflict detection
- Proxy configuration with global settings
- Environment-specific network setup

**Storage Management:**
- Four storage strategies: auto-volume, manual-volume, host, image
- Visual volume configuration
- Bind mount management
- Storage location preview

**Script Management:**
- Custom scripts for different lifecycle events
- Script parameter support with shell syntax
- Script file validation
- Stage-specific script organization

**Environment Variables:**
- Visual editor with syntax highlighting
- Docker Compose-style variable substitution
- Stage-specific environment configuration
- Default value support

### Native Desktop Mode

When using `--native` flag:
- Opens in OS-native window instead of browser
- Provides native file dialogs for better file selection
- Requires `pywebview` package to be installed
- Offers desktop application experience
- Supports all standard GUI features

### Notes

- **Auto-port Selection**: If no port is specified, the system automatically finds an available port
- **Port Fallback**: If the specified port is in use, the next available port is automatically selected
- **Browser Launch**: The web interface automatically opens in your default browser (unless using `--native`)
- **Project Validation**: Configuration is validated before server startup to prevent runtime errors
- **Temp Projects**: Jump-to-page without project-dir creates temporary projects with timestamps
- **ZIP Export/Import**: Complete project backup and restoration via ZIP files
- **Real-time Updates**: All configuration changes are immediately validated and saved
