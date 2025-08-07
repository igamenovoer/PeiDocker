"""
Docker image configuration for PeiDocker.
"""

from attrs import define, field
from typing import Optional


@define(kw_only=True)
class ImageConfig:
    """
    Docker image configuration for base and output image names.
    
    Specifies the Docker images used in PeiDocker's two-stage build process.
    The base image provides the foundation, while the output image is the
    result of the current stage's build process.
    
    Attributes
    ----------
    base : str, optional
        Base Docker image name (e.g., "ubuntu:24.04", "python:3.9-slim").
        Required for Stage-1 configurations. For Stage-2, defaults to
        the output image from Stage-1 if not specified.
    output : str, optional
        Name for the output image after this stage's build completes.
        Auto-generated if not specified (e.g., "project-name:stage-1").
        
    Examples
    --------
    Stage-1 configuration:
        >>> config = ImageConfig(base="ubuntu:24.04", output="my-app:stage-1")
        
    Stage-2 configuration (inherits from Stage-1):
        >>> config = ImageConfig(output="my-app:stage-2")
        
    Notes
    -----
    The base image should be publicly available or present in the local
    Docker registry. Output image names follow Docker naming conventions
    and can include registry prefixes and tags.
    """
    base: Optional[str] = field(default=None)
    output: Optional[str] = field(default=None)