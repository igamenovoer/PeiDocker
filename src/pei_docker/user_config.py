"""
User Configuration Data Structures for PeiDocker.

This module defines type-safe data structures for PeiDocker configuration management
using the attrs library. It provides comprehensive validation, conversion, and
utility functions for handling Docker container configuration in a structured way.

The configuration follows PeiDocker's two-stage architecture:
- Stage 1: System-level setup (base image, SSH, proxy, APT repositories)
- Stage 2: Application-level configuration (custom mounts, scripts, entry points)

Data Structure Hierarchy
------------------------
UserConfig
├── stage_1: StageConfig
│   ├── image: ImageConfig (base and output image names)
│   ├── ssh: SSHConfig (SSH server and user configurations)
│   ├── proxy: ProxyConfig (HTTP proxy settings)
│   ├── apt: AptConfig (APT repository mirror settings)
│   ├── device: DeviceConfig (CPU/GPU hardware configuration)
│   ├── custom: CustomScriptConfig (lifecycle hook scripts)
│   ├── storage: Dict[str, StorageOption] (volume configurations)
│   ├── ports: List[str] (port mappings)
│   └── environment: Dict[str, str] (environment variables)
└── stage_2: StageConfig (same structure as stage_1)

Configuration Features
----------------------
- Type-safe validation with attrs decorators
- Automatic format conversion (list ↔ dict for environment variables)
- SSH key validation with multiple authentication methods
- Port mapping with range support ("8000-8010:9000-9010")
- Storage abstraction supporting Docker volumes, host mounts, and in-image storage
- Custom script lifecycle hooks (on_build, on_first_run, on_every_run, on_user_login)

Utility Functions
-----------------
port_mapping_str_to_dict : Convert port mapping strings to dictionary
port_mapping_dict_to_str : Convert port mapping dictionary to strings
env_str_to_dict : Convert environment variable strings to dictionary
env_dict_to_str : Convert environment variable dictionary to strings

Validation Features
-------------------
- SSH public/private key format validation
- Port range consistency checking
- Storage type validation with required field enforcement
- Password format validation (no spaces or commas)
- Environment variable format validation
- Custom script entry point constraints

Notes
-----
All data classes use attrs with kw_only=True for better API clarity.
Validation happens during object construction via __attrs_post_init__ methods.
The module supports both string and structured formats for flexible configuration.
"""

from attrs import define, field
import attrs.validators as av

__all__ = [
    'ImageConfig',
    'SSHUserConfig',
    'SSHConfig',
    'ProxyConfig',
    'AptConfig',
    'DeviceConfig',
    'CustomScriptConfig',
    'StorageOption',
    'StageConfig',
    'StorageTypes',
    'UserConfig',
    'port_mapping_str_to_dict',
    'port_mapping_dict_to_str',
    'env_str_to_dict',
    'env_dict_to_str',
]

