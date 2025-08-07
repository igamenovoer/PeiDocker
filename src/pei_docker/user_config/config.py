"""
Root configuration for PeiDocker.

This module provides the UserConfig class that represents the complete
user configuration for a PeiDocker project.
"""

from attrs import define, field
from typing import Optional

from pei_docker.user_config.stage import StageConfig


@define(kw_only=True)
class UserConfig:
    """
    Root configuration object for PeiDocker projects.
    
    Represents the complete user configuration for a PeiDocker project,
    containing both Stage-1 (system setup) and Stage-2 (application)
    configurations. This is the top-level object parsed from user_config.yml.
    
    Attributes
    ----------
    stage_1 : StageConfig, optional
        Stage-1 configuration for system-level setup including base image,
        SSH server, proxy settings, APT repositories, and system packages.
        At least one stage must be configured for a valid PeiDocker project.
    stage_2 : StageConfig, optional
        Stage-2 configuration for application-level setup including custom
        mounts, application-specific scripts, and final image configuration.
        Optional; if omitted, only Stage-1 will be built.
        
    Examples
    --------
    Single-stage configuration (Stage-1 only):
        >>> config = UserConfig(
        ...     stage_1=StageConfig(
        ...         image=ImageConfig(base="ubuntu:24.04", output="my-app:latest"),
        ...         ssh=SSHConfig(users={"user": SSHUserConfig(password="password")})
        ...     )
        ... )
        
    Two-stage configuration:
        >>> config = UserConfig(
        ...     stage_1=StageConfig(
        ...         image=ImageConfig(base="ubuntu:24.04", output="my-app:stage-1"),
        ...         ssh=SSHConfig(users={"admin": SSHUserConfig(password="admin123")})
        ...     ),
        ...     stage_2=StageConfig(
        ...         image=ImageConfig(output="my-app:stage-2"),
        ...         storage={"data": StorageOption(type="host", host_path="/data")}
        ...     )
        ... )
        
    Notes
    -----
    Two-stage architecture benefits:
    - Stage-1: System foundation with consistent base across projects
    - Stage-2: Application-specific customization building on Stage-1
    - Better Docker layer caching and build optimization
    - Separation of system vs application concerns
    
    The configuration is processed by PeiConfigProcessor to generate:
    - Docker Compose files for both stages
    - Custom script files for lifecycle hooks
    - Environment configuration files
    - Container networking and storage setup
    
    If only stage_1 is specified, the system will build and run a single-stage
    container. If both stages are specified, stage_2 uses stage_1's output
    image as its base image automatically.
    """
    stage_1: Optional[StageConfig] = field(default=None)
    stage_2: Optional[StageConfig] = field(default=None)