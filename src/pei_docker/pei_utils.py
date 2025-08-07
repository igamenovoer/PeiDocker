"""
PeiDocker Utility Functions.

This module provides essential utility functions for PeiDocker's configuration
processing, environment variable substitution, SSH key management, and file
operations. These utilities support the core framework functionality across
both CLI and GUI applications.

Key Features
------------
- Environment variable substitution with Docker Compose-style ${VAR:-default} syntax
- SSH key discovery, validation, and management across platforms
- Configuration processing with recursive structure handling
- Cross-platform file operations for Docker container integration
- Secure temporary file handling for SSH key operations

Environment Variable Substitution
---------------------------------
Supports Docker Compose-compatible syntax:
- ${VAR}: Replace with environment variable value
- ${VAR:-default}: Replace with environment variable or default if unset

This enables deployment-specific customization without modifying configuration
files, essential for CI/CD pipelines and multi-environment deployments.

SSH Key Management
------------------
Provides comprehensive SSH key handling:
- Discovery of system SSH keys with priority ordering (id_rsa, id_dsa, id_ecdsa, id_ed25519)
- Validation of public and private key formats (OpenSSH and PEM)
- Key type detection from private key content
- Public key generation from private keys
- Secure temporary file operations with proper permissions
- Cross-platform path resolution with ~ syntax support

Configuration Processing
------------------------
Handles complex configuration structures:
- Recursive processing of nested dictionaries and lists
- OmegaConf integration for type-safe configuration management
- Environment variable substitution throughout configuration trees
- Null value cleanup and structure validation

Notes
-----
This module is platform-agnostic and handles Windows/WSL, Linux, and macOS
specific requirements for SSH key discovery and file operations.

Examples
--------
Environment variable substitution:
    >>> substitute_env_vars("${HOME}/workspace")
    '/home/user/workspace'
    
    >>> substitute_env_vars("${UNDEFINED:-/default/path}")
    '/default/path'

SSH key discovery:
    >>> key_path = find_system_ssh_key(prefer_public=True)
    >>> print(key_path)
    '/home/user/.ssh/id_rsa.pub'

Configuration processing:
    >>> config = OmegaConf.create({'path': '${HOME}/data'})
    >>> processed = process_config_env_substitution(config)
    >>> print(processed.path)
    '/home/user/data'
"""

# utility methods
import omegaconf as oc
from omegaconf.omegaconf import DictConfig
import os
import re
from typing import Any

def remove_null_keys(cfg: DictConfig) -> DictConfig:
    """
    Remove all keys with None values from configuration in place.
    
    Recursively traverses the configuration structure and removes any keys
    that have None as their value. This is useful for cleaning up
    configurations where optional values are explicitly set to None.
    
    Parameters
    ----------
    cfg : DictConfig
        OmegaConf DictConfig object to clean up
        
    Returns
    -------
    DictConfig
        The same configuration object with None values removed
        
    Notes
    -----
    This function modifies the input configuration in place for efficiency.
    Use cfg.copy() before calling if you need to preserve the original.
    
    Examples
    --------
    >>> from omegaconf import OmegaConf
    >>> cfg = OmegaConf.create({'a': 1, 'b': None, 'c': {'d': None, 'e': 2}})
    >>> remove_null_keys(cfg)
    >>> print(cfg)
    {'a': 1, 'c': {'e': 2}}
    """
    shadow = cfg.copy()
    for k, v in shadow.items():
        if v is None:
            print(f'removing key {k!r}')
            cfg.pop(k)
        elif isinstance(v, DictConfig):
            remove_null_keys(cfg.get(k))
    return cfg

