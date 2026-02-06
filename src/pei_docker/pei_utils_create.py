"""
Utility function for creating PeiDocker projects.

This module provides a direct function for creating projects without Click decorators,
allowing it to be called from other Python code like the GUI.
"""

import os
import shutil
import logging
import sys
from typing import Optional
from pei_docker.config_processor import Defaults

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s]\t%(message)s')


def get_available_quick_templates() -> list[str]:
    """
    Get list of available quick templates from the templates/quick directory.
    
    Returns
    -------
    list[str]
        List of template names (without 'config-' prefix and '.yml' suffix)
    """
    this_dir: str = os.path.dirname(os.path.realpath(__file__))
    quick_templates_dir = os.path.join(this_dir, 'templates', 'quick')
    
    templates = []
    if os.path.exists(quick_templates_dir):
        for file in os.listdir(quick_templates_dir):
            if file.startswith('config-') and file.endswith('.yml'):
                # Extract template name from config-<name>.yml
                template_name = file[7:-4]  # Remove 'config-' prefix and '.yml' suffix
                templates.append(template_name)
    
    return sorted(templates)


def create_project_direct(project_dir: str, with_examples: bool = True, quick: Optional[str] = None) -> None:
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
    quick : str, optional
        Name of quick template to use for user_config.yml. If not specified,
        the full template is used. Available templates: minimal, cn-dev, cn-ml
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
    
    # Always copy full template as reference_config.yml
    src_config_template: str = f'{this_dir}/{Defaults.ConfigTemplatePath}'
    dst_reference_config: str = f'{project_dir}/reference_config.yml'
    logging.info(f'Copying full config template to {dst_reference_config} as reference')
    shutil.copy2(src_config_template, dst_reference_config)
    
    # Copy appropriate template to user_config.yml based on quick option
    dst_user_config: str = f'{project_dir}/{Defaults.OutputConfigName}'
    
    if quick:
        # Validate quick template exists
        quick_template_path = f'{this_dir}/templates/quick/config-{quick}.yml'
        if not os.path.exists(quick_template_path):
            available = get_available_quick_templates()
            if available:
                logging.error(f'Quick template "{quick}" not found. Available templates: {", ".join(available)}')
            else:
                logging.error(f'Quick template "{quick}" not found. No quick templates available.')
            raise ValueError(f'Quick template "{quick}" not found')
        
        logging.info(f'Using quick template "{quick}" for {dst_user_config}')
        shutil.copy2(quick_template_path, dst_user_config)
    else:
        # Use full template for user_config.yml (default behavior)
        logging.info(f'Copying full config template to {dst_user_config}')
        shutil.copy2(src_config_template, dst_user_config)
    
    # Copy compose template
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