"""Constants for the PeiDocker WebGUI application.

This module centralizes all constant strings used throughout the WebGUI
to prevent typos and make the codebase more maintainable.
"""

from typing import List, Tuple


class CustomScriptLifecycleTypes:
    """Constants for custom script lifecycle types.
    
    These constants correspond to the lifecycle hooks defined in user_config.yml:
    - on_build: Scripts that run during Docker image building
    - on_first_run: Scripts that run on first container start
    - on_every_run: Scripts that run on every container start
    - on_user_login: Scripts that run when a user logs in via SSH
    """
    
    ON_BUILD: str = 'on_build'
    ON_FIRST_RUN: str = 'on_first_run'
    ON_EVERY_RUN: str = 'on_every_run'
    ON_USER_LOGIN: str = 'on_user_login'
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all lifecycle type constants as a list."""
        return [cls.ON_BUILD, cls.ON_FIRST_RUN, cls.ON_EVERY_RUN, cls.ON_USER_LOGIN]
    
    @classmethod
    def get_types_with_descriptions(cls) -> List[Tuple[str, str]]:
        """Get lifecycle types with their descriptions for UI display."""
        return [
            (cls.ON_BUILD, 'Runs during image building'),
            (cls.ON_FIRST_RUN, 'Runs on first container start (respective stage)'),
            (cls.ON_EVERY_RUN, 'Runs on every container start (respective stage)'),
            (cls.ON_USER_LOGIN, 'Runs when user logs in via SSH (respective stage)')
        ]


class StorageTypes:
    """Constants for storage configuration types."""
    
    AUTO_VOLUME: str = 'auto-volume'
    MANUAL_VOLUME: str = 'manual-volume'
    HOST: str = 'host'
    IMAGE: str = 'image'
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all storage type constants as a list."""
        return [cls.AUTO_VOLUME, cls.MANUAL_VOLUME, cls.HOST, cls.IMAGE]


class DeviceTypes:
    """Constants for device configuration types."""
    
    CPU: str = 'cpu'
    GPU: str = 'gpu'
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all device type constants as a list."""
        return [cls.CPU, cls.GPU]