"""
PeiDocker CLI - Main Command Line Interface.

This module provides the primary command-line interface for PeiDocker, implementing
three main commands for Docker container project lifecycle management: create,
configure, and remove.

Command Line Usage
------------------
The CLI provides three main commands:

1. **Create a new project**:
   pei-docker-cli create -p ./my-project [--with-examples]
   
   Creates project directory structure with templates, configuration files,
   and optionally example configurations.

2. **Configure project** (generate docker-compose.yml):
   pei-docker-cli configure -p ./my-project [-c config.yml] [--full-compose]
   
   Processes user configuration and generates Docker Compose files for
   container deployment.

3. **Remove project resources**:
   pei-docker-cli remove -p ./my-project [--yes]
   
   Safely removes Docker images and containers created by the project,
   with optional confirmation bypass.

Architecture
------------
The CLI orchestrates the following components:
- Configuration processing via PeiConfigProcessor
- Environment variable substitution for deployment flexibility
- Docker Compose template generation and transformation
- Safe Docker resource cleanup with dependency checking

Environment Variable Substitution
---------------------------------
All configuration files support Docker Compose-style variable substitution:
- ${VAR}: Replace with environment variable value
- ${VAR:-default}: Replace with environment variable or default value

This enables deployment-specific customization without modifying config files.

Safety Features
---------------
- Confirmation prompts before destructive operations
- Container dependency checking before image removal
- Graceful handling of missing Docker resources
- Comprehensive error reporting and logging

Examples
--------
Create a new project with examples:
    pei-docker-cli create -p ./my-docker-project --with-examples
    
Configure project with custom config:
    pei-docker-cli configure -p ./my-docker-project -c my-config.yml
    
Remove all project resources without prompting:
    pei-docker-cli remove -p ./my-docker-project --yes

Notes
-----
This CLI requires Docker to be installed and accessible on the system.
All operations work with the project directory structure created by the
'create' command.
"""

# Main command implementation for PeiDocker utility
import logging

# Configure logging with consistent format
logging.basicConfig(level=logging.INFO, format='[%(levelname)s]\t%(message)s')

import click
import os
import shutil
import subprocess
import sys

import omegaconf as oc
from pei_docker.config_processor import *
from pei_docker.pei_utils import process_config_env_substitution
        
@click.group()
def cli() -> None:
    """
    PeiDocker CLI - Docker Container Configuration Made Easy.
    
    Transform YAML configurations into reproducible containerized environments
    without requiring deep knowledge of Dockerfiles or docker-compose syntax.
    
    Use the subcommands 'create', 'configure', and 'remove' to manage your
    Docker container projects throughout their lifecycle.
    """
    pass
    
@click.command()
@click.option('--project-dir', '-p', help='project directory', required=True, 
              type=click.Path(exists=False, file_okay=False))
@click.option('--with-examples', '-e', is_flag=True, default=True, 
              help='copy example files to the project dir')
