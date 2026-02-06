"""
Utility functions for ui_state_bridge module.
"""

from typing import Dict, List, Any, Optional


def clean_config_dict(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Clean up the configuration dictionary by removing None values and empty structures.
    
    This ensures the YAML output is clean and doesn't contain empty structures like
    'proxy: {}' or port mappings like '- ':''.
    """
    def clean_value(value: Any) -> Any:
        """Recursively clean a value."""
        if value is None:
            return None
        elif isinstance(value, dict):
            cleaned_dict: Dict[str, Any] = {}
            for k, v in value.items():
                cleaned_v = clean_value(v)
                # Skip None values and empty dicts (except for special keys like _inline_scripts)
                if cleaned_v is not None and (not isinstance(cleaned_v, dict) or cleaned_v or k.startswith('_')):
                    cleaned_dict[k] = cleaned_v
            return cleaned_dict if cleaned_dict else None
        elif isinstance(value, list):
            cleaned_list: List[Any] = []
            for item in value:
                cleaned_item = clean_value(item)
                # Skip None values and empty strings in lists
                if cleaned_item is not None and cleaned_item != '':
                    # Special handling for port mappings - skip invalid ones
                    if isinstance(cleaned_item, str) and ':' in cleaned_item:
                        parts = cleaned_item.split(':')
                        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                            cleaned_list.append(cleaned_item)
                    else:
                        cleaned_list.append(cleaned_item)
            return cleaned_list if cleaned_list else None
        else:
            return value
    
    result = {}
    for key, value in config_dict.items():
        cleaned_value = clean_value(value)
        if cleaned_value is not None:
            result[key] = cleaned_value
    
    return result


def extract_project_info(ui_project: Any) -> Dict[str, Any]:
    """Extract project information for adapter.
    
    Args:
        ui_project: ProjectUI object
        
    Returns:
        Dictionary with project information
    """
    return {
        'project_name': ui_project.project_name or "untitled",
        'project_directory': ui_project.project_directory or "",
        'base_image': ui_project.base_image,
        'image_output_name': ui_project.image_output_name,
        'template': ui_project.template
    }


def parse_proxy_url(proxy_url: str) -> tuple[str, int, bool]:
    """Parse proxy URL to extract address, port, and https flag.
    
    Args:
        proxy_url: Proxy URL (e.g., 'http://proxy.company.com:8080')
        
    Returns:
        Tuple of (address, port, use_https)
    """
    if '://' in proxy_url:
        scheme, rest = proxy_url.split('://', 1)
        use_https = scheme == 'https'
    else:
        rest = proxy_url
        use_https = False
    
    if ':' in rest:
        address, port_str = rest.rsplit(':', 1)
        try:
            port = int(port_str)
        except ValueError:
            port = 8080
    else:
        address = rest
        port = 8080
    
    return address, port, use_https


def build_proxy_url(address: str, port: int, use_https: bool = False) -> str:
    """Build proxy URL from components.
    
    Args:
        address: Proxy address
        port: Proxy port
        use_https: Whether to use HTTPS
        
    Returns:
        Formatted proxy URL
    """
    scheme = 'https' if use_https else 'http'
    return f"{scheme}://{address}:{port}"