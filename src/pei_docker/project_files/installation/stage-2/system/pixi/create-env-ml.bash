#!/bin/bash
# create pixi global environment for machine learning

# prevent interactive prompts
export DEBIAN_FRONTEND=noninteractive

# source the pixi utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/pixi-utils.bash"

echo "Creating pixi global environment for machine learning..."

# list of packages to install
packages=(
    "scipy"
    "networkx"
    "trimesh"
    "pytorch"
    "torchvision"
    "click"
    "attrs"
    "omegaconf"
    "open3d"
    "pyvista"
    "pyvistaqt"
    "mkdocs-material"
    "pyqt"
    "opencv"
)

# Install packages for all users who have pixi
install_packages_for_all_users "${packages[@]}"

echo ""
echo "Machine learning package installation completed!"
echo "Note: Some packages may have failed if not available for your platform"
echo "Each user can check their packages with: pixi global list"