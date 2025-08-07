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

Web-based graphical interface for managing PeiDocker projects.

**Usage:** `pei-docker-gui [OPTIONS] COMMAND [ARGS]...`

### Commands

| Command | Description |
| --- | --- |
| `start` | Start the NiceGUI web application server |

---

## `start` (GUI)

**Usage:** `pei-docker-gui start [OPTIONS]`

Starts the web interface for visual project configuration.

### Options

| Option | Description |
| --- | --- |
| `--port PORT` | Port to run the web application (default: auto-select free port) |
| `--project-dir PATH` | Project directory to load/create on startup |
| `--jump-to-page PAGE` | Navigate to specific page after startup |
| `--help` | Show this message and exit. |

### Page Options for `--jump-to-page`

| Page | Description |
| --- | --- |
| `home` | Main welcome page |
| `project` | Project configuration page |
| `ssh` | SSH configuration page |
| `network` | Network and port configuration page |
| `environment` | Environment variables page |
| `storage` | Volume and mount configuration page |
| `scripts` | Custom scripts configuration page |
| `summary` | Complete project overview page |

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
```

### Notes

- If no port is specified, the system automatically selects a free port
- If the specified port is in use, the next available port is used
- The web interface provides project import/export functionality (ZIP files)
- All project configurations can be visually edited with real-time validation
