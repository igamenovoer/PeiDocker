# Terminology for many tasks

This file contains the terminology that is useful for many tasks, so that we are consistent in our language and avoid confusion.

## Project Terminology

These terminologies are about the idea of the PeiDocker project, used project-wide.

- `user_config.yml`: This is the configuration file for the PeiDocker project, which contains settings for SSH, environment variables, and other configurations. It is located in the project directory and can be edited to customize the project. Its master template is in `src/pei_docker/templates/config-template-full.yml`
  
- `stage-1` and `stage-2`: These refer to the two stages of the PeiDocker project. Stage-1 is the initial stage where the base image is built, the purpose is to install system-level dependencies using `apt` or alike, intended to be useful for many applications. Stage-2 is the second stage where the docker image is built, based on the image from stage-1, and it is intended to be used for a specific application, installing application-level dependencies (like `pip`, `npm`, installing `ros2` packages, etc.). 
  
- `peidocker-data-model`: This is the data model that represents the `user_config.yml` file during the configuration process, mainly used by the `pei-docker-cli` command line interface and `config_processor.py` module. 

## GUI Terminology

These terminologies are about the web-based GUI of the PeiDocker project, used in the context of the GUI tasks.

- `ui-data-model`: The data model that represents the state of the GUI, source code is in `src\pei_docker\webgui\models\ui_state.py`.
- `business-data-model`: The data model that represents `user_config.yml`, which is what `pei-docker-cli configure` command reads and configures the docker building `docker-compose.yml` , this is the "business logic" data model, because in the end, the GUI is just an easy way to generate the `user_config.yml` file (see `context/tasks/prefix/prefix-terminology.md`). The `business-data-model` is implemented using `pydantic` and is located in `src/pei_docker/webgui/models/config.py`.
- `ui-to-business-bridge`: The bridge that connects the `ui-data-model` and the `business-data-model`, implemented in `src/pei_docker/webgui/utils/ui_state_bridge.py`. We should implement bidirectional transformation between the two models, so that changes in the GUI can be validated and saved to the `business-data-model`, and when loading existing projects, the `user_config.yml` will be first loaded into the `business-data-model`, then transformed to the `ui-data-model` for the GUI to display.
