# CLI Reference

PeiDocker provides two command-line tools:
- `pei-docker-cli` - CLI for project management
- `pei-docker-gui` - Web GUI launcher

## pei-docker-cli

**Usage:** `pei-docker-cli [OPTIONS] COMMAND [ARGS]...`

### Commands

| Command | Description |
| --- | --- |
| `create` | Create new project |
| `configure` | Generate docker-compose.yml from user_config.yml |
| `remove` | Remove Docker images and containers |

### create

Creates new PeiDocker project with template files.

**Usage:** `pei-docker-cli create [OPTIONS]`

**Options:**
- `-p, --project-dir DIRECTORY` - Project directory (required)
- `-e, --with-examples` - Include example files (default: enabled)
- `--with-contrib` - Include contrib directory (default: enabled)

**Examples:**
```sh
# Create with all files
pei-docker-cli create -p ./my-project

# Minimal project
pei-docker-cli create -p ./minimal --no-with-examples --no-with-contrib
```

### configure

Generates docker-compose.yml and Dockerfiles from user_config.yml.

**Usage:** `pei-docker-cli configure [OPTIONS]`

**Options:**
- `-p, --project-dir DIRECTORY` - Project directory (default: current)
- `-c, --config FILE` - Config file name (default: user_config.yml)
- `-f, --full-compose` - Generate extended compose file
- `--with-merged` - Generate standalone merged build artifacts (merged.Dockerfile, merged.env, build-merged.sh)

**Examples:**
```sh
# Use current directory
pei-docker-cli configure

# Specify directory
pei-docker-cli configure -p ./my-project

# Custom config file
pei-docker-cli configure -c prod-config.yml

# Full compose file
pei-docker-cli configure -f

# Generate merged build artifacts (build without docker compose)
pei-docker-cli configure --with-merged

# Build using the generated script
./build-merged.sh

# Override output image tag at build time
./build-merged.sh --output-image myorg/myapp:dev
./build-merged.sh -o myorg/myapp:dev

# Pass extra flags directly to `docker build`
./build-merged.sh -- --no-cache --progress=plain
./build-merged.sh --build-arg HTTP_PROXY=http://host.docker.internal:7890

# Run the generated image with helper script
./run-merged.sh -d -p 8080:8080

# Show script help
./build-merged.sh --help
./run-merged.sh --help
```

### remove

Removes Docker images and containers created by project.

**Usage:** `pei-docker-cli remove [OPTIONS]`

**Options:**
- `-p, --project-dir DIRECTORY` - Project directory (required)
- `-y, --yes` - Skip confirmation

**Examples:**
```sh
# Remove with confirmation
pei-docker-cli remove -p ./my-project

# Remove without confirmation
pei-docker-cli remove -p ./my-project -y
```

## pei-docker-gui

Web interface for PeiDocker project configuration.

**Usage:** `pei-docker-gui [OPTIONS] COMMAND [ARGS]...`

### start

Starts web interface server.

**Usage:** `pei-docker-gui start [OPTIONS]`

**Options:**
- `--port PORT` - Server port (default: auto-select)
- `--project-dir PATH` - Project directory to load/create
- `--jump-to-page PAGE` - Start on specific page
- `--native` - Run in OS window (requires pywebview)

**Page Options:**

| Page | Function |
| --- | --- |
| `home` | Project management |
| `project` | Docker image settings |
| `ssh` | SSH configuration |
| `network` | Port and proxy settings |
| `environment` | Environment variables |
| `storage` | Volume configuration |
| `scripts` | Custom scripts |
| `summary` | Configuration overview |

**Project Directory Behavior:**

| Condition | Action |
| --- | --- |
| Has `user_config.yml` | Load project |
| Empty directory | Create new project |
| Non-existent | Create directory and project |
| Has other files | Show error |
| Not specified | Show project selector |

**Examples:**
```sh
# Auto-select port
pei-docker-gui start

# Specific port
pei-docker-gui start --port 8080

# Load project
pei-docker-gui start --project-dir /path/to/project

# New project, jump to SSH
pei-docker-gui start --project-dir /tmp/new --jump-to-page ssh

# Native window mode
pei-docker-gui start --native
```

## GUI Configuration Pages

### SSH Configuration
- Multiple users
- Password authentication
- SSH key files (public/private)
- Inline key input
- UID assignment

### Network Configuration  
- Stage-1 ports (system services)
- Stage-2 ports (applications)
- Proxy settings
- Global proxy enable/disable

### Storage Management
- Storage types: auto-volume, manual-volume, host, image
- Volume configuration
- Bind mount paths
- Stage-2 directories: /soft/app, /soft/data, /soft/workspace

### Script Management
- Lifecycle hooks: on_build, on_first_run, on_every_run, on_user_login
- Script parameters
- Stage-specific scripts

### Environment Variables
- Docker Compose syntax: `${VAR:-default}`
- Stage-specific variables
- List format

Boolean handling for environment variables used by PeiDocker scripts and Dockerfiles:
- Accept `true`/`false` in a case-insensitive manner and numeric `1`/`0`.
- Empty value means “use system/default” (not forced true/false).
- When using `--with-merged`, `merged.env` emits lowercase `true`/`false`.

Merged script quick reference:
- `build-merged.sh` options:
  - `-o, --output-image <name:tag>` override output tag
  - `--` pass additional flags straight to `docker build`
  - `-h, --help` show help
- `run-merged.sh` options:
  - `-n, --name`, `-d, --detach`, `--no-rm`, `--image <name:tag>`
  - `-p, --publish`, `-v, --volume`, `--gpus auto|all|none`
  - `--` pass a command to run in the container
  - `-h, --help` show help

## Features

### Auto-port Selection
Automatically finds available port when not specified or port is in use.

### Project Validation
Validates configuration before generating docker-compose.yml.

### ZIP Export/Import
Export project as ZIP for backup or sharing.

### Native Mode
With `--native` flag and pywebview installed:
- OS window instead of browser
- Native file dialogs
- Desktop application interface

## Notes

- Generated files: docker-compose.yml, stage-1.Dockerfile, stage-2.Dockerfile
- Template files should not be modified
- Scripts in installation/ directory are copied to /pei-from-host in image
- Stage-1 builds base image with system packages
- Stage-2 builds application image with custom packages
- External storage only available in stage-2