def retain_ssh_users(ssh_config: DictConfig, user: list[str]) -> None:
    """
    Retain only specified SSH users in the configuration.
    
    Filters the SSH configuration to keep only the users specified in the
    user list, removing all other user configurations. This is useful for
    creating deployment-specific configurations with limited user access.
    
    Parameters
    ----------
    ssh_config : DictConfig
        SSH configuration object from the stage_?.ssh section containing
        a 'users' dictionary with user-specific configurations
    user : list[str]
        List of usernames to retain in the configuration. All other users
        will be removed from the ssh_config.users dictionary
        
    Raises
    ------
    AssertionError
        If user parameter is not a list
        
    Notes
    -----
    This function modifies the ssh_config in place by removing unwanted
    user entries from the users dictionary.
    
    Examples
    --------
    >>> from omegaconf import OmegaConf
    >>> ssh_cfg = OmegaConf.create({
    ...     'users': {'admin': {}, 'guest': {}, 'developer': {}}
    ... })
    >>> retain_ssh_users(ssh_cfg, ['admin', 'developer'])
    >>> print(list(ssh_cfg.users.keys()))
    ['admin', 'developer']
    """
    assert isinstance(user, list), 'user must be a list'
    
    ssh_users_to_remove = set(ssh_config.users.keys())-set(user)
    for u in ssh_users_to_remove:
        ssh_config.users.pop(u)

def substitute_env_vars(value: str) -> str:
    """
    Substitute environment variables in string with Docker Compose-style syntax.
    
    Processes environment variable references using Docker Compose-compatible
    syntax with both simple variable substitution and fallback values. This
    function is essential for deployment-specific configuration without
    modifying config files.
    
    Parameters
    ----------
    value : str
        String that may contain environment variable references in the format
        ${VAR} or ${VAR:-default}. Non-string values are returned unchanged.
        
    Returns
    -------
    str or any
        String with environment variables substituted, or original value if
        not a string. Undefined variables without defaults are left unchanged.
        
    Notes
    -----
    Supports two syntax patterns:
    - ${VAR}: Simple substitution, returns original if variable undefined
    - ${VAR:-default}: Substitution with fallback default value
    
    The function uses regex pattern `\\$\\{([^}]+)\\}` to match variable
    references and handles nested fallback syntax parsing.
    
    Examples
    --------
    Simple variable substitution (assuming HOME=/home/user):
        >>> substitute_env_vars("${HOME}/workspace")
        '/home/user/workspace'
        
    Fallback syntax with undefined variable:
        >>> substitute_env_vars("${UNDEFINED_VAR:-/default/path}")
        '/default/path'
        
    Complex path with fallback:
        >>> substitute_env_vars("${SHARED_HOST_PATH:-/mnt/d/docker-space/workspace}")
        '/mnt/d/docker-space/workspace'
        
    Non-string input (returned unchanged):
        >>> substitute_env_vars(42)
        42
    """
    if not isinstance(value, str):
        return value
    
    # Pattern to match ${VAR} or ${VAR:-default}
    pattern = r'\$\{([^}]+)\}'
    
    def replacer(match: re.Match[str]) -> str:
        var_expr = match.group(1)
        
        # Check if it has fallback syntax (VAR:-default)
        if ':-' in var_expr:
            var_name, default_value = var_expr.split(':-', 1)
            return os.environ.get(var_name, default_value)
        else:
            # Simple variable substitution ${VAR}
            return os.environ.get(var_expr, match.group(0))  # Return original if not found
    
    return re.sub(pattern, replacer, value)

