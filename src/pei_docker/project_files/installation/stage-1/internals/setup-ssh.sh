#!/bin/bash

# if WITH_SSH is false or not set, exit
if [ "$WITH_SSH" != "true" ]; then
  exit 0
fi

# if openssh server is not installed, skip it
if [ ! -f /etc/ssh/sshd_config ]; then
  echo "openssh-server is not installed, skipping ssh setup"
  exit 0
fi

# if SSH_USER_NAME is not set, exit
if [ -z "$SSH_USER_NAME" ]; then
  echo "SSH_USER_NAME is not set, exiting"
  exit 0
fi

# setup
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# permit root login
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
# printf "\nPermitRootLogin yes\n" >> /etc/ssh/sshd_config

# Set custom SSH port if SSH_CONTAINER_PORT is defined
if [ -n "$SSH_CONTAINER_PORT" ]; then
    echo "Port $SSH_CONTAINER_PORT" >> /etc/ssh/sshd_config
    sed -i "s/^#Port 22/Port $SSH_CONTAINER_PORT/" /etc/ssh/sshd_config
fi

# permit password authentication
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config

# allow x11 forwarding, trust x11 forwarding
echo "X11Forwarding yes" >> /etc/ssh/sshd_config
echo "X11UseLocalhost no" >> /etc/ssh/sshd_config

# create a user group named users
groupadd ssh_users

# SSH_USER_NAME contains a list of users separated by comma
# SSH_USER_PASSWORD contains a list of passwords separated by comma
# SSH_PUBKEY_FILE contains a list of public keys separated by comma
# SSH_PRIVKEY_FILE contains a list of private keys separated by comma
# SSH_USER_UID contains a list of uids separated by comma
# for each user, configure it
IFS=',' read -ra users <<< "$SSH_USER_NAME"
IFS=',' read -ra passwords <<< "$SSH_USER_PASSWORD"
IFS=',' read -ra pubkey_files <<< "$SSH_PUBKEY_FILE"
IFS=',' read -ra privkey_files <<< "$SSH_PRIVKEY_FILE"
IFS=',' read -ra uids <<< "$SSH_USER_UID"


for i in "${!users[@]}"; do
  user=${users[$i]}
  password=${passwords[$i]}
  pubkey_file=${pubkey_files[$i]}
  privkey_file=${privkey_files[$i]}
  uid=${uids[$i]}
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
    # For non-root users, create account with specified UID if provided
    if [ -n "$uid" ]; then
      echo "Creating user with uid $uid"
      adduser --gecos "" --disabled-password --uid $uid $user
    else
      echo "Creating user with system-assigned uid"
      adduser --gecos "" --disabled-password $user
    fi
    usermod -aG sudo $user
    usermod -aG ssh_users $user
    echo "$user:$password" | chpasswd
    ssh_dir="/home/$user/.ssh"
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

  # Set correct ownership
  if [ "$user" = "root" ]; then
    chown -R root:root $ssh_dir
  else
    chown -R $user:$user $ssh_dir
  fi
done

# generate ssh key for host
ssh-keygen -A