def port_mapping_str_to_dict(port_mapping : list[str]) -> dict[int, int]:
    """
    Convert port mapping strings to dictionary format.
    
    Transforms a list of Docker-style port mapping strings into a dictionary
    mapping host ports to container ports. Supports both single port mappings
    and port ranges.
    
    Parameters
    ----------
    port_mapping : List[str]
        List of port mapping strings in formats:
        - Single: "8080:80" (host port 8080 maps to container port 80)
        - Range: "8000-8010:9000-9010" (11 ports mapped sequentially)
        
    Returns
    -------
    Dict[int, int]
        Dictionary mapping host port numbers to container port numbers.
        
    Raises
    ------
    ValueError
        If port ranges have different lengths between host and container sides.
        
    Examples
    --------
    Single port mappings:
        >>> port_mapping_str_to_dict(["8080:80", "3000:3000"])
        {8080: 80, 3000: 3000}
        
    Port range mapping:
        >>> port_mapping_str_to_dict(["8000-8002:9000-9002"])
        {8000: 9000, 8001: 9001, 8002: 9002}
        
    Notes
    -----
    Port ranges must have equal lengths on both host and container sides.
    The range format uses inclusive endpoints (8000-8002 includes 8000, 8001, 8002).
    """
    output : dict[int, int] = {}
    
    for ent in port_mapping:
        # split the string into host and container port
        host_port, container_port = ent.split(':')
        
        # are we mapping a range of ports? in the format 'host_start-host_end:container_start-container_end'
        if '-' in host_port:
            # find the range of host ports
            host_port_start_str, host_port_end_str = host_port.split('-')
            host_port_start: int = int(host_port_start_str)
            host_port_end: int = int(host_port_end_str)
            
            # find the range of container ports
            container_port_start_str, container_port_end_str = container_port.split('-')
            container_port_start: int = int(container_port_start_str)
            container_port_end: int = int(container_port_end_str)
            
            # check if the ranges are of the same length
            if host_port_end - host_port_start != container_port_end - container_port_start:
                raise ValueError('Port ranges must be of the same length')
            
            # add the port mappings to the output
            for u, v in zip(range(host_port_start, host_port_end + 1), range(container_port_start, container_port_end + 1)):
                output[u] = v
        else:
            output[int(host_port)] = int(container_port)
    return output
    
def port_mapping_dict_to_str(port_mapping: dict[int, int]) -> list[str]:
    """
    Convert port mapping dictionary to string format.
    
    Transforms a dictionary of host-to-container port mappings into Docker-style
    port mapping strings. Automatically detects and optimizes consecutive port
    ranges into range notation for cleaner configuration.
    
    Parameters
    ----------
    port_mapping : Dict[int, int]
        Dictionary mapping host port numbers to container port numbers.
        
    Returns
    -------
    List[str]
        List of port mapping strings in formats:
        - Single: "8080:80" for individual port mappings
        - Range: "8000-8010:9000-9010" for consecutive port sequences
        
    Examples
    --------
    Individual port mappings:
        >>> port_mapping_dict_to_str({8080: 80, 3000: 3000})
        ['8080:80', '3000:3000']
        
    Consecutive ports optimized to range:
        >>> port_mapping_dict_to_str({8000: 9000, 8001: 9001, 8002: 9002})
        ['8000-8002:9000-9002']
        
    Mixed individual and range mappings:
        >>> port_mapping_dict_to_str({8080: 80, 9000: 9000, 9001: 9001})
        ['8080:80', '9000-9001:9000-9001']
        
    Notes
    -----
    The function automatically detects consecutive port sequences and converts
    them to range notation for more compact representation. Port mappings are
    sorted by host port number for consistent output.
    """
    
    output : list[str] = []
    
    if len(port_mapping) == 0:
        return output
    
    port_from_range_start : int = -1
    port_to_range_start : int = -1
    port_from_prev : int = -1
    port_to_prev : int = -1
    
    for port_from, port_to in sorted(port_mapping.items()):
        # first port, initialize the range
        if port_from_prev == -1:
            port_from_range_start = port_from
            port_to_range_start = port_to
        elif port_from_prev == port_from - 1 and port_to_prev == port_to - 1:
            # we are in a range, no need to do anything
            pass
        else:
            # the previous range has ended, add it to the output
            if port_from_range_start == port_from_prev: # single port
                port_mapping_entry = f'{port_from_range_start}:{port_to_range_start}'
                output.append(port_mapping_entry)
            else:
                port_mapping_entry = f'{port_from_range_start}-{port_from_prev}:{port_to_range_start}-{port_to_prev}'
                output.append(port_mapping_entry)
            
            # start a new range
            port_from_range_start = port_from
            port_to_range_start = port_to
            
        # update prev
        port_from_prev = port_from
        port_to_prev = port_to
        
    # output the last range
    if port_from_range_start == port_from_prev: # single port
        port_mapping_entry = f'{port_from_range_start}:{port_to_range_start}'
        output.append(port_mapping_entry)
    else:
        port_mapping_entry = f'{port_from_range_start}-{port_from_prev}:{port_to_range_start}-{port_to_prev}'
        output.append(port_mapping_entry)
            
    return output
    
    # return [f'{k}:{v}' for k, v in port_mapping.items()]