def process_config_env_substitution(cfg: DictConfig) -> DictConfig:
    """
    Recursively process configuration object for environment variable substitution.
    
    Traverses the entire configuration structure (nested dictionaries and lists)
    and applies environment variable substitution to all string values using
    Docker Compose-compatible syntax. This enables deployment-specific
    customization throughout the configuration hierarchy.
    
    Parameters
    ----------
    cfg : DictConfig
        OmegaConf DictConfig object containing the configuration structure
        to process. Must be a dictionary-like structure.
        
    Returns
    -------
    DictConfig
        New DictConfig object with all environment variable references
        substituted throughout the structure. Original structure is preserved.
        
    Raises
    ------
    ValueError
        If the configuration is not a dictionary structure after processing
        
    Notes
    -----
    The function:
    1. Converts OmegaConf to regular dict to avoid interpolation conflicts
    2. Recursively processes all nested structures via _process_dict_env_substitution
    3. Converts back to OmegaConf DictConfig for type safety
    4. Preserves all non-string values unchanged
    
    This approach ensures environment variable substitution works correctly
    with OmegaConf's interpolation system without conflicts.
    
    Examples
    --------
    Process simple configuration:
        >>> from omegaconf import OmegaConf
        >>> cfg = OmegaConf.create({
        ...     'data_path': '${HOME}/data',
        ...     'nested': {'workspace': '${WORKSPACE:-/tmp/work}'}
        ... })
        >>> result = process_config_env_substitution(cfg)
        >>> print(result.data_path)  # Assuming HOME=/home/user
        '/home/user/data'
        
    Process configuration with lists:
        >>> cfg = OmegaConf.create({
        ...     'paths': ['${HOME}/bin', '${CUSTOM_PATH:-/usr/local/bin}']
        ... })
        >>> result = process_config_env_substitution(cfg)
        >>> print(result.paths[0])  # Assuming HOME=/home/user
        '/home/user/bin'
    """
    # Convert to regular dict to avoid OmegaConf interpolation issues
    raw_dict = oc.OmegaConf.to_container(cfg, resolve=False)
    processed_dict = _process_dict_env_substitution(raw_dict)
    result = oc.OmegaConf.create(processed_dict)
    
    # Ensure we return a DictConfig
    if isinstance(result, oc.DictConfig):
        return result
    else:
        raise ValueError("Configuration must be a dictionary structure")

