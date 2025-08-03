# Gemini Code Assistant Context

This document provides a comprehensive overview of the PeiDocker project, designed to help the Gemini code assistant understand the project's structure, purpose, and development conventions.

## Project Overview

**PeiDocker** is a Python-based command-line tool that simplifies and automates the creation of Docker images. It allows users to define complex, multi-stage Docker builds using a simple YAML configuration file, abstracting away the need to write complex Dockerfiles. The project also includes a web-based GUI for a more interactive configuration experience.

### Key Features

- **YAML-based Configuration**: Define Docker images, build stages, SSH access, networking, and storage in a human-readable YAML file.
- **Multi-Stage Builds**: Supports a two-stage build process, separating system-level dependencies (stage-1) from application-level setup (stage-2).
- **Custom Scripting**: Execute custom shell scripts at various points in the container lifecycle (e.g., on build, on first run, on user login).
- **Web GUI**: A NiceGUI-based web interface for creating and managing project configurations.
- **CLI Tool**: A command-line interface for creating, configuring, and managing PeiDocker projects.
- **Documentation**: The project uses MkDocs to generate comprehensive documentation from Markdown files.

### Core Technologies

- **Python**: The primary programming language.
- **Click**: For creating the command-line interface.
- **OmegaConf**: For managing YAML configurations.
- **cattrs**: For structuring and validating configuration data.
- **NiceGUI**: For the web-based graphical user interface.
- **MkDocs**: For generating project documentation.
- **Pixi**: For managing Python dependencies and development environments.

### Project Structure

The project is organized into the following key directories:

- `src/pei_docker/`: Contains the main source code for the PeiDocker application.
  - `pei.py`: The main entry point for the command-line interface.
  - `config_processor.py`: The core logic for processing the user's YAML configuration and generating the `docker-compose.yml` file.
  - `user_config.py`: Defines the data structures for the user's configuration.
  - `webgui/`: The source code for the NiceGUI-based web interface.
- `peidocker_gui.py`: A launcher script for the web GUI.
- `docs/`: Contains the Markdown files for the project's documentation.
- `scripts/`: Contains build and utility scripts.
- `tests/`: Contains the project's test suite.
- `pyproject.toml`: Defines the project's metadata, dependencies, and build settings.
- `mkdocs.yml`: The configuration file for the MkDocs documentation generator.

## Building and Running

The project uses **Pixi** to manage dependencies and development tasks. The following commands are defined in the `pyproject.toml` file:

- **Install dependencies**:
  ```bash
  pixi install
  ```

- **Run the command-line interface**:
  ```bash
  pixi run pei-docker-cli -- --help
  ```

- **Run the web GUI**:
  ```bash
  pixi run pei-docker-gui
  ```

- **Run tests**:
  ```bash
  pixi run test
  ```

- **Run linter**:
  ```bash
  pixi run lint
  ```

- **Run type checker**:
  ```bash
  pixi run type-check
  ```

- **Serve the documentation locally**:
  ```bash
  pixi run docs-serve
  ```

## Development Conventions

- **Coding Style**: The project uses **Black** for code formatting and **Ruff** for linting.
- **Type Hinting**: The project uses type hints, and **MyPy** is used for static type checking.
- **Testing**: The project uses **pytest** for testing.
- **Documentation**: The project uses **MkDocs** with the **Material** theme to generate documentation from Markdown files. The documentation is deployed to GitHub Pages via a GitHub Actions workflow defined in `.github/workflows/deploy-docs.yml`.
- **Configuration**: The project uses **OmegaConf** to manage YAML configurations, allowing for flexible and hierarchical configuration management.
- **CLI**: The command-line interface is built using **Click**, with commands for creating, configuring, and removing PeiDocker projects.
