# Advanced Examples

[](){#environment-variables}
## Environment Variable Substitution

PeiDocker supports environment variable substitution in configuration files, allowing you to customize your setup without modifying the `user_config.yml` file directly. This is particularly useful for:

- Different development environments (development, staging, production)
- Team collaboration with different local paths
- CI/CD pipelines with environment-specific configurations

### Syntax

Use the `${VARIABLE_NAME:-default_value}` syntax in your `user_config.yml`:

```yaml
stage_1:
  ssh:
    host_port: "${SSH_HOST_PORT:-2222}"
    
stage_2:
  mount:
    shared_folder:
      type: host
      host_path: "${SHARED_PATH:-C:\\tmp\\default}"
      dst_path: "/shared"
```

### Examples

#### Example 1: Configurable SSH Port

```yaml
stage_1:
  ssh:
    enable: true
    port: 22
    host_port: "${SSH_HOST_PORT:-2222}"  # Default to 2222 if not set
```

Usage:
```bash
# Use default port (2222)
python -m pei_docker.pei configure -p ./my-project

# Use custom port (3333)
export SSH_HOST_PORT=3333  # Linux/macOS
# or
$env:SSH_HOST_PORT='3333'  # Windows PowerShell
python -m pei_docker.pei configure -p ./my-project
```

#### Example 2: Flexible Mount Paths

```yaml
stage_2:
  mount:
    project_data:
      type: host
      host_path: "${PROJECT_DATA_PATH:-C:\\workspace\\data}"
      dst_path: "/project/data"
    
    shared_tools:
      type: host
      host_path: "${TOOLS_PATH:-C:\\tools}"
      dst_path: "/tools"
```

Usage:
```bash
# Windows PowerShell
$env:PROJECT_DATA_PATH='D:\my-project\data'
$env:TOOLS_PATH='D:\shared-tools'
python -m pei_docker.pei configure -p ./my-project

# Linux/macOS
export PROJECT_DATA_PATH='/home/user/project-data'
export TOOLS_PATH='/usr/local/shared-tools'
python -m pei_docker.pei configure -p ./my-project
```

#### Example 3: Environment-Specific Base Images

```yaml
stage_1:
  image:
    base: "${BASE_IMAGE:-ubuntu:24.04}"
    output: "${OUTPUT_IMAGE:-my-app}:stage-1"
```

This allows you to use different base images for different environments:
```bash
# Development (default Ubuntu)
python -m pei_docker.pei configure -p ./my-project

# GPU development
$env:BASE_IMAGE='nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04'
python -m pei_docker.pei configure -p ./my-project

# Production
$env:BASE_IMAGE='ubuntu:22.04'
$env:OUTPUT_IMAGE='my-production-app'
python -m pei_docker.pei configure -p ./my-project
```

### Advanced Usage

You can combine environment variables with complex configurations:

```yaml
stage_1:
  image:
    base: "${BASE_IMAGE:-ubuntu:24.04}"
    output: "${PROJECT_NAME:-my-app}:stage-1"
  
  ssh:
    enable: true
    host_port: "${SSH_PORT:-2222}"
    users:
      "${USERNAME:-developer}":
        password: "${USER_PASSWORD:-defaultpass}"
        uid: "${USER_UID:-1000}"

stage_2:
  storage:
    workspace:
      type: "${STORAGE_TYPE:-auto-volume}"
      host_path: "${WORKSPACE_PATH:-}"
      volume_name: "${PROJECT_NAME:-my-app}-workspace"
  
  mount:
    project_root:
      type: host
      host_path: "${PROJECT_ROOT:-C:\\workspace}"
      dst_path: "/workspace"
```

### Best Practices

1. **Always provide defaults**: Use `${VAR:-default}` rather than `${VAR}` to ensure the configuration works even when environment variables aren't set.

2. **Use meaningful variable names**: Choose descriptive names like `PROJECT_DATA_PATH` instead of generic names like `PATH1`.

3. **Document your variables**: Include comments in your `user_config.yml` explaining what each environment variable controls.

4. **Test both scenarios**: Verify your configuration works both with and without environment variables set.

## Hardware-accelerated OpenGL

### Windows

The following example demonstrates how to build a Docker image with hardware-accelerated OpenGL support on Windows. The critical part is to: 

* install necessary packages (e.g., `libglvnd-dev`) in the Dockerfile, see [setup-opengl-win32.sh](https://github.com/igamenovoer/PeiDocker/blob/627abb919fca23a24e7bc95da0af9c6ac9c88166/pei_docker/project_files/installation/stage-2/system/opengl/setup-opengl-win32.sh)

* mount the necessary directories for WSLg to work properly, see [WSLg GPU selection](https://github.com/microsoft/wslg/wiki/GPU-selection-in-WSLg).


```yaml
# all paths are relative to /installation directory
# for windows, you need to add these to the final docker-compose.yml file
# see https://github.com/microsoft/wslg/wiki/GPU-selection-in-WSLg

# volumes:
#     - /tmp/.X11-unix:/tmp/.X11-unix
#     - /mnt/wslg:/mnt/wslg
#     - /usr/lib/wsl:/usr/lib/wsl
#     - /dev:/dev

stage_1:
  # input/output image settings
  image:
    base: nvidia/cuda:12.3.2-base-ubuntu22.04    
    output: pei-opengl:stage-1

  # ssh settings
  ssh:
    enable: true
    port: 22  # port in container
    host_port: 2222  # port in host

    # ssh users, the key is user name, value is user info
    users:
      me:
        password: '123456'

  # proxy settings
  # inside the container, the proxy will accessed as http://{address}:{port}
  # note that whether the proxy is used or not depends on the applications
  proxy:
    address: host.docker.internal # default value, this will map to the host machine
    port: 7890  # if address==host.docker.internal, this will be the proxy port on host machine
    enable_globally: false  # enable proxy for all shell commands during build and run?
    remove_after_build: false # remove global proxy after build?
    use_https: false # use https proxy?


  # apt settings
  apt:
    repo_source: 'tuna'

  # device settings
  device:
    type: gpu # can be cpu or gpu
    
stage_2:

  # input/output image settings
  image:
    output: pei-opengl:stage-2

  # additional environment variables
  # see https://docs.docker.com/compose/environment-variables/set-environment-variables/
  environment:  # use list intead of dict
    NVIDIA_VISIBLE_DEVICES: all
    NVIDIA_DRIVER_CAPABILITIES: all

  # device settings, will override the stage-1 device settings
  device:
    type: gpu # can be cpu or gpu

  storage:
    app:
      type: auto-volume
    data:
      type: auto-volume
    workspace:
      type: auto-volume

  # custom scripts in stage-2, run after stage-1 custom scripts
  custom:
    # scripts run during build
    on_build: 
      - 'stage-2/system/opengl/setup-opengl-win32.sh' # install opengl
```

```yaml
# this is the docker-compose.yml file

version: '3'
services:
  stage-2:
    image: pei-opengl:stage-2
    stdin_open: true
    tty: true
    command: /bin/bash
    deploy:
      resources:
        reservations:
          devices:
          - driver: nvidia
            capabilities:
            - gpu
    extra_hosts:
    - host.docker.internal:host-gateway
    build:
      context: .
      dockerfile: stage-2.Dockerfile
      extra_hosts:
      - host.docker.internal:host-gateway
      args:
        BASE_IMAGE: pei-opengl:stage-1
        WITH_ESSENTIAL_APPS: true
        PEI_STAGE_HOST_DIR_2: ./installation/stage-2
        PEI_STAGE_DIR_2: /pei-from-host/stage-2
        PEI_PREFIX_APPS: app
        PEI_PREFIX_DATA: data
        PEI_PREFIX_WORKSPACE: workspace
        PEI_PREFIX_VOLUME: volume
        PEI_PREFIX_IMAGE: image
        PEI_PATH_HARD: /hard
        PEI_PATH_SOFT: /soft
        PEI_HTTP_PROXY_2: http://host.docker.internal:7890
        PEI_HTTPS_PROXY_2: http://host.docker.internal:7890
        ENABLE_GLOBAL_PROXY: false
        REMOVE_GLOBAL_PROXY_AFTER_BUILD: false
    ports:
    - '2222:22'
    environment:
      NVIDIA_VISIBLE_DEVICES: all
      NVIDIA_DRIVER_CAPABILITIES: all
    volumes:
    - app:/hard/volume/app
    - data:/hard/volume/data
    - workspace:/hard/volume/workspace
    - /tmp/.X11-unix:/tmp/.X11-unix # for wslg
    - /mnt/wslg:/mnt/wslg   # for wslg
    - /usr/lib/wsl:/usr/lib/wsl # for wslg
    - /dev:/dev # for wslg
  stage-1:
    image: pei-opengl:stage-1
    stdin_open: true
    tty: true
    command: /bin/bash
    deploy:
      resources:
        reservations:
          devices:
          - driver: nvidia
            capabilities:
            - gpu
    environment: {}
    extra_hosts:
    - host.docker.internal:host-gateway
    build:
      context: .
      dockerfile: stage-1.Dockerfile
      extra_hosts:
      - host.docker.internal:host-gateway
      args:
        BASE_IMAGE: nvidia/cuda:12.3.2-base-ubuntu22.04
        WITH_ESSENTIAL_APPS: true
        WITH_SSH: true
        SSH_USER_NAME: me
        SSH_USER_PASSWORD: '123456'
        SSH_PUBKEY_FILE: ''
        APT_SOURCE_FILE: tuna
        KEEP_APT_SOURCE_FILE: true
        APT_USE_PROXY: false
        APT_KEEP_PROXY: false
        PEI_HTTP_PROXY_1: http://host.docker.internal:7890
        PEI_HTTPS_PROXY_1: http://host.docker.internal:7890
        ENABLE_GLOBAL_PROXY: false
        REMOVE_GLOBAL_PROXY_AFTER_BUILD: false
        PEI_STAGE_HOST_DIR_1: ./installation/stage-1
        PEI_STAGE_DIR_1: /pei-from-host/stage-1
        ROOT_PASSWORD: ''
    ports:
    - '2222:22'
volumes:
  app: {}
  data: {}
  workspace: {}
```

## InvokeAI Installation (behind GFW)

[InvokeAI](https://github.com/invoke-ai/InvokeAI) is a professional AIGC tool that has many nice GUI features, and the developers have provided simple installation scripts for Linux and Windows. However, installing behind GFW is hard, as it requires installing many components as well as models to work. Here we provide an example to install it behind GFW, as well as how to configure the app to make it more performant.

### using pip

**IMPORTANT**: To make it easier to download models in the future, we have enabled global proxy and assumed that you have a proxy running in your host over port `30080`. If you don't have a proxy, you can disable it by setting `enable_globally` to `false` in the `proxy` section of the config file.

The [official guide](https://invoke-ai.github.io/InvokeAI/installation/020_INSTALL_MANUAL/#installation-walkthrough) provides details about how to install it via pip. We automate the process here using China mainland mirrors. We use `root` to install and run InvokeAI.

Here is the config file, you can find it in `pei_docker/examples/invoke-ai-by-pip.yml`:

```yaml
# create a docker for latest invoke ai

stage_1:
  # input/output image settings
  image:
    base: nvidia/cuda:12.1.1-runtime-ubuntu22.04
    output: invoke-ai-pip:stage-1

  # ssh settings
  ssh:
    enable: true
    port: 22  # port in container
    host_port: 3333  # port in host

    # ssh users, the key is user name, value is user info
    users:
      me:
        password: '123456'
      root:
        password: 'root'

  # proxy settings
  # inside the container, the proxy will accessed as http://{address}:{port}
  # note that whether the proxy is used or not depends on the applications
  proxy:
    address: host.docker.internal # default value, this will map to the host machine
    port: 7890  # if address==host.docker.internal, this will be the proxy port on host machine
    enable_globally: false  # enable proxy for all shell commands during build and run?
    remove_after_build: false # remove global proxy after build?

  device:
    type: gpu

  # apt settings
  # replace the default apt source with a custom one, use empty string to disable this
  # repo_source: 'stage-1/system/apt/ubuntu-22.04-tsinghua-x64.list'
  # special values that refer to well known apt sources:
  # 'tuna' : 'http://mirrors.tuna.tsinghua.edu.cn/ubuntu/'
  # 'aliyun' : 'http://mirrors.aliyun.com/ubuntu/'
  # '163' : 'http://mirrors.163.com/ubuntu/'
  # 'ustc' : 'http://mirrors.ustc.edu.cn/ubuntu/'
  # 'cn' : 'http://cn.archive.ubuntu.com/ubuntu/
  repo_source: 'tuna'
  keep_repo_after_build: true # keep the apt source file after build?
  use_proxy: false  # use proxy for apt?
  keep_proxy_after_build: false # keep proxy settings after build?

  # custom scripts
  custom:
    # run twice, make sure installation is successful
    on_build: 
      - 'stage-1/system/invoke-ai/install-invoke-ai-deps.sh'
      - 'stage-1/system/invoke-ai/install-invoke-ai-deps.sh'

stage_2:
  # input/output image settings
  image:
    output: invoke-ai-pip:stage-2

  # port mapping, will be appended to the stage-1 port mapping
  # see https://docs.docker.com/compose/networking/
  ports:
    - '9090-9099:9090-9099'

  # device settings, will override the stage-1 device settings
  device:
    type: gpu # can be cpu or gpu

  environment:
    - 'AI_USERS=user_9090,user_9091,user_9092'
    - 'AI_PORTS=9090,9091,9092'
    - 'AI_DEVICES=cuda:0,cuda:1,cuda:2' # device for each user, DO NOT ADD SPACE here
    - 'AI_DATA_DIR=/invokeai-data'  # where the data is stored inside the container, different users will have different subdir there
    - 'INVOKEAI_ROOT=/soft/app/invokeai'  # where invokeai is installed, inside the container
    - 'INVOKEAI_RAM=12'  # per-user CPU memory cache size in GB, larger size leads to faster running by avoiding data reload
    - 'INVOKEAI_VRAM=2' # per-user GPU memory cache size, in GB, larger size leads to faster running by avoiding data reload

  # storage configurations
  storage:
    app:
      type: auto-volume # auto-volume, manual-volume, host, image
    data:
      type: auto-volume
    workspace:
      type: auto-volume

  # mount external volumes to container
  # the volumes can be given any names, mounted anywhere
  # the volume type cannot be 'image', or otherwise it will be ignored
  mount:
    home-root:
      type: auto-volume   # auto-volume, manual-volume, host
      dst_path: /root
    invokeai-data:
      type: auto-volume
      dst_path: /invokeai-data
    models: # for external models
      type: auto-volume
      dst_path: /models
    pei_init:
      type: auto-volume
      dst_path: /pei-init
  
  custom:
    on_first_run:
      - stage-2/system/conda/auto-install-miniconda.sh
      - stage-2/system/invoke-ai/install-invoke-ai-conda.sh

    on_every_run:
      # normally, you can start InvokeAI manually using stage-2/system/invoke-ai/run-invoke-ai-mutli-user.sh
      # if you want to run invoke-ai on startup, create stage-2/custom/start-invokeai.sh, and run the above there
      - stage-2/system/invoke-ai/invoke-ai-entrypoint.sh
```

To run InvokeAI, we need some information through environment variables, for more environment variables, see `stage-2/system/invoke-ai/setup-invoke-ai-envs.sh`. 

Here are the most important environment variables:

- AI_USERS: the users that will run InvokeAI, separated by `,`
- AI_PORTS: the ports that will be used by each user, separated by `,`
- AI_DEVICES: the devices that will be used by each user, separated by `,`
- AI_DATA_DIR: the directory where the data is stored inside the container
- INVOKEAI_ROOT: the directory where InvokeAI is installed inside the container
- INVOKEAI_RAM: the per-user CPU memory cache size in GB
- INVOKEAI_VRAM: the per-user GPU memory cache size in GB

Note that these environment variables are NOT directly available to SSH logins, they are only available to the `root` that starts by `docker compose`, so you need to attach to the container to run InvokeAI.

```bash
# find out the container id
docker ps -a

# you get something like this
# CONTAINER ID   IMAGE   NAMES
# fdf2953454f2   invoke-ai-pip:stage-2 build-invokeai-stage-2-1

# then, attach to the container
docker container attach build-invokeai-stage-2-1

# now you are inside the container, you can run InvokeAI with
/pei-from-host/stage-2/system/invoke-ai/run-invoke-ai-mutli-user.sh

# after that, you can detach from the container by pressing `Ctrl+P` and `Ctrl+Q`
```

If successful, you can access InvokeAI by visiting `http://localhost:9090` in your browser,
or `http://localhost:9091`, `http://localhost:9092` for different InvokeAI users, they have their own data but share the same models.

If you ssh into the container, you need to set the environment variables manually, or you can create a script to set them automatically. Then you can again use `run-invoke-ai-mutli-user.sh` to start InvokeAI.

The `run-invoke-ai-mutli-user.sh` script will create a process in tmux for each user, and you can access the GUI using the ports you specified in the environment variables. To see InvokeAI logs, use `tmux` to attach to the corresponding session ([how to use tmux](https://tmuxcheatsheet.com/)).

To find out the installation details and where models are downloaded, outputs are kept, check the scripts in `stage-2/system/invoke-ai`