def env_str_to_dict(env_list: list[str]) -> dict[str, str]:
    """
    Convert environment variable strings to dictionary format.
    
    Transforms a list of environment variable strings in KEY=VALUE format
    into a dictionary for easier programmatic access and manipulation.
    
    Parameters
    ----------
    env_list : List[str]
        List of environment variable strings in "KEY=VALUE" format.
        
    Returns
    -------
    Dict[str, str]
        Dictionary mapping environment variable names to their values.
        
    Examples
    --------
    Basic environment variables:
        >>> env_str_to_dict(["NODE_ENV=production", "PORT=3000"])
        {'NODE_ENV': 'production', 'PORT': '3000'}
        
    Variables with complex values:
        >>> env_str_to_dict(["PATH=/usr/bin:/bin", "DB_URL=postgres://user:pass@host/db"])
        {'PATH': '/usr/bin:/bin', 'DB_URL': 'postgres://user:pass@host/db'}
        
    Notes
    -----
    Each string is split on the first '=' character, so values can contain
    additional '=' characters without issues. This is compatible with standard
    Unix environment variable format.
    """
    return {x.split('=')[0]: x.split('=')[1] for x in env_list}

def env_dict_to_str(env_dict: dict[str, str]) -> list[str]:
    """
    Convert environment variable dictionary to string format.
    
    Transforms a dictionary of environment variables into a list of KEY=VALUE
    strings suitable for Docker Compose environment sections or shell export.
    
    Parameters
    ----------
    env_dict : Dict[str, str]
        Dictionary mapping environment variable names to their values.
        
    Returns
    -------
    List[str]
        List of environment variable strings in "KEY=VALUE" format.
        
    Examples
    --------
    Basic environment variables:
        >>> env_dict_to_str({'NODE_ENV': 'production', 'PORT': '3000'})
        ['NODE_ENV=production', 'PORT=3000']
        
    Variables with complex values:
        >>> env_dict_to_str({'PATH': '/usr/bin:/bin', 'DB_URL': 'postgres://user:pass@host/db'})
        ['PATH=/usr/bin:/bin', 'DB_URL=postgres://user:pass@host/db']
        
    Notes
    -----
    The output format is compatible with Docker Compose environment sections
    and can be used directly in shell scripts or configuration files.
    Order is not guaranteed as it depends on dictionary iteration.
    """
    return [f'{k}={v}' for k, v in env_dict.items()]

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
    base : str | None = field(default=None)
    output : str | None = field(default=None)
    