def create(project_dir : str, with_examples : bool) -> None:
    """
    Create a new PeiDocker project with template files and directory structure.
    
    Sets up a complete project directory containing:
    - Installation scripts and templates for Stage-1 and Stage-2
    - Configuration template (user_config.yml)
    - Docker Compose template
    - Example configurations (optional)
    - Project file structure for custom scripts and resources
    
    Parameters
    ----------
    project_dir : str
        Path where the project directory will be created. Directory will be
        created if it doesn't exist. Contents will be merged if directory exists.
    with_examples : bool
        Whether to include example configuration files. Default is True.
        Examples help users understand configuration options and patterns.
        
    Examples
    --------
    Create project with examples:
        pei-docker-cli create -p ./my-project
        
    Create project without examples:
        pei-docker-cli create -p ./my-project --no-with-examples
        
    Notes
    -----
    The created project structure follows PeiDocker's two-stage architecture:
    - installation/stage-1/: System-level setup scripts and templates
    - installation/stage-2/: Application-level configuration scripts
    - examples/: Sample configuration files for various use cases
    - user_config.yml: Main configuration template
    - compose-template.yml: Docker Compose template
    
    After creation, edit user_config.yml and run 'configure' to generate
    the final docker-compose.yml file.
    """
    logging.info(f'Creating PeiDocker project in {project_dir}')
    os.makedirs(project_dir, exist_ok=True)
    
    # the directory should be empty
    # if len(os.listdir(project_dir)) > 0:
    #     logging.error(f'Directory {project_dir} is not empty')
    #     return
    
    # copy all the files and folders in project_files to the output dir
    this_dir : str = os.path.dirname(os.path.realpath(__file__))
    project_template_dir = f'{this_dir}/project_files'    
    for item in os.listdir(project_template_dir):
        s = os.path.join(project_template_dir, item)
        d = os.path.join(project_dir, item)
        if os.path.isdir(s):
            logging.info(f'Copying directory {s} to {d}')
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            logging.info(f'Copying file {s} to {d}')
            shutil.copy2(s, d)
            
    # copy config and compose template files to the output dir
    src_config_template : str = f'{this_dir}/{Defaults.ConfigTemplatePath}'
    dst_config_template : str = f'{project_dir}/{Defaults.OutputConfigName}'
    logging.info(f'Copying config template {src_config_template} to {dst_config_template}')
    shutil.copy2(src_config_template, dst_config_template)
    
    src_compose_template : str = f'{this_dir}/{Defaults.ComposeTemplatePath}'
    dst_compose_template : str = f'{project_dir}/{Defaults.OutputComposeTemplateName}'
    logging.info(f'Copying compose template {src_compose_template} to {dst_compose_template}')
    shutil.copy2(src_compose_template, dst_compose_template)
    
    # copy example files to the project dir
    # the examples is in Defaults.ConfigExamplesDir
    if with_examples:
        examples_dir : str = f'{this_dir}/{Defaults.ConfigExamplesDir}'
        
        # copy this dir to project_dir/examples
        examples_dst_dir : str = f'{project_dir}/examples'
        logging.info(f'Copying examples from {examples_dir} to {examples_dst_dir}')
        shutil.copytree(examples_dir, examples_dst_dir, dirs_exist_ok=True)
        
    logging.info('Done')
        
@click.command()
@click.option('--project-dir', '-p', help='project directory (default: current working directory)', required=False, 
              default=None, type=click.Path(exists=False, file_okay=False))
@click.option('--config', '-c', default=f'{Defaults.OutputConfigName}', help='config file name, relative to the project dir', 
              type=click.Path(exists=False, file_okay=True, dir_okay=False))
