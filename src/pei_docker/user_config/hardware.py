"""
Hardware configuration classes for PeiDocker.

This module provides hardware device configuration for Docker containers,
primarily for GPU support in machine learning and graphics applications.
"""

from attrs import define, field


@define(kw_only=True)
class DeviceConfig:
    """
    Hardware device configuration for container access.
    
    Specifies hardware device access requirements for Docker containers,
    primarily for GPU support in machine learning and graphics applications.
    Controls Docker runtime device forwarding and driver access.
    
    Attributes
    ----------
    type : str, default "cpu"
        Type of hardware device access required. Valid values:
        - "cpu": CPU-only access (default, no special hardware requirements)
        - "gpu": GPU access with NVIDIA Docker runtime support
        
    Examples
    --------
    CPU-only configuration (default):
        >>> device = DeviceConfig(type="cpu")
        
    GPU-enabled configuration:
        >>> device = DeviceConfig(type="gpu")
        
    Notes
    -----
    GPU support requirements:
    - NVIDIA GPU hardware installed on host
    - NVIDIA Docker runtime (nvidia-docker2) installed
    - Compatible GPU drivers for the base image
    - CUDA-compatible base image (e.g., nvidia/cuda:*)
    
    GPU configuration automatically:
    - Forwards GPU devices to the container
    - Sets appropriate Docker runtime flags
    - Configures CUDA environment variables
    - Enables GPU-accelerated applications
    
    No automatic GPU detection is performed; users must explicitly
    request GPU access when needed.
    """
    type: str = field(default='cpu')