@define(kw_only=True)
class SSHUserConfig:
    """
    SSH user account configuration with multiple authentication methods.
    
    Defines an SSH user account that will be created in the Docker container,
    supporting password authentication, public key authentication, and private
    key provisioning. Provides flexible authentication options for different
    security requirements.
    
    Attributes
    ----------
    password : str, optional
        Password for SSH authentication. Cannot contain spaces or commas
        due to implementation constraints in shell script processing.
    pubkey_file : str, optional
        Path to SSH public key file. Supports relative paths (from project
        installation directory), absolute paths, or "~" for system key discovery.
        Mutually exclusive with pubkey_text.
    pubkey_text : str, optional
        SSH public key content as text. Must be in valid OpenSSH public key
        format (e.g., "ssh-rsa AAAAB3NzaC1yc2E..."). Mutually exclusive with pubkey_file.
    privkey_file : str, optional
        Path to SSH private key file. Supports relative paths, absolute paths,
        or "~" for system key discovery. Mutually exclusive with privkey_text.
    privkey_text : str, optional
        SSH private key content as text. Must be in valid OpenSSH or PEM format.
        Mutually exclusive with privkey_file.
    uid : int, optional
        User ID for the SSH account. Defaults to system assignment if not specified.
        Recommended to use UIDs >= 1100 to avoid conflicts with system users.
        
    Raises
    ------
    ValueError
        If password contains spaces or commas, if mutually exclusive key options
        are both specified, if no authentication method is provided, or if
        SSH key formats are invalid.
        
    Examples
    --------
    Password-only authentication:
        >>> user = SSHUserConfig(password="secure123", uid=1100)
        
    Public key authentication:
        >>> user = SSHUserConfig(
        ...     pubkey_text="ssh-rsa AAAAB3NzaC1yc2E... user@host",
        ...     uid=1100
        ... )
        
    System SSH key discovery:
        >>> user = SSHUserConfig(pubkey_file="~", uid=1100)
        
    Combined authentication methods:
        >>> user = SSHUserConfig(
        ...     password="backup123",
        ...     pubkey_file="/path/to/key.pub",
        ...     uid=1100
        ... )
        
    Notes
    -----
    At least one authentication method (password, public key, or private key)
    must be provided. Public and private key options are mutually exclusive
    within their respective categories but can be combined with passwords.
    
    SSH key validation ensures proper format before container deployment.
    The "~" syntax automatically discovers system SSH keys with priority:
    id_rsa, id_dsa, id_ecdsa, id_ed25519.
    """
    password : str | None = field(default=None)
    pubkey_file : str | None = field(default=None)
    pubkey_text : str | None = field(default=None)
    privkey_file : str | None = field(default=None)
    privkey_text : str | None = field(default=None)
    uid : int | None = field(default=None)
    
    def __attrs_post_init__(self) -> None:
        # Validate password format
        if self.password is not None:
            # password cannot contain space and comma
            assert ' ' not in self.password and ',' not in self.password, f'Password cannot contain space or comma: {self.password}'
        
        # Validate mutually exclusive public key options
        if self.pubkey_file is not None and self.pubkey_text is not None:
            raise ValueError('Cannot specify both pubkey_file and pubkey_text')
        
        # Validate mutually exclusive private key options
        if self.privkey_file is not None and self.privkey_text is not None:
            raise ValueError('Cannot specify both privkey_file and privkey_text')
        
        # At least one authentication method required
        has_password = self.password is not None
        has_pubkey = self.pubkey_file is not None or self.pubkey_text is not None
        has_privkey = self.privkey_file is not None or self.privkey_text is not None
        
        if not (has_password or has_pubkey or has_privkey):
            raise ValueError('Must provide at least one authentication method: password, public key, or private key')
        
        # Validate SSH key formats
        if self.pubkey_text is not None:
            self._validate_public_key_format(self.pubkey_text)
        
        if self.privkey_text is not None:
            self._validate_private_key_format(self.privkey_text)
    
    def _validate_public_key_format(self, key_text: str) -> None:
        """Validate SSH public key format"""
        import re
        key_text = key_text.strip()
        
        # SSH public key should start with algorithm name and contain base64 data
        ssh_key_pattern = r'^(ssh-rsa|ssh-dss|ssh-ed25519|ecdsa-sha2-nistp256|ecdsa-sha2-nistp384|ecdsa-sha2-nistp521)\s+[A-Za-z0-9+/]+=*\s*.*$'
        
        if not re.match(ssh_key_pattern, key_text):
            raise ValueError(f'Invalid SSH public key format: {key_text[:50]}...')
    
    def _validate_private_key_format(self, key_text: str) -> None:
        """Validate SSH private key format"""
        key_text = key_text.strip()
        
        # Check for OpenSSH private key format
        if key_text.startswith('-----BEGIN OPENSSH PRIVATE KEY-----') and key_text.endswith('-----END OPENSSH PRIVATE KEY-----'):
            return
        
        # Check for traditional private key formats
        traditional_headers = [
            '-----BEGIN RSA PRIVATE KEY-----',
            '-----BEGIN DSA PRIVATE KEY-----',
            '-----BEGIN EC PRIVATE KEY-----',
            '-----BEGIN PRIVATE KEY-----'
        ]
        
        for header in traditional_headers:
            if key_text.startswith(header):
                return
        
        raise ValueError('Invalid SSH private key format. Must be in OpenSSH or traditional PEM format.')
    
