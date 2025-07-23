# main command of PeiDocker utility
import logging

# configure logging
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
def cli():
    pass
    
# create the output dir and copy the template files there
@click.command()
@click.option('--project-dir', '-p', help='project directory', required=True, 
              type=click.Path(exists=False, file_okay=False))
@click.option('--with-examples', '-e', is_flag=True, default=True, 
              help='copy example files to the project dir')
def create(project_dir : str, with_examples : bool):
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
        
# generate the docker compose file from the config file
@click.command()
@click.option('--project-dir', '-p', help='project directory (default: current working directory)', required=False, 
              default=None, type=click.Path(exists=False, file_okay=False))
@click.option('--config', '-c', default=f'{Defaults.OutputConfigName}', help='config file name, relative to the project dir', 
              type=click.Path(exists=False, file_okay=True, dir_okay=False))
@click.option('--full-compose', '-f', is_flag=True, default=False, help='generate full compose file with x-??? sections')
def configure(project_dir:str, config:str, full_compose:bool):
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
    
    # Process environment variable substitution
    logging.info('Processing environment variable substitution')
    in_config = process_config_env_substitution(in_config)
    
    # read the compose template file
    compose_path : str = os.path.join(project_dir, Defaults.OutputComposeTemplateName)
    in_compose = oc.OmegaConf.load(compose_path)
    
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
    """Run a docker command and return (success, output)"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def get_containers_using_image(image_name: str) -> list[str]:
    """Get list of container IDs using the specified image"""
    success, output = run_docker_command(['docker', 'ps', '-a', '--filter', f'ancestor={image_name}', '--format', '{{.ID}}'])
    if success and output:
        return output.split('\n')
    return []

def stop_and_remove_containers(container_ids: list[str], force_yes: bool = False) -> bool:
    """Stop and remove containers. Returns True if user confirmed or force_yes is True"""
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
    """Remove Docker image. Returns True if user confirmed or force_yes is True"""
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

# remove images built by the project
@click.command()
@click.option('--project-dir', '-p', help='project directory', required=True, 
              type=click.Path(exists=True, file_okay=False))
@click.option('--yes', '-y', is_flag=True, default=False, help='skip confirmation prompts')
def remove(project_dir: str, yes: bool):
    """Remove Docker images and containers created by this project"""
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
        
cli.add_command(create)
cli.add_command(configure)
cli.add_command(remove)

if __name__ == '__main__':
    # Run the command line interface
    cli()