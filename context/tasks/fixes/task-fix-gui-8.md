# Do this task

Fix the following issues of the GUI. We use the terminology as said in `context/tasks/prefix/prefix-terminology.md`.

## Network Tab

- remove the "HTTPS Proxy" setting, we do not have this
- remove the "No Proxy" setting, we do not have this

note that, `peidocker-data-model` does not have these settings, it only allows you to specify whether you use the same http proxy for https protocol or not. You need to update the `ui-data-model` as well

```python

#src\pei_docker\user_config.py

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
    address : str | None = field(default=None)
    port : int | None = field(default=None)
    enable_globally : bool | None = field(default=None)
    remove_after_build : bool | None = field(default=None)
    use_https : bool = field(default=False)
```