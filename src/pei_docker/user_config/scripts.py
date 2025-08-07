"""
Custom script configuration for PeiDocker.

This module provides lifecycle hook configuration for executing custom scripts
at different stages of the container lifecycle.
"""

from attrs import define, field
from typing import List, Optional


@define(kw_only=True)
class CustomScriptConfig:
    """
    Custom script configuration for container lifecycle hooks.
    
    Defines custom shell scripts to execute at different stages of the container
    lifecycle, enabling flexible customization of container behavior without
    modifying core PeiDocker functionality.
    
    All script paths are relative to the project's installation directory and
    can include parameters using shell syntax (e.g., "script.sh --param=value").
    
    Attributes
    ----------
    on_build : List[str], default empty
        Scripts executed during Docker image build process. Runs in the build
        context with access to build-time resources and environment variables.
        Useful for custom package installation or configuration.
    on_first_run : List[str], default empty
        Scripts executed only on the first container startup. Runs once per
        container instance for initialization tasks like database setup,
        user account creation, or initial configuration.
    on_every_run : List[str], default empty
        Scripts executed on every container startup. Runs each time the
        container starts, useful for dynamic configuration, service startup,
        or environment validation.
    on_user_login : List[str], default empty
        Scripts executed when users log in via SSH. Runs in the user's shell
        context, useful for user-specific environment setup, welcome messages,
        or session initialization.
    on_entry : List[str], default empty
        Custom entry point scripts. Can contain at most one script per stage.
        Replaces the default container entry point with custom initialization.
        
    Raises
    ------
    ValueError
        If more than one entry point script is specified in on_entry.
        
    Examples
    --------
    Build-time customization:
        >>> scripts = CustomScriptConfig(
        ...     on_build=["stage-1/custom/install-dev-tools.sh --verbose"]
        ... )
        
    Runtime initialization:
        >>> scripts = CustomScriptConfig(
        ...     on_first_run=["stage-2/custom/setup-database.sh"],
        ...     on_every_run=["stage-2/custom/check-services.sh"]
        ... )
        
    User environment setup:
        >>> scripts = CustomScriptConfig(
        ...     on_user_login=["stage-1/custom/setup-aliases.sh"]
        ... )
        
    Custom entry point:
        >>> scripts = CustomScriptConfig(
        ...     on_entry=["stage-2/custom/app-entrypoint.sh --mode=production"]
        ... )
        
    Notes
    -----
    Script execution order:
    1. on_build: During 'docker build' (build context)
    2. on_entry: Container startup (if specified, replaces default)
    3. on_first_run: First container startup only
    4. on_every_run: Every container startup
    5. on_user_login: SSH login (per session)
    
    Scripts can include shell parameters and will be parsed safely.
    All scripts should be executable and handle errors appropriately.
    Logging output is captured and available in container logs.
    """
    on_build: List[str] = field(factory=list)
    on_first_run: List[str] = field(factory=list)
    on_every_run: List[str] = field(factory=list)
    on_user_login: List[str] = field(factory=list)
    on_entry: List[str] = field(factory=list)
    
    def __attrs_post_init__(self) -> None:
        # Validate on_entry constraints - should have at most one entry point
        if len(self.on_entry) > 1:
            raise ValueError(f'on_entry can have at most one entry point per stage, got {len(self.on_entry)}: {self.on_entry}')
    
    def get_entry_script(self) -> Optional[str]:
        """
        Get the single entry script path, or None if not specified.
        
        Returns
        -------
        str or None
            The entry script path with parameters if specified, or None
            if no entry script is configured.
            
        Notes
        -----
        This method provides safe access to the entry script since only
        one entry point is allowed per stage configuration.
        """
        if len(self.on_entry) == 0:
            return None
        return self.on_entry[0]