@click.option('--full-compose', '-f', is_flag=True, default=False, help='generate full compose file with x-??? sections')
def configure(project_dir:str, config:str, full_compose:bool) -> None:
    """
    Configure PeiDocker project by generating docker-compose.yml from user configuration.
    
    Processes the user configuration file through environment variable substitution
    and the PeiDocker configuration engine to produce a complete Docker Compose
    file ready for deployment.
    
    Parameters
    ----------
    project_dir : str, optional
        Project directory containing the configuration files. If not specified,
        uses the current working directory.
    config : str, default 'user_config.yml'
        Configuration file name, relative to project directory. Can also be
        an absolute path to a config file.
    full_compose : bool, default False
        Whether to include debugging sections (x-cfg-*) in the output compose file.
        Useful for troubleshooting configuration processing.
        
    Process Flow
    ------------
    1. Load user configuration file (YAML)
    2. Process environment variable substitution (${VAR:-default} syntax)
    3. Load Docker Compose template
    4. Transform configuration through PeiConfigProcessor
    5. Generate final docker-compose.yml file
    6. Create custom script files for container lifecycle hooks
    
    Environment Variable Substitution
    ---------------------------------
    The configuration supports Docker Compose-style variable substitution:
    - ${HOME}: Replaced with HOME environment variable value
    - ${DATA_PATH:-/default/path}: Replaced with DATA_PATH or default if unset
    - ${SHARED_HOST_PATH:-/mnt/workspace}: Flexible deployment configuration
    
    Examples
    --------
    Configure with default settings:
        pei-docker-cli configure -p ./my-project
        
    Configure with custom config file:
        pei-docker-cli configure -p ./my-project -c my-custom-config.yml
        
    Generate full compose with debug sections:
        pei-docker-cli configure -p ./my-project --full-compose
        
    Notes
    -----
    After successful configuration, the project directory will contain:
    - docker-compose.yml: Ready for 'docker compose build' and 'docker compose up'
    - Generated script files in installation/stage-*/generated/
    - Environment files for container runtime
    
    The generated compose file supports the two-stage build process where
    stage-1 handles system setup and stage-2 handles application configuration.
    """
    if project_dir is None:
        project_dir = os.getcwd()
    
    logging.info(f'Configuring PeiDocker project from {project_dir}/{config}')
    # is config file a relative path?
    # if yes, then append to project dir
    # if no, then use as is
    if not os.path.isabs(config) or config == Defaults.OutputConfigName:
        config_path = os.path.join(project_dir, config)
    else:
        config_path = config

    
    # file exists?
    if not os.path.exists(config_path):
        logging.error(f'Config file {config_path} does not exist')
        return
    
    in_config = oc.OmegaConf.load(config_path)
    if not isinstance(in_config, oc.DictConfig):
        raise ValueError("Configuration file must contain a dictionary, not a list")
    
    # Process environment variable substitution
    logging.info('Processing environment variable substitution')
    in_config = process_config_env_substitution(in_config)
    
    # read the compose template file
    compose_path : str = os.path.join(project_dir, Defaults.OutputComposeTemplateName)
    in_compose = oc.OmegaConf.load(compose_path)
    if not isinstance(in_compose, oc.DictConfig):
        raise ValueError("Compose template file must contain a dictionary, not a list")
    
    # process the config file
    proc : PeiConfigProcessor = PeiConfigProcessor.from_config(in_config, in_compose, project_dir=project_dir)
    out_compose = proc.process(remove_extra=not full_compose)
    out_yaml = oc.OmegaConf.to_yaml(out_compose)
    
    # write the compose file to the same directory as config file
    out_compose_path = os.path.join(project_dir, Defaults.OutputComposeName)
    logging.info(f'Writing compose file to {out_compose_path}')
    with open(out_compose_path, 'w') as f:
        f.write(out_yaml)
    
    logging.info('Done')

