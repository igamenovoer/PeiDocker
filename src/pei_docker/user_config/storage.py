"""
Storage configuration classes for PeiDocker.

This module provides storage abstraction for Docker containers, supporting
various storage strategies including Docker volumes, host mounts, and in-image storage.
"""

from attrs import define, field
import attrs.validators as av
from typing import Optional, List


class StorageTypes:
    """
    Constants for storage type specifications in PeiDocker configurations.
    
    Defines the available storage options for container data persistence
    and volume management. Each type represents a different strategy for
    handling data storage in Docker containers.
    
    Class Attributes
    ----------------
    AutoVolume : str
        Automatically managed Docker volume. Docker creates and manages
        the volume lifecycle. Best for persistent data that doesn't need
        host access.
    ManualVolume : str
        Manually managed Docker volume. User creates the volume externally
        and specifies its name. Useful for sharing volumes between containers.
    Host : str
        Host directory mount. Maps a host filesystem path into the container.
        Enables direct host-container file sharing and persistence.
    Image : str
        In-image storage. Data is stored within the Docker image layers.
        Non-persistent but enables self-contained image distribution.
        
    Methods
    -------
    get_all_types() : List[str]
        Returns list of all valid storage type values for validation.
        
    Notes
    -----
    Storage type selection affects:
    - Data persistence across container restarts
    - Performance characteristics (host vs volume vs image)
    - Sharing capabilities between containers
    - Image size and portability
    - Backup and migration strategies
    
    The storage abstraction uses symbolic links in containers to enable
    seamless switching between storage types without changing application paths.
    """
    AutoVolume = 'auto-volume'
    ManualVolume = 'manual-volume'
    Host = 'host'
    Image = 'image'
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """
        Get list of all valid storage type values.
        
        Returns
        -------
        List[str]
            List containing all valid storage type constants.
        """
        return [cls.AutoVolume, cls.ManualVolume, cls.Host, cls.Image]


@define(kw_only=True)
class StorageOption:
    """
    Storage configuration option for container data persistence.
    
    Defines how data should be stored and accessed within Docker containers,
    supporting various storage strategies from host mounts to Docker volumes
    to in-image storage.
    
    Attributes
    ----------
    type : str
        Storage type specification. Must be one of StorageTypes constants:
        "auto-volume", "manual-volume", "host", or "image".
    host_path : str, optional
        Host filesystem path for "host" storage type. Must be provided
        when type is "host". Ignored for other storage types.
    volume_name : str, optional
        Docker volume name for "manual-volume" storage type. Must be provided
        when type is "manual-volume". The volume must exist or be created
        externally. Ignored for other storage types.
    dst_path : str, optional
        Destination path inside the container where storage should be mounted.
        If not specified, uses predefined paths based on storage prefix
        (app, data, workspace).
        
    Raises
    ------
    ValueError
        If required fields are missing for the specified storage type.
        
    Examples
    --------
    Host directory mount:
        >>> storage = StorageOption(
        ...     type="host",
        ...     host_path="/home/user/data",
        ...     dst_path="/app/data"
        ... )
        
    Automatic Docker volume:
        >>> storage = StorageOption(
        ...     type="auto-volume",
        ...     dst_path="/app/workspace"
        ... )
        
    Manual Docker volume:
        >>> storage = StorageOption(
        ...     type="manual-volume",
        ...     volume_name="shared-data",
        ...     dst_path="/app/shared"
        ... )
        
    In-image storage:
        >>> storage = StorageOption(
        ...     type="image",
        ...     dst_path="/app/assets"
        ... )
        
    Notes
    -----
    Storage validation ensures that required fields are provided based on
    the storage type. The validation occurs during object construction.
    
    PeiDocker uses symbolic links to abstract storage locations, allowing
    applications to use consistent paths regardless of the underlying
    storage implementation.
    """
    # Storage type with validation against allowed values
    type: str = field(validator=av.in_(StorageTypes.get_all_types()))
    host_path: Optional[str] = field(default=None)
    volume_name: Optional[str] = field(default=None)
    dst_path: Optional[str] = field(default=None)
    
    def __attrs_post_init__(self) -> None:
        if self.type == 'manual-volume' and self.volume_name is None:
            raise ValueError('volume_name must be provided for manual-volume storage')
        if self.type == 'host' and self.host_path is None:
            raise ValueError('host_path must be provided for host storage')