#!/bin/bash
# create pixi global environment for common packages

# prevent interactive prompts
export DEBIAN_FRONTEND=noninteractive

# source the pixi utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/pixi-utils.bash"

echo "Creating pixi global environment for common packages..."

# list of packages to install
packages=(
    "scipy"
    "click"
    "attrs"
    "omegaconf"
    "rich"
    "networkx"
    "ipykernel"
)

# Install packages for all users who have pixi
install_packages_for_all_users "${packages[@]}"

echo ""
echo "Common package installation completed!"
echo "Each user can check their packages with: pixi global list"