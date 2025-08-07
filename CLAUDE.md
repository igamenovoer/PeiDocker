# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PeiDocker is a sophisticated Docker automation framework that transforms YAML configurations into reproducible containerized environments. The core philosophy is: **"Don't keep your docker images around, keep the build files!"** - enabling reproducible Docker images without requiring deep knowledge of Dockerfiles or docker-compose.

### Design Philosophy
- **Configuration-driven**: Everything is controlled through `user_config.yml` with extensive customization options
- **Two-stage architecture**: Separates system-level setup (stage-1) from application-level configuration (stage-2)
- **Flexible storage strategy**: Automatic switching between external volumes and in-image storage
- **Environment variable substitution**: Docker Compose-style `${VAR:-default}` syntax throughout all configurations
- **Cross-platform compatibility**: Works consistently across Windows (WSL), Linux, and macOS

## Development Best Practices
- Temporary test scripts and outputs should NOT be stored in workspace root, save them in `<workspace_root>/tmp` dir, if not exist then create it, better with specialized subdir named after purpose

## Development Environment

PeiDocker uses Pixi integrated with pyproject.toml for package management. Install dependencies:
```bash
# Install pixi if not already installed
curl -fsSL https://pixi.sh/install.sh | bash

# Install project dependencies (this will also install the package in editable mode)
pixi install

# Run development commands using pixi tasks
pixi run pei-docker-cli create -p ./build

# Or use installed CLI directly
pei-docker-cli create -p ./build
```

## Memory Management
- When using promptx mcp to save long term memory, DO NOT do it automatically, memory should be updated by explicit command

[... rest of the existing content remains unchanged ...]