@define(kw_only=True)
class SSHConfig:
    """
    SSH server configuration for Docker container access.
    
    Manages SSH server setup including port configuration, user accounts,
    and container-to-host port mapping. SSH provides the primary method
    for interactive terminal access to running containers.
    
    Attributes
    ----------
    enable : bool, default True
        Whether to enable SSH server in the container. When disabled,
        users must use 'docker exec' commands for container access.
    port : int, default 22
        Port number for SSH server inside the container. Standard SSH
        port is 22, but can be changed for security or conflict avoidance.
    host_port : int, optional
        Port number on the host machine that maps to the container SSH port.
        If not specified, Docker will assign a random available port.
        Common choice is 2222 to avoid conflicts with host SSH (port 22).
    users : Dict[str, SSHUserConfig], default empty
        Dictionary mapping usernames to SSH user configurations. Each user
        can have different authentication methods and system properties.
        
    Examples
    --------
    Basic SSH configuration:
        >>> ssh_config = SSHConfig(
        ...     enable=True,
        ...     port=22,
        ...     host_port=2222,
        ...     users={
        ...         "admin": SSHUserConfig(password="admin123", uid=1100)
        ...     }
        ... )
        
    Disabled SSH (use docker exec instead):
        >>> ssh_config = SSHConfig(enable=False)
        
    Custom port configuration:
        >>> ssh_config = SSHConfig(
        ...     port=2022,
        ...     host_port=2022,
        ...     users={"user": SSHUserConfig(pubkey_file="~")}
        ... )
        
    Notes
    -----
    SSH is enabled by default as it provides the most convenient access method
    for development and debugging. When enabled, at least one user should be
    configured to allow container access.
    
    The host_port mapping allows external access to the container SSH server.
    If not specified, Docker assigns a random port accessible via 'docker port'.
    """
    # SSH enabled by default for convenient container access
    enable : bool = field(default=True)
    port : int = field(default=22)
    host_port : int | None = field(default=None)
    users : dict[str, SSHUserConfig] = field(factory=dict)
    
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
    repo_source : str | None = field(default=None)
    
    # Keep repository configuration by default for consistency
    keep_repo_after_build : bool = field(default=True)
    
    use_proxy : bool = field(default=False)
    keep_proxy_after_build : bool = field(default=False)
    
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
    type : str = field(default='cpu')
    
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
    on_build : list[str] = field(factory=list)
    on_first_run : list[str] = field(factory=list)
    on_every_run : list[str] = field(factory=list)
    on_user_login : list[str] = field(factory=list)
    on_entry : list[str] = field(factory=list)
    
    def __attrs_post_init__(self) -> None:
        # Validate on_entry constraints - should have at most one entry point
        if len(self.on_entry) > 1:
            raise ValueError(f'on_entry can have at most one entry point per stage, got {len(self.on_entry)}: {self.on_entry}')
    
    def get_entry_script(self) -> str | None:
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
    def get_all_types(cls) -> list[str]:
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
    type : str = field(validator=av.in_(StorageTypes.get_all_types()))
    host_path : str | None = field(default=None)
    volume_name : str | None = field(default=None)
    dst_path : str | None = field(default=None)
    
    def __attrs_post_init__(self) -> None:
        if self.type == 'manual-volume' and self.volume_name is None:
            raise ValueError('volume_name must be provided for manual-volume storage')
        if self.type == 'host' and self.host_path is None:
            raise ValueError('host_path must be provided for host storage')

