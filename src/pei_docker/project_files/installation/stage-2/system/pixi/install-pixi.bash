#!/bin/bash

#############################################################################
# Pixi Python Package Manager Installation Script
#############################################################################
#
# DESCRIPTION:
#   Install Pixi (Python package manager) for a single user only.
#   By default installs for the current user. Use --user <username>
#   to target another user (requires root). The script configures
#   the target user's shell environment and optional cache dir.
#
# USAGE:
#   ./install-pixi.bash [OPTIONS]
#
# OPTIONS:
#   --user <username>     Install for a specific user (defaults to current user).
#                         Only root may install for another user.
#
#   --cache-dir=PATH      Set custom Pixi cache directory for the target user
#                         Example: --cache-dir=/shared/pixi-cache
#
#   --install-dir=PATH    Set custom Pixi installation directory for the target user
#                         (overrides default ~/.pixi)
#                         Example: --install-dir=/opt/pixi
#
#   --pypi-repo <name>    Configure default PyPI index for pixi (project defaults)
#                         Supported: 'tuna' (https://pypi.tuna.tsinghua.edu.cn/simple),
#                                    'aliyun' (https://mirrors.aliyun.com/pypi/simple),
#                                    'official' (revert to PyPI defaults)
#                         This writes [pypi-config] to $PIXI_HOME/config.toml so new
#                         pixi projects default to the selected mirror.
#
#   --conda-repo <name>   Configure conda channel mirror(s) for pixi
#                         Supported: 'tuna' (Tsinghua TUNA mirrors for conda-forge),
#                                    'official' (remove mirror and use default)
#                         This writes [mirrors] to $PIXI_HOME/config.toml so conda channel
#                         traffic goes to the selected mirror.
#
#   --installer-url <url> Override the URL for the pixi installation script.
#                         Values: 'official' (default), 'cn' (currently same as official),
#                         or a custom URL (e.g., 'https://example.com/install.sh').
#
#   --verbose             Enable verbose output for debugging
#                         Shows detailed information about each step
#
# EXAMPLES:
#   # Basic installation (installs to current user's ~/.pixi)
#   ./install-pixi.bash
#
#   # Install with custom cache directory
#   ./install-pixi.bash --cache-dir=/shared/pixi-cache
#
#   # Install to custom directory with verbose output
#   ./install-pixi.bash --install-dir=/opt/pixi --verbose
#
#   # Install for another user (requires root)
#   ./install-pixi.bash --user alice --install-dir=/home/alice/.pixi --cache-dir=/shared/pixi-cache
#
# BEHAVIOR:
#   - Installs Pixi using the official installer from https://pixi.sh/install.sh
#   - Updates the target user's ~/.bashrc to add Pixi to PATH
#   - Skips installation if Pixi is already present for the target user
#   - Sets appropriate file permissions and ownership
#
# REQUIREMENTS:
#   - Root privileges required only when using --user to target another user
#   - Internet connection (downloads Pixi installer)
#   - curl command available
#   - Bash shell environment
#
# OUTPUT:
#   - Progress messages showing installation status for the target user
#   - Success/failure indicators (✓/✗) for the installation
#   - Summary of installation directories and configuration
#
# FILES MODIFIED:
#   - ~/.bashrc for the target user (adds PATH and cache config)
#   - Creates ~/.pixi/ directory structure for the target user
#
# DEPENDENCIES:
#   - May source pixi-utils.bash if available in the same directory
#   - Falls back to embedded function definitions if utilities not found
#
# AUTHOR: PeiDocker Project
# VERSION: 1.0
#############################################################################

# prevent interactive prompts
export DEBIAN_FRONTEND=noninteractive