def run_docker_command(cmd: list[str]) -> tuple[bool, str]:
    """
    Execute a Docker command and return success status with output.
    
    Provides a safe wrapper around Docker CLI commands with proper error
    handling and output capture. Used by the remove command for Docker
    resource management.
    
    Parameters
    ----------
    cmd : List[str]
        Docker command as a list of arguments (e.g., ['docker', 'ps', '-a'])
        
    Returns
    -------
    tuple[bool, str]
        Tuple containing:
        - bool: True if command succeeded (exit code 0), False otherwise
        - str: Command output (stdout if success, stderr if failure)
        
    Notes
    -----
    This function captures both stdout and stderr, returning the appropriate
    stream based on command success. All output is stripped of trailing whitespace.
    
    Examples
    --------
    Check if Docker is available:
        >>> success, output = run_docker_command(['docker', '--version'])
        >>> if success:
        ...     print(f"Docker version: {output}")
        
    List all containers:
        >>> success, output = run_docker_command(['docker', 'ps', '-a'])
        >>> if success:
        ...     print(f"Containers: {output}")
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def get_containers_using_image(image_name: str) -> list[str]:
    """
    Retrieve container IDs that are using the specified Docker image.
    
    Queries Docker to find all containers (running and stopped) that were
    created from the specified image. This is essential for safe image
    removal as Docker prevents removing images that have dependent containers.
    
    Parameters
    ----------
    image_name : str
        Full Docker image name including tag (e.g., "my-app:stage-1")
        
    Returns
    -------
    List[str]
        List of container IDs using the image. Empty list if no containers
        found or if Docker command fails.
        
    Notes
    -----
    Uses 'docker ps -a --filter ancestor=<image>' to find containers.
    The filter includes both running and stopped containers to ensure
    complete dependency checking before image removal.
    
    Examples
    --------
    Find containers using an image:
        >>> containers = get_containers_using_image("my-app:stage-1")
        >>> if containers:
        ...     print(f"Found {len(containers)} containers using the image")
    """
    success, output = run_docker_command(['docker', 'ps', '-a', '--filter', f'ancestor={image_name}', '--format', '{{.ID}}'])
    if success and output:
        return output.split('\n')
    return []

def stop_and_remove_containers(container_ids: list[str], force_yes: bool = False) -> bool:
    """
    Stop and remove Docker containers with optional user confirmation.
    
    Safely stops and removes the specified containers, with user confirmation
    unless bypassed. This ensures containers are properly cleaned up before
    removing their associated Docker images.
    
    Parameters
    ----------
    container_ids : List[str]
        List of Docker container IDs to stop and remove.
    force_yes : bool, default False
        If True, skip user confirmation prompts. If False, prompt user
        for confirmation before proceeding.
        
    Returns
    -------
    bool
        True if user confirmed the operation or force_yes was True.
        False if user cancelled the operation.
        
    Process
    -------
    1. If containers exist and force_yes is False, prompt for confirmation
    2. Stop all containers using 'docker stop <id>'
    3. Remove all containers using 'docker rm <id>'
    4. Log warnings for any containers that fail to stop or remove
    
    Notes
    -----
    Stopping containers gracefully allows them to clean up resources.
    Removal is necessary before Docker images can be deleted.
    Individual container failures don't stop the overall process.
    
    Examples
    --------
    Remove containers with confirmation:
        >>> container_ids = ["abc123", "def456"]
        >>> if stop_and_remove_containers(container_ids):
        ...     print("Containers removed successfully")
        
    Force removal without confirmation:
        >>> stop_and_remove_containers(container_ids, force_yes=True)
    """
    if not container_ids:
        return True
    
    if not force_yes:
        container_list = ', '.join(container_ids)
        if not click.confirm(f'Stop and remove containers: {container_list}?'):
            return False
    
    # Stop containers
    for container_id in container_ids:
        logging.info(f'Stopping container {container_id}')
        success, output = run_docker_command(['docker', 'stop', container_id])
        if not success:
            logging.warning(f'Failed to stop container {container_id}: {output}')
    
    # Remove containers
    for container_id in container_ids:
        logging.info(f'Removing container {container_id}')
        success, output = run_docker_command(['docker', 'rm', container_id])
        if not success:
            logging.warning(f'Failed to remove container {container_id}: {output}')
    
    return True

def remove_image(image_name: str, force_yes: bool = False) -> bool:
    """
    Remove a Docker image with optional user confirmation.
    
    Safely removes the specified Docker image after checking for its existence.
    Provides user confirmation unless bypassed, and handles cases where the
    image doesn't exist gracefully.
    
    Parameters
    ----------
    image_name : str
        Full Docker image name including tag to remove (e.g., "my-app:stage-1")
    force_yes : bool, default False
        If True, skip user confirmation prompts. If False, prompt user
        for confirmation before proceeding.
        
    Returns
    -------
    bool
        True if image was removed successfully, image didn't exist, or user
        confirmed the operation. False if user cancelled or removal failed.
        
    Process
    -------
    1. Check if image exists using 'docker images -q <image_name>'
    2. If image doesn't exist, return True (nothing to do)
    3. If force_yes is False, prompt user for confirmation
    4. Remove image using 'docker rmi <image_name>'
    5. Log success or failure messages
    
    Notes
    -----
    Image removal will fail if containers are using the image.
    Use stop_and_remove_containers() first to handle dependencies.
    Non-existent images are treated as success to simplify cleanup scripts.
    
    Examples
    --------
    Remove image with confirmation:
        >>> if remove_image("my-app:stage-1"):
        ...     print("Image removed or didn't exist")
        
    Force removal without confirmation:
        >>> remove_image("my-app:stage-1", force_yes=True)
    """
    # Check if image exists
    success, output = run_docker_command(['docker', 'images', '-q', image_name])
    if not success or not output:
        logging.info(f'Image {image_name} not found, skipping')
        return True
    
    if not force_yes:
        if not click.confirm(f'Remove image: {image_name}?'):
            return False
    
    logging.info(f'Removing image {image_name}')
    success, output = run_docker_command(['docker', 'rmi', image_name])
    if not success:
        logging.error(f'Failed to remove image {image_name}: {output}')
        return False
    
    logging.info(f'Successfully removed image {image_name}')
    return True

@click.command()
@click.option('--project-dir', '-p', help='project directory', required=True, 
              type=click.Path(exists=True, file_okay=False))
@click.option('--yes', '-y', is_flag=True, default=False, help='skip confirmation prompts')
def remove(project_dir: str, yes: bool) -> None:
    """
    Remove Docker images and containers created by PeiDocker project.
    
    Safely removes all Docker resources (images and containers) associated with
    the specified project by parsing the generated docker-compose.yml file and
    cleaning up dependencies in the correct order.
    
    Parameters
    ----------
    project_dir : str
        Path to the PeiDocker project directory. Must exist and contain
        a docker-compose.yml file generated by the 'configure' command.
    yes : bool, default False
        Skip confirmation prompts for destructive operations. When False,
        prompts user before removing each set of containers and images.
        
    Safety Features
    ---------------
    - Checks for docker-compose.yml existence before proceeding
    - Identifies container dependencies before removing images
    - Stops containers gracefully before removal
    - Provides individual confirmation for each resource type
    - Handles missing Docker resources gracefully
    - Continues cleanup even if individual operations fail
    
    Process Flow
    ------------
    1. Load and parse docker-compose.yml from project directory
    2. Extract image names from all services
    3. For each image:
       a. Find containers using the image
       b. Stop and remove containers (with confirmation)
       c. Remove the image (with confirmation)
    4. Report cleanup completion status
    
    Examples
    --------
    Remove with confirmations:
        pei-docker-cli remove -p ./my-project
        
    Force removal without prompts:
        pei-docker-cli remove -p ./my-project --yes
        
    Notes
    -----
    This command requires:
    - Project directory created by 'create' command
    - docker-compose.yml file generated by 'configure' command
    - Docker daemon running and accessible
    
    The removal process is designed to be safe and reversible - images can
    always be rebuilt using 'docker compose build' after cleanup.
    
    Warning
    -------
    This operation removes Docker images and containers permanently.
    Ensure you have saved any important data from containers before removal.
    """
    logging.info(f'Removing images from PeiDocker project in {project_dir}')
    
    # Look for the generated docker-compose.yml file
    compose_path = os.path.join(project_dir, Defaults.OutputComposeName)
    
    # Check if docker-compose.yml exists
    if not os.path.exists(compose_path):
        logging.error(f'Docker compose file {compose_path} does not exist. Run "configure" command first.')
        return
    
    try:
        # Load docker-compose.yml
        compose_config = oc.OmegaConf.load(compose_path)
        
        # Extract image names from services
        images_to_remove = []
        
        if 'services' in compose_config:
            for service_name, service_config in compose_config.services.items():
                if 'image' in service_config:
                    image_name = service_config.image
                    if image_name and image_name not in images_to_remove:
                        images_to_remove.append(image_name)
        
        if not images_to_remove:
            logging.info('No images found in configuration')
            return
        
        logging.info(f'Found images to remove: {", ".join(images_to_remove)}')
        
        # Process each image
        for image_name in images_to_remove:
            # Find containers using this image
            container_ids = get_containers_using_image(image_name)
            
            if container_ids:
                logging.info(f'Found {len(container_ids)} container(s) using image {image_name}')
                if not stop_and_remove_containers(container_ids, yes):
                    logging.info(f'Skipping removal of image {image_name} due to user cancellation')
                    continue
            else:
                logging.info(f'No containers found using image {image_name}')
            
            # Remove the image
            if not remove_image(image_name, yes):
                logging.info(f'Skipping due to user cancellation or error')
                continue
        
        logging.info('Cleanup completed')
        
    except Exception as e:
        logging.error(f'Error processing config file: {e}')
        sys.exit(1)
        
# Register commands with the CLI group
cli.add_command(create)
cli.add_command(configure) 
cli.add_command(remove)

if __name__ == '__main__':
    # Run the command line interface when script is executed directly
    cli()