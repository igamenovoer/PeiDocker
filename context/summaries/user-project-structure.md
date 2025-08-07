# PeiDocker User Project Structure

This document describes the typical directory structure created when a user runs the PeiDocker project creation commands (`pei-docker-cli create` or via GUI). This structure is based on the `build-example` directory and represents what users will see in their project workspace.

## Project Root Structure

```
my-project/                          # User's project directory
├── user_config.yml                  # Main configuration file (YAML format)
├── stage-1.Dockerfile               # Generated Dockerfile for stage-1 build
├── stage-2.Dockerfile               # Generated Dockerfile for stage-2 build  
├── compose-template.yml             # Docker Compose template for container orchestration
├── examples/                        # Example configuration files and templates
└── installation/                    # Core installation scripts and resources
    ├── stage-1/                     # Stage-1 specific installation files
    └── stage-2/                     # Stage-2 specific installation files
```

## Root Level Files

### user_config.yml
- **Purpose**: Primary configuration file controlling all aspects of the Docker container setup
- **Content**: YAML configuration with stage-1 and stage-2 settings including:
  - Base image specification (e.g., `ubuntu:24.04`)
  - SSH configuration (users, ports, keys)
  - Environment variables and proxy settings
  - Custom scripts and lifecycle hooks
  - Volume mounts and device configurations
- **User Action**: Users modify this file to customize their container environment

### stage-1.Dockerfile & stage-2.Dockerfile  
- **Purpose**: Generated Docker build files created from user_config.yml
- **Content**: Docker instructions for building the two-stage container architecture
- **User Action**: Auto-generated - users typically don't modify these directly

### compose-template.yml
- **Purpose**: Docker Compose configuration template for container orchestration
- **Content**: Service definitions, port mappings, volume mounts, environment variables
- **User Action**: Users can modify for advanced Docker Compose configurations

## Examples Directory

```
examples/                            # Configuration examples and templates
├── environment-variables.yml        # Environment variable configuration examples
├── gpu-with-host-mount.yml         # GPU support with host directory mounting
├── gpu-with-opengl-win32.yml       # GPU + OpenGL configuration for Windows
├── invoke-ai-by-pip.yml            # InvokeAI installation via pip
├── minimal-ubuntu-ssh.yml          # Basic Ubuntu setup with SSH access
├── mount-arbitrary-vol.yml         # Custom volume mounting examples
├── mount-external-docker-vol.yml   # External Docker volume mounting
├── pixi-basic-cpu.yml              # Pixi package manager setup (CPU)
├── pixi-ml-gpu.yml                 # Pixi setup for machine learning with GPU
├── pixi-with-volumes.yml           # Pixi with volume configurations
├── python-with-opengl.yml          # Python development with OpenGL support
├── ssh-keys-inline.yml             # SSH key configuration examples
├── with-everything.yml             # Comprehensive configuration example
├── with-proxy-across-stages.yml    # Proxy configuration across both stages
├── with-proxy-in-build.yml         # Proxy only during build phase
├── with-proxy-in-run.yml           # Proxy only during runtime
└── with-proxy-manually.yml         # Manual proxy configuration
```

**Purpose**: Pre-configured examples demonstrating various use cases and configuration patterns. Users can copy and modify these as starting points for their own configurations.

## Installation Directory Structure

```
installation/                       # Core installation scripts and resources
├── stage-1/                        # Stage-1: System foundation setup
│   ├── custom/                     # User-provided custom scripts
│   ├── generated/                  # Auto-generated script orchestrators
│   ├── internals/                  # PeiDocker core system scripts
│   ├── system/                     # System-level installation utilities
│   └── tmp/                        # Temporary files and build artifacts
└── stage-2/                        # Stage-2: Application and user setup
    ├── custom/                     # User-provided custom scripts
    ├── generated/                  # Auto-generated script orchestrators  
    ├── internals/                  # PeiDocker core system scripts
    ├── system/                     # System-level installation utilities
    ├── tmp/                        # Temporary files and build artifacts
    └── utilities/                  # Additional utility scripts
```

## Stage-1 Directory Details

