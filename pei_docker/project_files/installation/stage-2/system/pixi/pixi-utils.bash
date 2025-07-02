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
    
    # Check per-user installation first
    if [ -f "$user_home/.pixi/bin/pixi" ]; then
        echo "$user_home/.pixi/bin/pixi"
        return 0
    fi
    
    # Check shared locations
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
    
    # Check per-user installation first
    if [ -f "$user_home/.pixi/bin/pixi" ]; then
        export PATH="$user_home/.pixi/bin:$PATH"
        return 0
    fi
    
    # Check shared locations
    if [ -d "/hard/volume/app/pixi/bin" ]; then
        export PATH="/hard/volume/app/pixi/bin:$PATH"
        return 0
    elif [ -d "/hard/image/app/pixi/bin" ]; then
        export PATH="/hard/image/app/pixi/bin:$PATH"
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
    local pixi_path=""
    
    # Find pixi for this user
    if [ -f "$user_home/.pixi/bin/pixi" ]; then
        pixi_path="$user_home/.pixi/bin"
    elif [ -f "/hard/volume/app/pixi/bin/pixi" ]; then
        pixi_path="/hard/volume/app/pixi/bin"
    elif [ -f "/hard/image/app/pixi/bin/pixi" ]; then
        pixi_path="/hard/image/app/pixi/bin"
    fi
    
    if [ -n "$pixi_path" ]; then
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
                if find_user_pixi "$home" >/dev/null; then
                    echo "Running for user $username: pixi $pixi_command"
                    run_as_user "$username" "pixi $pixi_command"
                    found_any=true
                fi
            done < <(get_all_users)
            
            # Also check root
            if find_user_pixi "/root" >/dev/null; then
                echo "Running for root: pixi $pixi_command"
                HOME=/root setup_pixi_path "/root"
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

# Function to check if root user has a password set
root_has_password() {
    # Check if root has a password by examining /etc/shadow
    local root_shadow_entry=$(getent shadow root)
    local password_field=$(echo "$root_shadow_entry" | cut -d: -f2)
    
    # If password field is empty, !, or *, root has no password
    if [ -z "$password_field" ] || [ "$password_field" = "!" ] || [ "$password_field" = "*" ]; then
        return 1  # No password
    else
        return 0  # Has password
    fi
}

# Function to install pixi packages for all users
install_packages_for_all_users() {
    local packages=("$@")
    
    echo "Installing packages for all users with pixi..."
    
    # Install for regular users
    while IFS=: read -r username home uid gid; do
        if find_user_pixi "$home" >/dev/null; then
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
    if find_user_pixi "/root" >/dev/null; then
        if root_has_password; then
            echo "Installing packages for root user..."
            HOME=/root setup_pixi_path "/root"
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
export -f root_has_password
export -f install_packages_for_all_users