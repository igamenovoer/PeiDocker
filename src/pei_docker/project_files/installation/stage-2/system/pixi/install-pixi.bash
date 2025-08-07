#!/bin/bash

# prevent interactive prompts
export DEBIAN_FRONTEND=noninteractive

# Parse command line parameters
PIXI_CACHE_DIR=""
PIXI_INSTALL_DIR=""
VERBOSE=false

for arg in "$@"; do
    case $arg in
        --cache-dir=*)
            PIXI_CACHE_DIR="${arg#*=}"
            shift
            ;;
        --install-dir=*)
            PIXI_INSTALL_DIR="${arg#*=}"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            # Unknown option
            ;;
    esac
done

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

if [ "$VERBOSE" = true ]; then
    echo "Verbose output enabled for debugging"
fi

verbose_echo "Script directory: $SCRIPT_DIR"
verbose_echo "Parameters parsed - Cache dir: '$PIXI_CACHE_DIR', Install dir: '$PIXI_INSTALL_DIR', Verbose: $VERBOSE"

# Source common utilities if available (might not exist on first run)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
            chown "$user_name:$user_name" "$bashrc_file"
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

# Always install pixi to each user's home directory (default pixi behavior)
echo "Installing pixi to each user's home directory..."
verbose_echo "Starting user enumeration and pixi installation process"

# Install pixi for each regular user
verbose_echo "Processing users from get_all_users function"
while IFS=: read -r username home uid gid; do
    verbose_echo "Processing user: $username (UID: $uid, GID: $gid, HOME: $home)"
    
    if ! user_has_password "$username"; then
        echo "WARNING: Skipping user $username - no password set (not accessible via SSH)"
        verbose_echo "User $username has no password, cannot SSH login"
        continue
    fi
    
    verbose_echo "User $username has password set, proceeding with installation"
    echo "Installing pixi for user: $username (UID: $uid, HOME: $home)"
    
    # Determine the install directory for this user
    if [ -n "$PIXI_INSTALL_DIR" ]; then
        USER_PIXI_DIR="$PIXI_INSTALL_DIR"
        verbose_echo "Using custom install directory for $username: $USER_PIXI_DIR"
    else
        USER_PIXI_DIR="$home/.pixi"
        verbose_echo "Using default install directory for $username: $USER_PIXI_DIR"
    fi
    
    # Skip if already installed
    verbose_echo "Checking if pixi already exists at: $USER_PIXI_DIR/bin/pixi"
    if [ -d "$USER_PIXI_DIR" ] && [ -f "$USER_PIXI_DIR/bin/pixi" ]; then
        echo "Pixi already installed for $username at $USER_PIXI_DIR, updating bashrc..."
        verbose_echo "Pixi binary found, updating bashrc configuration only"
        add_pixi_to_bashrc "$username" "$home" "$USER_PIXI_DIR/bin" "$PIXI_CACHE_DIR"
        continue
    fi
    verbose_echo "Pixi not found, proceeding with fresh installation"
    
    # Install pixi directly to the target directory using PIXI_HOME
    echo "Installing pixi to $USER_PIXI_DIR for user $username..."
    verbose_echo "Setting PIXI_HOME=$USER_PIXI_DIR for installation"
    
    # Run installation as the target user to ensure proper permissions
    if [ "$username" = "root" ]; then
        # Install as root
        verbose_echo "Installing as root user"
        export PIXI_HOME="$USER_PIXI_DIR"
        verbose_echo "Running: curl -fsSL https://pixi.sh/install.sh | bash"
        if [ "$VERBOSE" = true ]; then
            curl -fsSL https://pixi.sh/install.sh | bash
        else
            curl -fsSL https://pixi.sh/install.sh | bash >/dev/null 2>&1
        fi
    else
        # Install as the target user
        verbose_echo "Installing as user $username using su"
        verbose_echo "Running: su - $username -c \"export PIXI_HOME='$USER_PIXI_DIR'; curl -fsSL https://pixi.sh/install.sh | bash\""
        if [ "$VERBOSE" = true ]; then
            su - "$username" -c "export PIXI_HOME='$USER_PIXI_DIR'; curl -fsSL https://pixi.sh/install.sh | bash"
        else
            su - "$username" -c "export PIXI_HOME='$USER_PIXI_DIR'; curl -fsSL https://pixi.sh/install.sh | bash" >/dev/null 2>&1
        fi
    fi
    
    # Verify the installation worked
    verbose_echo "Verifying installation at: $USER_PIXI_DIR/bin/pixi"
    if [ -f "$USER_PIXI_DIR/bin/pixi" ]; then
        echo "✓ Pixi successfully installed for $username at $USER_PIXI_DIR"
        verbose_echo "Installation verification successful"
        
        # Ensure proper permissions
        if [ "$username" != "root" ]; then
            verbose_echo "Setting ownership to $username:$username for $USER_PIXI_DIR"
            chown -R "$username:$username" "$USER_PIXI_DIR"
        else
            verbose_echo "Skipping ownership change for root user"
        fi
        verbose_echo "Setting permissions to 755 for $USER_PIXI_DIR"
        chmod -R 755 "$USER_PIXI_DIR"
        
        # Add to user's bashrc
        verbose_echo "Adding pixi to bashrc for $username"
        verbose_echo "Calling: add_pixi_to_bashrc \"$username\" \"$home\" \"$USER_PIXI_DIR/bin\" \"$PIXI_CACHE_DIR\""
        add_pixi_to_bashrc "$username" "$home" "$USER_PIXI_DIR/bin" "$PIXI_CACHE_DIR"
    else
        echo "✗ Pixi installation failed for $username"
        echo "Expected: $USER_PIXI_DIR/bin/pixi"
        verbose_echo "Installation verification failed - binary not found"
        verbose_echo "Checking if any pixi files were created in $USER_PIXI_DIR:"
        if [ "$VERBOSE" = true ] && [ -d "$USER_PIXI_DIR" ]; then
            ls -la "$USER_PIXI_DIR" || verbose_echo "Failed to list contents of $USER_PIXI_DIR"
        fi
        continue
    fi
    
