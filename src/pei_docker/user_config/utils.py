"""
Utility functions for PeiDocker configuration processing.

This module provides helper functions for converting between different
configuration formats, particularly for port mappings and environment variables.
"""

from typing import Dict, List, Optional


def port_mapping_str_to_dict(port_mapping: List[str]) -> Dict[int, int]:
    """
    Convert port mapping strings to dictionary format.
    
    Transforms a list of Docker-style port mapping strings into a dictionary
    mapping host ports to container ports. Supports both single port mappings
    and port ranges.
    
    Parameters
    ----------
    port_mapping : List[str]
        List of port mapping strings in formats:
        - Single: "8080:80" (host port 8080 maps to container port 80)
        - Range: "8000-8010:9000-9010" (11 ports mapped sequentially)
        
    Returns
    -------
    Dict[int, int]
        Dictionary mapping host port numbers to container port numbers.
        
    Raises
    ------
    ValueError
        If port ranges have different lengths between host and container sides.
        
    Examples
    --------
    Single port mappings:
        >>> port_mapping_str_to_dict(["8080:80", "3000:3000"])
        {8080: 80, 3000: 3000}
        
    Port range mapping:
        >>> port_mapping_str_to_dict(["8000-8002:9000-9002"])
        {8000: 9000, 8001: 9001, 8002: 9002}
        
    Notes
    -----
    Port ranges must have equal lengths on both host and container sides.
    The range format uses inclusive endpoints (8000-8002 includes 8000, 8001, 8002).
    """
    output: Dict[int, int] = {}
    
    for ent in port_mapping:
        # split the string into host and container port
        host_port, container_port = ent.split(':')
        
        # are we mapping a range of ports? in the format 'host_start-host_end:container_start-container_end'
        if '-' in host_port:
            # find the range of host ports
            host_port_start_str, host_port_end_str = host_port.split('-')
            host_port_start: int = int(host_port_start_str)
            host_port_end: int = int(host_port_end_str)
            
            # find the range of container ports
            container_port_start_str, container_port_end_str = container_port.split('-')
            container_port_start: int = int(container_port_start_str)
            container_port_end: int = int(container_port_end_str)
            
            # check if the ranges are of the same length
            if host_port_end - host_port_start != container_port_end - container_port_start:
                raise ValueError('Port ranges must be of the same length')
            
            # add the port mappings to the output
            for u, v in zip(range(host_port_start, host_port_end + 1), range(container_port_start, container_port_end + 1)):
                output[u] = v
        else:
            output[int(host_port)] = int(container_port)
    return output


def port_mapping_dict_to_str(port_mapping: Dict[int, int]) -> List[str]:
    """
    Convert port mapping dictionary to string format.
    
    Transforms a dictionary of host-to-container port mappings into Docker-style
    port mapping strings. Automatically detects and optimizes consecutive port
    ranges into range notation for cleaner configuration.
    
    Parameters
    ----------
    port_mapping : Dict[int, int]
        Dictionary mapping host port numbers to container port numbers.
        
    Returns
    -------
    List[str]
        List of port mapping strings in formats:
        - Single: "8080:80" for individual port mappings
        - Range: "8000-8010:9000-9010" for consecutive port sequences
        
    Examples
    --------
    Individual port mappings:
        >>> port_mapping_dict_to_str({8080: 80, 3000: 3000})
        ['8080:80', '3000:3000']
        
    Consecutive ports optimized to range:
        >>> port_mapping_dict_to_str({8000: 9000, 8001: 9001, 8002: 9002})
        ['8000-8002:9000-9002']
        
    Mixed individual and range mappings:
        >>> port_mapping_dict_to_str({8080: 80, 9000: 9000, 9001: 9001})
        ['8080:80', '9000-9001:9000-9001']
        
    Notes
    -----
    The function automatically detects consecutive port sequences and converts
    them to range notation for more compact representation. Port mappings are
    sorted by host port number for consistent output.
    """
    
    output: List[str] = []
    
    if len(port_mapping) == 0:
        return output
    
    port_from_range_start: int = -1
    port_to_range_start: int = -1
    port_from_prev: int = -1
    port_to_prev: int = -1
    
    for port_from, port_to in sorted(port_mapping.items()):
        # first port, initialize the range
        if port_from_prev == -1:
            port_from_range_start = port_from
            port_to_range_start = port_to
        elif port_from_prev == port_from - 1 and port_to_prev == port_to - 1:
            # we are in a range, no need to do anything
            pass
        else:
            # the previous range has ended, add it to the output
            if port_from_range_start == port_from_prev:  # single port
                port_mapping_entry = f'{port_from_range_start}:{port_to_range_start}'
                output.append(port_mapping_entry)
            else:
                port_mapping_entry = f'{port_from_range_start}-{port_from_prev}:{port_to_range_start}-{port_to_prev}'
                output.append(port_mapping_entry)
            
            # start a new range
            port_from_range_start = port_from
            port_to_range_start = port_to
            
        # update prev
        port_from_prev = port_from
        port_to_prev = port_to
        
    # output the last range
    if port_from_range_start == port_from_prev:  # single port
        port_mapping_entry = f'{port_from_range_start}:{port_to_range_start}'
        output.append(port_mapping_entry)
    else:
        port_mapping_entry = f'{port_from_range_start}-{port_from_prev}:{port_to_range_start}-{port_to_prev}'
        output.append(port_mapping_entry)
            
    return output


