"""File utilities for the GUI."""

import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def ensure_dir_exists(path: str) -> bool:
    """Ensure directory exists, create if it doesn't."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def check_path_writable(path: str) -> bool:
    """Check if path is writable."""
    try:
        test_path = Path(path)
        if not test_path.exists():
            # Try to create parent directory
            test_path.parent.mkdir(parents=True, exist_ok=True)
            # Try to create a test file
            test_file = test_path / ".test_write"
            test_file.touch()
            test_file.unlink()
            return True
        else:
            # Directory exists, try to write a test file
            test_file = test_path / ".test_write"
            test_file.touch()
            test_file.unlink()
            return True
    except (OSError, PermissionError):
        return False


def save_user_config(config_dict: Dict[str, Any], file_path: str) -> bool:
    """Save configuration to user_config.yml file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        return True
    except (OSError, yaml.YAMLError):
        return False


def load_user_config(file_path: str) -> Optional[Dict[str, Any]]:
    """Load configuration from user_config.yml file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return None


def copy_file_to_project(src_path: str, project_dir: str, relative_path: str) -> bool:
    """Copy a file to the project directory."""
    try:
        src = Path(src_path)
        dst = Path(project_dir) / relative_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except (OSError, shutil.Error):
        return False


def get_ssh_key_from_system(key_type: str = "rsa") -> Optional[str]:
    """Get SSH public key from system default location."""
    try:
        home = Path.home()
        key_file = home / ".ssh" / f"id_{key_type}.pub"
        if key_file.exists():
            return key_file.read_text().strip()
        return None
    except (OSError, UnicodeDecodeError):
        return None


def validate_ssh_public_key(key_text: str) -> bool:
    """Validate SSH public key format."""
    if not key_text.strip():
        return False
    
    parts = key_text.strip().split()
    if len(parts) < 2:
        return False
    
    # Check if it starts with known key types
    valid_types = ['ssh-rsa', 'ssh-dss', 'ssh-ed25519', 'ecdsa-sha2-nistp256', 
                   'ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp521']
    return parts[0] in valid_types


def validate_port_mapping(port_str: str) -> bool:
    """Validate port mapping format (e.g., '8080:80' or '100-200:300-400')."""
    try:
        if ':' not in port_str:
            return False
        
        host_part, container_part = port_str.split(':', 1)
        
        # Check for port ranges
        if '-' in host_part and '-' in container_part:
            host_start, host_end = map(int, host_part.split('-'))
            container_start, container_end = map(int, container_part.split('-'))
            return (1 <= host_start <= host_end <= 65535 and 
                    1 <= container_start <= container_end <= 65535 and
                    (host_end - host_start) == (container_end - container_start))
        elif '-' not in host_part and '-' not in container_part:
            host_port = int(host_part)
            container_port = int(container_part)
            return 1 <= host_port <= 65535 and 1 <= container_port <= 65535
        else:
            return False
    except (ValueError, TypeError):
        return False


def validate_environment_var(env_str: str) -> bool:
    """Validate environment variable format (KEY=VALUE)."""
    if '=' not in env_str:
        return False
    
    key, value = env_str.split('=', 1)
    # Key should not be empty and should be valid identifier-like
    if not key or not key.replace('_', '').replace('-', '').isalnum():
        return False
    
    return True