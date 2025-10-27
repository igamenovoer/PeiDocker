#!/bin/bash

# set the pixi repository to use Tsinghua mirror

# prevent interactive prompts
export DEBIAN_FRONTEND=noninteractive

# source the pixi utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/pixi-utils.bash"

echo "Configuring pixi to use Tsinghua mirrors..."

# Function to create pixi config for a specific user
create_pixi_config() {
    local user_name="$1"
    local user_home="$2"
    local pixi_config_dir="$user_home/.pixi"
    local pixi_config_file="$pixi_config_dir/config.toml"
    
    # Create config directory if it doesn't exist
    if [ ! -d "$pixi_config_dir" ]; then
        mkdir -p "$pixi_config_dir"
        chown "$user_name:$user_name" "$pixi_config_dir"
    fi
    
    # Create or update the config.toml file
    cat > "$pixi_config_file" << 'EOF'
# Pixi configuration with Tsinghua mirrors

[mirrors]
# Redirect conda-forge to Tsinghua mirror
"https://conda.anaconda.org/conda-forge" = [
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/"
]

# Redirect all anaconda.org channels to Tsinghua
"https://conda.anaconda.org" = [
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/",
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r/",
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2/"
]

[pypi-config]
# Use Tsinghua PyPI mirror
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
# Set keyring provider
keyring-provider = "subprocess"

[repodata-config]
# Optimize repodata fetching
disable-jlap = false
disable-bzip2 = false
disable-zstd = false
EOF
    
    # Set proper ownership
    chown "$user_name:$user_name" "$pixi_config_file"
    
    echo "Created pixi config for user $user_name at $pixi_config_file"
}

# Function to get all users with proper home directories (same as in install script)
get_all_users() {
    # Get users from passwd file, excluding system users (UID < 1000) and nologin users
    while IFS=: read -r username password uid gid gecos home shell; do
        if [ "$uid" -ge 1000 ] && [ -d "$home" ] && [[ "$shell" != */nologin ]] && [[ "$shell" != */false ]]; then
            echo "$username:$home:$uid:$gid"
        fi
    done < /etc/passwd
}

# find_user_pixi function is now available from pixi-utils.bash

# Configure pixi for all users
echo "Configuring pixi mirrors for all users..."

# Configure for regular users
while IFS=: read -r username home uid gid; do
    if ! user_has_password "$username"; then
        echo "WARNING: Skipping user $username - no password set (not accessible via SSH)"
        continue
    fi
    
    echo "Checking pixi for user: $username"
    
    # Check if pixi is available for this user
    if pixi_path=$(find_user_pixi "$home" "$username"); then
        echo "Found pixi at: $pixi_path"
        create_pixi_config "$username" "$home"
    else
        echo "No pixi installation found for user $username, skipping..."
    fi
done < <(get_all_users)

# Also configure for root
echo "Checking pixi for root user..."
if pixi_path=$(find_user_pixi "/root" "root"); then
    if root_has_password; then
        echo "Found pixi at: $pixi_path"
        create_pixi_config "root" "/root"
    else
        echo "WARNING: Skipping root user - no password set (not accessible via SSH)"
    fi
else
    echo "No pixi installation found for root user"
fi

# Create a default config in /etc/skel for future users
echo "Creating default pixi config in /etc/skel for future users..."
mkdir -p /etc/skel/.pixi
cat > /etc/skel/.pixi/config.toml << 'EOF'
# Pixi configuration with Tsinghua mirrors

[mirrors]
# Redirect conda-forge to Tsinghua mirror
"https://conda.anaconda.org/conda-forge" = [
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/"
]

# Redirect all anaconda.org channels to Tsinghua
"https://conda.anaconda.org" = [
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/",
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r/",
    "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2/"
]

[pypi-config]
# Use Tsinghua PyPI mirror
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
# Set keyring provider
keyring-provider = "subprocess"

[repodata-config]
# Optimize repodata fetching
disable-jlap = false
disable-bzip2 = false
disable-zstd = false
EOF

echo ""
echo "Pixi mirror configuration completed!"
echo ""
echo "The following mirrors are now configured for all users:"
echo "  - Conda channels: Tsinghua mirror (mirrors.tuna.tsinghua.edu.cn)"
echo "  - PyPI packages: Tsinghua PyPI mirror (pypi.tuna.tsinghua.edu.cn)"
echo ""
echo "Future users will also get this configuration from /etc/skel/.pixi/config.toml"