def env_converter(x : list[str] | dict[str, str] | None) -> dict[str, str] | None:
    """
    Convert environment variables from list format to dictionary format.
    
    Provides automatic conversion for environment variable specifications,
    allowing users to provide either list or dictionary format in configuration
    files while ensuring consistent internal representation.
    
    Parameters
    ----------
    x : List[str] or Dict[str, str] or None
        Environment variables in list format ("KEY=VALUE") or dictionary format,
        or None for no environment variables.
        
    Returns
    -------
    Dict[str, str] or None
        Environment variables in dictionary format, or None if input was None.
        
    Examples
    --------
    List format conversion:
        >>> env_converter(["NODE_ENV=production", "PORT=3000"])
        {'NODE_ENV': 'production', 'PORT': '3000'}
        
    Dictionary format passthrough:
        >>> env_converter({'NODE_ENV': 'production', 'PORT': '3000'})
        {'NODE_ENV': 'production', 'PORT': '3000'}
        
    None passthrough:
        >>> env_converter(None)
        None
        
    Notes
    -----
    This function is used as an attrs converter to normalize environment
    variable input formats during object construction.
    """
    if x is None:
        return None
    if isinstance(x, list):
        return env_str_to_dict(x)
    else:
        return x
@define(kw_only=True)
class StageConfig:
    """
    Complete configuration for a single stage in PeiDocker's two-stage architecture.
    
    Represents all configuration options available for either Stage-1 (system setup)
    or Stage-2 (application configuration). Provides a comprehensive set of options
    for Docker image customization, networking, storage, and runtime behavior.
    
    Attributes
    ----------
    image : ImageConfig, optional
        Docker image configuration specifying base and output images.
        Required for Stage-1; optional for Stage-2 (inherits from Stage-1).
    ssh : SSHConfig, optional
        SSH server configuration for container access. Only supported in Stage-1
        as SSH setup requires system-level privileges.
    proxy : ProxyConfig, optional
        HTTP proxy configuration for build and runtime networking.
        Can be used in both stages for different proxy requirements.
    apt : AptConfig, optional
        APT package manager configuration including repository mirrors.
        Only supported in Stage-1 as it affects system package management.
    environment : Dict[str, str], optional
        Environment variables for the container. Automatically converts from
        list format ("KEY=VALUE") to dictionary format for consistency.
    ports : List[str], optional
        Port mappings in Docker format (e.g., "8080:80", "9000-9010:9000-9010").
        Supports both individual ports and port ranges.
    device : DeviceConfig, optional
        Hardware device configuration (CPU/GPU access requirements).
    custom : CustomScriptConfig, optional
        Custom scripts for container lifecycle hooks (build, startup, login).
    storage : Dict[str, StorageOption], optional
        Storage configurations for Stage-2 data persistence. Maps storage
        names to storage options (volumes, host mounts, in-image).
    mount : Dict[str, StorageOption], optional
        Mount configurations for both stages. Maps mount names to storage
        options, providing flexible volume management.
        
    Methods
    -------
    get_port_mapping_as_dict() : Dict[int, int] or None
        Convert port mappings to dictionary format for programmatic access.
    set_port_mapping_from_dict(port_mapping: Dict[int, int])
        Set port mappings from dictionary format.
    get_environment_as_dict() : Dict[str, str] or None
        Get environment variables as dictionary (handles legacy list format).
        
    Examples
    --------
    Stage-1 system configuration:
        >>> stage1 = StageConfig(
        ...     image=ImageConfig(base="ubuntu:24.04", output="my-app:stage-1"),
        ...     ssh=SSHConfig(users={"admin": SSHUserConfig(password="admin123")}),
        ...     proxy=ProxyConfig(address="proxy.company.com", port=8080),
        ...     apt=AptConfig(repo_source="tuna"),
        ...     environment={"DEBIAN_FRONTEND": "noninteractive"},
        ...     device=DeviceConfig(type="gpu")
        ... )
        
    Stage-2 application configuration:
        >>> stage2 = StageConfig(
        ...     image=ImageConfig(output="my-app:stage-2"),
        ...     ports=["8080:80", "3000:3000"],
        ...     storage={
        ...         "data": StorageOption(type="host", host_path="/data")
        ...     },
        ...     custom=CustomScriptConfig(
        ...         on_first_run=["stage-2/custom/setup-app.sh"]
        ...     )
        ... )
        
    Notes
    -----
    Stage-specific restrictions:
    - SSH configuration only supported in Stage-1
    - APT configuration only supported in Stage-1  
    - Storage configuration primarily used in Stage-2
    - Both stages support proxy, environment, ports, device, custom, and mount
    
    The configuration is processed by PeiConfigProcessor to generate
    Docker Compose files and container setup scripts.
    """
    image : ImageConfig | None = field(default=None)
    ssh : SSHConfig | None = field(default=None)
    proxy : ProxyConfig | None = field(default=None)
    apt : AptConfig | None = field(default=None)
    environment : dict[str,str] | None = field(default=None, converter=env_converter)
    ports : list[str] | None = field(factory=list)  # Port mappings in Docker format (e.g. "8080:80")
    device : DeviceConfig | None = field(default=None)
    custom : CustomScriptConfig | None = field(default=None)
    storage : dict[str, StorageOption] | None = field(factory=dict)
    mount: dict[str, StorageOption] | None = field(factory=dict)
    
    def get_port_mapping_as_dict(self) -> dict[int, int] | None:
        """
        Get port mappings as dictionary format for programmatic access.
        
        Returns
        -------
        Dict[int, int] or None
            Dictionary mapping host ports to container ports, or None
            if no port mappings are configured.
            
        Examples
        --------
        >>> config = StageConfig(ports=["8080:80", "9000-9002:9000-9002"])
        >>> config.get_port_mapping_as_dict()
        {8080: 80, 9000: 9000, 9001: 9001, 9002: 9002}
        """
        if self.ports is not None:
            return port_mapping_str_to_dict(self.ports)
        return None
        
    def set_port_mapping_from_dict(self, port_mapping: dict[int, int]) -> None:
        """
        Set port mappings from dictionary format.
        
        Parameters
        ----------
        port_mapping : Dict[int, int]
            Dictionary mapping host ports to container ports.
            
        Examples
        --------
        >>> config = StageConfig()
        >>> config.set_port_mapping_from_dict({8080: 80, 9000: 9000})
        >>> config.ports
        ['8080:80', '9000:9000']
        """
        self.ports = port_mapping_dict_to_str(port_mapping)
        
    def get_environment_as_dict(self) -> dict[str, str] | None:
        """
        Get environment variables as dictionary format.
        
        Handles legacy list format environment variables by converting them
        to dictionary format for consistent access.
        
        Returns
        -------
        Dict[str, str] or None
            Environment variables as key-value pairs, or None if no
            environment variables are configured.
            
        Examples
        --------
        Dictionary format (modern):
            >>> config = StageConfig(environment={"NODE_ENV": "production"})
            >>> config.get_environment_as_dict()
            {'NODE_ENV': 'production'}
            
        List format (legacy, auto-converted):
            >>> config = StageConfig()
            >>> config.environment = ["NODE_ENV=production", "PORT=3000"]
            >>> config.get_environment_as_dict()
            {'NODE_ENV': 'production', 'PORT': '3000'}
        """
        if self.environment is not None and isinstance(self.environment, list):
            return env_str_to_dict(self.environment)
        else:
            return self.environment
    
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
    stage_1 : StageConfig | None = field(default=None)
    stage_2 : StageConfig | None = field(default=None)