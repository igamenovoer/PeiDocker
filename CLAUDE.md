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

## Development Environment

PeiDocker uses Pixi for package management. Install dependencies:
```bash
# Install pixi if not already installed
curl -fsSL https://pixi.sh/install.sh | bash

# Install project dependencies 
pixi install

# Run development commands
pixi run python -m pei_docker.pei create -p ./build
```

## Common Development Commands

```bash
# Create a new project
python -m pei_docker.pei create -p ./build

# Configure the project (generates docker-compose.yml)
python -m pei_docker.pei configure -p ./build

# Remove project images and containers
python -m pei_docker.pei remove -p ./build

# Build Docker images
cd build
docker compose build stage-1
docker compose build stage-2

# Run containers
docker compose up stage-2

# Access container via SSH
ssh -i ssh_keys/admin admin@localhost -p 2222

# Documentation
pixi run docs-serve    # Serve docs locally
pixi run docs-build    # Build documentation
```

## Architecture

### Core Components

1. **CLI Entry Point** (`pei_docker/pei.py`): Click-based CLI with `create`, `configure`, and `remove` commands
2. **Configuration Processor** (`pei_docker/config_processor.py`): Core transformation engine converting user config to Docker artifacts
3. **Data Models** (`pei_docker/user_config.py`): Attrs-based type-safe configuration structures
4. **Utilities** (`pei_docker/pei_utils.py`): Environment variable substitution with Docker Compose compatibility

### Two-Stage Build System

The architecture separates concerns through a sophisticated two-stage build process:

**Stage 1: System Foundation**
- Base image setup with system packages (apt/yum)
- SSH server configuration and user management  
- System-level dependencies and tools
- Repository mirrors and proxy configuration
- Generated artifact: `stage-1.Dockerfile`

**Stage 2: Application Layer**
- Builds upon Stage 1 image as base
- Application-specific installations and configurations
- External storage mounting and symbolic link management
- User data and workspace setup
- Generated artifact: `stage-2.Dockerfile`

### Intelligent Storage Strategy

PeiDocker implements a flexible storage abstraction through symbolic links:

```
/soft/app ──────► /hard/volume/app (if external storage mounted)
              └─► /hard/image/app  (fallback to in-image storage)

/soft/data ─────► /hard/volume/data (if external storage mounted)
              └─► /hard/image/data  (fallback to in-image storage)

/soft/workspace ► /hard/volume/workspace (if external storage mounted)
                └─► /hard/image/workspace (fallback to in-image storage)
```

This allows seamless switching between development (external volumes) and production (baked-in image) without changing application paths.

### Lifecycle Hooks

Extensible hook system for custom behavior:
- `on_build`: Scripts executed during Docker image build process
- `on_first_run`: One-time initialization when container first starts
- `on_every_run`: Scripts executed on every container startup
- `on_user_ssh_login`: User-specific setup when SSH sessions begin

## Key Features to Maintain

1. **Environment Variable Substitution**: Docker Compose-style `${VAR:-default}` syntax across all configuration fields, enabling deployment-specific customization without config file modification

2. **Advanced SSH Configuration**: 
   - Multiple authentication methods: password, public key, private key, inline keys
   - Auto-discovery of system SSH keys using `~` syntax  
   - Cross-platform SSH key handling (Windows/WSL, Linux, macOS)
   - Encrypted private key support with no auto-decryption

3. **Intelligent Proxy Support**: 
   - Global proxy configuration affecting all build and runtime operations
   - Selective proxy usage (apt-only, build-only, runtime-only) 
   - Automatic proxy removal after build for production images

4. **Repository Mirror Support**: 
   - Extensive mirror support for Chinese users (Tsinghua/tuna, Aliyun, 163, USTC)
   - Automatic apt source replacement and conda/pip mirror configuration
   - Environment-specific mirror selection

5. **Hardware Acceleration**: 
   - NVIDIA GPU support with proper device forwarding
   - Hardware-accelerated OpenGL with WSLg support on Windows
   - CUDA development environment configurations

6. **Application Ecosystem Support**:
   - Conda/Miniconda environments with automatic initialization
   - Pixi package manager for modern Python development
   - ROS2 robotics development environments
   - AI/ML tools (InvokeAI, CUDA, scientific computing)

