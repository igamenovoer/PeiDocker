"""
Docker System Utilities for PeiDocker GUI.

This module provides utility functions for Docker system integration within
the PeiDocker GUI application. It handles Docker availability detection,
version checking, image existence verification, and system information
retrieval.

The utilities are designed to be robust against various Docker installation
states and provide graceful degradation when Docker is not available or
malfunctioning.

Functions
---------
check_docker_available : Check Docker availability and version
check_docker_images_exist : Verify local Docker image existence
get_docker_info : Retrieve comprehensive Docker system information

Notes
-----
All functions handle common Docker-related exceptions gracefully and use
appropriate timeouts to prevent GUI blocking. Failed operations return
safe default values rather than raising exceptions.
"""

import subprocess
import shutil
from typing import Optional, List, Tuple, Dict, Any, cast


def check_docker_available() -> Tuple[bool, Optional[str]]:
    """
    Check Docker availability and retrieve version information.
    
    Attempts to execute 'docker --version' to determine if Docker is
    installed, accessible, and functioning properly. This is used for
    system validation during application startup.
    
    Returns
    -------
    tuple[bool, str or None]
        A tuple containing:
        - bool: True if Docker is available and responsive, False otherwise
        - str or None: Docker version string if available, None if not accessible
        
    Notes
    -----
    The function handles the following scenarios gracefully:
    - Docker not installed (FileNotFoundError)
    - Docker installed but not running (subprocess errors)
    - Docker command timeout (5 second limit)
    - Permission issues accessing Docker
    
    The version string typically follows the format "Docker version X.X.X, build XXXXXXX"
    and is returned exactly as reported by the docker --version command.
    
    Examples
    --------
    >>> available, version = check_docker_available()
    >>> if available:
    ...     print(f"Docker is available: {version}")
    ... else:
    ...     print("Docker is not available")
    """
    try:
        result = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, None
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False, None


def check_docker_images_exist(image_names: List[str]) -> List[Tuple[str, bool]]:
    """
    Check if specified Docker images exist in the local Docker registry.
    
    Verifies the existence of Docker images locally by querying the Docker
    daemon. This is useful for determining whether images need to be built
    or pulled before container operations.
    
    Parameters
    ----------
    image_names : List[str]
        List of Docker image names to check. Names can include tags
        (e.g., "ubuntu:20.04") or use default "latest" tag.
        
    Returns
    -------
    List[Tuple[str, bool]]
        List of tuples where each tuple contains:
        - str: The image name as provided in the input
        - bool: True if the image exists locally, False otherwise
        
    Notes
    -----
    The function uses 'docker images -q <image_name>' to check for image
    existence. This command returns the image ID if found, or empty output
    if not found.
    
    Error handling:
    - If Docker is not available, all images are marked as non-existent
    - Network issues or Docker daemon problems result in False for affected images
    - Individual image check failures don't affect other images in the list
    - 10-second timeout per image prevents GUI blocking
    
    Examples
    --------
    >>> images = ["ubuntu:20.04", "python:3.9", "nonexistent:latest"]
    >>> results = check_docker_images_exist(images)
    >>> for name, exists in results:
    ...     print(f"{name}: {'Found' if exists else 'Not found'}")
    """
    results = []
    for image in image_names:
        try:
            result = subprocess.run(
                ["docker", "images", "-q", image],
                capture_output=True,
                text=True,
                timeout=10
            )
            exists = bool(result.stdout.strip())
            results.append((image, exists))
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            results.append((image, False))
    
    return results


def get_docker_info() -> Optional[Dict[Any, Any]]:
    """
    Retrieve comprehensive Docker system information.
    
    Executes 'docker info --format "{{json .}}"' to obtain detailed
    information about the Docker installation, daemon configuration,
    and system resources. This information can be used for advanced
    system validation and troubleshooting.
    
    Returns
    -------
    Dict[Any, Any] or None
        Dictionary containing Docker system information if successful,
        None if Docker is not available or the command fails.
        
    Notes
    -----
    The returned dictionary typically includes:
    - Docker version and build information
    - Storage driver details
    - Container and image counts
    - Registry configuration
    - System resources (CPU, memory)
    - Plugin information
    - Security settings
    
    Error handling:
    - Returns None if Docker is not installed or not running
    - JSON parsing errors result in None return value
    - 10-second timeout prevents GUI blocking
    - All exceptions are caught and handled gracefully
    
    Examples
    --------
    >>> info = get_docker_info()
    >>> if info:
    ...     print(f"Docker version: {info.get('ServerVersion', 'Unknown')}")
    ...     print(f"Storage driver: {info.get('Driver', 'Unknown')}")
    ... else:
    ...     print("Could not retrieve Docker information")
    """
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            import json
                return cast(Dict[Any, Any], json.loads(result.stdout))
        return None
    except Exception:
        return None