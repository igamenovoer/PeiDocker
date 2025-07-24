"""
PeiDocker - A Sophisticated Docker Automation Framework.

This package provides a comprehensive Docker automation framework that transforms
YAML configurations into reproducible containerized environments. The core philosophy
is "Don't keep your docker images around, keep the build files!" - enabling
reproducible Docker images without requiring deep knowledge of Dockerfiles or 
docker-compose syntax.

Core Features
-------------
- Configuration-driven Docker container creation from YAML files
- Two-stage build architecture separating system and application layers
- Flexible storage strategy with automatic volume/image switching
- Environment variable substitution with Docker Compose-style ${VAR:-default} syntax
- Cross-platform compatibility (Windows/WSL, Linux, macOS)
- Advanced SSH configuration with multiple authentication methods
- Intelligent proxy support for build and runtime environments
- Repository mirror support for optimized package installation
- Hardware acceleration support (NVIDIA GPU, OpenGL)

Command Line Usage
------------------
PeiDocker provides three main CLI commands:

1. Create a new project:
    pei-docker-cli create -p ./my-project

2. Configure project (generate docker-compose.yml):
    pei-docker-cli configure -p ./my-project

3. Remove project images and containers:
    pei-docker-cli remove -p ./my-project

Architecture
------------
PeiDocker uses a two-stage build process:

- **Stage 1**: System-level setup (base image, SSH, proxy, APT mirrors, system packages)
- **Stage 2**: Application-level configuration (custom mounts, scripts, entry points)

This separation allows for optimized caching and modular container construction.

Storage Strategy
----------------
The framework implements an intelligent storage abstraction through symbolic links:

- `/soft/app` → `/hard/volume/app` (external storage) or `/hard/image/app` (baked-in)
- `/soft/data` → `/hard/volume/data` (external storage) or `/hard/image/data` (baked-in) 
- `/soft/workspace` → `/hard/volume/workspace` (external) or `/hard/image/workspace` (baked-in)

This enables seamless switching between development (external volumes) and
production (baked-in image) deployments without changing application paths.

Package Structure
-----------------
config_processor : Main configuration transformation engine
pei : CLI entry point with Click commands
pei_utils : Utility functions for environment substitution and SSH key handling
user_config : Type-safe data structures for configuration management
gui : Terminal-based GUI application for interactive configuration
project_files : Template files and installation scripts
templates : Configuration and Docker Compose templates
examples : Sample configuration files for various use cases

Notes
-----
This package requires Docker to be installed and accessible on the system.
For GUI usage, install the package with the 'gui' extra: pip install pei-docker[gui]
"""

# Version discovery with fallback for development environments
try:
    from importlib.metadata import version
    __version__ = version("pei-docker")
except ImportError:
    # Fallback version for development or when package is not installed
    __version__ = "0.1.0"

__all__ = ["__version__"]