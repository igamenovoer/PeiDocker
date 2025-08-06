# Terminology for many tasks

This file contains the terminology that is useful for many tasks, so that we are consistent in our language and avoid confusion.

## Project Terminology

These terminologies are about the idea of the PeiDocker project, used project-wide.

- `user_config.yml`: This is the configuration file for the PeiDocker project, which contains settings for SSH, environment variables, and other configurations. It is located in the project directory and can be edited to customize the project. Its master template is in `src/pei_docker/templates/config-template-full.yml`
  
- `stage-1` and `stage-2`: These refer to the two stages of the PeiDocker project. Stage-1 is the initial stage where the base image is built, the purpose is to install system-level dependencies using `apt` or alike, intended to be useful for many applications. Stage-2 is the second stage where the docker image is built, based on the image from stage-1, and it is intended to be used for a specific application, installing application-level dependencies (like `pip`, `npm`, installing `ros2` packages, etc.). 
  
- `peidocker-data-model`: This is the data model that represents the `user_config.yml` file during the configuration process, mainly used by the `pei-docker-cli` command line interface and `config_processor.py` module. source code is in `src/pei_docker/user_config.py`.

- `pei-docker-cli`: the command line interface for PeiDocker, used to create and manage projects, source code is in `src/pei_docker/pei.py`

## GUI Terminology

These terminologies are about the web-based GUI of the PeiDocker project, used in the context of the GUI tasks.

- `nicegui-web`: the web GUI implemented using `nicegui`, source code is in `src/pei_docker/webgui`

- `ui-data-model`: The data model that represents the state of the GUI, source code is in `src\pei_docker\webgui\models\ui_state.py`.

- `ui-data-adapter`: The adapter that converts between the `peidocker-data-model` and the `ui-data-model`, source code in `src\pei_docker\webgui\models\config_adapter.py`

## PeiDocker Assumptions and Conventions

- the `peidocker-data-model` source code (`src\pei_docker\user_config.py`) has defined many rules to follow, about in `user_config.yml` what is acceptable and what is not, those rules are in the docstring of different classes and methods, please read them carefully.