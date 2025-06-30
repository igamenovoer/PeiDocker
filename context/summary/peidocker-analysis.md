# PeiDocker Tool Analysis Summary

**Generated on:** June 30, 2025  
**Location:** `d:\code\PeiDocker\context\summary\peidocker-analysis.md`

## Overview

**PeiDocker** (配 docker) is a Python-based automation tool that simplifies Docker image building and container management without requiring deep knowledge of Dockerfiles and docker-compose. The name "配 docker" (pèi docker) means "to configure/set up docker" in Chinese.

## Core Purpose

- **Simplifies Docker workflow**: Eliminates the need to write complex Dockerfiles and docker-compose files manually
- **Reproducible builds**: Ensures Docker images can be rebuilt consistently from configuration files
- **Two-stage building**: Uses a structured approach with `stage-1` (base system setup) and `stage-2` (application setup)

## Key Features

### 1. SSH Support
- Automatically sets up SSH access to containers
- Configurable users with passwords and/or SSH keys
- Customizable SSH ports (host and container)

### 2. Proxy Support
- Handles network proxy configuration for package installation
- Can be enabled globally or for specific operations
- Supports HTTP/HTTPS proxies

### 3. Storage Management
Flexible options for installing applications in different locations:
- **In-image directories**: `/hard/image`
- **Docker volumes**: `/hard/volume`
- **Host bind mounts**: `/soft`

### 4. Custom Script Execution
Run custom shell scripts at different lifecycle points:
- **During image building**: `on_build`
- **On container first run**: `on_first_run`
- **On every container start**: `on_every_run`
- **When users SSH into container**: `on_user_login`

### 5. Repository Mirror Support
- Use alternative package repositories (like Aliyun mirrors)
- Configurable APT repository sources
- Proxy support for package installation

### 6. GPU Support
- Configuration options for GPU-enabled containers
- OpenGL support for Windows containers

## Architecture

### Core Components

1. **`pei_docker/pei.py`**: Main CLI interface with two commands:
   - `create`: Sets up new project with templates
   - `configure`: Processes config and generates docker files

2. **`pei_docker/config_processor.py`**: Core logic for processing user configuration and generating Docker artifacts

3. **`pei_docker/user_config.py`**: Configuration data structures and validation

4. **Templates**: Base templates for configuration and docker-compose files

5. **Examples**: Pre-configured examples for common use cases

### Workflow

1. **Create Project**: 
   ```bash
   python -m pei_docker.pei create -p ./build
   ```
   - Sets up project directory with templates and examples

2. **Configure**: 
   - Edit `user_config.yml` with your requirements
   - Define base images, SSH users, proxy settings, custom scripts, etc.

3. **Generate**: 
   ```bash
   python -m pei_docker.pei configure -p ./build
   ```
   - Processes config and generates `docker-compose.yml` and Dockerfiles

4. **Build & Run**: 
   ```bash
   docker compose build stage-1
   docker compose build stage-2
   docker compose up stage-2
   ```

## Configuration Structure

The tool uses YAML configuration files with the following main sections:

### Stage 1 (Base Image)
- Base image selection (e.g., `ubuntu:24.04`)
- SSH configuration
- Proxy settings
- APT repository configuration
- System-level customizations

### Stage 2 (Application Layer)
- Built on top of Stage 1
- Application installations
- Data mounting and storage
- Runtime configurations

## Example Use Cases

Based on the examples in the workspace:

1. **Minimal Ubuntu with SSH**: Basic Ubuntu container with SSH access
2. **GPU-enabled containers**: For ML/AI workloads
3. **Development environments**: With specific toolchains and dependencies
4. **Proxy-enabled builds**: For corporate environments
5. **Multi-storage setups**: Combining volumes, bind mounts, and in-image storage

## Target Users

- Developers who need reproducible Docker environments but don't want to learn Dockerfile syntax
- People who frequently rebuild Docker images with slight variations
- Users who need SSH-enabled containers for development work
- Teams that want to standardize their Docker build processes
- Organizations with specific proxy/mirror requirements

## Dependencies

- Python 3.x with packages: `click`, `omegaconf`, `attrs`, `cattrs`
- Docker and docker-compose
- Currently supports Ubuntu-based images

## Documentation

The project includes MkDocs-based documentation with:
- Introduction and setup guides
- Configuration examples
- Advanced usage patterns

## Project Structure Insights

- **Modular design**: Clear separation of concerns between CLI, config processing, and templates
- **Template-based**: Uses Jinja-like templating for generating Docker artifacts
- **Example-driven**: Rich set of examples for different scenarios
- **Documentation-focused**: Comprehensive docs with MkDocs