def env_str_to_dict(env_list: List[str]) -> Dict[str, str]:
    """
    Convert environment variable strings to dictionary format.
    
    Transforms a list of environment variable strings in KEY=VALUE format
    into a dictionary for easier programmatic access and manipulation.
    
    Parameters
    ----------
    env_list : List[str]
        List of environment variable strings in "KEY=VALUE" format.
        
    Returns
    -------
    Dict[str, str]
        Dictionary mapping environment variable names to their values.
        
    Examples
    --------
    Basic environment variables:
        >>> env_str_to_dict(["NODE_ENV=production", "PORT=3000"])
        {'NODE_ENV': 'production', 'PORT': '3000'}
        
    Variables with complex values:
        >>> env_str_to_dict(["PATH=/usr/bin:/bin", "DB_URL=postgres://user:pass@host/db"])
        {'PATH': '/usr/bin:/bin', 'DB_URL': 'postgres://user:pass@host/db'}
        
    Notes
    -----
    Each string is split on the first '=' character, so values can contain
    additional '=' characters without issues. This is compatible with standard
    Unix environment variable format.
    """
    return {x.split('=')[0]: x.split('=')[1] for x in env_list}


def env_dict_to_str(env_dict: Dict[str, str]) -> List[str]:
    """
    Convert environment variable dictionary to string format.
    
    Transforms a dictionary of environment variables into a list of KEY=VALUE
    strings suitable for Docker Compose environment sections or shell export.
    
    Parameters
    ----------
    env_dict : Dict[str, str]
        Dictionary mapping environment variable names to their values.
        
    Returns
    -------
    List[str]
        List of environment variable strings in "KEY=VALUE" format.
        
    Examples
    --------
    Basic environment variables:
        >>> env_dict_to_str({'NODE_ENV': 'production', 'PORT': '3000'})
        ['NODE_ENV=production', 'PORT=3000']
        
    Variables with complex values:
        >>> env_dict_to_str({'PATH': '/usr/bin:/bin', 'DB_URL': 'postgres://user:pass@host/db'})
        ['PATH=/usr/bin:/bin', 'DB_URL=postgres://user:pass@host/db']
        
    Notes
    -----
    The output format is compatible with Docker Compose environment sections
    and can be used directly in shell scripts or configuration files.
    Order is not guaranteed as it depends on dictionary iteration.
    """
    return [f'{k}={v}' for k, v in env_dict.items()]


def env_converter(x: Optional[List[str] | Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    Convert environment variables from list format to dictionary format.
    
    Provides automatic conversion for environment variable specifications,
    allowing users to provide either list or dictionary format in configuration
    files while ensuring consistent internal representation.
    
    Parameters
    ----------
    x : List[str] or Dict[str, str] or None
        Environment variables in list format ("KEY=VALUE") or dictionary format,
        or None for no environment variables.
        
    Returns
    -------
    Dict[str, str] or None
        Environment variables in dictionary format, or None if input was None.
        
    Examples
    --------
    List format conversion:
        >>> env_converter(["NODE_ENV=production", "PORT=3000"])
        {'NODE_ENV': 'production', 'PORT': '3000'}
        
    Dictionary format passthrough:
        >>> env_converter({'NODE_ENV': 'production', 'PORT': '3000'})
        {'NODE_ENV': 'production', 'PORT': '3000'}
        
    None passthrough:
        >>> env_converter(None)
        None
        
    Notes
    -----
    This function is used as an attrs converter to normalize environment
    variable input formats during object construction.
    """
    if x is None:
        return None
    if isinstance(x, list):
        return env_str_to_dict(x)
    else:
        return x