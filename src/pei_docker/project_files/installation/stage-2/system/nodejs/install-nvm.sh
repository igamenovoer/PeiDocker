#!/bin/bash

# =================================================================
# Install Node Version Manager (NVM)
# =================================================================
# Usage: ./install-nvm.sh [OPTIONS]
#
# Options:
#   --install-dir <dir>    Custom directory to install NVM
#                          Default: $HOME/.nvm
#   --with-cn-mirror       Configure npm registry to Chinese mirror
#   --version <ver>        NVM git tag/version to install (e.g., v0.39.7 or 0.39.7)
#                          Default: latest from source/cached copy
#
# Description:
#   This script installs NVM (Node Version Manager) which allows you
#   to install and manage multiple versions of Node.js. It either
#   clones NVM from GitHub or copies from a cached directory if available.
#   The script also configures your ~/.bashrc to load NVM automatically.
#   Optionally sets npm registry to the CN mirror.
#
# Prerequisites:
#   - Git must be installed
#   - Internet connection required (if no cached version available)
#   - $PEI_STAGE_DIR_2 environment variable should be set for cached install
#
# Post-installation:
#   - Restart your shell or run: source ~/.bashrc
#   - Use install-nodejs.sh to install Node.js versions
#
# Examples:
#   ./install-nvm.sh                           # Install to $HOME/.nvm
#   ./install-nvm.sh --install-dir /opt/nvm    # Install to /opt/nvm
# =================================================================

# Installs NVM (and optionally CN npm mirror).
# To install Node.js versions, use install-nodejs.sh
export DEBIAN_FRONTEND=noninteractive

# Parse command line arguments
NVM_INSTALL_DIR="$HOME/.nvm"
USE_CN_MIRROR=false
NVM_VERSION=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-dir)
            NVM_INSTALL_DIR="$2"
            shift 2
            ;;
        --with-cn-mirror)
            USE_CN_MIRROR=true
            shift 1
            ;;
        --version)
            NVM_VERSION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--install-dir <directory>] [--with-cn-mirror] [--version <ver>]"
            echo "  --install-dir <dir>  Custom directory to install NVM (default: \$HOME/.nvm)"
            echo "  --with-cn-mirror     Configure npm registry to Chinese mirror"
            echo "  --version <ver>      NVM git tag/version to install (e.g., 0.39.7)"
            exit 1
            ;;
    esac
done

# Set NVM_DIR environment variable
export NVM_DIR="$NVM_INSTALL_DIR"

stage_dir=$PEI_STAGE_DIR_2
tmp_dir=$stage_dir/tmp

# do we have tmp/nvm directory? if not, git clone nvm
if [ ! -d "$tmp_dir/nvm" ]; then
    echo "cloning nvm to $NVM_DIR ..."
    git clone https://github.com/nvm-sh/nvm.git "$NVM_DIR"
else
    # copy tmp/nvm to $NVM_DIR
    echo "copying $tmp_dir/nvm to $NVM_DIR ..."
    cp -r $tmp_dir/nvm "$NVM_DIR"
fi

# If a specific NVM version was requested, attempt to check out that version
if [ -n "$NVM_VERSION" ]; then
    # Normalize version to start with 'v'
    if [[ "$NVM_VERSION" != v* ]]; then
        NVM_TAG="v$NVM_VERSION"
    else
        NVM_TAG="$NVM_VERSION"
    fi
    if [ -d "$NVM_DIR/.git" ]; then
        echo "Switching NVM to tag $NVM_TAG ..."
        # Ensure tags are available, but tolerate offline or shallow clones
        git -C "$NVM_DIR" fetch --tags >/dev/null 2>&1 || true
        if git -C "$NVM_DIR" rev-parse -q --verify "$NVM_TAG^{tag}" >/dev/null 2>&1 || \
           git -C "$NVM_DIR" rev-parse -q --verify "$NVM_TAG" >/dev/null 2>&1; then
            git -C "$NVM_DIR" -c advice.detachedHead=false checkout -q "$NVM_TAG" || true
        else
            echo "Warning: requested NVM version '$NVM_TAG' not found; continuing with current copy." >&2
        fi
    else
        echo "Warning: NVM directory is not a git repository; cannot switch to version '$NVM_TAG'." >&2
    fi
fi

# Create NVM_SCRIPT with the actual installation directory
NVM_SCRIPT="export NVM_DIR=\"$NVM_DIR\"
[ -s \"\$NVM_DIR/nvm.sh\" ] && \\. \"\$NVM_DIR/nvm.sh\"  # This loads nvm
[ -s \"\$NVM_DIR/bash_completion\" ] && \\. \"\$NVM_DIR/bash_completion\"  # This loads nvm bash_completion"

# add NVM_SCRIPT to ~/.bashrc
echo "" >> ~/.bashrc
echo "$NVM_SCRIPT" >> ~/.bashrc
echo "" >> ~/.bashrc

echo "NVM installed to: $NVM_DIR"
echo "Please restart your shell or run: source ~/.bashrc"

# Optional: configure npm registry to CN mirror
if [ "$USE_CN_MIRROR" = true ]; then
    echo "Configuring npm registry to https://registry.npmmirror.com/ ..."
    NPMRC_PATH="$HOME/.npmrc"
    mkdir -p "$(dirname "$NPMRC_PATH")"
    if [ -f "$NPMRC_PATH" ] && grep -q '^registry=' "$NPMRC_PATH"; then
        # Replace existing registry line
        sed -i 's#^registry=.*#registry=https://registry.npmmirror.com/#' "$NPMRC_PATH"
    else
        # Append registry config
        echo "registry=https://registry.npmmirror.com/" >> "$NPMRC_PATH"
    fi
    # If npm is already available, also set via npm config (best-effort)
    if command -v npm >/dev/null 2>&1; then
        npm config set registry https://registry.npmmirror.com/ || true
    fi
else
    echo "Using default npm registry (no --with-cn-mirror provided)"
fi
