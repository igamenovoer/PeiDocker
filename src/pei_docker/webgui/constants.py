"""Constants for the PeiDocker WebGUI application.

This module centralizes all constant strings used throughout the WebGUI
to prevent typos and make the codebase more maintainable.
"""

from typing import List, Tuple, Dict


class CustomScriptLifecycleTypes:
    """Constants for custom script lifecycle types.
    
    These constants correspond to the lifecycle hooks defined in user_config.yml:
    - on_build: Scripts that run during Docker image building
    - on_first_run: Scripts that run on first container start
    - on_every_run: Scripts that run on every container start
    - on_user_login: Scripts that run when a user logs in via SSH
    - on_entry: Custom entry point script that replaces the default container entry point
    """
    
    ON_BUILD: str = 'on_build'
    ON_FIRST_RUN: str = 'on_first_run'
    ON_EVERY_RUN: str = 'on_every_run'
    ON_USER_LOGIN: str = 'on_user_login'
    ON_ENTRY: str = 'on_entry'
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all lifecycle type constants as a list."""
        return [cls.ON_BUILD, cls.ON_FIRST_RUN, cls.ON_EVERY_RUN, cls.ON_USER_LOGIN, cls.ON_ENTRY]
    
    @classmethod
    def get_types_with_descriptions(cls) -> List[Tuple[str, str]]:
        """Get lifecycle types with their descriptions for UI display."""
        return [
            (cls.ON_BUILD, 'Runs during image building'),
            (cls.ON_FIRST_RUN, 'Runs on first container start (respective stage)'),
            (cls.ON_EVERY_RUN, 'Runs on every container start (respective stage)'),
            (cls.ON_USER_LOGIN, 'Runs when user logs in via SSH (respective stage)')
        ]


class DeviceTypes:
    """Constants for device configuration types."""
    
    CPU: str = 'cpu'
    GPU: str = 'gpu'
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all device type constants as a list."""
        return [cls.CPU, cls.GPU]


class ScriptTypes:
    """Constants for script configuration types in the UI."""
    
    FILE: str = 'file'
    INLINE: str = 'inline'
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all script type constants as a list."""
        return [cls.FILE, cls.INLINE]


class EntryModes:
    """Constants for entry point configuration modes."""
    
    NONE: str = 'none'
    FILE: str = 'file'
    INLINE: str = 'inline'
    
    @classmethod
    def get_all_modes(cls) -> List[str]:
        """Get all entry mode constants as a list."""
        return [cls.NONE, cls.FILE, cls.INLINE]


class AptMirrors:
    """Constants for known APT mirror shortcuts.
    
    These special values in repo_source get expanded to full mirror URLs.
    """
    
    TUNA: str = 'tuna'  # Tsinghua University mirror
    ALIYUN: str = 'aliyun'  # Alibaba Cloud mirror
    MIRRORS_163: str = '163'  # NetEase mirror
    USTC: str = 'ustc'  # University of Science and Technology of China mirror
    CN_ARCHIVE: str = 'cn'  # China archive mirror
    
    @classmethod
    def get_all_mirrors(cls) -> List[str]:
        """Get all mirror constants as a list."""
        return [cls.TUNA, cls.ALIYUN, cls.MIRRORS_163, cls.USTC, cls.CN_ARCHIVE]
    
    @classmethod
    def get_mirror_urls(cls) -> Dict[str, str]:
        """Get mapping of mirror shortcuts to their URLs."""
        return {
            cls.TUNA: 'http://mirrors.tuna.tsinghua.edu.cn/ubuntu/',
            cls.ALIYUN: 'http://mirrors.aliyun.com/ubuntu/',
            cls.MIRRORS_163: 'http://mirrors.163.com/ubuntu/',
            cls.USTC: 'http://mirrors.ustc.edu.cn/ubuntu/',
            cls.CN_ARCHIVE: 'http://cn.archive.ubuntu.com/ubuntu/'
        }