### custom/
```
custom/                              # User-provided custom scripts
├── install-dev-tools.sh            # Example: Development tools installation
├── my-build-1.sh                   # Example: Custom build script #1
├── my-build-2.sh                   # Example: Custom build script #2  
├── my-on-every-run-1.sh            # Example: Script run on every container start
├── my-on-every-run-2.sh            # Example: Script run on every container start
├── my-on-first-run-1.sh            # Example: Script run on first container start
├── my-on-first-run-2.sh            # Example: Script run on first container start
├── my-on-user-login-1.sh           # Example: Script run when user logs in via SSH
├── my-on-user-login-2.sh           # Example: Script run when user logs in via SSH
└── readme.md                       # Instructions for custom scripts
```
**Purpose**: Users place their custom installation and configuration scripts here. These are executed at various lifecycle points according to the naming convention.

### generated/
```
generated/                          # Auto-generated script orchestrators
├── _custom-on-build.sh             # Orchestrates all custom build scripts
├── _custom-on-every-run.sh         # Orchestrates all custom every-run scripts
├── _custom-on-first-run.sh         # Orchestrates all custom first-run scripts
├── _custom-on-user-login.sh        # Orchestrates all custom user-login scripts
└── readme.md                       # Information about generated files  
```
**Purpose**: Auto-generated by PeiDocker to orchestrate custom scripts. Users should not modify these directly.

### internals/
```
internals/                          # PeiDocker core system scripts
├── _setup-cuda.sh                  # CUDA/GPU support initialization
├── cleanup.sh                      # Build cleanup operations
├── custom-on-build.sh              # Custom script execution during build
├── custom-on-every-run.sh          # Custom script execution on every run
├── custom-on-first-run.sh          # Custom script execution on first run  
├── custom-on-user-login.sh         # Custom script execution on user login
├── entrypoint.sh                   # Container entrypoint script
├── install-essentials.sh           # Essential system packages installation
├── on-entry.sh                     # Entry point lifecycle hook
├── on-every-run.sh                 # Every run lifecycle hook
├── on-first-run.sh                 # First run lifecycle hook
├── setup-env.sh                    # Environment variables setup
├── setup-profile-d.sh              # Shell profile configuration
├── setup-ssh.sh                    # SSH server and key configuration
└── setup-users.sh                  # User account creation and configuration
```
**Purpose**: Core PeiDocker system scripts that handle fundamental container setup. Users typically don't modify these.

### system/
```
system/                             # System-level installation utilities
├── apt/                            # APT package manager configurations
│   ├── disable-external-cache.sh   # Disable external APT cache
│   ├── disable-shadow-cache.sh     # Disable shadow APT cache
│   ├── enable-external-cache.sh    # Enable external APT cache
│   └── enable-shadow-cache.sh      # Enable shadow APT cache
├── clang/                          # Clang compiler installation
│   ├── install-clang.sh            # Install Clang compiler
│   └── setup-latest-clang-as-default.sh # Set latest Clang as default
├── firefox/                        # Firefox browser setup
│   └── setup-firefox-repo.sh       # Setup Firefox repository
├── invoke-ai/                      # InvokeAI installation utilities
│   └── install-invoke-ai-deps.sh   # Install InvokeAI dependencies
├── proxy/                          # Proxy configuration utilities
│   ├── disable-pei-proxy.sh        # Disable PeiDocker proxy settings
│   └── enable-pei-proxy.sh         # Enable PeiDocker proxy settings
├── ros2/                           # ROS2 robotics framework setup
│   ├── init-rosdep.sh              # Initialize ROS dependency manager
│   ├── install-ros2.sh             # Install ROS2 framework
│   ├── setup-locale.sh             # Setup locale for ROS2
│   └── setup-ros2-repo.sh          # Setup ROS2 repositories
├── ssh/                            # SSH configuration and keys
│   └── keys/                       # SSH key examples and templates
│       ├── example-pubkey.pub      # Example public key
│       ├── mykey.rsa               # Example private key
│       ├── mykey.rsa.pub           # Example public key
│       └── pass_is_123456          # Example password file
└── vision-dev/                     # Computer vision development tools
    ├── README.md                   # Vision development documentation
    └── install-vision-dev.bash     # Install vision development packages
```
**Purpose**: System-level utilities and configuration scripts for various software packages and services. Users can reference these for custom installations.

