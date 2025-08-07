"""
SSH configuration classes for PeiDocker.

This module provides SSH server and user account configuration for Docker containers,
supporting multiple authentication methods including passwords and SSH keys.
"""

from attrs import define, field
from typing import Optional, Dict
import re


@define(kw_only=True)
class SSHUserConfig:
    """
    SSH user account configuration with multiple authentication methods.
    
    Defines an SSH user account that will be created in the Docker container,
    supporting password authentication, public key authentication, and private
    key provisioning. Provides flexible authentication options for different
    security requirements.
    
    Attributes
    ----------
    password : str, optional
        Password for SSH authentication. Cannot contain spaces or commas
        due to implementation constraints in shell script processing.
    pubkey_file : str, optional
        Path to SSH public key file. Supports relative paths (from project
        installation directory), absolute paths, or "~" for system key discovery.
        Mutually exclusive with pubkey_text.
    pubkey_text : str, optional
        SSH public key content as text. Must be in valid OpenSSH public key
        format (e.g., "ssh-rsa AAAAB3NzaC1yc2E..."). Mutually exclusive with pubkey_file.
    privkey_file : str, optional
        Path to SSH private key file. Supports relative paths, absolute paths,
        or "~" for system key discovery. Mutually exclusive with privkey_text.
    privkey_text : str, optional
        SSH private key content as text. Must be in valid OpenSSH or PEM format.
        Mutually exclusive with privkey_file.
    uid : int, optional
        User ID for the SSH account. Defaults to system assignment if not specified.
        Recommended to use UIDs >= 1100 to avoid conflicts with system users.
        
    Raises
    ------
    ValueError
        If password contains spaces or commas, if mutually exclusive key options
        are both specified, if no authentication method is provided, or if
        SSH key formats are invalid.
        
    Examples
    --------
    Password-only authentication:
        >>> user = SSHUserConfig(password="secure123", uid=1100)
        
    Public key authentication:
        >>> user = SSHUserConfig(
        ...     pubkey_text="ssh-rsa AAAAB3NzaC1yc2E... user@host",
        ...     uid=1100
        ... )
        
    System SSH key discovery:
        >>> user = SSHUserConfig(pubkey_file="~", uid=1100)
        
    Combined authentication methods:
        >>> user = SSHUserConfig(
        ...     password="backup123",
        ...     pubkey_file="/path/to/key.pub",
        ...     uid=1100
        ... )
        
    Notes
    -----
    At least one authentication method (password, public key, or private key)
    must be provided. Public and private key options are mutually exclusive
    within their respective categories but can be combined with passwords.
    
    SSH key validation ensures proper format before container deployment.
    The "~" syntax automatically discovers system SSH keys with priority:
    id_rsa, id_dsa, id_ecdsa, id_ed25519.
    """
    password: Optional[str] = field(default=None)
    pubkey_file: Optional[str] = field(default=None)
    pubkey_text: Optional[str] = field(default=None)
    privkey_file: Optional[str] = field(default=None)
    privkey_text: Optional[str] = field(default=None)
    uid: Optional[int] = field(default=None)
    
    def __attrs_post_init__(self) -> None:
        # Validate password format
        if self.password is not None:
            # password cannot contain space and comma
            assert ' ' not in self.password and ',' not in self.password, f'Password cannot contain space or comma: {self.password}'
        
        # Validate mutually exclusive public key options
        if self.pubkey_file is not None and self.pubkey_text is not None:
            raise ValueError('Cannot specify both pubkey_file and pubkey_text')
        
        # Validate mutually exclusive private key options
        if self.privkey_file is not None and self.privkey_text is not None:
            raise ValueError('Cannot specify both privkey_file and privkey_text')
        
        # At least one authentication method required
        has_password = self.password is not None
        has_pubkey = self.pubkey_file is not None or self.pubkey_text is not None
        has_privkey = self.privkey_file is not None or self.privkey_text is not None
        
        if not (has_password or has_pubkey or has_privkey):
            raise ValueError('Must provide at least one authentication method: password, public key, or private key')
        
        # Validate SSH key formats
        if self.pubkey_text is not None:
            self._validate_public_key_format(self.pubkey_text)
        
        if self.privkey_text is not None:
            self._validate_private_key_format(self.privkey_text)
    
    def _validate_public_key_format(self, key_text: str) -> None:
        """Validate SSH public key format"""
        key_text = key_text.strip()
        
        # SSH public key should start with algorithm name and contain base64 data
        ssh_key_pattern = r'^(ssh-rsa|ssh-dss|ssh-ed25519|ecdsa-sha2-nistp256|ecdsa-sha2-nistp384|ecdsa-sha2-nistp521)\s+[A-Za-z0-9+/]+=*\s*.*$'
        
        if not re.match(ssh_key_pattern, key_text):
            raise ValueError(f'Invalid SSH public key format: {key_text[:50]}...')
    
    def _validate_private_key_format(self, key_text: str) -> None:
        """Validate SSH private key format"""
        key_text = key_text.strip()
        
        # Check for OpenSSH private key format
        if key_text.startswith('-----BEGIN OPENSSH PRIVATE KEY-----') and key_text.endswith('-----END OPENSSH PRIVATE KEY-----'):
            return
        
        # Check for traditional private key formats
        traditional_headers = [
            '-----BEGIN RSA PRIVATE KEY-----',
            '-----BEGIN DSA PRIVATE KEY-----',
            '-----BEGIN EC PRIVATE KEY-----',
            '-----BEGIN PRIVATE KEY-----'
        ]
        
        for header in traditional_headers:
            if key_text.startswith(header):
                return
        
        raise ValueError('Invalid SSH private key format. Must be in OpenSSH or traditional PEM format.')