# Parse command line parameters
PIXI_CACHE_DIR=""
PIXI_INSTALL_DIR=""
PIXI_PYPI_REPO_NAME=""
PIXI_CONDA_REPO_NAME=""
INSTALLER_URL="official"
TARGET_USER=""
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --user)
            TARGET_USER="$2"; shift 2 ;;
        --cache-dir=*)
            PIXI_CACHE_DIR="${1#*=}"; shift 1 ;;
        --install-dir=*)
            PIXI_INSTALL_DIR="${1#*=}"; shift 1 ;;
        --pypi-repo)
            PIXI_PYPI_REPO_NAME="$2"; shift 2 ;;
        --conda-repo)
            PIXI_CONDA_REPO_NAME="$2"; shift 2 ;;
        --installer-url)
            INSTALLER_URL="$2"; shift 2 ;;
        --verbose)
            VERBOSE=true; shift 1 ;;
        *)
            # Unknown option
            shift 1 ;;
    esac
done

# Resolve Installer URL
case "$INSTALLER_URL" in
    official)
        INSTALLER_URL="https://pixi.sh/install.sh"
        ;;
    cn)
        INSTALLER_URL="https://pixi.sh/install.sh" # Currently no known reliable CN mirror for pixi install script itself, defaulting to official but could be updated later.
        echo "Warning: No dedicated CN mirror for pixi installer script known, using official."
        ;;
    http://*|https://*)
        # Use as is
        ;;
    *)
        echo "Error: Unknown --installer-url value: $INSTALLER_URL. Use 'official', 'cn', or a valid URL."
        exit 1
        ;;
esac

# Verbose logging function
verbose_echo() {
    if [ "$VERBOSE" = true ]; then
        echo "[VERBOSE] $*"
    fi
}

echo "Installing Pixi Python Package Manager..."

if [ -n "$PIXI_CACHE_DIR" ]; then
    echo "Cache directory will be set to: $PIXI_CACHE_DIR"
fi

if [ -n "$PIXI_INSTALL_DIR" ]; then
    echo "Custom install directory will be used: $PIXI_INSTALL_DIR"
fi

echo "Installer URL: $INSTALLER_URL"

if [ "$VERBOSE" = true ]; then
    echo "Verbose output enabled for debugging"
fi

if [ -n "$PIXI_PYPI_REPO_NAME" ]; then
    echo "PyPI mirror preference: $PIXI_PYPI_REPO_NAME"
fi
if [ -n "$PIXI_CONDA_REPO_NAME" ]; then
    echo "Conda channel mirror preference: $PIXI_CONDA_REPO_NAME"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
verbose_echo "Script directory: $SCRIPT_DIR"
verbose_echo "Parameters parsed - Cache dir: '$PIXI_CACHE_DIR', Install dir: '$PIXI_INSTALL_DIR', Verbose: $VERBOSE, Target user: '${TARGET_USER}'"

# Source common utilities if available (might not exist on first run)
UTILS_SOURCED=false

verbose_echo "Looking for pixi-utils.bash at: $SCRIPT_DIR/pixi-utils.bash"

if [ -f "$SCRIPT_DIR/pixi-utils.bash" ]; then
    verbose_echo "Sourcing pixi-utils.bash"
    source "$SCRIPT_DIR/pixi-utils.bash"
    UTILS_SOURCED=true
    verbose_echo "Successfully sourced pixi-utils.bash"
else
    verbose_echo "pixi-utils.bash not found, will use local function definitions"
fi

# Define local functions if utilities weren't sourced
if [ "$UTILS_SOURCED" = false ]; then
    # Function to add pixi to a user's bashrc
    add_pixi_to_bashrc() {
        local user_name="$1"
        local user_home="$2"
        local pixi_path="$3"
        local cache_dir="$4"
        local bashrc_file="$user_home/.bashrc"
        
        # Create .bashrc if it doesn't exist
        if [ ! -f "$bashrc_file" ]; then
            echo "Creating $bashrc_file for user $user_name"
            touch "$bashrc_file"
            primary_group=$(id -gn "$user_name" 2>/dev/null || echo "$user_name")
            chown "$user_name:$primary_group" "$bashrc_file" || true
        fi
        
        # Check if this exact pixi path is already in bashrc
        if ! grep -qF "export PATH=\"$pixi_path:\$PATH\"" "$bashrc_file"; then
            echo "export PATH=\"$pixi_path:\$PATH\"" >> "$bashrc_file"
            echo "Added pixi to $bashrc_file"
        else
            echo "Pixi path already in $bashrc_file"
        fi
        
        # Add cache directory setting if provided
        if [ -n "$cache_dir" ]; then
            if ! grep -qF "export PIXI_CACHE_DIR=\"$cache_dir\"" "$bashrc_file"; then
                echo "export PIXI_CACHE_DIR=\"$cache_dir\"" >> "$bashrc_file"
                echo "Added pixi cache directory setting to $bashrc_file"
            else
                echo "Pixi cache directory already configured in $bashrc_file"
            fi
        fi
    }
