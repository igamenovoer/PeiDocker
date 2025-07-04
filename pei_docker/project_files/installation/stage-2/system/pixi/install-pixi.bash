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

echo "Installing Pixi Python Package Manager..."

# Source common utilities if available (might not exist on first run)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILS_SOURCED=false

if [ -f "$SCRIPT_DIR/pixi-utils.bash" ]; then
    source "$SCRIPT_DIR/pixi-utils.bash"
    UTILS_SOURCED=true
fi

# Define local functions if utilities weren't sourced
if [ "$UTILS_SOURCED" = false ]; then
    # Function to add pixi to a user's bashrc
    add_pixi_to_bashrc() {
        local user_name="$1"
        local user_home="$2"
        local pixi_path="$3"
        local bashrc_file="$user_home/.bashrc"
        
        # Create .bashrc if it doesn't exist
        if [ ! -f "$bashrc_file" ]; then
            echo "Creating $bashrc_file for user $user_name"
            touch "$bashrc_file"
            chown "$user_name:$user_name" "$bashrc_file"
        fi
        
        # Check if this exact pixi path is already in bashrc
        if ! grep -qF "export PATH=\"$pixi_path:\$PATH\"" "$bashrc_file"; then
            echo "export PATH=\"$pixi_path:\$PATH\"" >> "$bashrc_file"
            echo "Added pixi to $bashrc_file"
        else
            echo "Pixi path already in $bashrc_file"
        fi
    }
    
    # Function to get all users with proper home directories
    get_all_users() {
        # Get users from passwd file, excluding system users (UID < 1000) and nologin users
        while IFS=: read -r username password uid gid gecos home shell; do
            if [ "$uid" -ge 1000 ] && [ -d "$home" ] && [[ "$shell" != */nologin ]] && [[ "$shell" != */false ]]; then
                echo "$username:$home:$uid:$gid"
            fi
        done < /etc/passwd
    }
    
    # Function to check if any user has a password set
    user_has_password() {
        local username="$1"
        
        # Check if user has a password by examining /etc/shadow
        local user_shadow_entry=$(getent shadow "$username" 2>/dev/null)
        
        # If getent fails, user doesn't exist in shadow file
        if [ -z "$user_shadow_entry" ]; then
            return 1  # No shadow entry, assume no password
        fi
        
        local password_field=$(echo "$user_shadow_entry" | cut -d: -f2)
        
        # If password field is empty, !, or *, user has no password
        if [ -z "$password_field" ] || [ "$password_field" = "!" ] || [ "$password_field" = "*" ]; then
            return 1  # No password
        else
            return 0  # Has password
        fi
    }
    
    # Function to check if root user has a password set (wrapper around user_has_password)
    root_has_password() {
        user_has_password "root"
    }
fi