@define(kw_only=True)
class SSHConfig:
    """
    SSH server configuration for Docker container access.
    
    Manages SSH server setup including port configuration, user accounts,
    and container-to-host port mapping. SSH provides the primary method
    for interactive terminal access to running containers.
    
    Attributes
    ----------
    enable : bool, default True
        Whether to enable SSH server in the container. When disabled,
        users must use 'docker exec' commands for container access.
    port : int, default 22
        Port number for SSH server inside the container. Standard SSH
        port is 22, but can be changed for security or conflict avoidance.
    host_port : int, optional
        Port number on the host machine that maps to the container SSH port.
        If not specified, Docker will assign a random available port.
        Common choice is 2222 to avoid conflicts with host SSH (port 22).
    users : Dict[str, SSHUserConfig], default empty
        Dictionary mapping usernames to SSH user configurations. Each user
        can have different authentication methods and system properties.
        
    Examples
    --------
    Basic SSH configuration:
        >>> ssh_config = SSHConfig(
        ...     enable=True,
        ...     port=22,
        ...     host_port=2222,
        ...     users={
        ...         "admin": SSHUserConfig(password="admin123", uid=1100)
        ...     }
        ... )
        
    Disabled SSH (use docker exec instead):
        >>> ssh_config = SSHConfig(enable=False)
        
    Custom port configuration:
        >>> ssh_config = SSHConfig(
        ...     port=2022,
        ...     host_port=2022,
        ...     users={"user": SSHUserConfig(pubkey_file="~")}
        ... )
        
    Notes
    -----
    SSH is enabled by default as it provides the most convenient access method
    for development and debugging. When enabled, at least one user should be
    configured to allow container access.
    
    The host_port mapping allows external access to the container SSH server.
    If not specified, Docker assigns a random port accessible via 'docker port'.
    """
    # SSH enabled by default for convenient container access
    enable: bool = field(default=True)
    port: int = field(default=22)
    host_port: Optional[int] = field(default=None)
    users: Dict[str, SSHUserConfig] = field(factory=dict)