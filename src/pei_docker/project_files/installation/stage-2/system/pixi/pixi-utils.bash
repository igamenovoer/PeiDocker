#!/bin/bash
# Common utility functions for pixi scripts

# Function to get all users with proper home directories
get_all_users() {
    # Get users from passwd file, excluding system users (UID < 1000) and nologin users
    while IFS=: read -r username password uid gid gecos home shell; do
        if [ "$uid" -ge 1000 ] && [ -d "$home" ] && [[ "$shell" != */nologin ]] && [[ "$shell" != */false ]]; then
            echo "$username:$home:$uid:$gid"
        fi
    done < /etc/passwd
}

# Function to find pixi binary for a user
find_user_pixi() {
    local user_home="$1"
    local username="${2:-$(basename "$user_home")}"
    
    # First try to find pixi in the user's PATH by running as that user
    if [ "$username" != "root" ]; then
        local pixi_path=$(su - "$username" -c "command -v pixi 2>/dev/null" 2>/dev/null)
        if [ -n "$pixi_path" ] && [ -f "$pixi_path" ]; then
            echo "$pixi_path"
            return 0
        fi
    else
        # For root, check directly
        if command -v pixi &>/dev/null; then
            echo "$(command -v pixi)"
            return 0
        fi
    fi
    
    # Check per-user default installation location
    if [ -f "$user_home/.pixi/bin/pixi" ]; then
        echo "$user_home/.pixi/bin/pixi"
        return 0
    fi
    
    # Check for custom install directories by looking in bashrc
    local bashrc_file="$user_home/.bashrc"
    if [ -f "$bashrc_file" ]; then
        # Look for PATH export that contains a pixi directory
        local pixi_paths=$(grep -o 'export PATH="[^"]*pixi[^"]*bin[^"]*' "$bashrc_file" 2>/dev/null | sed 's/export PATH="//; s/:.*$//' | head -1)
        if [ -n "$pixi_paths" ] && [ -f "$pixi_paths/pixi" ]; then
            echo "$pixi_paths/pixi"
            return 0
        fi
    fi
    
    # Check legacy shared locations (for backward compatibility)
    for pixi_dir in "/hard/volume/app/pixi" "/hard/image/app/pixi"; do
        if [ -f "$pixi_dir/bin/pixi" ]; then
            echo "$pixi_dir/bin/pixi"
            return 0
        fi
    done
    
    return 1
}

# Function to setup PATH for pixi (for current shell)
setup_pixi_path() {
    local user_home="${1:-$HOME}"
    local username="${2:-$(whoami)}"
    
    # Use find_user_pixi to get the correct pixi location
    local pixi_binary=$(find_user_pixi "$user_home" "$username")
    if [ -n "$pixi_binary" ]; then
        local pixi_bin_dir=$(dirname "$pixi_binary")
        export PATH="$pixi_bin_dir:$PATH"
        return 0
    fi
    
    return 1
}

# Function to run a command as a specific user with their environment
run_as_user() {
    local username="$1"
    shift  # Remove username from arguments
    local command="$@"
    
    # Set up pixi PATH for the user and run the command
    local user_home=$(getent passwd "$username" | cut -d: -f6)
    
    # Find pixi for this user using the enhanced find function
    local pixi_binary=$(find_user_pixi "$user_home" "$username")
    
    if [ -n "$pixi_binary" ]; then
        local pixi_path=$(dirname "$pixi_binary")
        # Run command with pixi in PATH
        su - "$username" -c "export PATH=\"$pixi_path:\$PATH\"; $command"
    else
        # No pixi found, run command without modification
        su - "$username" -c "$command"
    fi
}

# Function to check if pixi is available in current environment
check_pixi_available() {
    if ! command -v pixi &> /dev/null; then
        echo "Error: pixi command not found in PATH"
        echo "Current PATH: $PATH"
        echo "Checking common locations:"
        echo "  ~/.pixi/bin: $(ls -la ~/.pixi/bin/pixi 2>/dev/null || echo 'not found')"
        echo "  /hard/volume/app/pixi/bin: $(ls -la /hard/volume/app/pixi/bin/pixi 2>/dev/null || echo 'not found')"
        echo "  /hard/image/app/pixi/bin: $(ls -la /hard/image/app/pixi/bin/pixi 2>/dev/null || echo 'not found')"
        return 1
    fi
    return 0
}

# Function to run pixi command for all users (or current user if not root)
run_pixi_for_users() {
    local pixi_command="$@"
    
    if [ "$EUID" -ne 0 ]; then
        # Not root, just run for current user
        if setup_pixi_path "$HOME" && check_pixi_available; then
            echo "Running as user $USER: pixi $pixi_command"
            pixi $pixi_command
        else
            echo "Error: pixi not found for user $USER"
            return 1
        fi
    else
        # Running as root, check if we should run for all users
        local found_any=false
        
        # Check for shared installation first
        if setup_pixi_path && check_pixi_available; then
            echo "Found shared pixi installation, running: pixi $pixi_command"
            pixi $pixi_command
            found_any=true
        else
            # No shared installation, check per-user installations
            echo "No shared pixi installation found, checking per-user installations..."
            
            # Run for regular users
            while IFS=: read -r username home uid gid; do
                if find_user_pixi "$home" "$username" >/dev/null; then
                    echo "Running for user $username: pixi $pixi_command"
                    run_as_user "$username" "pixi $pixi_command"
                    found_any=true
                fi
            done < <(get_all_users)
            
            # Also check root
            if find_user_pixi "/root" "root" >/dev/null; then
                echo "Running for root: pixi $pixi_command"
                HOME=/root setup_pixi_path "/root" "root"
                pixi $pixi_command
                found_any=true
            fi
        fi
        
        if [ "$found_any" = false ]; then
            echo "Error: No pixi installation found for any user"
            return 1
        fi
    fi
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

# Function to add pixi to a user's bashrc with optional cache directory configuration
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

# Function to install pixi packages for all users
install_packages_for_all_users() {
    local packages=("$@")
    
    echo "Installing packages for all users with pixi..."
    
    # Install for regular users
    while IFS=: read -r username home uid gid; do
        if ! user_has_password "$username"; then
            echo "WARNING: Skipping user $username - no password set (not accessible via SSH)"
            continue
        fi
        
        if find_user_pixi "$home" "$username" >/dev/null; then
            echo "Installing packages for user: $username"
            for package in "${packages[@]}"; do
                echo "  Installing $package for $username..."
                run_as_user "$username" "pixi global install '$package'" || echo "    Failed to install $package for $username"
            done
        else
            echo "No pixi installation found for user $username, skipping..."
        fi
    done < <(get_all_users)
    
    # Handle root user
    if find_user_pixi "/root" "root" >/dev/null; then
        if root_has_password; then
            echo "Installing packages for root user..."
            HOME=/root setup_pixi_path "/root" "root"
            for package in "${packages[@]}"; do
                echo "  Installing $package for root..."
                pixi global install "$package" || echo "    Failed to install $package for root"
            done
        else
            echo "WARNING: Skipping root user - no password set (not accessible via SSH)"
        fi
    else
        echo "No pixi installation found for root user"
    fi
}

# Export functions so they're available to scripts that source this file
export -f get_all_users
export -f find_user_pixi
export -f setup_pixi_path
export -f run_as_user
export -f check_pixi_available
export -f run_pixi_for_users
export -f user_has_password
export -f root_has_password
export -f add_pixi_to_bashrc
export -f install_packages_for_all_users