7. **Professional Development Features**:
   - Team collaboration through environment variable templating
   - CI/CD pipeline integration with configurable parameters
   - Multi-user SSH configurations with proper UID management
   - Volume and bind mount abstractions for data persistence

## Testing Approach

Manual testing with automated test scripts:
1. Use test scripts in `tests/scripts/` for different scenarios:
   - `enhanced-pixi-test.bash`: Full workflow testing with Pixi
   - `run-ssh-abspath-test.bash`: SSH key absolute path testing 
   - `test-ssh-abspath.bash`: SSH key path validation
2. Test configurations in `tests/configs/`:
   - `simple-pixi-test-passwordless.yml`: Automated testing config
   - `ssh-abspath-test.yml`: SSH absolute path testing
3. Manual workflow: create → configure → build → run → verify SSH access

### Important Testing Notes

**SSH User UID Conflicts**: When creating SSH users, avoid UIDs in the 1000-1099 range as they can conflict with system users and groups. Use UID ≥ 1100 for testing to prevent conflicts like:
- UID 1000: Often used by `ubuntu` user in Ubuntu images
- UID 1001: Can conflict with auto-generated groups like `ssh_users`
- **Recommended**: Use UID ≥ 1100 for all test configurations

**Automated Testing SSH Keys**: For automated testing without manual password/passphrase entry:
- Use the passwordless SSH keys in `tests/test-keys/`
- Test configuration: `tests/configs/simple-pixi-test-passwordless.yml`
- Keys are RSA 2048-bit without passphrase (testing only, never for production)
- Enhanced test script automatically uses passwordless configuration

**SSH Testing with sshpass**: When using sshpass for password-based SSH testing:
- Always include `-o PreferredAuthentications=password` to force password authentication
- Example: `sshpass -p 'admin123' ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password admin@localhost -p 2222`
- This prevents SSH from trying other authentication methods that might hang or timeout

**SSH Private Key Handling**: When providing encrypted private keys:
- **No automatic decryption**: Encrypted private keys are copied as-is without passphrase attempts
- **Standard filenames**: User-provided keys replace auto-generated keys using standard names (`id_rsa`, `id_ecdsa`, etc.)
- **No public key generation**: When private keys are provided, no corresponding `.pub` files are auto-generated
- **Manual public key creation**: Users must manually generate public keys if needed using `ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub`
- **Absolute path support**: Can use absolute paths (`/home/user/.ssh/id_rsa`) or `~` syntax for system key discovery

## Development Workflow

When implementing new features:
1. Create test configurations in `tests/configs/`
2. Add test scripts to `tests/scripts/` for validation
3. Update relevant sections in `context/tasks/` with implementation plans
4. Test with: create → configure → build → run workflow
5. Verify all SSH authentication methods work correctly
6. Update documentation and examples as needed

## Active Development Areas

Based on recent commits and tasks:
- CLI parameter enhancements and development tools
- SSH key handling improvements (absolute paths, ~ syntax, pubkey_text/privkey_text)
- Enhanced encrypted private key support (no auto-decryption, standard filenames)
- Environment variable substitution with Docker Compose compatibility
- Pixi integration and improved testing workflows

## Important Files

- `pei_docker/templates/config-template-full.yml`: Complete configuration reference
- `pei_docker/examples/`: Working examples and test configurations  
- `tests/configs/`: Test-specific YAML configurations
- `tests/scripts/`: Automated testing and validation scripts
- `context/tasks/`: Development tasks, implementation plans, and specifications
- `pixi.toml`: Package dependencies and development tasks

## Mirrors and Testing Strategies

- Use `cn` (`https://cn.archive.ubuntu.com/`) apt mirror for testing the user config (yaml) and docker image building
- Clean up the test docker image and container after finished
- During test, if anything inside `pei_docker\project_files\installation` is modified, you need to use `docker compose build` with `--no-cache` to rebuild the image, otherwise the changes will not take effect
- Docker image building takes time, do not interrupt the process, wait until it finishes

## Testing Notes

Make sure you know what platform you are working on.

Windows specific:
- WSL provides `sshpass` for your testing
- Use powershell to run commands