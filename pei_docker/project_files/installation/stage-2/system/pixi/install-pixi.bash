#!/bin/bash

# prevent interactive prompts
export DEBIAN_FRONTEND=noninteractive

# install python3 first as it's required for pixi
echo "Checking for Python3..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing Python3..."
    apt-get update
    apt-get install -y python3 python3-pip python3-venv
else
    echo "Python3 is already installed, skipping..."
fi

# install the pixi python package manager to a custom location
# following the same pattern as miniforge installation

echo "Installing Pixi Python Package Manager..."

# determine installation directory - check for volume storage first, then fall back to image storage
# this follows the same pattern as miniforge installation for consistency
if [ -d "/hard/volume/app" ]; then
    # volume storage takes precedence, note that it only exists in stage-2
    PIXI_INSTALL_DIR="/hard/volume/app/pixi"
else
    # otherwise, use the image storage
    PIXI_INSTALL_DIR="/hard/image/app/pixi"
fi

# already installed? skip
if [ -d "$PIXI_INSTALL_DIR" ] && [ -f "$PIXI_INSTALL_DIR/bin/pixi" ]; then
    echo "pixi is already installed in $PIXI_INSTALL_DIR, skipping ..."
    exit 0
fi

# create the installation directory
echo "Creating pixi installation directory: $PIXI_INSTALL_DIR"
mkdir -p "$PIXI_INSTALL_DIR"

# install pixi to custom location using PIXI_HOME environment variable
echo "Installing pixi to $PIXI_INSTALL_DIR ..."
export PIXI_HOME="$PIXI_INSTALL_DIR"
echo "PIXI_HOME is set to: $PIXI_HOME"

# download and run the installer
curl -fsSL https://pixi.sh/install.sh | bash

# verify the installation worked
if [ -f "$PIXI_INSTALL_DIR/bin/pixi" ]; then
    echo "✓ Pixi successfully installed to $PIXI_INSTALL_DIR/bin/pixi"
else
    echo "✗ Pixi installation failed or installed to wrong location"
    echo "Expected: $PIXI_INSTALL_DIR/bin/pixi"
    echo "Checking default location:"
    if [ -f "/root/.pixi/bin/pixi" ]; then
        echo "Found pixi at default location: /root/.pixi/bin/pixi"
        echo "Moving to desired location..."
        mkdir -p "$PIXI_INSTALL_DIR/bin"
        cp /root/.pixi/bin/pixi "$PIXI_INSTALL_DIR/bin/pixi"
        chmod +x "$PIXI_INSTALL_DIR/bin/pixi"
    else
        echo "Pixi not found in any location!"
        exit 1
    fi
fi

# make pixi installation accessible to all users
echo "Setting permissions for $PIXI_INSTALL_DIR ..."
chmod -R 755 "$PIXI_INSTALL_DIR"

# add pixi to PATH for all users by creating a profile script
echo "Adding pixi to system PATH ..."
cat > /etc/profile.d/pixi.sh << 'EOF'
# Add pixi to PATH - check both possible locations
if [ -d "/hard/volume/app/pixi/bin" ]; then
    export PATH="/hard/volume/app/pixi/bin:$PATH"
elif [ -d "/hard/image/app/pixi/bin" ]; then
    export PATH="/hard/image/app/pixi/bin:$PATH"
fi
EOF

# make the profile script executable
chmod +x /etc/profile.d/pixi.sh

# also add to bashrc for immediate availability in current session
# use the actual installation directory
echo "export PATH=\"$PIXI_INSTALL_DIR/bin:\$PATH\"" >> /etc/bash.bashrc

echo "Pixi installation completed successfully!"
echo "Pixi installed to: $PIXI_INSTALL_DIR"
echo "Binary location: $PIXI_INSTALL_DIR/bin/pixi"