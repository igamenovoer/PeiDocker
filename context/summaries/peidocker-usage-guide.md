# PeiDocker Usage Guide

## Overview

PeiDocker is a Python-based Docker automation tool that simplifies Docker container creation through YAML configuration files. It generates Dockerfiles and docker-compose.yml files from user-friendly configuration, eliminating the need to learn Dockerfile syntax.

## Key Concepts

### Two-Stage Build System

PeiDocker uses a two-stage approach:
- **Stage 1**: Base system setup (OS, SSH, system packages)
- **Stage 2**: Application layer (custom software, persistent storage)

### Storage Strategy

- `/hard/image`: In-image persistent storage
- `/hard/volume`: Docker volume mounts (only in stage-2)
- `/soft`: Bind mounts for development

## Configuration Format

Configuration files use YAML format with two main sections: `stage_1` and `stage_2`.

### Basic Structure

```yaml
stage_1:
  image:
    base: ubuntu:24.04              # Base Docker image
    output: my-image:stage-1        # Output image name
  
  ssh:
    enable: true                    # Enable SSH server
    port: 22                        # Container SSH port
    host_port: 2222                 # Host port mapping
    
    users:
      admin:
        password: 'mypassword'      # User password
        uid: 1000                   # User ID
        # SSH key options (all optional):
        pubkey_text: |              # Inline public key
          ssh-rsa AAAAB3...
        privkey_text: |             # Inline private key
          -----BEGIN OPENSSH PRIVATE KEY-----
          ...
          -----END OPENSSH PRIVATE KEY-----
        pubkey_file: 'path/to/key.pub'   # Or file path
        privkey_file: 'path/to/key'      # Or file path

  apt:
    repo_source: ''                 # Mirror: tuna, aliyun, 163, ustc, cn
    
  proxy:
    address: host.docker.internal   # Proxy address
    port: 7890                      # Proxy port
    enable_globally: false          # Apply globally
    
  environment:
    - 'MY_VAR=value'                # Environment variables
    
  device:
    type: cpu                       # cpu or gpu
    
  custom:
    on_build:                       # Scripts run during build
      - 'stage-1/custom/script.sh'
    on_first_run:                   # Scripts on first start
      - 'stage-1/custom/init.sh'
    on_every_run:                   # Scripts on every start
      - 'stage-1/custom/startup.sh'
    on_user_login:                  # Scripts on SSH login
      - 'stage-1/custom/welcome.sh'

stage_2:
  image:
    output: my-image:stage-2        # Stage 2 output image
    
  storage:                          # Persistent storage config
    app:
      type: host                    # host, auto-volume, manual-volume, image
      host_path: /path/on/host      # For type: host
      volume_name: my-volume        # For type: manual-volume
    data:
      type: auto-volume             # Auto-managed volume
    workspace:
      type: host
      host_path: /workspace/shared
      
  mount:                            # Additional mounts
    cache:
      type: auto-volume
      dst_path: /var/cache
      
  custom:
    on_build:
      - 'stage-2/system/install-app.sh'
```

### Key Features

1. **Environment Variable Substitution**: 
   - Supports Docker Compose style: `${VAR:-default}`
   - Works in any configuration value

2. **SSH Key Management**:
   - `pubkey_text`/`privkey_text`: Inline key specification
   - `pubkey_file`/`privkey_file`: File-based keys
   - Text and file options are mutually exclusive
   - Private keys auto-generate public keys

3. **Lifecycle Hooks**:
   - `on_build`: During image build
   - `on_first_run`: First container startup
   - `on_every_run`: Every container start
   - `on_user_login`: SSH login

4. **Storage Types**:
   - `host`: Bind mount from host
   - `auto-volume`: Automatically managed Docker volume
   - `manual-volume`: User-specified Docker volume
   - `image`: Stored in the image itself

## How to Use PeiDocker

### 1. Prerequisites

Install required dependencies:
```bash
pip install click omegaconf attrs cattrs
```