# Check if we should install pixi in each user's home directory
if [ "$PIXI_INSTALL_AT_HOME" = "1" ]; then
    echo "PIXI_INSTALL_AT_HOME is set to 1, installing pixi to each user's home directory..."
    
    # First, download pixi to a temporary location
    TEMP_PIXI_DIR="/tmp/pixi_install_temp"
    mkdir -p "$TEMP_PIXI_DIR"
    
    echo "Downloading pixi to temporary location: $TEMP_PIXI_DIR"
    export PIXI_HOME="$TEMP_PIXI_DIR"
    curl -fsSL https://pixi.sh/install.sh | bash
    
    if [ ! -f "$TEMP_PIXI_DIR/bin/pixi" ]; then
        # Check default location
        if [ -f "/root/.pixi/bin/pixi" ]; then
            echo "Found pixi at default location, copying to temp dir..."
            mkdir -p "$TEMP_PIXI_DIR/bin"
            cp -r /root/.pixi/* "$TEMP_PIXI_DIR/"
        else
            echo "Failed to download pixi!"
            exit 1
        fi
    fi
    
    # Install pixi for each regular user
    while IFS=: read -r username home uid gid; do
        if ! user_has_password "$username"; then
            echo "WARNING: Skipping user $username - no password set (not accessible via SSH)"
            continue
        fi
        
        echo "Installing pixi for user: $username (UID: $uid, HOME: $home)"
        
        USER_PIXI_DIR="$home/.pixi"
        
        # Skip if already installed
        if [ -d "$USER_PIXI_DIR" ] && [ -f "$USER_PIXI_DIR/bin/pixi" ]; then
            echo "Pixi already installed for $username, updating bashrc..."
            add_pixi_to_bashrc "$username" "$home" "$USER_PIXI_DIR/bin"
            continue
        fi
        
        # Copy pixi to user's home
        cp -r "$TEMP_PIXI_DIR" "$USER_PIXI_DIR"
        
        # Set ownership to the user
        chown -R "$username:$username" "$USER_PIXI_DIR"
        
        # Set permissions - 777 as requested (though 755 would be more secure)
        chmod -R 777 "$USER_PIXI_DIR"
        
        # Add to user's bashrc
        add_pixi_to_bashrc "$username" "$home" "$USER_PIXI_DIR/bin"
        
        echo "✓ Pixi installed for $username at $USER_PIXI_DIR"
    done < <(get_all_users)
    
    # Also install for root (if root has a password)
    if root_has_password; then
        if [ ! -d "/root/.pixi" ] || [ ! -f "/root/.pixi/bin/pixi" ]; then
            echo "Installing pixi for root user..."
            cp -r "$TEMP_PIXI_DIR" "/root/.pixi"
            chmod -R 777 "/root/.pixi"
        fi
        add_pixi_to_bashrc "root" "/root" "/root/.pixi/bin"
    else
        echo "WARNING: Skipping root user - no password set (not accessible via SSH)"
    fi
    
    # Clean up temp directory
    rm -rf "$TEMP_PIXI_DIR"
    
    # Add to /etc/skel/.bashrc for future users
    echo "Adding pixi setup to /etc/skel/.bashrc for future users..."
    if [ -f "/etc/skel/.bashrc" ]; then
        if ! grep -qF "# Pixi setup" "/etc/skel/.bashrc"; then
            cat >> /etc/skel/.bashrc << 'EOF'

# Pixi setup
if [ -d "$HOME/.pixi/bin" ]; then
    export PATH="$HOME/.pixi/bin:$PATH"
fi
EOF
        fi
    fi
    
else
    # Original behavior - install to shared location
    
    # determine installation directory - check for volume storage first, then fall back to image storage
    if [ -d "/hard/volume/app" ]; then
        # volume storage takes precedence, note that it only exists in stage-2
        PIXI_INSTALL_DIR="/hard/volume/app/pixi"
    else
        # otherwise, use the image storage
        PIXI_INSTALL_DIR="/hard/image/app/pixi"
    fi
    
    # already installed? skip installation but still update bashrc files
    if [ -d "$PIXI_INSTALL_DIR" ] && [ -f "$PIXI_INSTALL_DIR/bin/pixi" ]; then
        echo "pixi is already installed in $PIXI_INSTALL_DIR, updating bashrc files..."
    else
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
                cp -r /root/.pixi/* "$PIXI_INSTALL_DIR/"
                chmod +x "$PIXI_INSTALL_DIR/bin/pixi"
            else
                echo "Pixi not found in any location!"
                exit 1
            fi
        fi
        
        # make pixi installation accessible to all users
        echo "Setting permissions for $PIXI_INSTALL_DIR ..."
        chmod -R 777 "$PIXI_INSTALL_DIR"
    fi
    
    # Add pixi to each user's bashrc
    echo "Adding pixi to user bashrc files..."
    
    # Add to all regular users
    while IFS=: read -r username home uid gid; do
        if ! user_has_password "$username"; then
            echo "WARNING: Skipping user $username bashrc - no password set (not accessible via SSH)"
            continue
        fi
        add_pixi_to_bashrc "$username" "$home" "$PIXI_INSTALL_DIR/bin"
    done < <(get_all_users)
    
    # Also add to root's bashrc (if root has a password)
    if root_has_password; then
        add_pixi_to_bashrc "root" "/root" "$PIXI_INSTALL_DIR/bin"
    else
        echo "WARNING: Skipping root user bashrc - no password set (not accessible via SSH)"
    fi
    
    # Add to /etc/bash.bashrc for system-wide availability
    # This ensures new users and non-login shells also get pixi
    if ! grep -qF "# Pixi system-wide setup" /etc/bash.bashrc; then
        echo "Adding pixi to /etc/bash.bashrc for system-wide availability..."
        cat >> /etc/bash.bashrc << EOF

# Pixi system-wide setup
if [ -d "$PIXI_INSTALL_DIR/bin" ]; then
    export PATH="$PIXI_INSTALL_DIR/bin:\$PATH"
fi
EOF
    fi
    
    echo "Pixi installation completed successfully!"
    echo "Pixi installed to: $PIXI_INSTALL_DIR"
    echo "Binary location: $PIXI_INSTALL_DIR/bin/pixi"
fi