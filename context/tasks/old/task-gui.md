we need to create a terminal GUI for our project, using `textual` library, you can find the docs using `context7` mcp, and some detail is in `context/hints/howto-use-textual.md`.

the gui is launched with `pei-docker-gui` command:
- `pei-docker-gui --project-dir <path>` to specify the project directory, will launch the GUI for that project.

create a subdir in `src\pei_docker` for this, do not write the whole GUI in a single file, split it into several files as needed.

# Design

The gui should proceeds as follows, mainly focuses on guiding the user to create a simple project. For advanced features, let the user directly edit the config file.

see `src\pei_docker\templates\config-template-full.yml` for what options is possible, this file is called `user_config` in this document.

Functionality of GUI:
- on startup, ask the user where to output the project, see `src\pei_docker\pei.py` for the `create` command, and it will then create the project directory, future operations work on this directory. Let's name the project as `my_project` in description.
- on startup, if the GUI is launched with `--project-dir <path>`, it will use that path as the project directory, no need to ask the user.
- on startup, look for `docker` command, if not found, show a warning message, some functions will not work without it.

after the project is created, the user now selects between two modes:
- `simple` mode, which uses quetions to guide the user through the process of creating a simple project
- `advanced` mode, which allows the user select between options, and edit details.

## Simple Mode

Ask these questions in order (adjust it if needed), when finished, show a summary of the project configuration, and ask if the user wants to save it. If the user chooses to save, write the `user_config` to the project directory, otherwise do not save anything and go back to the main menu.

### Project Information

ask for name of the project, no default, let's call it `my_project_name`, the built docker image will be named `my_project_name:stage-1` and `my_project_name:stage-2`. If `docker images` command is available (and you have permission to run it), check if the image already exists, if it does, warn the user that it will be overwritten. 

ask for base image name, default is `ubuntu:24.04`, this is a docker tag in dockerhub, will be used as the base image for the project

### SSH Configurations

IMPORTANT: this will only be set in `stage-1` of `user_config`, for `stage-2` the user needs to edit the config file directly.

ask whether the user wants to use `ssh` for remote access, default is `yes`. If `no`, warn that user needs to use native docker commands to access the container. If `yes`, then follow these steps:

- ask for the ssh in-container port, default is `22`, let's call it `ssh_container_port`, this port will be configured inside the container, useful if you want to use `host` network mode, to avoid confilicting with host ssh port.

- ask for the ssh host port, default is `2222`, let's call it `ssh_host_port`, this port will be used on the host machine to access the container.
  
- ask for the ssh user name, default is `me`.
  
- ask for the ssh user password, default is `123456`. Note that, do not use `,` or space in the password, due to implementation details, warn the user.
  
- ask if the user wants to specify the public key for `me` to allow remote access via ssh key, default is `no`. If `yes`, then ask for the public key string, and if the user enters `~`, then use the `~` functionality in `user_config`.
  
- ask if the user wants to specify the private key for `me`, default is `no`. If `yes`, then ask for the private key file path, and if the user enters `~`, then use the `~` functionality in `user_config`.
  
- ask if the root user should be able to login via ssh, default is `no`. If `yes`, then ask for the root password, default is `root`. You cannot set ssh keys for root user in GUI mode.

### Proxy Configuration

IMPORTANT: this will only be set in `stage-1` of `user_config`, for `stage-2` the user needs to edit the config file directly.

ask if the user wants to use a proxy in host for the container, default is `no`. If `yes`, tell the user that this will set `http_proxy` and `https_proxy` environment variables in the container.

Then ask for the following information:

- ask for proxy port, no default, this is the port on the host machine that the container will use to access the internet.
- ask for if the proxy is only used during the build process, if `yes`, then the proxy will not be available after build. If `no`, then the proxy will be available after build, affecting the container runtime environment with `http_proxy` and `https_proxy` environment variables. Default is `yes`.

### Apt Configuration

IMPORTANT: this will only be set in `stage-1` of `user_config`, for `stage-2` the user needs to edit the config file directly.

ask if the user wants to use a different mirror other than default, default is `no`. If `yes`, then ask for the mirror name, this is given as choices, the options are 
- `tuna`: Tsinghua University mirror
- `aliyun`: Aliyun mirror
- `163`: 163 mirror
- `ustc`: University of Science and Technology of China mirror
- `cn`: Ubuntu official China mirror
- `default`: the default Ubuntu mirror (no change)