Make sure Docker and docker-compose are installed.

### 2. Get PeiDocker

```bash
git clone <peidocker-repo>
cd PeiDocker
```

### 3. Create Project

Create a new project directory with default template:

```bash
# Create project with examples and contrib files (default)
python -m pei_docker.pei create -p ./build

# Or create minimal project
python -m pei_docker.pei create -p ./build --no-with-examples --no-with-contrib
```

This generates:
- Project directory structure
- Default `user_config.yml` template
- Installation script directories
- Example files (if not disabled)

### 4. Edit Configuration

Edit the `user_config.yml` file in your project directory according to your needs.

### 5. Configure Project

Generate docker-compose.yml from your configuration:

```bash
# Use default config file (user_config.yml)
python -m pei_docker.pei configure -p ./build

# Use custom config file
python -m pei_docker.pei configure -p ./build -c my-custom-config.yml

# Generate full compose file with extended sections
python -m pei_docker.pei configure -p ./build -f
```

This generates:
- `docker-compose.yml` with proper volume and network configuration
- Dockerfiles for both stages
- Environment setup

### 6. Build and Run

```bash
cd build  # or your project directory

# Build stage 1 (base system)
docker compose build stage-1 --progress=plain

# Build stage 2 (application layer)
docker compose build stage-2 --progress=plain

# Run container (typically stage-2)
docker compose up stage-2

# SSH into container (if SSH is configured)
# Default user is 'me' with password '123456' on port 2222
ssh me@127.0.0.1 -p 2222
```

## How It Works

### Project Structure

After creation and configuration, your project will have:
```
build/                          # Project directory
├── user_config.yml             # Your configuration file
├── docker-compose.yml          # Generated Docker Compose file (after configure)
├── stage-1.Dockerfile          # Stage 1 Dockerfile (after configure)
├── stage-2.Dockerfile          # Stage 2 Dockerfile (after configure)
├── installation/               # Installation scripts
│   ├── stage-1/
│   │   ├── system/            # System scripts (SSH, etc.)
│   │   └── custom/            # Your custom scripts
│   └── stage-2/
│       ├── system/
│       └── custom/
├── ssh_keys/                   # Generated SSH keys (after configure)
├── examples/                   # Example configurations (optional)
└── contrib/                    # Contributed scripts (optional)
```

### Build Process

1. **Stage 1 Build**:
   - Sets up base image
   - Configures SSH server and users
   - Installs system packages
   - Runs stage-1 `on_build` scripts

2. **Stage 2 Build**:
   - Builds on stage-1 image
   - Sets up persistent storage
   - Runs stage-2 `on_build` scripts
   - Configures application environment

3. **Runtime**:
   - Executes `on_first_run` scripts on initial start
   - Runs `on_every_run` scripts on each start
   - Triggers `on_user_login` scripts on SSH login

### Advanced Features

#### GPU Support
```yaml
device:
  type: gpu
```

#### Chinese Mirrors
```yaml
apt:
  repo_source: tuna  # or aliyun, 163, ustc
```

#### Proxy Configuration
```yaml
proxy:
  address: host.docker.internal
  port: 7890
  enable_globally: true
```

#### Multiple Storage Volumes
```yaml
storage:
  app:
    type: manual-volume
    volume_name: app-data
  workspace:
    type: host
    host_path: ${WORKSPACE_PATH:-/workspace}
  cache:
    type: auto-volume
```

## Best Practices

1. **Use Stage 1** for system-level setup and dependencies
2. **Use Stage 2** for application code and user data
3. **Leverage lifecycle hooks** for initialization and configuration
4. **Use environment variables** for flexible configuration
5. **Bind mount development directories** to `/soft` for easy access
6. **Use volume storage** for persistent application data

## Example Use Cases

- Development environments with persistent workspaces
- ROS2 robotics development containers
- GPU-accelerated computing environments
- Multi-user SSH-accessible containers
- Reproducible research environments