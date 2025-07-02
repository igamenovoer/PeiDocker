# utility methods
import omegaconf as oc
from omegaconf.omegaconf import DictConfig
import os
import re

def remove_null_keys(cfg: DictConfig) -> DictConfig:
    ''' remove all keys with value None in place
    '''
    shadow = cfg.copy()
    for k, v in shadow.items():
        if v is None:
            print(f'removing key {k}')
            cfg.pop(k)
        elif isinstance(v, DictConfig):
            remove_null_keys(cfg.get(k))
    return cfg

def retain_ssh_users(ssh_config: DictConfig, user: list[str]):
    ''' retain only the ssh user specified
    
    parameters
    -------------
    ssh_config : DictConfig
        the ssh configuration, in the stage_?.ssh section
    user : list[str]
        the list of users to retain
    '''
    assert isinstance(user, list), 'user must be a list'
    
    ssh_users_to_remove = set(ssh_config.users.keys())-set(user)
    for u in ssh_users_to_remove:
        ssh_config.users.pop(u)

def substitute_env_vars(value: str) -> str:
    """
    Substitute environment variables in a string with fallback syntax.
    Supports both ${VAR} and ${VAR:-default} syntax.
    
    Examples:
        "${HOME}" -> "/home/user" (if HOME env var exists)
        "${UNDEFINED_VAR:-/default/path}" -> "/default/path" (if UNDEFINED_VAR doesn't exist)
        "${SHARED_HOST_PATH:-/mnt/d/docker-space/workspace/minimal-gpu}" -> uses env var or default
    
    Args:
        value: String that may contain environment variable references
        
    Returns:
        String with environment variables substituted
    """
    if not isinstance(value, str):
        return value
    
    # Pattern to match ${VAR} or ${VAR:-default}
    pattern = r'\$\{([^}]+)\}'
    
    def replacer(match):
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
    Recursively process a configuration object to substitute environment variables.
    
    Args:
        cfg: OmegaConf DictConfig object
        
    Returns:
        DictConfig with environment variables substituted
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

def _process_dict_env_substitution(data):
    """
    Recursively process a dictionary/list structure to substitute environment variables.
    
    Args:
        data: Dictionary, list, or primitive value
        
    Returns:
        Processed data with environment variables substituted
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
    Generate SSH public key from private key text.
    
    Args:
        private_key_text: SSH private key in OpenSSH or PEM format
        
    Returns:
        SSH public key in OpenSSH format
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
    Detect SSH key type from private key text.
    
    Args:
        private_key_text: SSH private key content
        
    Returns:
        Key type: 'rsa', 'ed25519', 'ecdsa', or 'dsa'
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
    Validate SSH public key format.
    
    Args:
        public_key_text: SSH public key content
        
    Returns:
        True if valid, False otherwise
    """
    import re
    
    key_text = public_key_text.strip()
    
    # SSH public key should start with algorithm name and contain base64 data
    ssh_key_pattern = r'^(ssh-rsa|ssh-dss|ssh-ed25519|ecdsa-sha2-nistp256|ecdsa-sha2-nistp384|ecdsa-sha2-nistp521)\s+[A-Za-z0-9+/]+=*\s*.*$'
    
    return bool(re.match(ssh_key_pattern, key_text))

def validate_ssh_private_key(private_key_text: str) -> bool:
    """
    Validate SSH private key format.
    
    Args:
        private_key_text: SSH private key content
        
    Returns:
        True if valid, False otherwise
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
    Write SSH key content to temporary file and return relative path.
    
    Args:
        key_content: SSH key content
        key_type: Type of key ('rsa', 'ed25519', etc.)
        user_name: Username for file naming
        project_dir: Project directory path
        is_public: True for public key, False for private key
        
    Returns:
        Relative path to the created key file (relative to project directory)
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