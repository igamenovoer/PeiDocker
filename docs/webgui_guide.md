# PeiDocker Web GUI Guide

The PeiDocker Web GUI provides a modern, intuitive interface for creating and managing Docker projects without needing deep knowledge of Docker configuration files. Built with the NiceGUI framework, it offers both browser-based and native desktop experiences.

## Table of Contents
- [Getting Started](#getting-started)
- [Launch Options](#launch-options)
- [Interface Overview](#interface-overview)
- [Configuration Pages](#configuration-pages)
- [Advanced Features](#advanced-features)
- [Tips and Best Practices](#tips-and-best-practices)

## Getting Started

### Quick Start

The simplest way to start the GUI is:

```sh
pei-docker-gui start
```

This will:
1. Automatically find an available port
2. Start the web server
3. Open your default browser to the GUI
4. Display the welcome page for project management

### Launch with Existing Project

To load an existing PeiDocker project:

```sh
pei-docker-gui start --project-dir /path/to/your/project
```

### Create New Project in Specific Location

```sh
pei-docker-gui start --project-dir /path/to/new/project
```

If the directory doesn't exist or is empty, a new project will be created there.

## Launch Options

### Port Selection

The GUI intelligently handles port selection:

- **Auto-selection** (default): Finds the first available port starting from 8050
- **Specific port**: Use `--port 8080` to request a specific port
- **Fallback**: If requested port is busy, automatically finds the next available

```sh
# Auto-select port
pei-docker-gui start

# Request specific port
pei-docker-gui start --port 9090
```

### Native Desktop Mode

For a desktop application experience:

```sh
pei-docker-gui start --native
```

Requirements:
- Install `pywebview`: `pip install pywebview`
- Provides OS-native window instead of browser
- Enables native file dialogs
- Better integration with desktop environment

### Jump to Specific Page

For development or debugging, jump directly to a configuration page:

```sh
# Jump to SSH configuration
pei-docker-gui start --jump-to-page ssh

# Jump to network settings with existing project
pei-docker-gui start --project-dir ./my-project --jump-to-page network
```

Available pages: `home`, `project`, `ssh`, `network`, `environment`, `storage`, `scripts`, `summary`

## Interface Overview

### Navigation

The GUI uses a tab-based wizard interface with:

- **Tab Bar**: Quick access to all configuration sections
- **Progress Indicators**: Visual feedback on configuration completeness
- **Navigation Buttons**: Previous/Next for sequential configuration
- **Validation Status**: Real-time error checking with helpful messages

### Home Page

The welcome page provides:

- **Create New Project**: Start fresh with wizard guidance
- **Load Existing Project**: Browse and open existing projects
- **Recent Projects**: Quick access to recently used projects
- **Import Project**: Upload a ZIP file to restore a project

### Project Management

- **Auto-save**: All changes are automatically saved
- **Validation**: Real-time configuration validation
- **Export**: Download project as ZIP for backup/sharing
- **Templates**: Quick-start configurations for common setups

## Configuration Pages

### 1. Project Configuration

Basic Docker image settings:

- **Base Image**: Select Ubuntu version or custom image
- **Output Image Name**: Define your image name and tag
- **Stage Configuration**: Separate settings for stage-1 (system) and stage-2 (application)

### 2. SSH Configuration

Comprehensive SSH server setup:

#### User Management
- Add multiple users with different permissions
- Set custom UIDs for each user
- Configure root access if needed

#### Authentication Methods

The GUI supports four authentication methods:

1. **Password Only**: Simple password authentication
2. **Public Key File**: Reference an existing `.pub` file
3. **Inline Public Key**: Paste public key directly
4. **Private Key Input**: Provide private key (public key auto-generated)

Example configurations:

```yaml
# Method 1: Password only
users:
  myuser:
    password: 'secure-password'
    uid: 1000

# Method 2: Public key file
users:
  myuser:
    password: 'secure-password'
    pubkey_file: 'stage-1/system/ssh/keys/mykey.pub'
    uid: 1000

# Method 3: Inline public key
users:
  myuser:
    password: 'secure-password'
    pubkey_text: 'ssh-rsa AAAAB3NzaC1yc2EA...'
    uid: 1000

# Method 4: Private key (public generated)
users:
  myuser:
    password: 'secure-password'
    privkey_text: |
      -----BEGIN OPENSSH PRIVATE KEY-----
      b3BlbnNzaC1rZXktdjEAA...
      -----END OPENSSH PRIVATE KEY-----
    uid: 1000
```

### 3. Network Configuration

#### Port Mappings

Separate port configurations for different purposes:

- **Stage-1 Ports**: System services (databases, cache, monitoring)
  - Example: `5432:5432` for PostgreSQL
  - Example: `6379:6379` for Redis

- **Stage-2 Ports**: Application services (web apps, APIs)
  - Example: `8080:8080` for web application
  - Example: `3000:3000` for Node.js app

#### Proxy Settings

Configure HTTP/HTTPS proxy for package downloads:

- **Proxy Address**: Default `host.docker.internal` for host proxy
- **Proxy Port**: Port number for proxy service
- **Global Enable**: Apply proxy to all commands
- **HTTPS Support**: Use HTTPS proxy protocol
- **Build-time Only**: Remove proxy after image build

### 4. Environment Variables

Flexible environment configuration with Docker Compose syntax:

```yaml
# Static values
environment:
  - 'NODE_ENV=production'
  
# With default fallback
environment:
  - 'API_URL=${API_URL:-http://localhost:8080}'
  - 'DB_HOST=${DB_HOST:-postgres}'
  
# Reference other variables
environment:
  - 'FULL_URL=${PROTOCOL:-https}://${DOMAIN:-example.com}'
```

Features:
- Stage-specific variables (stage-1 and stage-2 separate)
- Visual editor with syntax highlighting
- Variable substitution preview
- Import from `.env` files

### 5. Storage Configuration

#### Storage Strategies

Choose from four storage approaches:

1. **Auto-volume**: Docker manages volume creation
2. **Manual-volume**: Use specific named volumes
3. **Host Mount**: Bind to host directories
4. **In-image**: Store directly in image (not recommended for data)

#### Predefined Directories

Three standard directories with automatic management:

- `/soft/app`: Application installations
- `/soft/data`: Persistent data
- `/soft/workspace`: Working files and code

#### Custom Mounts

Add additional volume mounts:

```yaml
mount:
  home_user:
    type: auto-volume
    dst_path: /home/myuser
  
  shared_data:
    type: host
    dst_path: /shared
    host_path: /host/shared/data
```

### 6. Scripts Configuration

Automate tasks with custom scripts:

#### Script Execution Points

- **on_build**: During image building
- **on_first_run**: First container start only
- **on_every_run**: Every container start
- **on_user_login**: When user logs in via SSH

#### Script Parameters

Scripts support shell-like parameters:

```yaml
custom:
  on_build:
    - 'install-tools.sh --verbose --config=/tmp/build.conf'
    - 'setup-environment.sh --mode=production --port=8080'
```

#### Script Organization

- Stage-1 scripts: System-level setup
- Stage-2 scripts: Application-level configuration
- Scripts stored in `installation/stage-*/custom/`

### 7. Summary Page

Complete configuration overview:

- **Review All Settings**: Comprehensive configuration display
- **Validation Summary**: List of any errors or warnings
- **Export Options**:
  - Download as ZIP file
  - Generate docker-compose.yml
  - Create Dockerfiles
- **Copy Commands**: Ready-to-use Docker commands

## Advanced Features

### Project Templates

Quick-start configurations for common scenarios:

1. **Minimal Config**: Bare minimum for simple containers
2. **Development Environment**: Full development setup with tools
3. **Production Server**: Optimized for production deployment
4. **Data Science**: Jupyter, Python packages, data tools

### Configuration Import/Export

#### Export Project

1. Navigate to Summary page
2. Click "Export as ZIP"
3. Save the downloaded file

#### Import Project

1. From Home page, click "Import Project"
2. Select ZIP file
3. Choose destination directory
4. Review imported configuration

### Minimal Config Mode

For simple projects, use minimal configuration:

```yaml
# Minimal user_config.yml
stage_1:
  image:
    base: ubuntu:24.04
    output: my-app:latest
  ssh:
    enable: true
    users:
      me:
        password: '123456'
```

The GUI will use defaults for all other settings.

### Real-time Validation

The GUI provides immediate feedback:

- **Red highlights**: Configuration errors
- **Yellow warnings**: Potential issues
- **Green checks**: Valid configuration
- **Inline help**: Hover for detailed explanations

### Keyboard Shortcuts

When in browser mode:

- `Ctrl+S`: Save current configuration
- `Tab`: Navigate between fields
- `Shift+Tab`: Navigate backwards
- `Enter`: Submit current form

## Tips and Best Practices

### 1. Project Organization

- Use descriptive project names
- Keep related projects in the same parent directory
- Regular exports for backup
- Document custom scripts

### 2. Security Considerations

- Use strong passwords for SSH users
- Prefer key-based authentication over passwords
- Don't commit sensitive data to version control
- Use environment variables for secrets

### 3. Performance Optimization

- Use specific base image tags (not `latest`)
- Minimize stage-1 for faster rebuilds
- Cache apt packages with persistent volumes
- Use multi-stage builds effectively

### 4. Development Workflow

1. Start with templates for quick setup
2. Use jump-to-page for rapid testing
3. Export projects before major changes
4. Test with minimal configs first

### 5. Troubleshooting

Common issues and solutions:

- **Port conflicts**: Use auto-selection or change port
- **Validation errors**: Check inline help messages
- **Import failures**: Ensure ZIP file is valid PeiDocker export
- **SSH connection issues**: Verify port mappings and user configuration

### 6. GUI Performance

For better performance:

- Use native mode for large projects
- Close unnecessary browser tabs
- Clear browser cache if sluggish
- Use modern browsers (Chrome, Firefox, Edge)

## Command Reference

### Full CLI Options

```sh
pei-docker-gui start [OPTIONS]

Options:
  --port PORT           Port number (default: auto-select)
  --project-dir PATH    Project directory path
  --jump-to-page PAGE   Start page (home|project|ssh|network|
                       environment|storage|scripts|summary)
  --native             Native desktop mode
  --help               Show help message
```

### Examples Collection

```sh
# Development setup
pei-docker-gui start --project-dir ./dev-env --jump-to-page ssh

# Production configuration
pei-docker-gui start --project-dir ./prod --port 8080

# Quick testing
pei-docker-gui start --jump-to-page network

# Desktop application
pei-docker-gui start --native --project-dir ~/docker-projects/myapp

# Full configuration
pei-docker-gui start \
  --port 9090 \
  --project-dir ./my-project \
  --jump-to-page storage \
  --native
```

## Conclusion

The PeiDocker Web GUI makes Docker project configuration accessible to users of all skill levels. With its intuitive interface, comprehensive validation, and powerful features, you can create sophisticated Docker configurations without editing YAML files directly.

For more information:
- [Main Documentation](index.md)
- [CLI Reference](cli_reference.md)
- [Configuration Examples](examples/basic.md)
- [Advanced Examples](examples/advanced.md)