### tmp/
```
tmp/                                # Temporary files and build artifacts
└── readme.md                      # Information about temporary directory usage
```
**Purpose**: Workspace for temporary files during build and runtime operations.

## Stage-2 Directory Details

### custom/
```
custom/                             # User-provided custom scripts  
├── install-gui-tools.sh            # Example: GUI tools installation
├── install-my-conda.sh             # Example: Conda environment setup
├── my-build-1.sh                   # Example: Custom build script #1
├── my-build-2.sh                   # Example: Custom build script #2
├── my-on-every-run-1.sh            # Example: Script run on every container start
├── my-on-every-run-2.sh            # Example: Script run on every container start
├── my-on-first-run-1.sh            # Example: Script run on first container start
├── my-on-first-run-2.sh            # Example: Script run on first container start
├── my-on-user-login-1.sh           # Example: Script run when user logs in via SSH
├── my-on-user-login-2.sh           # Example: Script run when user logs in via SSH
└── test-params-echo.bash           # Example: Script parameter testing
```
**Purpose**: Stage-2 specific custom scripts focusing on application-level setup and user environment configuration.

### generated/
```
generated/                          # Auto-generated script orchestrators
├── _custom-on-build.sh             # Orchestrates all custom build scripts
├── _custom-on-every-run.sh         # Orchestrates all custom every-run scripts
├── _custom-on-first-run.sh         # Orchestrates all custom first-run scripts
├── _custom-on-user-login.sh        # Orchestrates all custom user-login scripts
└── readme.md                       # Information about generated files
```
**Purpose**: Auto-generated orchestration scripts for Stage-2 custom scripts.

### internals/
```
internals/                          # PeiDocker core system scripts
├── _setup-cuda.sh                  # CUDA/GPU support initialization
├── cleanup.sh                      # Build cleanup operations
├── create-dirs.sh                  # Directory structure creation
├── create-links.sh                 # Symbolic link management for volumes
├── custom-on-build.sh              # Custom script execution during build
├── custom-on-every-run.sh          # Custom script execution on every run
├── custom-on-first-run.sh          # Custom script execution on first run
├── custom-on-user-login.sh         # Custom script execution on user login
├── entrypoint.sh                   # Container entrypoint script
├── install-essentials.sh           # Essential system packages installation
├── on-entry.sh                     # Entry point lifecycle hook
├── on-every-run.sh                 # Every run lifecycle hook
├── on-first-run.sh                 # First run lifecycle hook
├── readme.md                       # Documentation for internal scripts
├── setup-env.sh                    # Environment variables setup
├── setup-profile-d.sh              # Shell profile configuration
└── setup-users.sh                  # User account configuration
```
**Purpose**: Core Stage-2 system scripts handling application-level setup and volume management.