fi

# Determine current and target users
CURRENT_USER="$(whoami)"
if [[ -z "${TARGET_USER}" ]]; then
    TARGET_USER="${CURRENT_USER}"
fi

# Enforce root for cross-user installs and validate user exists
if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
    if [[ "${CURRENT_USER}" != "root" ]]; then
        echo "Error: only root can install for another user (requested --user '${TARGET_USER}')" >&2
        exit 1
    fi
    if ! id -u "${TARGET_USER}" >/dev/null 2>&1; then
        echo "Error: target user '${TARGET_USER}' does not exist" >&2
        exit 1
    fi
fi

# Resolve target user's home directory
if [[ "${TARGET_USER}" == "root" ]]; then
    TARGET_HOME="/root"
else
    if command -v getent >/dev/null 2>&1; then
        TARGET_HOME="$(getent passwd "${TARGET_USER}" | cut -d: -f6)"
    else
        TARGET_HOME="$(eval echo "~${TARGET_USER}")"
    fi
fi

echo "Installing pixi for user: ${TARGET_USER} (invoked by ${CURRENT_USER})"

# Determine the install directory for the target user
if [ -n "$PIXI_INSTALL_DIR" ]; then
    USER_PIXI_DIR="$PIXI_INSTALL_DIR"
    verbose_echo "Using custom install directory for ${TARGET_USER}: $USER_PIXI_DIR"
else
    USER_PIXI_DIR="$TARGET_HOME/.pixi"
    verbose_echo "Using default install directory for ${TARGET_USER}: $USER_PIXI_DIR"
fi
    
    # Skip if already installed
verbose_echo "Checking if pixi already exists at: $USER_PIXI_DIR/bin/pixi"
if [ -d "$USER_PIXI_DIR" ] && [ -f "$USER_PIXI_DIR/bin/pixi" ]; then
    echo "Pixi already installed for ${TARGET_USER} at $USER_PIXI_DIR, updating bashrc..."
    verbose_echo "Pixi binary found, updating bashrc configuration only"
    add_pixi_to_bashrc "${TARGET_USER}" "$TARGET_HOME" "$USER_PIXI_DIR/bin" "$PIXI_CACHE_DIR"
