#!/bin/bash
# create pixi global environment for common packages

# prevent interactive prompts
export DEBIAN_FRONTEND=noninteractive

echo "Creating pixi global environment for common packages..."

# ensure pixi is in PATH - check all possible locations
if [ -d "/hard/volume/app/pixi/bin" ]; then
    export PATH="/hard/volume/app/pixi/bin:$PATH"
elif [ -d "/hard/image/app/pixi/bin" ]; then
    export PATH="/hard/image/app/pixi/bin:$PATH"
elif [ -d "/root/.pixi/bin" ]; then
    export PATH="/root/.pixi/bin:$PATH"
fi

# also source the updated bashrc to get any PATH updates
source /etc/bash.bashrc 2>/dev/null || true

# check if pixi is available
if ! command -v pixi &> /dev/null; then
    echo "Error: pixi command not found. Make sure pixi is installed and in PATH."
    echo "Checking possible locations:"
    echo "  /hard/volume/app/pixi/bin: $(ls -la /hard/volume/app/pixi/bin 2>/dev/null || echo 'not found')"
    echo "  /hard/image/app/pixi/bin: $(ls -la /hard/image/app/pixi/bin 2>/dev/null || echo 'not found')"
    echo "  /root/.pixi/bin: $(ls -la /root/.pixi/bin 2>/dev/null || echo 'not found')"
    echo "Current PATH: $PATH"
    exit 1
fi

# install common packages globally
# note: pixi global install creates isolated environments for each package
echo "Installing common packages globally..."

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

# install packages one at a time
for package in "${packages[@]}"; do
    echo "Installing $package..."
    if pixi global install "$package"; then
        echo "✓ Successfully installed $package"
    else
        echo "✗ Failed to install $package"
        exit 1
    fi
done

echo "All common packages installed successfully!"
echo "You can list all globally installed packages with: pixi global list"