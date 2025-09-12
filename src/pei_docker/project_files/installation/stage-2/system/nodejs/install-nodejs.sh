#!/bin/bash

# =================================================================
# Install Node.js LTS and pnpm (requires NVM to be installed first)
# =================================================================
# Usage: ./install-nodejs.sh [OPTIONS]
#
# Options:
#   --npm-cn-mirror    Use Chinese npm mirror (registry.npmmirror.com)
#                      Default: Use official npm registry
#
# Description:
#   This script installs the latest LTS version of Node.js using NVM
#   and also installs pnpm package manager. Optionally configures
#   npm to use the Chinese mirror for faster downloads in China.
#
# Prerequisites:
#   - NVM must be installed (run install-nvm.sh first)
#   - Internet connection required
#
# Examples:
#   ./install-nodejs.sh                 # Install with official npm registry
#   ./install-nodejs.sh --npm-cn-mirror # Install with Chinese npm mirror
# =================================================================

# install latest lts nodejs, assuming nvm is already installed
export DEBIAN_FRONTEND=noninteractive

# Parse command line arguments
USE_CN_MIRROR=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --npm-cn-mirror)
            USE_CN_MIRROR=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--npm-cn-mirror]"
            echo "  --npm-cn-mirror    Use Chinese npm mirror (registry.npmmirror.com)"
            exit 1
            ;;
    esac
done

bash -c " . $HOME/.nvm/nvm.sh ; nvm install --lts ; "

echo "Installing pnpm ..."
wget -qO- https://get.pnpm.io/install.sh | sh -

# set npm registry based on option
if [ "$USE_CN_MIRROR" = true ]; then
    echo "Setting npm registry to Chinese mirror (taobao) ..."
    bash -c " . $HOME/.nvm/nvm.sh ; npm config set registry https://registry.npmmirror.com/ ; "
else
    echo "Using default npm registry ..."
fi

echo "Done installing nodejs and pnpm."