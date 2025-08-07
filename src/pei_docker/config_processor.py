"""
Processes user-defined configuration for PeiDocker.

This module is responsible for parsing and processing user configurations,
applying them to a Docker Compose template to generate a final `docker-compose.yml` file.
It handles various settings, including APT repositories, proxy configurations,
SSH access, storage volumes, and custom scripts for different build and run stages.

The main entry point for processing is the `PeiConfigProcessor` class, which
orchestrates the entire configuration transformation.
"""
import os
import logging
import shlex
import omegaconf as oc
from omegaconf import DictConfig
from attrs import define, field
import cattrs
from typing import Optional, Tuple

from pei_docker.user_config import *

logging.basicConfig(level=logging.INFO)

__all__ = [
    'StorageTypes',
    'StoragePrefixes',
    'StoragePaths',
    'Defaults',
    'PeiConfigProcessor',
]
    
class StoragePrefixes:
    """Defines prefixes for different types of storage volumes."""
    App = 'app'
    """Prefix for application-related storage."""
    Data = 'data'
    """Prefix for data storage."""
    Workspace = 'workspace'
    """Prefix for workspace storage."""
    
    @classmethod
    def get_all_prefixes(cls) -> list[str]:
        """
        Get all defined storage prefixes.

        Returns
        -------
        list[str]
            A list containing all storage prefixes.
        """
        return [cls.App, cls.Data, cls.Workspace]
    
class StoragePaths:
    """
    Defines standard in-container paths for storage.
    
    These paths are used as mount points inside the Docker container.
    """
    Soft = '/soft'
    """Base path for soft-linked storage mounted inside the container."""
    HardImage = '/hard/image'
    """Path for data baked directly into the Docker image."""
    HardVolume = '/hard/volume'
    """Base path for persistent Docker volumes."""

class Defaults:
    """
    Defines default values and constants used throughout the configuration process.
    
    This class centralizes default paths, names, and settings to ensure consistency.
    """
    ConfigTemplatePath='templates/config-template-full.yml'
    ComposeTemplatePath='templates/base-image-gen.yml'
    ConfigExamplesDir='examples'
    OutputConfigName='user_config.yml'
    OutputComposeTemplateName = 'compose-template.yml'
    OutputComposeName='docker-compose.yml'
    BuildDir='build'
    ContainerInstallationDir='/pei-from-host'
    ProjectDirectory='./project_files'
    HostInstallationDir='./installation' # relative to the project directory
    Stage1_ImageName='pei-image:stage-1'
    Stage2_ImageName='pei-image:stage-2'
    Stage1_BaseImageName='ubuntu:22.04'
    RunDevice='cpu'    
    SpecialAptSources : list[str] = [
        'tuna','aliyun','163','ustc','cn'
    ]
    
    # ubuntu versions
    UbuntuCuda='nvidia/cuda:12.3.2-runtime-ubuntu22.04'
    UbuntuLTS='ubuntu:24.04'
    
@define(kw_only=True)
class GeneratedScripts:
    """
    Data class for storing paths to generated shell scripts.

    These scripts are created by the processor to be executed at different
    stages of the container lifecycle (e.g., on build, on first run).
    """
    on_build_script : Optional[str] = field(default=None)
    on_first_run_script : Optional[str] = field(default=None)
    on_every_run_script : Optional[str] = field(default=None)
    