this will set the `apt` section in the user config file, see `src\pei_docker\templates\config-template-full.yml` for details.

### Port Mapping

IMPORTANT: this will only be set in `stage-1` of `user_config`, for `stage-2` the user needs to edit the config file directly.

ask if the user wants to map additional ports from host to container, default is `no` (note that ssh ports are already mapped). If `yes`, then ask for the following information

- ask the user for port mapping, format is `host_port:container_port`,can be single port like `8080:80`, or port range like `100-200:300-400`.
- user enters a valid port mapping, and then press Enter to add it to the list, already added port mappings will be shown, no way to delete them in GUI mode.
- as long as the user enters a valid port mapping, it will be added to the `ports` section in the user config file, finish when the user enters an empty string.

### Environment Variables

IMPORTANT: this will only be set in `stage-1` of `user_config`, for `stage-2` the user needs to edit the config file directly.

ask if the user wants to set environment variables, default is `no`. If `yes`, then ask for the following information:

- ask for the env variable in the format `key=value`
- user enters a valid env variable setting, press Enter to add it to the list, already added env variables will be shown. To delete it, set the already-set env variable to an empty string.

### Device

IMPORTANT: this will only be set in `stage-1` of `user_config`, for `stage-2` the user needs to edit the config file directly.

ask if the user wants to use gpu, default is `no`. If `yes`, set the `user_config` accordingly. Note that, we DO NOT detect if the user has gpu or not, this is up to the user to decide. 


### Additional Mounts

ask if the user wants to set mounts for `stage-1`, default is `no`. If `yes`, then ask for the following information:

ask if the user wants to mount additional drives into the container, default is `no`. If `yes`, then present the user with following options about volume type:
- `automatic docker volume`: use a docker volume, mapping to `auto-volume` in `user_config`, the volume will be created automatically.
- `manual docker volume`: use a docker volume, mapping to `manual-volume` in `user_config`.
- - with this option, ask for the volume name
- `host directory`: use a host directory, mapping to `host` type of volume in `user_config`.
- - with this option, ask for the host directory path, handles Windows path and linux path automatically. Check if the path exists, if not, warn the user but simply accept it, doing nothing about it.
- - `image`: this option is valid but has no effect in the mount setting, will be ignored and not even writen to the `user_config`.
- - `done`: finish the mount setting, no more mounts will be added.

ask if the user wants to set the mounts for `stage-2`, default is `no`. If `yes`, then present the user with the same options as above, and warn the user that the mounts for `stage-2` will override the mounts for `stage-1`, completely replacing them.

### Custom Entry Point

ask the user if they want to set a custom entry point for `stage-1`, default is `no`. If `yes`, then follow these steps:

ask for a custom entry point script, in `.sh` format.
- if the user enters empty string, then no custom entry point will be set, go to next step.
- if the user enters a valid path, then set the `custom.on_entry` in `user_config`, the file will be copied to the project directory, and the path set to the `user_config` will be relative to the project directory (see `user_config` for details).

ask if the user wants to set a custom entry point for `stage-2`, default is `no`. If `yes`, do the same as above, but warn the user that the custom entry point for `stage-2` will override the custom entry point for `stage-1`, completely replacing it.

### Custom Scripts

ask if the user wants to set custom scripts for `stage-1`, default is `no`. If `yes`, then follow these steps:

we have several kinds of custom scripts, like `on_build`, `on_first_run`, `on_every_run` and `on_user_login`, see `user_config` and project docs for details.

for each kind of custom script
- explain to the user what it is, and what it does
- let user enter the script path, can also with cli args, like `--arg1 value1 --arg2 value2`. The script will be added to the corresponding section in `user_config`.
- user enters one script path at a time, and previously entered scripts will be shown, no way to delete them in GUI mode.
- when user enters an empty string, finish the custom script for that kind of script, and go to the next kind of script.

ask if the user wants to set custom scripts for `stage-2`, default is `no`. If `yes`, do the same as above, add to the `user_config` for `stage-2`.

### Finishing Up

Now show a summary of the project configuration, including all the settings the user has made, and ask if the user wants to save it. If the user chooses to save, write the `user_config` to the project directory, otherwise do not save anything and go back to the main menu.

## Advanced Mode

In advanced mode, the above settings will be presented as a form with options to select and edit. The user can choose to edit any section of the `user_config` directly.