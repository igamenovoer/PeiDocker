# Project Summary: PeiDocker (配 docker)

## Purpose

PeiDocker is a Docker automation framework designed for users who want to create reproducible Docker images without learning the intricacies of Dockerfiles and docker-compose. It transforms YAML configurations into sophisticated containerized environments, making Docker containerization accessible to developers and system administrators who need quick, reproducible setups. The project emphasizes "keeping build files, not images" to ensure reproducibility and maintainability.

## Concepts

**Two-Stage Building Process**: PeiDocker uses a two-stage image building approach:
- **Stage-1**: Base image for installing system packages via `apt install`
- **Stage-2**: Final image based on Stage-1, for installing custom applications and packages

**Configuration-Driven**: Everything is controlled through YAML configuration files (`user_config.yml`) with support for environment variable substitution using Docker Compose syntax (`${VAR:-default}`).

**Flexible Storage Architecture**: The `/soft/` directory structure provides intelligent linking:
- `/soft/app`, `/soft/data`, `/soft/workspace` can automatically link to either in-image storage (`/hard/image/`) or external storage (`/hard/volume/`) based on mount configuration

**SSH Integration**: Built-in SSH server support for easy container access and debugging.

**Custom Scripts**: Support for custom shell scripts during build time, startup, and first-run scenarios with parameter passing capabilities.

**Proxy and Mirror Support**: Built-in support for package repository mirrors and proxy configurations for restricted network environments.

## Usage

**Prerequisites**: Docker, docker-compose, Python 3.11+, and Python packages: `click`, `omegaconf`, `attrs`, `cattrs`

**Basic Workflow**:
1. **Create a project**: `pei-docker-cli create -p ./my-project`
2. **Configure**: Edit `user_config.yml` to specify base image, packages, SSH settings, etc.
3. **Generate compose files**: `pei-docker-cli configure -p ./my-project`
4. **Build images**: 
   - `docker compose build stage-1 --progress=plain`
   - `docker compose build stage-2 --progress=plain`
5. **Run container**: `docker compose up stage-2`
6. **Access via SSH**: `ssh me@127.0.0.1 -p 2222` (if SSH is configured)

**Environment Variable Support**: Configuration files support Docker Compose-style variable substitution for deployment flexibility across different environments.

## Inner Workings

PeiDocker is structured as a Python-based CLI tool with a modular architecture:

**Core Components**:
- **CLI Interface** (`pei.py`): Main command-line interface with create, configure, and remove commands
- **Configuration Processor** (`config_processor.py`): Handles YAML configuration parsing and validation
- **Template System**: Generates Docker Compose files and Dockerfiles from templates
- **Project Management**: Creates and manages project directory structures with examples and templates

**Project Directory Structure**:
```
project-directory/
├── compose-template.yml     # Docker Compose template (auto-generated)
├── docker-compose.yml       # Generated Docker Compose file
├── stage-1.Dockerfile       # Auto-generated Dockerfile for stage-1
├── stage-2.Dockerfile       # Auto-generated Dockerfile for stage-2
├── user_config.yml          # User configuration file (main interface)
├── installation/            # Scripts and files copied to container
│   ├── stage-1/
│   │   ├── custom/          # User custom scripts for stage-1
│   │   ├── system/          # System configuration files
│   │   └── tmp/             # Temporary files and packages
│   └── stage-2/
│       ├── custom/          # User custom scripts for stage-2
│       ├── system/          # System configuration files
│       └── tmp/             # Temporary files and packages
├── examples/                # Example configuration files
└── contrib/                 # Community contributions
```

**Main Repository Structure**:
```
PeiDocker/
├── README.md                # Project documentation
├── pyproject.toml           # Python project configuration
├── mkdocs.yml              # Documentation configuration
├── src/pei_docker/         # Main source code
│   ├── pei.py              # CLI entry point
│   ├── config_processor.py # Configuration handling
│   ├── user_config.py      # Configuration schema
│   ├── templates/          # File templates
│   ├── project_files/      # Project template files
│   └── webgui/             # Web GUI components
├── docs/                   # Documentation files
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── build_*/                # Example project instances
├── context/                # Project context and documentation
└── tmp/                    # Temporary development files
```

**Technology Stack**: Python 3.11+, Click (CLI framework), OmegaConf (configuration management), Attrs/Cattrs (data classes), Docker & Docker Compose, Shell scripting, YAML configuration, Jinja2 templating.

The framework emphasizes simplicity and reproducibility, automatically handling complex Docker configurations while allowing extensive customization through simple YAML files and shell scripts.

## References

**Documentation**:
- [Main Documentation](docs/index.md) - Complete user guide and setup instructions
- [CLI Reference](docs/cli_reference.md) - Detailed command-line interface documentation
- [Basic Examples](docs/examples/basic.md) - Getting started with basic configurations
- [Advanced Examples](docs/examples/advanced.md) - Complex configuration scenarios
- [Project README](README.md) - Quick start guide and overview

**Design and Architecture**:
- [Design Overview](context/design/README.md) - High-level design documentation
- [Web GUI Architecture](context/design/arch-webgui.md) - Web interface design specifications
- [Terminology](context/design/terminology.md) - Project-specific terms and concepts

**Development Plans**:
- [Development Plans](context/plans/README.md) - Project roadmap and feature plans
- [Web GUI Design](context/plans/web-gui/webgui-general-design.md) - Web interface development plans
- [Textual GUI Plans](context/plans/textual-gui/gui-simple-mode.md) - Terminal-based GUI specifications

**Project Context**:
- [Instructions](context/instructions/) - Development and maintenance instructions
- [Tasks](context/tasks/) - Current development tasks and TODOs
- [Summaries](context/summaries/) - Project documentation summaries
