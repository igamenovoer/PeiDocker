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
    return oc.OmegaConf.create(processed_dict)

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