#!/bin/bash
set -euo pipefail

# if WITH_SSH is false or not set, exit
if [ "${WITH_SSH:-false}" != "true" ]; then
  exit 0
fi

# if openssh server is not installed, skip it
if [ ! -f /etc/ssh/sshd_config ]; then
  echo "openssh-server is not installed, skipping ssh setup"
  exit 0
fi

# if SSH_USER_NAME is not set, exit
if [ -z "${SSH_USER_NAME:-}" ]; then
  echo "SSH_USER_NAME is not set, exiting"
  exit 0
fi

# setup
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# permit root login
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
# printf "\nPermitRootLogin yes\n" >> /etc/ssh/sshd_config

# Set custom SSH port if SSH_CONTAINER_PORT is defined
if [ -n "${SSH_CONTAINER_PORT:-}" ]; then
    echo "Port $SSH_CONTAINER_PORT" >> /etc/ssh/sshd_config
    sed -i "s/^#Port 22/Port $SSH_CONTAINER_PORT/" /etc/ssh/sshd_config
fi

# permit password authentication
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config

# allow x11 forwarding, trust x11 forwarding
echo "X11Forwarding yes" >> /etc/ssh/sshd_config
echo "X11UseLocalhost no" >> /etc/ssh/sshd_config

# create a user group named users
# Ensure ssh_users group exists (idempotent)
if ! getent group ssh_users >/dev/null 2>&1; then
  groupadd -r ssh_users
fi

# SSH_USER_NAME contains a list of users separated by comma
# SSH_USER_PASSWORD contains a list of passwords separated by comma
# SSH_PUBKEY_FILE contains a list of public keys separated by comma
# SSH_PRIVKEY_FILE contains a list of private keys separated by comma
# SSH_USER_UID contains a list of uids separated by comma
# for each user, configure it
IFS=',' read -ra users <<< "${SSH_USER_NAME:-}"
IFS=',' read -ra passwords <<< "${SSH_USER_PASSWORD:-}"
IFS=',' read -ra pubkey_files <<< "${SSH_PUBKEY_FILE:-}"
IFS=',' read -ra privkey_files <<< "${SSH_PRIVKEY_FILE:-}"
IFS=',' read -ra uids <<< "${SSH_USER_UID:-}"
# optional: per-user primary group gid list (comma-separated)
IFS=',' read -ra gids <<< "${SSH_USER_GID:-}"

# Helpers
get_user_home() {
  getent passwd "$1" | awk -F: '{print $6}' | head -n1
}

username_exists() {
  id -u "$1" >/dev/null 2>&1
}

uid_owner() {
  awk -F: -v uid="$1" '$3==uid{print $1; exit}' /etc/passwd || true
}

gid_exists() {
  awk -F: -v gid="$1" '$3==gid{found=1} END{exit(found?0:1)}' /etc/group
}

groupname_exists() {
  getent group "$1" >/dev/null 2>&1
}

find_next_free_uid() {
  # find next uid starting from 1000 that is not used
  local cand=1000
  while getent passwd | awk -F: -v u="$cand" '$3==u{found=1} END{exit(found?0:1)}'; do
    cand=$((cand+1))
  done
  echo "$cand"
}

find_available_username() {
  local base="$1"
  local cand="$base"
  local n=0
  while username_exists "$cand"; do
    n=$((n+1))
    cand="${base}_old${n}"
  done
  echo "$cand"
}