done < <(get_all_users)

# Also install for root (if root has a password)
verbose_echo "Checking if root user has password set"
if root_has_password; then
    echo "Installing pixi for root user..."
    verbose_echo "Root user has password set, proceeding with installation"
    
    # Determine the install directory for root
    if [ -n "$PIXI_INSTALL_DIR" ]; then
        ROOT_PIXI_DIR="$PIXI_INSTALL_DIR"
        verbose_echo "Using custom install directory for root: $ROOT_PIXI_DIR"
    else
        ROOT_PIXI_DIR="/root/.pixi"
        verbose_echo "Using default install directory for root: $ROOT_PIXI_DIR"
    fi
    
    verbose_echo "Checking if pixi already exists at: $ROOT_PIXI_DIR/bin/pixi"
    if [ ! -d "$ROOT_PIXI_DIR" ] || [ ! -f "$ROOT_PIXI_DIR/bin/pixi" ]; then
        verbose_echo "Pixi not found for root, proceeding with fresh installation"
        verbose_echo "Setting PIXI_HOME=$ROOT_PIXI_DIR for root installation"
        export PIXI_HOME="$ROOT_PIXI_DIR"
        verbose_echo "Running: curl -fsSL https://pixi.sh/install.sh | bash"
        if [ "$VERBOSE" = true ]; then
            curl -fsSL https://pixi.sh/install.sh | bash
        else
            curl -fsSL https://pixi.sh/install.sh | bash >/dev/null 2>&1
        fi
        
        verbose_echo "Verifying root installation at: $ROOT_PIXI_DIR/bin/pixi"
        if [ -f "$ROOT_PIXI_DIR/bin/pixi" ]; then
            echo "✓ Pixi successfully installed for root at $ROOT_PIXI_DIR"
            verbose_echo "Root installation verification successful"
            verbose_echo "Setting permissions to 755 for $ROOT_PIXI_DIR"
            chmod -R 755 "$ROOT_PIXI_DIR"
        else
            echo "✗ Pixi installation failed for root"
            verbose_echo "Root installation verification failed - binary not found"
        fi
    else
        verbose_echo "Pixi already installed for root, updating bashrc only"
    fi
    
    verbose_echo "Adding pixi to bashrc for root"
    add_pixi_to_bashrc "root" "/root" "$ROOT_PIXI_DIR/bin" "$PIXI_CACHE_DIR"
else
    echo "WARNING: Skipping root user - no password set (not accessible via SSH)"
    verbose_echo "Root user has no password, cannot SSH login"
fi

# Add to /etc/skel/.bashrc for future users
echo "Adding pixi setup to /etc/skel/.bashrc for future users..."
verbose_echo "Configuring /etc/skel/.bashrc for future user auto-setup"

if [ -f "/etc/skel/.bashrc" ]; then
    verbose_echo "/etc/skel/.bashrc exists, checking for existing pixi setup"
    if ! grep -qF "# Pixi setup" "/etc/skel/.bashrc"; then
        verbose_echo "No existing pixi setup found in /etc/skel/.bashrc, adding new configuration"
        
        # Determine the path to add for future users
        if [ -n "$PIXI_INSTALL_DIR" ]; then
            verbose_echo "Adding custom install directory path to skel: $PIXI_INSTALL_DIR/bin"
            cat >> /etc/skel/.bashrc << EOF

# Pixi setup
if [ -d "$PIXI_INSTALL_DIR/bin" ]; then
    export PATH="$PIXI_INSTALL_DIR/bin:\$PATH"
fi
EOF
        else
            verbose_echo "Adding default install directory path to skel: \$HOME/.pixi/bin"
            cat >> /etc/skel/.bashrc << 'EOF'

# Pixi setup
if [ -d "$HOME/.pixi/bin" ]; then
    export PATH="$HOME/.pixi/bin:$PATH"
fi
EOF
        fi
        
        # Add cache directory to skel if provided
        if [ -n "$PIXI_CACHE_DIR" ]; then
            verbose_echo "Adding cache directory to skel: $PIXI_CACHE_DIR"
            echo "export PIXI_CACHE_DIR=\"$PIXI_CACHE_DIR\"" >> /etc/skel/.bashrc
        fi
        verbose_echo "Successfully updated /etc/skel/.bashrc"
    else
        verbose_echo "Pixi setup already exists in /etc/skel/.bashrc, skipping"
    fi
else
    verbose_echo "WARNING: /etc/skel/.bashrc not found, future users will need manual setup"
fi

echo "Pixi installation completed successfully!"
verbose_echo "Installation process complete, generating summary"

if [ -n "$PIXI_INSTALL_DIR" ]; then
    echo "Pixi installed to custom directory: $PIXI_INSTALL_DIR"
    verbose_echo "Custom installation directory was used: $PIXI_INSTALL_DIR"
else
    echo "Pixi installed to each user's home directory at ~/.pixi"
    verbose_echo "Default per-user installation directories were used"
fi

if [ -n "$PIXI_CACHE_DIR" ]; then
    echo "Pixi cache directory configured: $PIXI_CACHE_DIR"
    verbose_echo "Custom cache directory was configured: $PIXI_CACHE_DIR"
fi

if [ "$VERBOSE" = true ]; then
    verbose_echo "Verbose mode was enabled during installation"
    verbose_echo "Installation summary complete"
fi