# PeiDocker GUI

A terminal-based GUI for PeiDocker using the Textual library.

## Overview

The PeiDocker GUI provides an intuitive interface for creating and configuring Docker container projects. It offers two modes:

- **Simple Mode**: A guided wizard that walks users through the most common configuration options
- **Advanced Mode**: Full control over all PeiDocker features (not yet implemented)

## Installation

The GUI is automatically installed when you install PeiDocker:

```bash
pixi install
```

## Usage

### Command Line Interface

Start the GUI with:

```bash
pei-docker-gui
```

Or specify a project directory:

```bash
pei-docker-gui --project-dir ./my-project
```

### GUI Flow

1. **Startup Screen**: Shows system status and Docker availability
2. **Project Directory**: Select or specify where to create your project
3. **Mode Selection**: Choose between Simple and Advanced modes
4. **Simple Mode Wizard**: Step-by-step configuration (currently implemented)
   - Project Information (name, base image)
   - SSH Configuration (users, ports, authentication)
   - Configuration Summary and save

## Architecture

```
src/pei_docker/gui/
├── app.py                    # Main application entry point
├── screens/
│   ├── startup.py            # System check and welcome screen
│   ├── mode_selection.py     # Mode selection screen
│   └── simple/
│       ├── wizard.py         # Wizard controller
│       ├── project_info.py   # Project settings
│       ├── ssh_config.py     # SSH configuration
│       └── summary.py        # Final review and save
├── models/
│   └── config.py            # Configuration data models
└── utils/
    ├── docker_utils.py      # Docker integration utilities
    └── file_utils.py        # File system utilities
```

## Features

### Currently Implemented

- ✅ Startup screen with system checks
- ✅ Project directory selection and validation
- ✅ Mode selection (Simple/Advanced)
- ✅ Simple mode wizard with:
  - Project information configuration
  - SSH configuration with multiple authentication methods
  - Configuration preview and saving
- ✅ Docker availability detection
- ✅ Input validation and error handling
- ✅ Cross-platform support (Windows, Linux, macOS)

### Simple Mode Features

- **Project Setup**: Configure project name and base Docker image
- **SSH Access**: Set up SSH users, ports, and authentication methods
- **Validation**: Real-time input validation and helpful error messages
- **Preview**: Review configuration before saving
- **Auto-save**: Generate `user_config.yml` in the project directory

### Planned Features

- 🔄 Advanced mode with full feature access
- 🔄 Additional wizard steps for:
  - Proxy configuration
  - APT mirror selection
  - Port mappings
  - Environment variables
  - GPU/device configuration
  - Volume mounts
  - Custom scripts
- 🔄 Configuration templates
- 🔄 Direct Docker build integration

## Technical Details

### Dependencies

- **Textual**: Terminal UI framework
- **Rich**: Text formatting and styling
- **Click**: Command-line interface
- **PyYAML**: Configuration file handling
- **Attrs**: Data classes

### Key Components

- **PeiDockerApp**: Main application class managing screen navigation
- **ProjectConfig**: Type-safe configuration data model
- **SimpleWizardScreen**: Wizard controller for step-by-step configuration
- **Individual Step Screens**: Focused screens for each configuration aspect

### Configuration Model

The GUI uses a structured configuration model that maps to the PeiDocker YAML format:

```python
ProjectConfig
├── project_name: str
├── project_dir: str
├── stage_1: Stage1Config
│   ├── base_image: str
│   ├── ssh: SSHConfig
│   └── ...
└── stage_2: Stage2Config
```

## Development

### Testing

Run the test suite:

```bash
python test_gui.py
```

This tests:
- Module imports
- Basic functionality
- Docker integration
- Input validation

### Extending the GUI

To add new wizard steps:

1. Create a new screen class in `screens/simple/`
2. Add it to the wizard steps in `wizard.py`
3. Implement the `compose()` method for the UI
4. Add an `is_valid()` method for validation
5. Update the configuration model if needed

## Troubleshooting

### Common Issues

1. **Docker not found**: The GUI will show a warning but still function. Some features require Docker.

2. **Permission errors**: Ensure you have write permissions to the project directory.

3. **Unicode encoding errors**: On Windows, use PowerShell or ensure your terminal supports UTF-8.

### Debug Mode

For debugging, you can run the GUI with Python directly:

```bash
python -m pei_docker.gui.app --project-dir ./debug-project
```

## Contributing

When contributing to the GUI:

1. Follow the existing architecture patterns
2. Add appropriate input validation
3. Include proper error handling
4. Test on multiple platforms
5. Update this documentation