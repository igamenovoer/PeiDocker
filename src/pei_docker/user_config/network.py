"""
Network configuration classes for PeiDocker.

This module provides proxy and APT repository configuration for Docker containers,
supporting corporate environments and mirror repositories.
"""

from attrs import define, field
from typing import Optional


@define(kw_only=True)
class ProxyConfig:
    """
    HTTP proxy configuration for container networking.
    
    Configures HTTP/HTTPS proxy settings for Docker containers, enabling
    internet access through proxy servers during build and/or runtime.
    Supports flexible proxy usage patterns for different deployment scenarios.
    
    Attributes
    ----------
    address : str, optional
        Proxy server address or hostname. Can be IP address ("192.168.1.100")
        or hostname ("proxy.company.com"). If not specified, proxy is disabled.
    port : int, optional
        Proxy server port number. Common proxy ports include 8080, 3128, 8888.
        Required when address is specified.
    enable_globally : bool, optional
        Whether to enable proxy settings globally in the container environment.
        When True, sets http_proxy and https_proxy environment variables.
    remove_after_build : bool, optional
        Whether to remove proxy settings after Docker image build completes.
        Useful for build-time-only proxy requirements while keeping runtime clean.
    use_https : bool, default False
        Whether to use HTTPS for proxy connections. When True, proxy URLs
        use "https://" scheme; when False, uses "http://" scheme.
        
    Examples
    --------
    Build-time only proxy:
        >>> proxy = ProxyConfig(
        ...     address="proxy.company.com",
        ...     port=8080,
        ...     enable_globally=True,
        ...     remove_after_build=True
        ... )
        
    Runtime proxy with HTTPS:
        >>> proxy = ProxyConfig(
        ...     address="secure-proxy.company.com",
        ...     port=8443,
        ...     enable_globally=True,
        ...     remove_after_build=False,
        ...     use_https=True
        ... )
        
    Disabled proxy:
        >>> proxy = ProxyConfig()  # All None/False values disable proxy
        
    Notes
    -----
    Proxy configuration affects both APT package installation and general
    internet access within containers. The proxy URL format becomes:
    - HTTP: "http://address:port"
    - HTTPS: "https://address:port"
    
    When remove_after_build is True, proxy settings are available during
    'docker build' but not in the running container, which is useful for
    corporate environments with build-time proxy requirements.
    """
    address: Optional[str] = field(default=None)
    port: Optional[int] = field(default=None)
    enable_globally: Optional[bool] = field(default=None)
    remove_after_build: Optional[bool] = field(default=None)
    use_https: bool = field(default=False)


@define(kw_only=True)
class AptConfig:
    """
    APT package manager configuration for Ubuntu-based containers.
    
    Configures APT repository sources and proxy settings for package installation
    in Ubuntu/Debian-based Docker images. Supports repository mirrors for
    improved download speeds and corporate proxy environments.
    
    Attributes
    ----------
    repo_source : str, optional
        APT repository source configuration. Can be:
        - Predefined mirrors: "tuna", "aliyun", "163", "ustc", "cn"
        - Custom repository file path (relative to project installation directory)
        - None to use default Ubuntu repositories
    keep_repo_after_build : bool, default True
        Whether to keep custom repository configuration in the final image.
        When False, reverts to default repositories after package installation.
    use_proxy : bool, default False
        Whether to use proxy settings for APT operations. Requires ProxyConfig
        to be properly configured in the same stage.
    keep_proxy_after_build : bool, default False
        Whether to maintain APT proxy settings in the final image.
        When False, removes proxy configuration after build completion.
        
    Examples
    --------
    Chinese mirror for faster downloads:
        >>> apt = AptConfig(
        ...     repo_source="tuna",
        ...     keep_repo_after_build=True
        ... )
        
    Corporate proxy environment:
        >>> apt = AptConfig(
        ...     use_proxy=True,
        ...     keep_proxy_after_build=False
        ... )
        
    Custom repository file:
        >>> apt = AptConfig(
        ...     repo_source="stage-1/custom/my-sources.list",
        ...     keep_repo_after_build=True
        ... )
        
    Default configuration (Ubuntu repositories):
        >>> apt = AptConfig()  # Uses defaults
        
    Notes
    -----
    Predefined mirrors include:
    - "tuna": Tsinghua University mirror (China)
    - "aliyun": Alibaba Cloud mirror (China)
    - "163": NetEase mirror (China)
    - "ustc": University of Science and Technology of China
    - "cn": Generic China mirror (cn.archive.ubuntu.com)
    
    Custom repository files should follow standard APT sources.list format
    and be placed in the project's installation directory structure.
    
    Repository configuration is applied during Stage-1 system setup and
    affects all subsequent APT operations in both stages.
    """
    repo_source: Optional[str] = field(default=None)
    
    # Keep repository configuration by default for consistency
    keep_repo_after_build: bool = field(default=True)
    
    use_proxy: bool = field(default=False)
    keep_proxy_after_build: bool = field(default=False)