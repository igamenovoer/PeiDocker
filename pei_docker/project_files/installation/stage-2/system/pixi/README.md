# Pixi Installation and Configuration Scripts

This directory contains scripts for installing and configuring [Pixi](https://pixi.sh), a modern package manager for conda ecosystems, within PeiDocker containers.

## Overview

Pixi is a cross-platform package manager that provides fast, reliable package management using conda-forge and PyPI ecosystems. These scripts automate the installation, configuration, and package management for pixi across all container users.

### Key Features

- **Smart Installation**: Supports both shared and per-user pixi installations
- **Password-Aware**: Only configures pixi for users who can SSH login (have passwords)
- **Chinese Mirror Support**: Configures Tsinghua mirrors for faster downloads in China
- **Future-Proof**: Sets up `/etc/skel` templates for new users
- **SSH Compatible**: Ensures pixi is available in SSH sessions via `.bashrc` modification

## Scripts

### Core Installation Scripts

#### `install-pixi.bash`
**Purpose**: Installs the pixi binary and configures PATH for all users

**Functionality**:
- Downloads and installs pixi binary
- Supports two installation modes via `PIXI_INSTALL_AT_HOME` environment variable
- Adds pixi to each user's `.bashrc` file
- Creates `/etc/skel/.bashrc` entry for future users
- Skips users without passwords (not SSH accessible)

**Installation Modes**:
- **Shared mode** (default): Installs to `/hard/volume/app/pixi` or `/hard/image/app/pixi`
- **Per-user mode** (`PIXI_INSTALL_AT_HOME=1`): Installs to each user's `~/.pixi` directory

#### `set-pixi-repo-tuna.bash`
**Purpose**: Configures pixi to use Tsinghua University mirrors for faster downloads

**Functionality**:
- Creates `~/.pixi/config.toml` for each user with Tsinghua mirror configuration
- Configures conda-forge and PyPI mirrors
- Creates `/etc/skel/.pixi/config.toml` for future users
- Skips users without passwords

**Mirror Configuration**:
- Conda channels: `mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/`
- PyPI packages: `pypi.tuna.tsinghua.edu.cn/simple`

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
# 1. Install pixi binary (run as root)
./install-pixi.bash

# 2. Configure mirrors (optional, for China users)
./set-pixi-repo-tuna.bash

# 3. Install common packages
./create-env-common.bash

# 4. Install ML packages (optional)
./create-env-ml.bash
```

### Environment Variables

#### `PIXI_INSTALL_AT_HOME`
Controls pixi installation location:
- **Not set** (default): Shared installation in `/hard/volume/app/pixi` or `/hard/image/app/pixi`
- **Set to `1`**: Per-user installation in each user's `~/.pixi` directory

```bash
# Install pixi per-user
export PIXI_INSTALL_AT_HOME=1
./install-pixi.bash

# Install pixi shared (default)
unset PIXI_INSTALL_AT_HOME
./install-pixi.bash
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

### Installation Modes Comparison

| Feature | Shared Mode | Per-User Mode |
|---------|-------------|---------------|
| **Location** | `/hard/volume/app/pixi` | `~/.pixi` for each user |
| **Disk Usage** | Single installation | Multiple installations |
| **User Isolation** | All users share | Each user independent |
| **Updates** | Update once for all | Update per user |
| **Permissions** | 777 (world writable) | User-owned |
| **Future Users** | Automatic access | Need individual setup |

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
# For shared installation
echo 'export PATH="/hard/volume/app/pixi/bin:$PATH"' >> ~/.bashrc

# For per-user installation  
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

# Check if user has pixi
ls -la /home/username/.pixi/bin/pixi  # per-user mode
ls -la /hard/volume/app/pixi/bin/pixi  # shared mode
```

### Debugging

#### Enable verbose output
```bash
# Run with bash debug mode
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
# In PeiDocker configuration
custom:
  on_first_run:
    - 'stage-2/system/pixi/install-pixi.bash'
    - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'  
    - 'stage-2/system/pixi/create-env-common.bash'
```

The scripts integrate with PeiDocker's storage strategy:
- **Volume storage**: `/hard/volume/app/pixi` (preferred for shared mode)
- **Image storage**: `/hard/image/app/pixi` (fallback for shared mode)
- **User homes**: `~/.pixi` (per-user mode)