class PeiConfigProcessor:
    """
    Processes user configuration and applies it to a Docker Compose template.

    This class reads a user-provided configuration, merges it with a base
    Docker Compose template, and generates a final `docker-compose.yml` file.
    It handles complex configurations including multi-stage builds, networking,
    volumes, and dynamic script generation.

    Attributes
    ----------
    m_config : Optional[DictConfig]
        The user's configuration loaded as an OmegaConf DictConfig.
    m_compose_template : Optional[DictConfig]
        The base Docker Compose template.
    m_compose_output : Optional[DictConfig]
        The final, processed Docker Compose configuration.
    m_generated_scripts : GeneratedScripts
        Paths to the generated helper scripts.
    m_project_dir : str
        The root directory of the user's project files.
    m_host_dir : str
        The directory on the host where installation files are stored, relative to `m_project_dir`.
    m_container_dir : str
        The corresponding directory inside the container for installation files.
    """
    def __init__(self) -> None:
        self.m_config : Optional[DictConfig] = None
        self.m_compose_template : Optional[DictConfig] = None
        self.m_compose_output : Optional[DictConfig] = None
        self.m_generated_scripts : GeneratedScripts = GeneratedScripts()
        
        # host dir is relative to the directory of the docker compose file
        self.m_project_dir = Defaults.ProjectDirectory
        self.m_host_dir = Defaults.HostInstallationDir
        self.m_container_dir = Defaults.ContainerInstallationDir
        
    @classmethod
    def from_config(cls, config : DictConfig, compose_template : DictConfig, project_dir: Optional[str] = None) -> 'PeiConfigProcessor':
        """
        Create a new instance from configuration objects.

        Parameters
        ----------
        config : DictConfig
            The user's configuration.
        compose_template : DictConfig
            The base Docker Compose template.
        project_dir : str, optional
            The root directory for the project files. If not provided,
            `Defaults.ProjectDirectory` is used.

        Returns
        -------
        PeiConfigProcessor
            A new instance of the processor.
        """
        self = cls()
        self.m_config = config
        self.m_compose_template = compose_template
        if project_dir is not None:
            self.m_project_dir = project_dir
        return self
    
    @classmethod
    def from_files(cls, config_file : str, compose_template_file : str, project_dir: Optional[str] = None) -> 'PeiConfigProcessor':
        """
        Create a new instance from configuration files.

        Parameters
        ----------
        config_file : str
            Path to the user's YAML configuration file.
        compose_template_file : str
            Path to the base Docker Compose template file.
        project_dir : str, optional
            The root directory for the project files. If not provided,
            `Defaults.ProjectDirectory` is used.

        Returns
        -------
        PeiConfigProcessor
            A new instance of the processor.

        Raises
        ------
        ValueError
            If the loaded configuration files are not dictionary-like.
        """
        config = oc.OmegaConf.load(config_file)
        compose = oc.OmegaConf.load(compose_template_file)
        
        # Ensure we have DictConfig objects
        if not isinstance(config, DictConfig):
            raise ValueError("Config file must contain a dictionary structure")
        if not isinstance(compose, DictConfig):
            raise ValueError("Compose template file must contain a dictionary structure")
            
        return cls.from_config(config, compose, project_dir)
    
    def _parse_script_and_args(self, script_with_args: str) -> Tuple[str, list[str]]:
        """
        Parse a script string into a script path and its arguments.

        Uses `shlex` to handle shell-like quoting and splitting.

        Parameters
        ----------
        script_with_args : str
            The script string, including optional arguments (e.g.,
            'path/to/script.sh --arg1 "value 2"').

        Returns
        -------
        Tuple[str, list[str]]
            A tuple containing the script path and a list of its arguments.

        Raises
        ------
        ValueError
            If the script specification is empty or cannot be parsed.
        """
        try:
            tokens = shlex.split(script_with_args)
            if not tokens:
                raise ValueError(f"Empty script specification: {script_with_args}")
            
            script_path = tokens[0]
            args = tokens[1:] if len(tokens) > 1 else []
            return script_path, args
        except ValueError as e:
            raise ValueError(f"Failed to parse script specification '{script_with_args}': {e}")
    
    def _check_custom_scripts(self, custom_config : CustomScriptConfig) -> bool:
        """
        Verify that all specified custom scripts exist on the host filesystem.

        This method checks for the existence of scripts for various hooks (`on_build`,
        `on_first_run`, etc.) and logs a warning if a script is not found.

        Parameters
        ----------
        custom_config : CustomScriptConfig
            The configuration object containing lists of custom scripts.

        Returns
        -------
        bool
            Always returns True. This method is for validation and logging, not
            for halting the process.
        """
        
        on_build_scripts = custom_config.on_build
        if on_build_scripts is not None:
            # check if all files listed in on_build_scripts exist, and replace it
            for i, script in enumerate(on_build_scripts):
                host_path = f'{self.m_project_dir}/{self.m_host_dir}/{script}'
                if not os.path.exists(host_path):
                    logging.warning(f'Script {host_path} not found')
            
        on_first_run_scripts = custom_config.on_first_run
        if on_first_run_scripts is not None:
            # check if all files listed in on_first_run_scripts exist
            for i, script in enumerate(on_first_run_scripts):
                host_path = f'{self.m_project_dir}/{self.m_host_dir}/{script}'
                if not os.path.exists(host_path):
                    logging.warning(f'Script {host_path} not found')
            
        on_every_run_scripts : list[str] = custom_config.on_every_run
        if on_every_run_scripts is not None:
            # check if all files listed in on_every_run_scripts exist
            for script in on_every_run_scripts:
                host_path = f'{self.m_project_dir}/{self.m_host_dir}/{script}'
                if not os.path.exists(host_path):
                    logging.warning(f'Script {host_path} not found')
                    
        on_user_login_scripts : list[str] = custom_config.on_user_login
        if on_user_login_scripts is not None:
            # check if all files listed in on_user_login_scripts exist
            for script in on_user_login_scripts:
                host_path = f'{self.m_project_dir}/{self.m_host_dir}/{script}'
                if not os.path.exists(host_path):
                    logging.warning(f'Script {host_path} not found')
                    
        on_entry_script = custom_config.get_entry_script()
        if on_entry_script is not None:
            # Parse script path and arguments
            script_path, _ = self._parse_script_and_args(on_entry_script)
            # check if the on_entry script exists
            host_path = f'{self.m_project_dir}/{self.m_host_dir}/{script_path}'
            if not os.path.exists(host_path):
                logging.warning(f'Script {host_path} not found')
                
        return True
    
    def _apply_apt(self, apt_config : AptConfig, build_compose : DictConfig) -> None:
        """
        Apply APT-related configurations to the Docker Compose build arguments.

        This updates the compose template with settings for APT sources, proxies,
        and cleanup behavior.

        Parameters
        ----------
        apt_config : AptConfig
            The user's APT configuration.
        build_compose : DictConfig
            The 'build' section of the Docker Compose configuration to be updated.
        
        Raises
        ------
        FileNotFoundError
            If a custom APT sources file is specified but not found.
        """
        
        oc_set = oc.OmegaConf.update
        repo_source = apt_config.repo_source
        
        if repo_source is not None and len(repo_source) > 0:
            if repo_source in Defaults.SpecialAptSources:
                oc_set(build_compose, 'apt.source_file', repo_source)
            else:
                # check if the repo path exists
                _repo_path_host = f'{self.m_project_dir}/{self.m_host_dir}/{repo_source}'
                if not os.path.exists(_repo_path_host):
                    raise FileNotFoundError(f'Repo source path {_repo_path_host} not found')
                
                _repo_path_container = self.m_container_dir + '/' + repo_source
                oc_set(build_compose, 'apt.source_file', _repo_path_container)
        
        # keep repo after build?
        keep_repo = bool(apt_config.keep_repo_after_build)  # convert to bool explicitly in case it's None
        oc_set(build_compose, 'apt.keep_source_file', keep_repo)
        
        # use proxy?
        use_proxy = bool(apt_config.use_proxy)
        oc_set(build_compose, 'apt.use_proxy', use_proxy)
        
        # keep proxy after build?
        keep_proxy = bool(apt_config.keep_proxy_after_build)
        oc_set(build_compose, 'apt.keep_proxy', keep_proxy)
    
    def _apply_proxy(self, proxy_config : ProxyConfig, build_compose : DictConfig) -> None:
        """
        Apply proxy settings to the Docker Compose build arguments.

        Configures HTTP/HTTPS proxy settings based on the user's configuration,
        including address, port, and whether it should be enabled globally.

        Parameters
        ----------
        proxy_config : ProxyConfig
            The user's proxy configuration.
        build_compose : DictConfig
            The 'build' section of the Docker Compose configuration to be updated.
        """
        oc_set = oc.OmegaConf.update
        
        adr = proxy_config.address
        if adr is not None:
            oc_set(build_compose, 'proxy.address', adr)
        
        port = proxy_config.port
        if port is not None:
            oc_set(build_compose, 'proxy.port', port)
        
        enable_globally = proxy_config.enable_globally
        if enable_globally is not None:
            oc_set(build_compose, 'proxy.enable_globally', enable_globally)
        
        remove_after_build = proxy_config.remove_after_build
        if remove_after_build is not None:
            oc_set(build_compose, 'proxy.remove_after_build', remove_after_build)
        
        use_https = proxy_config.use_https
        if use_https is not None:
            if use_https:
                oc_set(build_compose, 'proxy.https_header', 'https')
            else:
                oc_set(build_compose, 'proxy.https_header', 'http')
    
    def _apply_ssh_to_x_compose(self, ssh_config : Optional[SSHConfig], build_compose : DictConfig) -> None:
        """
        Apply SSH configurations to the Docker Compose build arguments.

        This configures the SSH server within the container, including enabling/disabling
        the server, setting up users, passwords, and public/private keys.

        Parameters
        ----------
        ssh_config : Optional[SSHConfig]
            The user's SSH configuration. If None, SSH is disabled.
        build_compose : DictConfig
            The 'build' section of the Docker Compose configuration to be updated.
        """
        
        oc_get = oc.OmegaConf.select
        oc_set = oc.OmegaConf.update
        
        if ssh_config is None:
            ssh_config = SSHConfig()
            ssh_config.enable = False
            ssh_config.host_port = None
        
        # set ssh
        enable_ssh = ssh_config.enable
        
        # if enable_ssh:
        oc_set(build_compose, 'ssh.enable', enable_ssh)
        
        # in-container port
        ssh_port = ssh_config.port
        oc_set(build_compose, 'ssh.port', ssh_port)
        
        # users
        ssh_users = ssh_config.users
        _ssh_names : list[str] = []
        _ssh_pwds : list[str] = []
        _ssh_pubkeys : list[str] = []
        _ssh_privkeys : list[str] = []
        _ssh_uids : list[str] = []
        
        for name, info in ssh_users.items():
            _ssh_names.append(name)
            
            # Handle password
            pw = info.password
            if pw is None:
                _ssh_pwds.append('')
            else:
                _ssh_pwds.append(str(pw))   # convert to string, in case it's a number
            
            # Handle public key sources
            pubkey_path = self._process_public_key_sources(name, info)
            _ssh_pubkeys.append(pubkey_path)
            
            # Handle private key sources
            privkey_path = self._process_private_key_sources(name, info)
            _ssh_privkeys.append(privkey_path)
            
            # Handle UID
            uid = info.uid
            if uid is not None:
                _ssh_uids.append(str(uid))
            else:
                _ssh_uids.append('')
                
        # set config - ensure consistent comma-separated format with empty placeholders
        # This ensures that each user gets the correct index when parsing in shell scripts
        oc_set(build_compose, 'ssh.username', ','.join(_ssh_names))
        oc_set(build_compose, 'ssh.password', ','.join(_ssh_pwds))
        oc_set(build_compose, 'ssh.pubkey_file', ','.join(_ssh_pubkeys))
        oc_set(build_compose, 'ssh.privkey_file', ','.join(_ssh_privkeys))
        oc_set(build_compose, 'ssh.uid', ','.join(_ssh_uids))
        
    def _apply_device(self, device_config : DeviceConfig, run_compose : DictConfig) -> None:
        """
        Apply device-related configurations to the Docker Compose run arguments.

        This specifies the primary device for the container (e.g., 'cpu' or 'gpu'),
        affecting resource allocation and runtime behavior.

        Parameters
        ----------
        device_config : DeviceConfig
            The user's device configuration.
        run_compose : DictConfig
            The 'run' section of the Docker Compose configuration to be updated.
        """
        device_name = device_config.type
        if device_name is None:
            device_name = Defaults.RunDevice
        
        # set to compose
        oc.OmegaConf.update(run_compose, 'run.device', device_name)
        
    def _process_config_and_apply_x_compose(self, user_config : UserConfig, compose_template : DictConfig) -> None:
        """
        Process the main user config and apply settings to the pre-resolution compose template.

        This method iterates through the stages defined in the user's configuration
        (e.g., `stage_1`, `stage_2`) and applies their respective settings for image,
        SSH, proxy, APT, and custom scripts to the `x-cfg-stage-*` sections
        of the compose template.

        Parameters
        ----------
        user_config : UserConfig
            The fully parsed user configuration object.
        compose_template : DictConfig
            The Docker Compose template to be updated in-place. This template
            should contain `x-cfg-stage-*` sections for pre-resolution values.
        """
        user_cfg = user_config
        compose_cfg = compose_template
        oc_get = oc.OmegaConf.select
        oc_set = oc.OmegaConf.update
        
        user_compose_obj = [
            (user_cfg.stage_1, oc_get(compose_cfg, 'x-cfg-stage-1')),
            (user_cfg.stage_2, oc_get(compose_cfg, 'x-cfg-stage-2')),
        ]
        
        install_root_host : str = self.m_host_dir
        oc_set(compose_cfg, 'x-paths.installation_root_host', install_root_host)

        for ith_stage, _configs in enumerate(user_compose_obj):
            _stage, _compose = _configs
            if _stage is None:
                continue
            
            build_compose = oc_get(_compose, 'build')
            run_compose = oc_get(_compose, 'run')
            
            # set base
            image_config = _stage.image
            assert image_config is not None, 'Image configuration must be provided'
            assert image_config.output is not None, 'Output image name must be provided'
            if ith_stage == 0:
                assert image_config.base is not None, 'Base image must be provided for stage 1'
                oc_set(build_compose, 'base_image', image_config.base)
                oc_set(build_compose, 'output_image_name', image_config.output)
            elif ith_stage == 1:
                # use the output of stage 1 as the base image if not specified
                if user_cfg.stage_1 is not None and user_cfg.stage_1.image is not None:
                    base_image = image_config.base if image_config.base else user_cfg.stage_1.image.output
                else:
                    base_image = image_config.base
                oc_set(build_compose, 'base_image', base_image)
                oc_set(build_compose, 'output_image_name', image_config.output)
            
            # ssh, can be None
            ssh_config = _stage.ssh
            if ssh_config is not None:
                assert ith_stage == 0, 'SSH is only available for stage 1'
            self._apply_ssh_to_x_compose(ssh_config, build_compose = build_compose)
        
            # proxy
            proxy_config = _stage.proxy
            if proxy_config is not None:
                # assert ith_stage == 0, 'Proxy is only available for stage 1'
                self._apply_proxy(proxy_config, build_compose = build_compose)
                
            # apt
            apt_config = _stage.apt
            if apt_config is not None:
                assert ith_stage == 0, 'APT is only available for stage 1'
                self._apply_apt(apt_config, build_compose=build_compose)
            
            # custom scripts
            custom_config = _stage.custom
            if custom_config is not None:
                self._check_custom_scripts(custom_config)
                
            # device
            if _stage.device is not None and _stage.device.type is not None:
                oc_set(run_compose, 'device', _stage.device.type)
        
    def _apply_config_to_resolved_compose(self, user_config : UserConfig, compose_template : DictConfig) -> None:
        """
        Apply final configurations to the fully resolved Docker Compose object.

        This method handles settings that depend on the resolved values from the
        compose template, such as port mappings, environment variables, and storage
        volumes. It directly modifies the `services` section of the final compose object.

        Parameters
        ----------
        user_config : UserConfig
            The fully parsed user configuration object.
        compose_template : DictConfig
            The resolved Docker Compose configuration to be updated in-place.
        """
        
        stages : list[tuple[Optional[StageConfig], Optional[DictConfig]]] = [
            (user_config.stage_1, oc.OmegaConf.select(compose_template, 'services.stage-1')),
            (user_config.stage_2, oc.OmegaConf.select(compose_template, 'services.stage-2')),
        ]
        
        # this will accumulate from stage 1 to stage 2
        port_dict : dict[int, int] = {}
        env_dict : dict[str, str] = {}
        
        for ith_stage, _data in enumerate(stages):
            stage_config, stage_compose = _data
            if stage_config is None or stage_compose is None:
                continue
                        
            # port mapping
            if stage_config.ports is not None:
                _port_dict = port_mapping_str_to_dict(stage_config.ports)
                port_dict.update(_port_dict)
            
            if stage_config.ssh is not None and stage_config.ssh.host_port is not None:
                port_dict[stage_config.ssh.host_port] = stage_config.ssh.port
            port_strings = port_mapping_dict_to_str(port_dict)
            
            # from rich import print as pprint
            # logging.info(f'Port mappings: {port_strings}')
            # pprint(oc.OmegaConf.to_yaml(stage_compose))
            oc.OmegaConf.update(stage_compose, 'ports', port_strings)
            # pprint(oc.OmegaConf.to_yaml(stage_compose))
            
            # environment variables
            if stage_config.environment is not None:
                _env_dict = stage_config.get_environment_as_dict()
                if _env_dict is not None:
                    env_dict.update(_env_dict)
            # env_strings : list[str] = [f'{k}={v}' for k, v in env_dict.items()]
            oc.OmegaConf.update(stage_compose, 'environment', env_dict)
            
            # deal with storage
            name2storage : dict[str, StorageOption] = {}
            if stage_config.storage is not None and ith_stage==1:   # only stage 2 has storage
                name2storage.update(stage_config.storage)
            if stage_config.mount is not None:
                name2storage.update(stage_config.mount)
                
            # create storage in docker compose
            vol_mapping_strings : list[str] = []
            for prefix, storage_opt in name2storage.items():
                # in-container path
                if prefix in StoragePrefixes.get_all_prefixes():
                    vol_path = StoragePaths.HardVolume + '/' + prefix
                else:
                    if storage_opt.dst_path is None:
                        raise ValueError(f"Storage '{prefix}' must have dst_path specified")
                    vol_path = storage_opt.dst_path
                    
                # mapping
                if storage_opt.type == StorageTypes.AutoVolume:
                    # add volume to docker compose
                    oc.OmegaConf.update(compose_template, f'volumes.{prefix}', {})
                    
                    # map volume to soft path
                    vol_mapping_strings.append(f'{prefix}:{vol_path}')
                elif storage_opt.type == StorageTypes.ManualVolume:
                    assert storage_opt.volume_name is not None, 'volume_name must be provided for manual-volume storage'
                    
                    # add volume to docker compose
                    oc.OmegaConf.update(compose_template, f'volumes.{prefix}', 
                                        {'external': True, 'name': storage_opt.volume_name})
                    
                    # map volume to soft path
                    vol_mapping_strings.append(f'{prefix}:{vol_path}')
                elif storage_opt.type == StorageTypes.Host:
                    assert storage_opt.host_path is not None, 'host_path must be provided for host storage'
                    
                    # map host path to soft path
                    vol_mapping_strings.append(f'{storage_opt.host_path}:{vol_path}')
                elif storage_opt.type == StorageTypes.Image:
                    # nothing to do here
                    pass
            
            # write to compose
            oc.OmegaConf.update(stage_compose, 'volumes', vol_mapping_strings)
        
    @staticmethod
    def _parse_script_entry(script_entry: str) -> Tuple[str, str]:
        """
        Parse a script entry to separate script path from parameters.
        
        Args:
            script_entry: Script entry like 'stage-1/custom/my-script.sh --param1=value1 --param2="value with spaces"'
            
        Returns:
            Tuple of (script_path, parameters_string)
            
        Examples:
            'stage-1/custom/script.sh' -> ('stage-1/custom/script.sh', '')
            'stage-1/custom/script.sh --verbose' -> ('stage-1/custom/script.sh', '--verbose')
            'stage-1/custom/script.sh --param="value with spaces"' -> ('stage-1/custom/script.sh', '--param="value with spaces"')
        """
        try:
            # Use shlex to parse shell-like arguments safely
            tokens = shlex.split(script_entry.strip())
        except ValueError as e:
            # If shlex parsing fails (e.g., unmatched quotes), treat entire string as script path
            logging.warning(f"Failed to parse script entry '{script_entry}': {e}. Treating as script path only.")
            return script_entry.strip(), ""
            
        if not tokens:
            return "", ""
            
        script_path = tokens[0]
        
        if len(tokens) == 1:
            # No parameters
            return script_path, ""
        else:
            # Rejoin parameters with proper shell escaping
            parameters = []
            for token in tokens[1:]:
                # If token contains spaces or special chars, quote it
                if ' ' in token or '"' in token or "'" in token or any(c in token for c in ['&', '|', ';', '(', ')', '<', '>', '$', '`', '\\', '!', '?', '*', '[', ']']):
                    # Use shlex.quote to properly escape the token
                    parameters.append(shlex.quote(token))
                else:
                    parameters.append(token)
            
            return script_path, " ".join(parameters)
    
    def _generate_script_text(self, on_what:str, filelist : Optional[list[str]]) -> str:
        """
        Generate the content of a shell script that executes a list of user scripts.

        This creates a wrapper script that calls each user-provided script for a
        specific lifecycle event (e.g., 'on-build').

        Parameters
        ----------
        on_what : str
            The lifecycle event name (e.g., 'on-build', 'on-first-run'). This is
            used for logging within the generated script.
        filelist : Optional[list[str]]
            A list of script entries to execute. Each entry can include a path
            and command-line arguments.

        Returns
        -------
        str
            The complete text content of the generated shell script.
        """
        cmds : list[str] = [
            "DIR=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" && pwd )\" ",
            f"echo \"Executing $DIR/_custom-{on_what}.sh\" "
        ]
        
        if filelist:
            if on_what == 'on-user-login':
                # for user login scripts, we use source instead of bash
                for script_entry in filelist:
                    script_path, parameters = self._parse_script_entry(script_entry)
                    if parameters:
                        # Note: source command with parameters - parameters are passed as positional args
                        cmds.append(f"source $DIR/../../{script_path} {parameters}")
                    else:
                        cmds.append(f"source $DIR/../../{script_path}")
            else:
                for script_entry in filelist:
                    script_path, parameters = self._parse_script_entry(script_entry)
                    if parameters:
                        cmds.append(f"bash $DIR/../../{script_path} {parameters}")
                    else:
                        cmds.append(f"bash $DIR/../../{script_path}")
            
        return '\n'.join(cmds)
    
    def _generate_etc_environment(self, user_config : UserConfig) -> None:
        """
        Generate environment files for each stage.

        Creates files containing environment variables that will be sourced by the
        container. These are stored in the host's installation directory.

        Parameters
        ----------
        user_config : UserConfig
            The user configuration object containing environment settings for each stage.
        """
        
        # stage 1
        # write to file
        filename = f'{self.m_project_dir}/{self.m_host_dir}/stage-1/generated/_etc_environment.sh'
        
        # if directory does not exist, create it
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        if user_config.stage_1 is not None and user_config.stage_1.environment:
            env_dict = user_config.stage_1.get_environment_as_dict()
            
            logging.info(f'Writing env to {filename}')
            with open(filename, 'w+') as f:
                if env_dict is not None:
                    for k, v in env_dict.items():
                        f.write(f'{k}={v}\n')
        else:
            # write an empty file
            logging.info(f'Writing empty env file to {filename}')
            with open(filename, 'w+') as f:
                f.write('')
        
        # stage 2
        # write to file
        filename = f'{self.m_project_dir}/{self.m_host_dir}/stage-2/generated/_etc_environment.sh'
        
        # if directory does not exist, create it
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if user_config.stage_2 is not None and user_config.stage_2.environment:
            env_dict = user_config.stage_2.get_environment_as_dict()
            
            logging.info(f'Writing env to {filename}')
            with open(filename, 'w+') as f:
                if env_dict is not None:
                    for k, v in env_dict.items():
                        f.write(f'{k}={v}\n')
        else:
            # write an empty file
            logging.info(f'Writing empty env file to {filename}')
            with open(filename, 'w+') as f:
                f.write('')
    
    def _generate_script_files(self, user_config : UserConfig) -> None:
        """
        Generate all necessary wrapper and helper script files.

        This method orchestrates the creation of scripts for all lifecycle events
        (`on-build`, `on-first-run`, etc.) for each stage, as well as handling
        the custom entry point configuration.

        Parameters
        ----------
        user_config : UserConfig
            The user configuration object containing custom script definitions.
        """
        
        infos : list[tuple[str, Optional[StageConfig]]] = [
            ('stage-1', user_config.stage_1),
            ('stage-2', user_config.stage_2),
        ]
        
        for name, stage_config in infos:
            if stage_config is None or stage_config.custom is None:
                # if the stage or custom section is not provided, we still need to generate the empty script files
                on_build_list = []
                on_first_run_list = []
                on_every_run_list = []
                on_user_login_list = []
                on_entry_script = None
            else:
                on_build_list = stage_config.custom.on_build
                on_first_run_list = stage_config.custom.on_first_run
                on_every_run_list = stage_config.custom.on_every_run
                on_user_login_list = stage_config.custom.on_user_login
                on_entry_script = stage_config.custom.get_entry_script()
            
            on_build_script = self._generate_script_text('on-build', on_build_list)
            filename_build = f'{self.m_project_dir}/{self.m_host_dir}/{name}/generated/_custom-on-build.sh'
            os.makedirs(os.path.dirname(filename_build), exist_ok=True)
            logging.info(f'Writing to {filename_build}')
            with open(filename_build, 'w+') as f:
                f.write(on_build_script)
            
            on_first_run_script = self._generate_script_text('on-first-run', on_first_run_list)
            filename_first_run = f'{self.m_project_dir}/{self.m_host_dir}/{name}/generated/_custom-on-first-run.sh'
            os.makedirs(os.path.dirname(filename_first_run), exist_ok=True)
            logging.info(f'Writing to {filename_first_run}')
            with open(filename_first_run, 'w+') as f:
                f.write(on_first_run_script)
            
            on_every_run_script = self._generate_script_text('on-every-run', on_every_run_list)
            filename_every_run = f'{self.m_project_dir}/{self.m_host_dir}/{name}/generated/_custom-on-every-run.sh'
            os.makedirs(os.path.dirname(filename_every_run), exist_ok=True)
            logging.info(f'Writing to {filename_every_run}')
            with open(filename_every_run, 'w+') as f:
                f.write(on_every_run_script)    
                
            on_user_login_script = self._generate_script_text('on-user-login', on_user_login_list)
            filename_user_login = f'{self.m_project_dir}/{self.m_host_dir}/{name}/generated/_custom-on-user-login.sh'
            os.makedirs(os.path.dirname(filename_user_login), exist_ok=True)
            logging.info(f'Writing to {filename_user_login}')
            with open(filename_user_login, 'w+') as f:
                f.write(on_user_login_script)
                
            # Handle custom entry point
            if on_entry_script is not None:
                # Parse script path and default arguments
                script_path, default_args = self._parse_script_and_args(on_entry_script)
                
                # Store script path
                custom_entry_path_file = f'{self.m_project_dir}/{self.m_host_dir}/{name}/internals/custom-entry-path'
                os.makedirs(os.path.dirname(custom_entry_path_file), exist_ok=True)
                logging.info(f'Writing custom entry path to {custom_entry_path_file}')
                # Convert the script path to absolute path within the container
                container_script_path = f'$PEI_STAGE_DIR_{name.replace("stage-", "").upper()}/{script_path}'
                with open(custom_entry_path_file, 'w+') as f:
                    f.write(container_script_path)
                
                # Store default arguments
                custom_entry_args_file = f'{self.m_project_dir}/{self.m_host_dir}/{name}/internals/custom-entry-args'
                logging.info(f'Writing custom entry default args to {custom_entry_args_file}')
                with open(custom_entry_args_file, 'w+') as f:
                    # Join arguments with spaces, properly escaping for shell
                    if default_args:
                        f.write(' '.join(shlex.quote(arg) for arg in default_args))
                    else:
                        f.write('')  # Empty file for no default arguments
            
    
    def process(self, remove_extra : bool = True, generate_custom_script_files : bool = True) -> DictConfig:
        """
        Process the full configuration to generate the final Docker Compose object.

        This is the main public method that orchestrates the entire process:
        1. Parses the user configuration.
        2. Applies settings to the pre-resolution compose template.
        3. Resolves the compose template variables.
        4. Applies final settings to the resolved compose object.
        5. Generates all necessary helper scripts.
        6. Cleans up the final compose object.

        Parameters
        ----------
        remove_extra : bool, optional
            If True (default), remove the `x-*` helper keys from the final compose object.
        generate_custom_script_files : bool, optional
            If True (default), generate the custom script files on the host.

        Returns
        -------
        DictConfig
            The final, processed Docker Compose configuration.

        Raises
        ------
        ValueError
            If the compose template is not set before processing.
        """
        # user_cfg = self.m_config
        # compose_cfg = self.m_compose_template.copy()
        
        # read files for test
        # fn_template = r'templates/base-image.yml'
        # fn_config = r'templates/config-template-full.yml'
        # user_cfg = oc.OmegaConf.load(fn_config)
        # compose_cfg = oc.OmegaConf.load(fn_template)
        
        config_dict = oc.OmegaConf.to_container(self.m_config, resolve=True)
        
        # convert environment from list to dict
        if isinstance(config_dict, dict):
            for stage in ['stage_1', 'stage_2']:
                if stage not in config_dict:
                    continue
                
                # Handle environment conversion
                if 'environment' in config_dict[stage]:
                    env = config_dict[stage]['environment']
                    if env is not None and isinstance(env, list):
                        config_dict[stage]['environment'] = env_str_to_dict(env)
                
                # Handle on_entry conversion from string to list
                if 'custom' in config_dict[stage] and config_dict[stage]['custom'] is not None:
                    custom = config_dict[stage]['custom']
                    if 'on_entry' in custom and custom['on_entry'] is not None:
                        on_entry = custom['on_entry']
                        if isinstance(on_entry, str):
                            # Convert string to single-element list
                            config_dict[stage]['custom']['on_entry'] = [on_entry]
        
        # parse the user config
        user_config : UserConfig = cattrs.structure(config_dict, UserConfig)
        
        # apply the user config to the compose template
        if self.m_compose_template is None:
            raise ValueError("compose_template is None")
        compose_template : DictConfig = self.m_compose_template.copy()
        self._process_config_and_apply_x_compose(user_config, compose_template)
        
        # resolve the compose template
        # oc.OmegaConf.resolve(compose_template)
        _resolve_dict = oc.OmegaConf.to_container(compose_template, resolve=True, 
                                                  throw_on_missing=True, 
                                                  structured_config_mode=oc.SCMode.DICT_CONFIG)
        compose_resolved = oc.OmegaConf.create(_resolve_dict)
        assert isinstance(compose_resolved, DictConfig), "Expected DictConfig"
        
        # apply the stage configuration to the compose template again
        self._apply_config_to_resolved_compose(user_config, compose_resolved)
        
        # generate script files
        if generate_custom_script_files:
            self._generate_script_files(user_config)
            
        # generate etc/environment files
        self._generate_etc_environment(user_config)
        
        # strip the x-? from the compose template
        if remove_extra:
            useless_keys = []
            for key in list(compose_resolved.keys()):
                if isinstance(key, str) and key.startswith('x-'):
                    useless_keys.append(key)
            for key in useless_keys:
                del compose_resolved[key]
                
        # if stage-2 does not exist, remove it from the compose template
        if user_config.stage_2 is None:
            del compose_resolved['services']['stage-2']
            
        # resolve the compose template
        self.m_compose_output = compose_resolved
        return compose_resolved
    
    def _process_public_key_sources(self, user_name: str, user_info: SSHUserConfig) -> str:
        """
        Process public key from file or text, return container path.
        Supports relative paths, absolute paths, and ~ syntax for system SSH keys.
        
        Args:
            user_name: SSH username
            user_info: SSHUserConfig object
            
        Returns:
            Container path to public key file, or empty string if none
        """
        from pei_docker.pei_utils import write_ssh_key_to_temp_file, resolve_ssh_key_path, read_ssh_key_content
        
        # Handle pubkey_file
        if user_info.pubkey_file is not None and len(user_info.pubkey_file) > 0:
            pubkey_file: str = user_info.pubkey_file
            
            # NEW: Check if absolute path or ~ syntax
            if os.path.isabs(pubkey_file) or pubkey_file == '~':
                # Resolve absolute path or system SSH key
                resolved_path = resolve_ssh_key_path(pubkey_file, prefer_public=True)
                key_content = read_ssh_key_content(resolved_path)
                
                # Write to temp file (similar to pubkey_text processing)
                relative_path = write_ssh_key_to_temp_file(
                    key_content, 
                    'pubkey',  # key type not needed for public keys
                    user_name, 
                    self.m_project_dir, 
                    is_public=True
                )
                return self.m_container_dir + '/' + relative_path
            else:
                # EXISTING: Relative path handling (unchanged)
                host_path = f'{self.m_project_dir}/{self.m_host_dir}/{pubkey_file}'
                if not os.path.exists(host_path):
                    raise FileNotFoundError(f'Pubkey file {host_path} not found')
                return self.m_container_dir + '/' + pubkey_file
        
        # Handle pubkey_text
        elif user_info.pubkey_text is not None and len(user_info.pubkey_text.strip()) > 0:
            # Write public key text to temporary file
            relative_path = write_ssh_key_to_temp_file(
                user_info.pubkey_text, 
                'pubkey',  # key type not needed for public keys
                user_name, 
                self.m_project_dir, 
                is_public=True
            )
            return self.m_container_dir + '/' + relative_path
        
        return ''
    
    def _process_private_key_sources(self, user_name: str, user_info: SSHUserConfig) -> str:
        """
        Process private key from file or text, return container path.
        Supports relative paths, absolute paths, and ~ syntax for system SSH keys.
        Note: Public key generation happens inside the container, not on host.
        
        Args:
            user_name: SSH username
            user_info: SSHUserConfig object
            
        Returns:
            Container path to private key file, or empty string if none
        """
        from pei_docker.pei_utils import write_ssh_key_to_temp_file, resolve_ssh_key_path, read_ssh_key_content
        
        # Handle privkey_file
        if user_info.privkey_file is not None and len(user_info.privkey_file) > 0:
            privkey_file: str = user_info.privkey_file
            
            # NEW: Check if absolute path or ~ syntax
            if os.path.isabs(privkey_file) or privkey_file == '~':
                # Resolve absolute path or system SSH key
                resolved_path = resolve_ssh_key_path(privkey_file, prefer_public=False)
                key_content = read_ssh_key_content(resolved_path)
                
                # Write to temp file (similar to privkey_text processing)
                privkey_relative_path = write_ssh_key_to_temp_file(
                    key_content,
                    'privkey',  # key type not critical for file naming
                    user_name,
                    self.m_project_dir,
                    is_public=False
                )
                return self.m_container_dir + '/' + privkey_relative_path
            else:
                # EXISTING: Relative path handling (unchanged)
                host_path = f'{self.m_project_dir}/{self.m_host_dir}/{privkey_file}'
                if not os.path.exists(host_path):
                    raise FileNotFoundError(f'Private key file {host_path} not found')
                return self.m_container_dir + '/' + privkey_file
        
        # Handle privkey_text
        elif user_info.privkey_text is not None and len(user_info.privkey_text.strip()) > 0:
            privkey_content = user_info.privkey_text
            
            # Write private key to file (public key generation will happen in container)
            privkey_relative_path = write_ssh_key_to_temp_file(
                privkey_content,
                'privkey',  # key type not critical for file naming
                user_name,
                self.m_project_dir,
                is_public=False
            )
            
            return self.m_container_dir + '/' + privkey_relative_path
        
        return ''