else
    verbose_echo "Pixi not found, proceeding with fresh installation"

    # Ensure install directory exists when running cross-user
    if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
        mkdir -p "$USER_PIXI_DIR" || true
        primary_group=$(id -gn "$TARGET_USER" 2>/dev/null || echo "$TARGET_USER")
        chown -R "${TARGET_USER}:${primary_group}" "$USER_PIXI_DIR" || true
    fi

    # Install pixi directly to the target directory using PIXI_HOME
    echo "Installing pixi to $USER_PIXI_DIR for user ${TARGET_USER}..."
    verbose_echo "Setting PIXI_HOME=$USER_PIXI_DIR for installation"

    INSTALL_CMD="export PIXI_HOME='$USER_PIXI_DIR'; curl -fsSL ${INSTALLER_URL} | bash"
    if [ "$VERBOSE" != true ]; then
        INSTALL_CMD="$INSTALL_CMD >/dev/null 2>&1"
    fi

    if [[ "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
        verbose_echo "Installing as current user ${CURRENT_USER}"
        bash -lc "$INSTALL_CMD"
    else
        verbose_echo "Installing as user ${TARGET_USER}"
        if command -v runuser >/dev/null 2>&1; then
            runuser -u "${TARGET_USER}" -- sh -lc "$INSTALL_CMD"
        else
            su -l "${TARGET_USER}" -c "$INSTALL_CMD"
        fi
    fi

    # Verify the installation worked
    verbose_echo "Verifying installation at: $USER_PIXI_DIR/bin/pixi"
    if [ -f "$USER_PIXI_DIR/bin/pixi" ]; then
        echo "✓ Pixi successfully installed for ${TARGET_USER} at $USER_PIXI_DIR"
        verbose_echo "Installation verification successful"
        # Ensure proper ownership on cross-user installs
        if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
            primary_group=$(id -gn "$TARGET_USER" 2>/dev/null || echo "$TARGET_USER")
            chown -R "${TARGET_USER}:${primary_group}" "$USER_PIXI_DIR" || true
        fi
        chmod -R 755 "$USER_PIXI_DIR" || true

        # Add to user's bashrc
        add_pixi_to_bashrc "${TARGET_USER}" "$TARGET_HOME" "$USER_PIXI_DIR/bin" "$PIXI_CACHE_DIR"

        # Optionally configure PyPI index mirror for pixi
        if [ -n "$PIXI_PYPI_REPO_NAME" ]; then
            # Determine index URL based on the selected mirror
            case "$PIXI_PYPI_REPO_NAME" in
                tuna|Tuna|TUNA)
                    PIXI_PYPI_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple" ;;
                aliyun|Aliyun|ALIYUN)
                    PIXI_PYPI_INDEX_URL="https://mirrors.aliyun.com/pypi/simple" ;;
                official|Official|OFFICIAL)
                    PIXI_PYPI_INDEX_URL="" ;;
                *)
                    echo "Warning: unknown --pypi-repo '$PIXI_PYPI_REPO_NAME'. Supported: tuna, aliyun, official. Skipping PyPI config." ;;
            esac

            if [ -n "${PIXI_PYPI_INDEX_URL:-}" ]; then
                PIXI_CFG_DIR="$USER_PIXI_DIR"
                PIXI_CFG_FILE="$PIXI_CFG_DIR/config.toml"
                mkdir -p "$PIXI_CFG_DIR" || true

                # If config exists, update [pypi-config]. Otherwise, create it.
                if [ -f "$PIXI_CFG_FILE" ]; then
                    # Ensure [pypi-config] section exists
                    if ! grep -qE '^\s*\[pypi-config\]\s*$' "$PIXI_CFG_FILE"; then
                        printf '\n[pypi-config]\n' >> "$PIXI_CFG_FILE"
                    fi
                    # Remove any existing index-url lines under [pypi-config] and append new
                    awk -v url="$PIXI_PYPI_INDEX_URL" '
                        BEGIN{in_pypi=0}
                        /^\s*\[/{
                            if(in_pypi==1){print "index-url = \"" url "\""}
                            in_pypi=0
                        }
                        /^\s*\[pypi-config\]\s*$/{in_pypi=1}
                        {
                            if(in_pypi==1){
                                if($0 ~ /^\s*index-url\s*=.*/){next}
                            }
                            print $0
                        }
                        END{ if(in_pypi==1){print "index-url = \"" url "\""} }
                    ' "$PIXI_CFG_FILE" > "$PIXI_CFG_FILE.tmp" && mv "$PIXI_CFG_FILE.tmp" "$PIXI_CFG_FILE"
                else
                    cat > "$PIXI_CFG_FILE" <<EOF
[pypi-config]
index-url = "$PIXI_PYPI_INDEX_URL"
# extra-index-urls = []
# keyring-provider = "subprocess"  # or "disabled"
EOF
                fi
                if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
                    primary_group=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")
                    chown -R "${TARGET_USER}:${primary_group}" "$PIXI_CFG_DIR" || true
                fi
                echo "Pixi PyPI index configured: $PIXI_PYPI_INDEX_URL"
            else
                # official: remove any index-url lines under [pypi-config]
                PIXI_CFG_DIR="$USER_PIXI_DIR"
                PIXI_CFG_FILE="$PIXI_CFG_DIR/config.toml"
                if [ -f "$PIXI_CFG_FILE" ]; then
                    awk '
                        BEGIN{in_pypi=0}
                        /^\s*\[pypi-config\]\s*$/{in_pypi=1}
                        /^\s*\[/{ if(in_pypi==1){in_pypi=0} }
                        {
                            if(in_pypi==1 && $0 ~ /^\s*index-url\s*=.*/){next}
                            print $0
                        }
                    ' "$PIXI_CFG_FILE" > "$PIXI_CFG_FILE.tmp" && mv "$PIXI_CFG_FILE.tmp" "$PIXI_CFG_FILE"
                    if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
                        primary_group=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")
                        chown -R "${TARGET_USER}:${primary_group}" "$PIXI_CFG_DIR" || true
                    fi
                    echo "Pixi PyPI index reverted to official PyPI"
                fi
            fi
        fi

        # Optionally configure conda channel mirror(s) for pixi
        if [ -n "$PIXI_CONDA_REPO_NAME" ]; then
            # Determine conda mirror URLs based on the selected mirror
            # For pixi, we configure [mirrors] mapping: original channel URL -> mirror URL
            case "$PIXI_CONDA_REPO_NAME" in
                tuna|Tuna|TUNA)
                    ORIG_CF_URL="https://conda.anaconda.org/conda-forge"
                    MIRROR_CF_URL="https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge"
                    ;;
                official|Official|OFFICIAL)
                    ORIG_CF_URL="https://conda.anaconda.org/conda-forge"
                    MIRROR_CF_URL="" ;;
                *)
                    echo "Warning: unknown --conda-repo '$PIXI_CONDA_REPO_NAME'. Supported: tuna, official. Skipping conda mirrors." ;;
            esac

            if [ -n "${ORIG_CF_URL:-}" ]; then
                PIXI_CFG_DIR="$USER_PIXI_DIR"
                PIXI_CFG_FILE="$PIXI_CFG_DIR/config.toml"
                mkdir -p "$PIXI_CFG_DIR" || true

                # Remove any existing mapping for conda-forge under [mirrors]
                if [ -f "$PIXI_CFG_FILE" ]; then
                    awk -v key="$ORIG_CF_URL" '
                        BEGIN{in_m=0}
                        /^\s*\[/{in_m=0}
                        /^\s*\[mirrors\]\s*$/{in_m=1}
                        {
                            if(in_m==1){
                                # skip lines defining the key
                                if($0 ~ "^\"" key "\"[[:space:]]*="){next}
                            }
                            print $0
                        }
                    ' "$PIXI_CFG_FILE" > "$PIXI_CFG_FILE.tmp" && mv "$PIXI_CFG_FILE.tmp" "$PIXI_CFG_FILE"
                fi

                if [ -n "${MIRROR_CF_URL:-}" ]; then
                    # Append mapping (re-open [mirrors] table to ensure correct context)
                    {
                        echo ""
                        echo "[mirrors]"
                        echo "\"$ORIG_CF_URL\" = [\"$MIRROR_CF_URL\"]"
                    } >> "$PIXI_CFG_FILE"
                    echo "Pixi conda-forge mirror configured: $MIRROR_CF_URL"
                else
                    # official: do not append mapping; only removal was done
                    echo "Pixi conda-forge mirror removed; using official channel"
                fi

                if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
                    primary_group=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")
                    chown -R "${TARGET_USER}:${primary_group}" "$PIXI_CFG_DIR" || true
                fi
            fi
        fi
    else
        echo "✗ Pixi installation failed for ${TARGET_USER}"
        echo "Expected: $USER_PIXI_DIR/bin/pixi"
        if [ "$VERBOSE" = true ] && [ -d "$USER_PIXI_DIR" ]; then
            ls -la "$USER_PIXI_DIR" || true
        fi
        exit 1
    fi
fi

echo "Pixi installation completed successfully!"
if [ -n "$PIXI_INSTALL_DIR" ]; then
    echo "Pixi installed to custom directory: $PIXI_INSTALL_DIR"
else
    echo "Pixi installed to: $USER_PIXI_DIR"
fi
if [ -n "$PIXI_CACHE_DIR" ]; then
    echo "Pixi cache directory configured: $PIXI_CACHE_DIR"
fi
