# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PeiDocker is a Python-based Docker automation tool that simplifies Docker container creation through YAML configuration files. It generates Dockerfiles and docker-compose.yml files from user-friendly configuration, targeting users who need Docker environments without learning Dockerfile syntax.

## Common Development Commands

```bash
# Create a new project
python -m pei_docker.pei create -p ./build

# Configure the project (generates docker-compose.yml)
python -m pei_docker.pei configure -p ./build

# Build Docker images
cd build
docker compose build stage-1
docker compose build stage-2

# Run containers
docker compose up stage-2

# Access container via SSH
ssh -i ssh_keys/admin admin@localhost -p 2222
```

## Architecture

### Core Components

1. **CLI Entry Point** (`pei_docker/pei.py`): Click-based CLI handling `create` and `configure` commands
2. **Configuration Processor** (`pei_docker/config_processor.py`): Core logic for transforming user config to Docker artifacts
3. **Data Models** (`pei_docker/user_config.py`): Attrs-based configuration structures
4. **Utilities** (`pei_docker/pei_utils.py`): Environment variable substitution with Docker Compose compatibility

### Two-Stage Build System

- **Stage 1**: Base image with system packages (apt), stored in `stage-1.Dockerfile`
- **Stage 2**: Application layer with custom installations, stored in `stage-2.Dockerfile`

### Lifecycle Hooks

Custom scripts can run at different lifecycle points:
- `on_build`: During image build
- `on_first_run`: First container startup
- `on_every_start`: Every container start
- `on_user_ssh_login`: When user SSHs into container

### Storage Strategy

- `/hard/image`: In-image persistent storage
- `/hard/volume`: Docker volume mounts
- `/soft`: Bind mounts for development

## Key Features to Maintain

1. **Environment Variable Substitution**: Docker Compose-style `${VAR:-default}` syntax in all YAML fields
2. **SSH Auto-Configuration**: Automatic SSH key generation and user setup
3. **Proxy Support**: HTTP/HTTPS proxy configuration for build and runtime
4. **Mirror Support**: Chinese repository mirrors (Aliyun, Tsinghua)
5. **GPU Support**: CUDA and OpenGL configuration options
6. **ROS2 Support**: Specific configurations for robotics development

## Testing Approach

Currently no automated tests. Manual testing involves:
1. Creating test projects in `build-*` directories
2. Running through the full workflow (create → configure → build → run)
3. Verifying SSH access and lifecycle hooks execution

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

## Active Development Areas

Based on recent commits and tasks:
- SSH key handling improvements (supporting pubkey_text/privkey_text, absolute paths, ~ syntax)
- Enhanced encrypted private key support (no auto-decryption, standard filenames)
- Environment variable substitution enhancements
- Documentation improvements

## Important Files

- `pei_docker/templates/config-template-full.yml`: Reference for all configuration options
- `pei_docker/examples/`: Working examples for different use cases
- `context/tasks/`: Current development tasks and requirements