for i in "${!users[@]}"; do
  user=${users[$i]}
  password=${passwords[$i]-}
  pubkey_file=${pubkey_files[$i]-}
  privkey_file=${privkey_files[$i]-}
  uid=${uids[$i]-}
  gid=${gids[$i]-}
  if [ -z "$user" ]; then
    continue
  fi

  echo "Configuring user $user, password $password, pubkey $pubkey_file, privkey $privkey_file"

  if [ "$user" = "root" ]; then
    # For root user, just set password and configure SSH
    echo "root:$password" | chpasswd
    usermod -aG ssh_users root
    ssh_dir="/root/.ssh"
  else
    # For non-root users: ensure requested (username, uid, gid) are available.
    # 1) Username conflict: rename existing user and its home directory.
    if username_exists "$user"; then
      old_home=$(get_user_home "$user")
      new_name=$(find_available_username "$user")
      echo "Username '$user' exists; renaming to '$new_name' and moving home if needed."
      # Compute new home path when old_home is under /home or matches /home/$user
      new_home="$old_home"
      if [ -n "$old_home" ] && [ -d "$old_home" ]; then
        base_dir=$(dirname "$old_home")
        new_home="$base_dir/$new_name"
        usermod -l "$new_name" -d "$new_home" -m "$user"
      else
        usermod -l "$new_name" "$user"
      fi
    fi

    # 2) UID conflict: if requested uid is taken, reassign the existing user's uid to a free one.
    if [ -n "${uid:-}" ]; then
      conflict_user=$(uid_owner "$uid")
      if [ -n "$conflict_user" ]; then
        if [ "$conflict_user" = "root" ]; then
          echo "ERROR: Requested UID $uid conflicts with root; cannot proceed." >&2
          exit 1
        fi
        new_uid=$(find_next_free_uid)
        echo "UID $uid in use by '$conflict_user'; changing '$conflict_user' UID to $new_uid."
        usermod -u "$new_uid" "$conflict_user"
      fi
    fi

    # 3) GID processing: if requested gid provided and group doesn't exist, create it.
    if [ -n "${gid:-}" ]; then
      if ! gid_exists "$gid"; then
        # choose a group name to bind to this gid
        grp_name="$user"
        if groupname_exists "$grp_name"; then
          grp_name="${user}_${gid}"
        fi
        echo "Creating group '$grp_name' with gid $gid"
        groupadd -g "$gid" "$grp_name"
      fi
    fi

    # 4) Create the user exactly as requested (with UID/GID if provided)
    add_args=( --gecos "" --disabled-password )
    if [ -n "${uid:-}" ]; then add_args+=( --uid "$uid" ); fi
    if [ -n "${gid:-}" ]; then add_args+=( --gid "$gid" ); fi
    echo "Creating user '$user' ${uid:+uid $uid }${gid:+gid $gid}"
    adduser "${add_args[@]}" "$user"

    # Add to groups; any failure should be treated as error (set -e is active)
    usermod -aG sudo "$user"
    usermod -aG ssh_users "$user"
    echo "$user:$password" | chpasswd
    ssh_dir="/home/$user/.ssh"
  fi

  # Final verification: ensure user exists and matches requested uid/gid (when provided)
  if [ "$user" != "root" ]; then
    if ! username_exists "$user"; then
      echo "ERROR: Failed to create user '$user'." >&2
      exit 1
    fi
    if [ -n "${uid:-}" ]; then
      actual_uid=$(id -u "$user")
      if [ "$actual_uid" != "$uid" ]; then
        echo "ERROR: User '$user' UID mismatch: expected $uid, got $actual_uid." >&2
        exit 1
      fi
    fi
    if [ -n "${gid:-}" ]; then
      actual_gid=$(id -g "$user")
      if [ "$actual_gid" != "$gid" ]; then
        echo "ERROR: User '$user' GID mismatch: expected $gid, got $actual_gid." >&2
        exit 1
      fi
    fi
  fi

  # Create SSH directory
  mkdir -p $ssh_dir
  
  # Check if user is providing a private key first
  if [ -n "$privkey_file" ]; then
    echo "Installing user-provided private key from $privkey_file"
    
    # Detect key type from file headers to use standard filename
    key_type="rsa"  # default
    key_filename="id_rsa"  # default standard filename
    
    if grep -q "BEGIN OPENSSH PRIVATE KEY" "$privkey_file"; then
      # For OpenSSH format, default to rsa (most common)
      key_filename="id_rsa"
    elif grep -q "BEGIN EC PRIVATE KEY" "$privkey_file"; then
      key_filename="id_ecdsa"
    elif grep -q "BEGIN DSA PRIVATE KEY" "$privkey_file"; then
      key_filename="id_dsa"
    elif grep -q "BEGIN RSA PRIVATE KEY" "$privkey_file"; then
      key_filename="id_rsa"
    fi
    
    # Copy user's private key to standard location (replaces auto-generated key)
    cp "$privkey_file" "$ssh_dir/$key_filename"
    chmod 600 "$ssh_dir/$key_filename"
    
    # Remove any existing .pub file for this key (since we can't generate it from encrypted key)
    rm -f "$ssh_dir/${key_filename}.pub"
    
    echo "Private key installed as $key_filename (encrypted, replaces auto-generated key)"
    
  else
    # No user-provided private key, generate standard key pair
    echo "Generating SSH key pair for $user"
    ssh-keygen -t rsa -C "$user" -f "$ssh_dir/id_rsa" -N ""
    
    # Print the generated private key
    echo "Generated SSH private key for $user:"
    cat "$ssh_dir/id_rsa"
    
    # Add generated public key to authorized_keys
    cat "$ssh_dir/id_rsa.pub" >> "$ssh_dir/authorized_keys"
  fi
  
  # Handle provided public key file (add to authorized_keys)
  if [ -n "$pubkey_file" ]; then
    echo "Adding public key from $pubkey_file to authorized_keys"
    cat $pubkey_file >> "$ssh_dir/authorized_keys"
  fi

  # Set correct ownership (use user's primary group name)
  if [ "$user" = "root" ]; then
    chown -R root:root $ssh_dir
  else
    primary_group=$(id -gn "$user")
    chown -R "$user":"$primary_group" $ssh_dir
  fi
done

# generate ssh key for host
ssh-keygen -A
