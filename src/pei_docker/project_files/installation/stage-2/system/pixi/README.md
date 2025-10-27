# Pixi Installation and Configuration Scripts

This directory contains scripts for installing and configuring [Pixi](https://pixi.sh), a modern package manager for conda ecosystems, within PeiDocker containers.

## Overview

Pixi is a cross-platform package manager that provides fast, reliable package management using conda-forge and PyPI ecosystems. These scripts automate the installation, configuration, and package management for pixi across all container users.

### Key Features

- **Smart Installation**: Supports both shared and per-user pixi installations
- **Password-Aware**: Only configures pixi for users who can SSH login (have passwords)
- **Chinese Mirror Support**: Configure PyPI and conda-forge mirrors (TUNA/Aliyun) or revert to official
- **Future-Proof**: Sets up `/etc/skel` templates for new users
- **SSH Compatible**: Ensures pixi is available in SSH sessions via `.bashrc` modification

## Scripts

### Core Installation Scripts

#### `install-pixi.bash`
**Purpose**: Installs the pixi binary and configures PATH for all users

**Functionality**:
- Downloads and installs pixi binary for a target user (default: current user)
- Adds pixi to the target user's `.bashrc` file
- Supports custom cache directory configuration via `--cache-dir`
- Supports custom install directory via `--install-dir`
- Optional: configure PyPI mirror via `--pypi-repo` (tuna/aliyun/official)
- Optional: configure conda-forge mirror via `--conda-repo` (tuna/official)

**Parameters**:
- `--cache-dir=<absolute_path>`: Optional. Sets custom cache directory for pixi (saved permanently to `.bashrc`)
- `--install-dir=<absolute_path>`: Optional. Sets custom installation directory for pixi (default: `~/.pixi`)
- `--pypi-repo <name>`: Optional. Configure PyPI index for pixi projects. Supported values:
  - `tuna` → https://pypi.tuna.tsinghua.edu.cn/simple
  - `aliyun` → https://mirrors.aliyun.com/pypi/simple
  - `official` → revert to PyPI (remove custom index)
- `--conda-repo <name>`: Optional. Configure conda-forge mirror for pixi. Supported values:
  - `tuna` → https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
  - `official` → revert to default (remove mirror mapping)
- `--verbose`: Optional. Enable verbose output during installation for debugging purposes

#### `set-pixi-repo-tuna.bash`
Legacy helper to force TUNA mirrors for all users. Prefer using `install-pixi.bash --pypi-repo tuna --conda-repo tuna` for per-user configuration and easier revert (`official`).

#### `create-env-common.bash`
**Purpose**: Installs common development packages globally for all users

**Packages Installed**:
- `scipy` - Scientific computing library
- `click` - Command line interface toolkit
- `attrs` - Classes without boilerplate
- `omegaconf` - Configuration management
- `rich` - Rich text and formatting
- `networkx` - Network analysis
- `ipykernel` - Jupyter kernel support

#### `create-env-ml.bash`
**Purpose**: Installs machine learning and data science packages globally for all users

**Packages Installed**:
- `pytorch`, `torchvision` - Deep learning framework
- `opencv` - Computer vision library
- `open3d` - 3D data processing
- `trimesh` - 3D mesh processing
- `pyvista`, `pyvistaqt` - 3D visualization
- `pyqt` - GUI framework
- `mkdocs-material` - Documentation generator

### Utility Script

#### `pixi-utils.bash`
**Purpose**: Common utility functions used by all other scripts

**Key Functions**:
- `get_all_users()` - Enumerate users from `/etc/passwd` (UID ≥ 1000, valid shell)
- `user_has_password(username)` - Check if user has password via `/etc/shadow`
- `find_user_pixi(home)` - Smart pixi discovery (per-user first, then shared)
- `setup_pixi_path(home)` - Configure PATH for current shell
- `run_as_user(username, command)` - Execute command as specific user with pixi in PATH
- `install_packages_for_all_users(packages...)` - Install packages for all accessible users

## Usage

### Basic Installation Workflow

```bash
# 1. Install pixi binary (run as root) - installs to each user's home directory
./install-pixi.bash

# 2. Install with custom cache directory (optional)
./install-pixi.bash --cache-dir=/custom/cache/path

# 3. Install with custom installation directory (optional)
./install-pixi.bash --install-dir=/custom/install/path

# 4. Install with both custom cache and install directories
./install-pixi.bash --cache-dir=/custom/cache --install-dir=/custom/install

# 5. Install with verbose debugging output (optional)
./install-pixi.bash --verbose

# 6. Configure mirrors per-user (optional)
#    - TUNA for both PyPI and conda-forge
./install-pixi.bash --pypi-repo tuna --conda-repo tuna

#    - Aliyun for PyPI only
./install-pixi.bash --pypi-repo aliyun

#    - Revert to official repositories
./install-pixi.bash --pypi-repo official --conda-repo official

# 7. Install common packages
./create-env-common.bash

# 8. Install ML packages (optional)
./create-env-ml.bash
```

### Command Line Parameters

#### `--cache-dir=<absolute_path>`
Sets a custom cache directory for pixi. The directory must be an absolute path inside the container.
- **Not specified**: Uses pixi's default cache directory
- **Specified**: Sets `PIXI_CACHE_DIR` environment variable permanently in each user's `.bashrc`

#### `--install-dir=<absolute_path>`
Sets a custom installation directory for pixi. The directory must be an absolute path inside the container.
- **Not specified**: Uses pixi's default installation directory (`~/.pixi` for each user)
- **Specified**: Installs pixi to the specified directory and adds it to PATH in each user's `.bashrc`

#### `--verbose`
Enables verbose output during the installation process for debugging purposes.
- **Not specified**: Shows only essential installation messages
- **Specified**: Shows detailed debugging information including parameter parsing, user enumeration, installation verification, permission setting, and configuration steps

```bash
# Install with default locations
./install-pixi.bash

# Install with custom cache directory
./install-pixi.bash --cache-dir=/tmp/pixi-cache

# Install with custom installation directory
./install-pixi.bash --install-dir=/usr/local/pixi

# Install with both custom cache and install directories
./install-pixi.bash --cache-dir=/hard/volume/pixi-cache --install-dir=/hard/volume/pixi

# Install with cache in shared volume
./install-pixi.bash --cache-dir=/hard/volume/pixi-cache

# Install with verbose output for debugging
./install-pixi.bash --verbose

# Install with all parameters for debugging
./install-pixi.bash --cache-dir=/custom/cache --install-dir=/custom/install --verbose
```

### Advanced Usage

#### Manual Package Installation
```bash
# Source utilities for manual operations
source pixi-utils.bash

# Install specific package for all users
install_packages_for_all_users "numpy" "matplotlib"

# Check if user has password
if user_has_password "admin"; then
    echo "Admin can SSH login"
fi
```

## Architecture

### Script Dependencies
```
install-pixi.bash
├── pixi-utils.bash (optional, has fallback functions)
└── Creates pixi installation

set-pixi-repo-tuna.bash
├── pixi-utils.bash (required)
└── Requires pixi to be installed

create-env-common.bash
├── pixi-utils.bash (required)
└── Requires pixi to be installed

create-env-ml.bash
├── pixi-utils.bash (required)
└── Requires pixi to be installed
```

### User Password Logic

All scripts implement smart user filtering:

1. **Check `/etc/shadow`** for each user's password field
2. **Skip users with no password**:
   - Empty password field
   - Password field contains `!` (disabled)
   - Password field contains `*` (no password)
   - User not in shadow file
3. **Show warning**: `"WARNING: Skipping user username - no password set (not accessible via SSH)"`

**Rationale**: Users without passwords cannot SSH login, so configuring pixi for them is wasteful.

### Installation Characteristics

The script always installs pixi to each user's home directory with the following characteristics:

| Feature | Per-User Installation |
|---------|----------------------|
| **Location** | `~/.pixi` for each user (default) or custom via `--install-dir` |
| **Disk Usage** | Multiple installations (one per user unless using shared custom directory) |
| **User Isolation** | Each user has independent pixi installation (unless using shared `--install-dir`) |
| **Updates** | Update per user as needed |
| **Permissions** | User-owned (secure isolation) |
| **Cache Directory** | Configurable via `--cache-dir` parameter |
| **Install Directory** | Configurable via `--install-dir` parameter |
| **Future Users** | Automatic setup via `/etc/skel/.bashrc` |

### PATH Configuration Strategy

The scripts ensure pixi is available in SSH sessions by:

1. **Direct `.bashrc` modification** - Not relying on `/etc/profile.d/` (not sourced by non-login SSH)
2. **User-specific entries** - Each user gets pixi added to their `.bashrc`
3. **System-wide fallback** - `/etc/bash.bashrc` updated for shared installations
4. **Future user support** - `/etc/skel/.bashrc` configured for new users

## Troubleshooting

### Common Issues

#### "pixi: command not found"
**Cause**: pixi not in PATH for SSH sessions
**Solution**: Scripts automatically add pixi to `.bashrc`. If manual fix needed:
```bash
# For per-user installation (default behavior)
echo 'export PATH="~/.pixi/bin:$PATH"' >> ~/.bashrc
```

#### "Function not found" errors
**Cause**: `pixi-utils.bash` not properly sourced
**Solution**: Ensure scripts are run from the correct directory, or source utilities manually:
```bash
source /path/to/pixi-utils.bash
```

#### Packages fail to install
**Cause**: User doesn't have pixi or no password
**Check**: Verify user has password and pixi installation:
```bash
# Check if user has password
getent shadow username | cut -d: -f2

# Check if user has pixi (per-user installation)
ls -la /home/username/.pixi/bin/pixi

# Check if cache directory is configured (if --cache-dir was used)
grep PIXI_CACHE_DIR /home/username/.bashrc
```

### Debugging

#### Enable verbose output
```bash
# Run with built-in verbose mode for detailed debugging
./install-pixi.bash --verbose

# Run with bash debug mode for script-level debugging
bash -x ./install-pixi.bash

# Check what users are detected
source pixi-utils.bash
get_all_users
```

#### Verify installations
```bash
# Check pixi version
pixi --version

# List installed packages
pixi global list

# Check mirror configuration
cat ~/.pixi/config.toml
```

## Security Considerations

- **Password checking**: Only configures pixi for users who can SSH login
- **Permission model**: Uses 777 permissions for shared installations (required for multi-user access)
- **Mirror usage**: Tsinghua mirrors are HTTPS and trustworthy, but can be disabled by skipping `set-pixi-repo-tuna.bash`
- **User isolation**: Per-user mode provides better security isolation than shared mode

## Integration with PeiDocker

These scripts are designed to run during the stage-2 container build process:

```yaml
# In PeiDocker configuration - basic usage
custom:
  on_first_run:
    - 'stage-2/system/pixi/install-pixi.bash'
    - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'  
    - 'stage-2/system/pixi/create-env-common.bash'

# With custom cache directory
custom:
  on_first_run:
    - 'stage-2/system/pixi/install-pixi.bash --cache-dir=/hard/volume/pixi-cache'
    - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'  
    - 'stage-2/system/pixi/create-env-common.bash'

# With custom installation directory
custom:
  on_first_run:
    - 'stage-2/system/pixi/install-pixi.bash --install-dir=/hard/volume/pixi'
    - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'  
    - 'stage-2/system/pixi/create-env-common.bash'

# With both custom cache and install directories
custom:
  on_first_run:
    - 'stage-2/system/pixi/install-pixi.bash --cache-dir=/hard/volume/cache --install-dir=/hard/volume/pixi'
    - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'  
    - 'stage-2/system/pixi/create-env-common.bash'

# With verbose output for debugging
custom:
  on_first_run:
    - 'stage-2/system/pixi/install-pixi.bash --verbose'
    - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'  
    - 'stage-2/system/pixi/create-env-common.bash'

# With all parameters for comprehensive debugging
custom:
  on_first_run:
    - 'stage-2/system/pixi/install-pixi.bash --cache-dir=/hard/volume/cache --install-dir=/hard/volume/pixi --verbose'
    - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'  
    - 'stage-2/system/pixi/create-env-common.bash'
```

The scripts integrate with PeiDocker's storage strategy:
- **Installation location**: `~/.pixi` (default) or custom directory via `--install-dir` parameter  
- **Cache location**: Configurable via `--cache-dir` parameter (can use volumes like `/hard/volume/pixi-cache`)
- **Shared installations**: Use `--install-dir=/hard/volume/pixi` for shared installations across users
- **Per-user isolation**: Default behavior ensures each user has independent pixi installation