### system/
```
system/                             # System-level installation utilities
├── conda/                          # Conda package manager setup
│   ├── activate-conda-on-login.sh  # Auto-activate conda on login
│   ├── auto-install-miniconda.sh   # Automatic Miniconda installation
│   ├── auto-install-miniforge.sh   # Automatic Miniforge installation
│   ├── conda-tsinghua.txt          # Tsinghua University conda mirror
│   ├── configure-conda-repo.sh     # Configure conda repositories
│   ├── configure-pip-repo.sh       # Configure pip repositories
│   └── install-miniconda.sh        # Manual Miniconda installation
├── invoke-ai/                      # InvokeAI setup and configuration
│   ├── from-source/                # Source installation files
│   ├── install-invoke-ai-conda.sh  # Install InvokeAI via conda
│   ├── invoke-ai-entrypoint.sh     # InvokeAI startup script
│   ├── readme.md                   # InvokeAI setup documentation
│   ├── run-invoke-ai-multi-user.sh # Multi-user InvokeAI setup
│   ├── setup-invoke-ai-envs.sh     # Environment setup for InvokeAI
│   ├── start-invokeai.sh           # Start InvokeAI service
│   └── stop-all-invoke-ai-sessions.sh # Stop all InvokeAI sessions
├── magnum/                         # Magnum graphics library
│   └── install-magnum-gl.sh        # Install Magnum OpenGL support
├── nodejs/                         # Node.js development environment
│   ├── install-angular.sh          # Install Angular framework
│   ├── install-nodejs-for-everyone.sh # System-wide Node.js installation
│   ├── install-nodejs.sh           # Standard Node.js installation
│   └── install-nvm.sh              # Install Node Version Manager
├── opencv/                         # OpenCV computer vision library
│   ├── install-opencv-cpu.sh       # CPU-only OpenCV installation
│   └── install-opencv-cuda.sh      # CUDA-enabled OpenCV installation
├── opengl/                         # OpenGL graphics support
│   ├── 10_nvidia.json              # NVIDIA OpenGL configuration
│   ├── docker-compose-win32.yml    # Windows OpenGL Docker Compose
│   └── setup-opengl-win32.sh       # Windows OpenGL setup
├── pixi/                           # Pixi package manager
│   ├── README.md                   # Pixi documentation
│   ├── create-env-common.bash      # Create common Pixi environment
│   ├── create-env-ml.bash          # Create ML-focused Pixi environment
│   ├── install-pixi.bash           # Install Pixi package manager
│   ├── pixi-utils.bash             # Pixi utility functions
│   └── set-pixi-repo-tuna.bash     # Configure Tsinghua mirror for Pixi
├── readme.md                       # System utilities documentation
└── set-locale.sh                   # System locale configuration
```
**Purpose**: Advanced system utilities for application-level software installation and configuration.

### utilities/
```
utilities/                          # Additional utility scripts
├── install-cv-essentials.sh        # Computer vision essential packages
└── install-python-packages.sh      # Common Python package installation
```
**Purpose**: Common utility scripts for frequently used package installations.

### tmp/
```
tmp/                                # Temporary files and build artifacts
└── readme.md                      # Information about temporary directory usage
```
**Purpose**: Stage-2 specific temporary file workspace.

## Key Design Principles

### Two-Stage Architecture
- **Stage-1**: System foundation setup (OS packages, SSH, users, proxy, system-level configurations)
- **Stage-2**: Application and user environment setup (development tools, frameworks, user data)

### Intelligent Volume Management  
- **Symbolic Link Strategy**: `/soft/` paths automatically link to either external volumes (`/hard/volume/`) or in-image storage (`/hard/image/`) based on availability
- **Flexible Storage**: Seamless switching between development (external volumes) and production (baked-in image) without path changes

### Lifecycle Hook System
- **on_build**: Scripts executed during Docker image build
- **on_first_run**: One-time initialization when container starts for the first time
- **on_every_run**: Scripts executed on every container startup  
- **on_user_login**: Scripts executed when users log in via SSH

### Environment Variable Substitution
- **Docker Compose Style**: `${VAR:-default}` syntax throughout all configuration files
- **Deployment Flexibility**: Change configurations without modifying files

## User Workflow

1. **Project Creation**: Run `pei-docker-cli create -p ./my-project` or use GUI
2. **Configuration**: Modify `user_config.yml` to customize container setup  
3. **Custom Scripts**: Add custom installation/configuration scripts to `custom/` directories
4. **Build Process**: Run `pei-docker-cli configure` to generate Dockerfiles and Compose files
5. **Container Operations**: Use standard Docker/Docker Compose commands to build and run containers

## Important Notes

- **Generated Files**: Files in `generated/` and `internals/` are auto-managed - users should not modify directly
- **Relative Paths**: All paths in configuration files are relative to the `installation/` directory
- **Cross-Platform**: Structure works consistently across Windows (WSL), Linux, and macOS
- **Extensible**: Users can add their own directories and scripts while following the established patterns

This structure provides a comprehensive, organized approach to Docker container configuration while maintaining flexibility for user customization and supporting complex multi-stage build processes.