# Terminology for many tasks

This file contains the terminology that is useful for many tasks, so that we are consistent in our language and avoid confusion.

- `user_config.yml`: This is the configuration file for the PeiDocker project, which contains settings for SSH, environment variables, and other configurations. It is located in the project directory and can be edited to customize the project. Its master template is in `src/pei_docker/templates/config-template-full.yml`
- `stage-1` and `stage-2`: These refer to the two stages of the PeiDocker project. Stage-1 is the initial stage where the base image is built, the purpose is to install system-level dependencies using `apt` or alike, intended to be useful for many applications. Stage-2 is the second stage where the docker image is built, based on the image from stage-1, and it is intended to be used for a specific application, installing application-level dependencies (like `pip`, `npm`, installing `ros2` packages, etc.). 
