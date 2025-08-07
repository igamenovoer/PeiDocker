"""
Utility function for creating PeiDocker projects.

This module provides a direct function for creating projects without Click decorators,
allowing it to be called from other Python code like the GUI.
"""

import os
import shutil
import logging
from pei_docker.config_processor import Defaults

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s]\t%(message)s')


def create_project_direct(project_dir: str, with_examples: bool = True) -> None:
    """
    Create a new PeiDocker project with template files and directory structure.
    
    This is the same logic as the CLI create command, but without Click decorators,
    making it callable from other Python code.
    
    Parameters
    ----------
    project_dir : str
        Path where the project directory will be created.
    with_examples : bool
        Whether to include example configuration files. Default is True.
    """
    logging.info(f'Creating PeiDocker project in {project_dir}')
    os.makedirs(project_dir, exist_ok=True)
    
    # copy all the files and folders in project_files to the output dir
    this_dir: str = os.path.dirname(os.path.realpath(__file__))
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
    src_config_template: str = f'{this_dir}/{Defaults.ConfigTemplatePath}'
    dst_config_template: str = f'{project_dir}/{Defaults.OutputConfigName}'
    logging.info(f'Copying config template {src_config_template} to {dst_config_template}')
    shutil.copy2(src_config_template, dst_config_template)
    
    src_compose_template: str = f'{this_dir}/{Defaults.ComposeTemplatePath}'
    dst_compose_template: str = f'{project_dir}/{Defaults.OutputComposeTemplateName}'
    logging.info(f'Copying compose template {src_compose_template} to {dst_compose_template}')
    shutil.copy2(src_compose_template, dst_compose_template)
    
    # copy example files to the project dir
    if with_examples:
        examples_dir: str = f'{this_dir}/{Defaults.ConfigExamplesDir}'
        
        # copy this dir to project_dir/examples
        examples_dst_dir: str = f'{project_dir}/examples'
        logging.info(f'Copying examples from {examples_dir} to {examples_dst_dir}')
        shutil.copytree(examples_dir, examples_dst_dir, dirs_exist_ok=True)
    
    logging.info('Done')