def _process_dict_env_substitution(data: Any) -> Any:
    """
    Recursively process dictionary/list structure for environment variable substitution.
    
    Internal helper function that handles the recursive traversal of nested
    data structures, applying environment variable substitution to string
    values while preserving the overall structure and non-string values.
    
    Parameters
    ----------
    data : dict, list, str, or any
        Data structure to process. Can be:
        - dict: Recursively processes all values
        - list: Recursively processes all items
        - str: Applies environment variable substitution
        - other: Returned unchanged
        
    Returns
    -------
    dict, list, str, or any
        Processed data structure with same type as input but with all
        string values having environment variables substituted.
        
    Notes
    -----
    This is an internal helper function used by process_config_env_substitution.
    It maintains the exact structure of the input data while only modifying
    string values through substitute_env_vars().
    
    The recursion handles arbitrarily nested structures including:
    - Nested dictionaries with multiple levels
    - Lists containing dictionaries
    - Dictionaries containing lists
    - Mixed primitive types (int, bool, float, None)
    
    Examples
    --------
    Process nested dictionary:
        >>> data = {
        ...     'config': {
        ...         'path': '${HOME}/config',
        ...         'items': ['${ITEM1:-default1}', '${ITEM2:-default2}']
        ...     }
        ... }
        >>> result = _process_dict_env_substitution(data)
        
    Process mixed types:
        >>> data = {'string': '${HOME}', 'number': 42, 'bool': True}
        >>> result = _process_dict_env_substitution(data)
        >>> # Only 'string' value is processed, others unchanged
    """
    if isinstance(data, dict):
        return {key: _process_dict_env_substitution(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_process_dict_env_substitution(item) for item in data]
    elif isinstance(data, str):
        return substitute_env_vars(data)
    else:
        return data

def generate_public_key_from_private(private_key_text: str) -> str:
    """
    Generate SSH public key from private key content.
    
    Uses ssh-keygen to derive the corresponding public key from a private key.
    This is essential for SSH key management when only private keys are provided
    and public keys need to be generated for container configuration.
    
    Parameters
    ----------
    private_key_text : str
        SSH private key content in OpenSSH or PEM format. Supports RSA,
        ECDSA, Ed25519, and DSA key types.
        
    Returns
    -------
    str
        SSH public key in OpenSSH format (e.g., "ssh-rsa AAAAB3... user@host")
        
    Raises
    ------
    ValueError
        If ssh-keygen fails to process the private key or if the private
        key format is invalid
    ValueError
        If ssh-keygen command is not found on the system
        
    Notes
    -----
    This function:
    1. Creates a temporary file with secure permissions (0o600)
    2. Writes the private key content to the temporary file
    3. Executes ssh-keygen -y -f <tempfile> to extract the public key
    4. Cleans up the temporary file regardless of success/failure
    
    The function requires ssh-keygen to be available in the system PATH,
    which is standard on most Unix-like systems and available in Windows
    through OpenSSH or WSL.
    
    Examples
    --------
    Generate public key from RSA private key:
        >>> private_key = "-----BEGIN OPENSSH PRIVATE KEY-----\n..."
        >>> public_key = generate_public_key_from_private(private_key)
        >>> print(public_key)
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB... user@hostname'
        
    Generate public key from Ed25519 private key:
        >>> private_key = "-----BEGIN OPENSSH PRIVATE KEY-----\n..."
        >>> public_key = generate_public_key_from_private(private_key)
        >>> print(public_key)
        'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@hostname'
    """
    import tempfile
    import subprocess
    import os
    
    # Create temporary file for the private key
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_privkey') as temp_file:
        temp_file.write(private_key_text.strip())
        temp_file_path = temp_file.name
    
    try:
        # Set proper permissions for private key file
        os.chmod(temp_file_path, 0o600)
        
        # Generate public key using ssh-keygen
        result = subprocess.run(
            ['ssh-keygen', '-y', '-f', temp_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout.strip()
        
    except subprocess.CalledProcessError as e:
        raise ValueError(f'Failed to generate public key from private key: {e.stderr}')
    except FileNotFoundError:
        raise ValueError('ssh-keygen command not found. Please ensure OpenSSH is installed.')
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def detect_ssh_key_type(private_key_text: str) -> str:
    """
    Detect SSH key algorithm type from private key content.
    
    Analyzes private key headers and content to determine the cryptographic
    algorithm used. This is essential for proper SSH key file naming and
    container configuration setup.
    
    Parameters
    ----------
    private_key_text : str
        SSH private key content in either OpenSSH or traditional PEM format
        
    Returns
    -------
    str
        Detected key type: 'rsa', 'ed25519', 'ecdsa', or 'dsa'.
        Returns 'rsa' as default fallback if type cannot be determined.
        
    Notes
    -----
    Detection methods in priority order:
    1. OpenSSH format: Generates public key and detects from public key prefix
    2. Traditional PEM format: Analyzes private key headers
    3. Fallback: Returns 'rsa' as most common type
    
    Supported formats:
    - OpenSSH: "-----BEGIN OPENSSH PRIVATE KEY-----"
    - RSA PEM: "-----BEGIN RSA PRIVATE KEY-----"
    - ECDSA PEM: "-----BEGIN EC PRIVATE KEY-----"
    - DSA PEM: "-----BEGIN DSA PRIVATE KEY-----"
    
    For OpenSSH format, the function temporarily generates the public key
    to determine the algorithm type, as OpenSSH private keys don't contain
    algorithm indicators in their headers.
    
    Examples
    --------
    Detect RSA key:
        >>> rsa_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
        >>> detect_ssh_key_type(rsa_key)
        'rsa'
        
    Detect Ed25519 key:
        >>> ed25519_key = "-----BEGIN OPENSSH PRIVATE KEY-----\n..."
        >>> detect_ssh_key_type(ed25519_key)  # Generates public key for detection
        'ed25519'
        
    Detect ECDSA key:
        >>> ecdsa_key = "-----BEGIN EC PRIVATE KEY-----\n..."
        >>> detect_ssh_key_type(ecdsa_key)
        'ecdsa'
    """
    key_text = private_key_text.strip()
    
    # Check OpenSSH format header
    if '-----BEGIN OPENSSH PRIVATE KEY-----' in key_text:
        # For OpenSSH format, we need to decode the key or use ssh-keygen
        # For simplicity, we'll generate the public key and detect from there
        try:
            public_key = generate_public_key_from_private(private_key_text)
            if public_key.startswith('ssh-rsa'):
                return 'rsa'
            elif public_key.startswith('ssh-ed25519'):
                return 'ed25519'
            elif public_key.startswith('ecdsa-sha2-'):
                return 'ecdsa'
            elif public_key.startswith('ssh-dss'):
                return 'dsa'
        except:
            pass
    
    # Check traditional PEM format headers
    if '-----BEGIN RSA PRIVATE KEY-----' in key_text:
        return 'rsa'
    elif '-----BEGIN EC PRIVATE KEY-----' in key_text:
        return 'ecdsa'
    elif '-----BEGIN DSA PRIVATE KEY-----' in key_text:
        return 'dsa'
    
    # Default fallback
    return 'rsa'

def validate_ssh_public_key(public_key_text: str) -> bool:
    """
    Validate SSH public key format using regex pattern matching.
    
    Checks if the provided string conforms to standard SSH public key format
    with proper algorithm prefix and base64-encoded key data. This validation
    ensures public keys can be safely used in SSH configurations.
    
    Parameters
    ----------
    public_key_text : str
        SSH public key content to validate
        
    Returns
    -------
    bool
        True if the public key format is valid, False otherwise
        
    Notes
    -----
    Validates against standard SSH public key format:
    <algorithm> <base64-data> [comment]
    
    Supported algorithms:
    - ssh-rsa: RSA keys
    - ssh-dss: DSA keys (legacy)
    - ssh-ed25519: Ed25519 keys
    - ecdsa-sha2-nistp256: ECDSA P-256 keys
    - ecdsa-sha2-nistp384: ECDSA P-384 keys
    - ecdsa-sha2-nistp521: ECDSA P-521 keys
    
    The regex pattern ensures:
    1. Valid algorithm prefix
    2. Base64-encoded key data (A-Za-z0-9+/=)
    3. Optional comment field
    4. Proper whitespace separation
    
    Examples
    --------
    Valid RSA public key:
        >>> key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB... user@host"
        >>> validate_ssh_public_key(key)
        True
        
    Valid Ed25519 public key without comment:
        >>> key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI..."
        >>> validate_ssh_public_key(key)
        True
        
    Invalid format:
        >>> validate_ssh_public_key("not-a-valid-key")
        False
        
    Empty or malformed:
        >>> validate_ssh_public_key("")
        False
    """
    import re
    
    key_text = public_key_text.strip()
    
    # SSH public key should start with algorithm name and contain base64 data
    ssh_key_pattern = r'^(ssh-rsa|ssh-dss|ssh-ed25519|ecdsa-sha2-nistp256|ecdsa-sha2-nistp384|ecdsa-sha2-nistp521)\s+[A-Za-z0-9+/]+=*\s*.*$'
    
    return bool(re.match(ssh_key_pattern, key_text))

def validate_ssh_private_key(private_key_text: str) -> bool:
    """
    Validate SSH private key format by checking standard headers and footers.
    
    Verifies that the provided string contains properly formatted SSH private
    key content with valid PEM-style headers. This validation ensures private
    keys can be safely processed by SSH tools and container configurations.
    
    Parameters
    ----------
    private_key_text : str
        SSH private key content to validate
        
    Returns
    -------
    bool
        True if the private key format is valid, False otherwise
        
    Notes
    -----
    Validates both modern and traditional private key formats:
    
    Modern OpenSSH format:
    - Header: "-----BEGIN OPENSSH PRIVATE KEY-----"
    - Footer: "-----END OPENSSH PRIVATE KEY-----"
    
    Traditional PEM formats:
    - RSA: "-----BEGIN RSA PRIVATE KEY-----"
    - DSA: "-----BEGIN DSA PRIVATE KEY-----"
    - ECDSA: "-----BEGIN EC PRIVATE KEY-----"
    - PKCS#8: "-----BEGIN PRIVATE KEY-----"
    
    The function checks for proper header presence and assumes the key
    structure is valid if headers match. It does not perform cryptographic
    validation of the key content itself.
    
    Examples
    --------
    Valid OpenSSH private key:
        >>> key = "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAA..."
        >>> validate_ssh_private_key(key)
        True
        
    Valid RSA private key:
        >>> key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA..."
        >>> validate_ssh_private_key(key)
        True
        
    Invalid format:
        >>> validate_ssh_private_key("not-a-private-key")
        False
        
    Empty input:
        >>> validate_ssh_private_key("")
        False
    """
    key_text = private_key_text.strip()
    
    # Check for OpenSSH private key format
    if key_text.startswith('-----BEGIN OPENSSH PRIVATE KEY-----') and key_text.endswith('-----END OPENSSH PRIVATE KEY-----'):
        return True
    
    # Check for traditional private key formats
    traditional_headers = [
        '-----BEGIN RSA PRIVATE KEY-----',
        '-----BEGIN DSA PRIVATE KEY-----',
        '-----BEGIN EC PRIVATE KEY-----',
        '-----BEGIN PRIVATE KEY-----'
    ]
    
    for header in traditional_headers:
        if key_text.startswith(header):
            return True
    
    return False

def write_ssh_key_to_temp_file(key_content: str, key_type: str, user_name: str, project_dir: str, is_public: bool = True) -> str:
    """
    Write SSH key content to temporary file with proper permissions.
    
    Creates a temporary SSH key file in the project's generated directory
    structure with appropriate file permissions for secure key handling.
    This is used during Docker container configuration to make SSH keys
    available for mounting.
    
    Parameters
    ----------
    key_content : str
        SSH key content (public or private key text)
    key_type : str
        SSH key algorithm type ('rsa', 'ed25519', 'ecdsa', 'dsa')
    user_name : str
        Username for file naming to avoid conflicts between multiple users
    project_dir : str
        Project directory path for creating the generated subdirectory
    is_public : bool, default True
        True for public key files (.pub), False for private key files
        
    Returns
    -------
    str
        Relative path from installation directory to the created key file,
        using forward slashes for container compatibility
        
    Notes
    -----
    File structure created:
    - Directory: <project_dir>/installation/stage-1/generated/
    - Public key: temp-<user_name>-pubkey.pub (permissions: 0o644)
    - Private key: temp-<user_name>-privkey (permissions: 0o600)
    
    The function:
    1. Creates the generated directory if it doesn't exist
    2. Writes key content with proper line endings
    3. Sets appropriate file permissions (644 for public, 600 for private)
    4. Returns path relative to installation directory for container mounting
    
    File permissions follow SSH security best practices:
    - Public keys (0o644): Readable by owner/group/others
    - Private keys (0o600): Readable/writable by owner only
    
    Examples
    --------
    Create public key file:
        >>> public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB..."
        >>> path = write_ssh_key_to_temp_file(
        ...     public_key, 'rsa', 'admin', '/project', is_public=True
        ... )
        >>> print(path)
        'stage-1/generated/temp-admin-pubkey.pub'
        
    Create private key file:
        >>> private_key = "-----BEGIN OPENSSH PRIVATE KEY-----\n..."
        >>> path = write_ssh_key_to_temp_file(
        ...     private_key, 'rsa', 'admin', '/project', is_public=False
        ... )
        >>> print(path)
        'stage-1/generated/temp-admin-privkey'
    """
    import os
    
    # Create generated directory structure as specified in requirements
    generated_dir = os.path.join(project_dir, 'installation', 'stage-1', 'generated')
    os.makedirs(generated_dir, exist_ok=True)
    
    # Generate filename
    key_suffix = 'pubkey.pub' if is_public else 'privkey'
    filename = f'temp-{user_name}-{key_suffix}'
    
    # Full path for writing
    full_path = os.path.join(generated_dir, filename)
    
    # Write key content
    with open(full_path, 'w') as f:
        f.write(key_content.strip() + '\n')
    
    # Set appropriate permissions
    if is_public:
        os.chmod(full_path, 0o644)  # Read for owner/group/others
    else:
        os.chmod(full_path, 0o600)  # Read/write for owner only
    
    # Return relative path from installation directory for container mounting
    installation_dir = os.path.join(project_dir, 'installation')
    return os.path.relpath(full_path, installation_dir).replace('\\', '/')


def find_system_ssh_key(prefer_public: bool = True) -> str:
    """
    Discover system SSH keys using standard naming conventions and priority order.
    
    Searches the user's ~/.ssh directory for SSH keys following standard naming
    patterns with a defined priority order. This enables automatic SSH key
    discovery for container configuration without manual key specification.
    
    Parameters
    ----------
    prefer_public : bool, default True
        Preference for key type discovery:
        - True: Look for .pub files first, fallback to private keys
        - False: Look for private keys first, fallback to .pub files
        
    Returns
    -------
    str
        Absolute path to the discovered SSH key file
        
    Raises
    ------
    ValueError
        If ~/.ssh directory doesn't exist or no SSH keys found
        
    Notes
    -----
    Key discovery priority (in order):
    1. id_rsa / id_rsa.pub
    2. id_dsa / id_dsa.pub
    3. id_ecdsa / id_ecdsa.pub
    4. id_ed25519 / id_ed25519.pub
    
    The function checks for key existence in this order and returns the
    first found key based on the prefer_public parameter. This priority
    order reflects common SSH key usage patterns and compatibility.
    
    For each key name, the search pattern is:
    - If prefer_public=True: Check .pub file first, then private key
    - If prefer_public=False: Check private key first, then .pub file
    
    Examples
    --------
    Find public key (default behavior):
        >>> key_path = find_system_ssh_key()
        >>> print(key_path)
        '/home/user/.ssh/id_rsa.pub'
        
    Find private key preferentially:
        >>> key_path = find_system_ssh_key(prefer_public=False)
        >>> print(key_path)
        '/home/user/.ssh/id_rsa'
        
    Handle missing SSH directory:
        >>> find_system_ssh_key()  # When ~/.ssh doesn't exist
        ValueError: SSH directory not found: /home/user/.ssh
    """
    import os
    
    ssh_dir = os.path.expanduser('~/.ssh')
    if not os.path.exists(ssh_dir):
        raise ValueError(f'SSH directory not found: {ssh_dir}')
    
    # Priority order as specified in requirements
    key_priorities = ['id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519']
    
    for key_name in key_priorities:
        if prefer_public:
            # Look for public key first
            public_key = os.path.join(ssh_dir, f'{key_name}.pub')
            if os.path.exists(public_key):
                return public_key
                
            # Fallback to private key
            private_key = os.path.join(ssh_dir, key_name)
            if os.path.exists(private_key):
                return private_key
        else:
            # Look for private key first
            private_key = os.path.join(ssh_dir, key_name)
            if os.path.exists(private_key):
                return private_key
                
            # Fallback to public key
            public_key = os.path.join(ssh_dir, f'{key_name}.pub')
            if os.path.exists(public_key):
                return public_key
    
    raise ValueError(f'No SSH key found in {ssh_dir}. Looked for: {key_priorities}')


def resolve_ssh_key_path(key_path: str, prefer_public: bool = True) -> str:
    """
    Resolve SSH key path with support for absolute paths and auto-discovery.
    
    Handles various SSH key path specifications including absolute paths,
    relative paths, and the special '~' syntax for automatic system key
    discovery. This provides flexible SSH key configuration options.
    
    Parameters
    ----------
    key_path : str
        SSH key path specification in one of these formats:
        - '~': Auto-discover system SSH key
        - Absolute path: '/home/user/.ssh/id_rsa'
        - Relative path: 'keys/my_key.pub'
    prefer_public : bool, default True
        For '~' syntax auto-discovery, whether to prefer public keys
        over private keys in the search order
        
    Returns
    -------
    str
        Absolute path to the SSH key file
        
    Raises
    ------
    FileNotFoundError
        If absolute path specified but key file doesn't exist
    ValueError
        If '~' syntax used but no suitable SSH key found in system
        
    Notes
    -----
    Path resolution behavior:
    
    1. '~' syntax: Calls find_system_ssh_key() with prefer_public parameter
    2. Absolute paths: Validates file existence and returns as-is
    3. Relative paths: Returns unchanged for caller to handle
    
    The '~' syntax is particularly useful for configuration templates
    where users want automatic key discovery without hardcoding paths.
    
    Examples
    --------
    Auto-discover system key:
        >>> resolve_ssh_key_path('~')
        '/home/user/.ssh/id_rsa.pub'
        
    Validate absolute path:
        >>> resolve_ssh_key_path('/home/user/.ssh/custom_key')
        '/home/user/.ssh/custom_key'
        
    Handle relative path (returned unchanged):
        >>> resolve_ssh_key_path('keys/project.pub')
        'keys/project.pub'
        
    Handle missing absolute path:
        >>> resolve_ssh_key_path('/nonexistent/key')
        FileNotFoundError: SSH key file not found: /nonexistent/key
    """
    import os
    
    if key_path == '~':
        # Special syntax: find system SSH key
        return find_system_ssh_key(prefer_public=prefer_public)
    elif os.path.isabs(key_path):
        # Absolute path: validate existence
        if not os.path.exists(key_path):
            raise FileNotFoundError(f'SSH key file not found: {key_path}')
        return key_path
    else:
        # Relative path: return as-is (existing logic will handle)
        return key_path


def read_ssh_key_content(key_path: str) -> str:
    """
    Read SSH key content from file with proper error handling.
    
    Safely reads SSH key content from the specified file path with
    comprehensive error handling for common file access issues.
    Used throughout the SSH key management system for secure key loading.
    
    Parameters
    ----------
    key_path : str
        Absolute path to the SSH key file to read
        
    Returns
    -------
    str
        SSH key content as string with trailing whitespace stripped
        
    Raises
    ------
    FileNotFoundError
        If the specified key file doesn't exist at the given path
    PermissionError
        If the current user lacks read permissions for the key file
    RuntimeError
        If any other error occurs during file reading (I/O errors, etc.)
        
    Notes
    -----
    Security considerations:
    - Function validates file existence before attempting to read
    - Proper exception handling preserves security information
    - Content is stripped to remove trailing whitespace/newlines
    - No automatic permission changes (respects existing file security)
    
    This function is typically used after resolve_ssh_key_path() to
    load the actual key content for processing or validation.
    
    Examples
    --------
    Read existing SSH key:
        >>> content = read_ssh_key_content('/home/user/.ssh/id_rsa.pub')
        >>> print(content[:20])  # First 20 characters
        'ssh-rsa AAAAB3NzaC1y'
        
    Handle missing file:
        >>> read_ssh_key_content('/nonexistent/key')
        FileNotFoundError: SSH key file not found: /nonexistent/key
        
    Handle permission denied:
        >>> read_ssh_key_content('/root/.ssh/id_rsa')  # As non-root user
        PermissionError: Permission denied reading SSH key file: /root/.ssh/id_rsa
    """
    import os
    
    if not os.path.exists(key_path):
        raise FileNotFoundError(f'SSH key file not found: {key_path}')
    
    try:
        with open(key_path, 'r') as f:
                content = f.read()
        return content.strip()
    except PermissionError:
        raise PermissionError(f'Permission denied reading SSH key file: {key_path}')
    except Exception as e:
        raise RuntimeError(f'Error reading SSH key file {key_path}: {e}')