# Advanced Examples

[](){#environment-variables}
## Environment Variable Substitution

PeiDocker supports environment variable substitution in configuration files using the `${VARIABLE_NAME:-default_value}` syntax, similar to Docker Compose. This feature allows you to create flexible configurations that can be customized without modifying the configuration file directly.

### Basic Example: Configurable SSH Port

```yaml
# user_config.yml
stage_1:
  image:
    base: ubuntu:24.04
    output: "${PROJECT_NAME:-my-app}:stage-1"
  ssh:
    enable: true
    port: 22
    host_port: "${SSH_HOST_PORT:-2222}"  # Default to 2222 if not set
    users:
      "${USERNAME:-developer}":
        password: "${USER_PASSWORD:-defaultpass}"
        uid: "${USER_UID:-1000}"
```

**Usage:**
```bash
# Use default values
python -m pei_docker.pei configure -p ./my-project

# Use custom values
export PROJECT_NAME="my-custom-app"     # Linux/macOS
export SSH_HOST_PORT="3333"
export USERNAME="john"
export USER_PASSWORD="secretpass"
# or on Windows PowerShell:
$env:PROJECT_NAME='my-custom-app'
$env:SSH_HOST_PORT='3333'
$env:USERNAME='john'
$env:USER_PASSWORD='secretpass'

python -m pei_docker.pei configure -p ./my-project
```

### Development vs Production Example

This example shows how to use different configurations for development and production environments:

```yaml
# user_config.yml
stage_1:
  image:
    base: "${BASE_IMAGE:-ubuntu:24.04}"
    output: "${PROJECT_NAME:-my-app}:stage-1"
  ssh:
    enable: true
    host_port: "${SSH_PORT:-2222}"
    users:
      "${DEV_USER:-developer}":
        password: "${DEV_PASSWORD:-devpass}"

stage_2:
  image:
    output: "${PROJECT_NAME:-my-app}:stage-2"
  
  storage:
    workspace:
      type: "${STORAGE_TYPE:-auto-volume}"
      host_path: "${WORKSPACE_PATH:-}"
      volume_name: "${PROJECT_NAME:-my-app}-workspace"
  
  mount:
    project_data:
      type: host
      host_path: "${DATA_PATH:-C:\\tmp\\project-data}"
      dst_path: "/data"
    
    shared_tools:
      type: host  
      host_path: "${TOOLS_PATH:-C:\\tools}"
      dst_path: "/tools"
```

**Development Environment:**
```bash
# Windows PowerShell
$env:PROJECT_NAME='myapp-dev'
$env:SSH_PORT='2222'
$env:DEV_USER='developer'
$env:DEV_PASSWORD='devpass123'
$env:STORAGE_TYPE='host'
$env:WORKSPACE_PATH='C:\dev\myapp\workspace'
$env:DATA_PATH='C:\dev\myapp\data'
$env:TOOLS_PATH='C:\dev\tools'

python -m pei_docker.pei configure -p ./my-project
```

**Production Environment:**
```bash
# Linux/macOS
export PROJECT_NAME="myapp-prod"
export BASE_IMAGE="ubuntu:22.04"
export SSH_PORT="22022"
export DEV_USER="appuser"
export DEV_PASSWORD="$(openssl rand -base64 32)"
export STORAGE_TYPE="manual-volume"
export DATA_PATH="/opt/myapp/data"
export TOOLS_PATH="/opt/shared-tools"

python -m pei_docker.pei configure -p ./my-project
```

### GPU Development with Flexible Paths

```yaml
# user_config.yml
stage_1:
  image:
    base: "${GPU_BASE_IMAGE:-nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04}"
    output: "${PROJECT_NAME:-gpu-dev}:stage-1"
  
  ssh:
    enable: true
    host_port: "${SSH_PORT:-3333}"
    users:
      "${DEV_USER:-developer}":
        password: "${DEV_PASSWORD:-devpass}"
  
  device:
    type: gpu
  
  apt:
    repo_source: "${APT_MIRROR:-aliyun}"

stage_2:
  image:
    output: "${PROJECT_NAME:-gpu-dev}:stage-2"
  
  device:
    type: gpu
  
  mount:
    datasets:
      type: host
      host_path: "${DATASETS_PATH:-C:\\datasets}"
      dst_path: "/datasets"
    
    models:
      type: host
      host_path: "${MODELS_PATH:-C:\\models}"
      dst_path: "/models"
    
    workspace:
      type: host
      host_path: "${WORKSPACE_PATH:-C:\\workspace}"
      dst_path: "/workspace"
    
    cache:
      type: auto-volume
      dst_path: "/root/.cache"
```

**Usage for different team members:**

**Team Member 1 (Windows):**
```powershell
$env:PROJECT_NAME='ml-project'
$env:SSH_PORT='4444'
$env:DEV_USER='alice'
$env:DATASETS_PATH='D:\datasets'
$env:MODELS_PATH='D:\trained-models'
$env:WORKSPACE_PATH='D:\ml-workspace'
```

**Team Member 2 (Linux):**
```bash
export PROJECT_NAME="ml-project"
export SSH_PORT="5555"
export DEV_USER="bob"
export DATASETS_PATH="/mnt/storage/datasets"
export MODELS_PATH="/mnt/storage/models"
export WORKSPACE_PATH="/home/bob/ml-workspace"
export APT_MIRROR="tuna"  # Use different mirror in China
```

### CI/CD Pipeline Example

This example shows how to use environment variables in CI/CD pipelines:

```yaml
# user_config.yml
stage_1:
  image:
    base: "${CI_BASE_IMAGE:-ubuntu:24.04}"
    output: "${CI_IMAGE_NAME:-ci-runner}:${CI_BUILD_NUMBER:-latest}"
  
  ssh:
    enable: "${CI_ENABLE_SSH:-false}"
    host_port: "${CI_SSH_PORT:-2222}"
    users:
      ci:
        password: "${CI_PASSWORD:-ci123}"

stage_2:
  image:
    output: "${CI_IMAGE_NAME:-ci-runner}:${CI_BUILD_NUMBER:-latest}-final"
  
  mount:
    ci_cache:
      type: "${CI_CACHE_TYPE:-auto-volume}"
      host_path: "${CI_CACHE_PATH:-}"
      dst_path: "/ci-cache"
    
    artifacts:
      type: host
      host_path: "${CI_ARTIFACTS_PATH:-./artifacts}"
      dst_path: "/artifacts"
```

**In your CI pipeline (GitHub Actions example):**
```yaml
# .github/workflows/build.yml
env:
  CI_IMAGE_NAME: "my-app"
  CI_BUILD_NUMBER: ${{ github.run_number }}
  CI_ENABLE_SSH: "false"
  CI_CACHE_TYPE: "manual-volume"
  CI_ARTIFACTS_PATH: "./build-artifacts"

steps:
  - name: Build Docker Image
    run: |
      python -m pei_docker.pei configure -p ./docker-project
      cd docker-project
      docker compose build stage-2
```

### Best Practices for Environment Variables

1. **Always provide sensible defaults:**
   ```yaml
   host_port: "${SSH_PORT:-2222}"  # ✓ Good
   host_port: "${SSH_PORT}"        # ✗ Bad - fails if not set
   ```

2. **Use descriptive variable names:**
   ```yaml
   host_path: "${PROJECT_DATA_PATH:-C:\\data}"  # ✓ Good
   host_path: "${PATH1:-C:\\data}"              # ✗ Bad - unclear purpose
   ```

3. **Group related variables:**
   ```bash
   # Database configuration
   export DB_HOST="localhost"
   export DB_PORT="5432"
   export DB_NAME="myapp"
   
   # Storage configuration  
   export DATA_PATH="/opt/data"
   export CACHE_PATH="/opt/cache"
   ```

4. **Document your variables:**
   ```yaml
   # user_config.yml
   stage_2:
     mount:
       # Set SHARED_DATA_PATH to your team's shared data directory
       shared_data:
         type: host
         host_path: "${SHARED_DATA_PATH:-C:\\shared\\data}"
         dst_path: "/shared-data"
   ```

[](){#ssh-keys-advanced}
## Advanced SSH Key Configuration

PeiDocker provides flexible SSH key management with support for multiple key formats and methods. This section demonstrates advanced SSH key configurations using the new inline key features.

### Example 1: Mixed Key Methods for Different Users

This example shows how to configure multiple users with different SSH key methods:

```yaml
# user_config.yml
stage_1:
  image:
    base: ubuntu:24.04
    output: my-secure-app:stage-1
  
  ssh:
    enable: true
    host_port: 2222
    users:
      # Admin user with inline private key (most secure for automation)
      admin:
        password: "${ADMIN_PASSWORD:-admin123}"
        uid: 1000
        privkey_text: |
          -----BEGIN OPENSSH PRIVATE KEY-----
          b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2g...
          -----END OPENSSH PRIVATE KEY-----
      
      # Developer user with inline public key (for shared development)
      developer:
        password: "${DEV_PASSWORD:-dev123}"
        uid: 1001
        pubkey_text: "${DEV_PUBLIC_KEY:-ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7vbqa...}"
      
      # Service user with public key file (for legacy integration)
      service:
        password: "${SERVICE_PASSWORD:-service123}"
        uid: 1002
        pubkey_file: 'stage-1/system/ssh/keys/service-key.pub'
      
      # Guest user with private key file reference
      guest:
        password: "${GUEST_PASSWORD:-guest123}"
        uid: 1003
        privkey_file: 'stage-1/system/ssh/keys/guest-private-key'
```

### Example 2: Environment-Driven SSH Key Configuration

Configure SSH keys entirely through environment variables for maximum flexibility:

```yaml
# user_config.yml
stage_1:
  ssh:
    enable: true
    host_port: "${SSH_PORT:-2222}"
    users:
      "${SSH_USERNAME:-developer}":
        password: "${SSH_PASSWORD:-defaultpass}"
        uid: "${SSH_UID:-1000}"
        # Use environment variables to choose key method
        pubkey_text: "${SSH_PUBLIC_KEY:-}"
        privkey_text: "${SSH_PRIVATE_KEY:-}"
        pubkey_file: "${SSH_PUBLIC_KEY_FILE:-}"
        privkey_file: "${SSH_PRIVATE_KEY_FILE:-}"
```

**Usage with different key sources:**

```bash
# Method 1: Using inline public key
export SSH_USERNAME="alice"
export SSH_PASSWORD="alicepass"
export SSH_PUBLIC_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC..."

# Method 2: Using inline private key
export SSH_USERNAME="bob"
export SSH_PASSWORD="bobpass"
export SSH_PRIVATE_KEY="-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2g...
-----END OPENSSH PRIVATE KEY-----"

# Method 3: Using key files
export SSH_USERNAME="charlie"
export SSH_PASSWORD="charliepass"
export SSH_PUBLIC_KEY_FILE="stage-1/system/ssh/keys/charlie.pub"

python -m pei_docker.pei configure -p ./my-project
```

### Example 3: Team Development with Multiple SSH Keys

Configure a container for team development where each team member has their own SSH access:

```yaml
# user_config.yml
stage_1:
  ssh:
    enable: true
    host_port: 2222
    users:
      # Team lead with full access
      teamlead:
        password: "${TEAMLEAD_PASSWORD:-lead123}"
        uid: 1000
        pubkey_text: "${TEAMLEAD_SSH_KEY:-ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC...}"
      
      # Senior developer
      senior-dev:
        password: "${SENIOR_DEV_PASSWORD:-senior123}"
        uid: 1001
        pubkey_file: 'stage-1/system/ssh/keys/senior-dev.pub'
      
      # Junior developer
      junior-dev:
        password: "${JUNIOR_DEV_PASSWORD:-junior123}"
        uid: 1002
        privkey_file: 'stage-1/system/ssh/keys/junior-dev-private'
      
      # CI/CD service account
      ci-service:
        password: "${CI_PASSWORD:-ci123}"
        uid: 1003
        privkey_text: "${CI_PRIVATE_KEY:-}"

stage_2:
  mount:
    # Shared project workspace
    project:
      type: host
      host_path: "${PROJECT_PATH:-C:\\team\\project}"
      dst_path: "/workspace"
    
    # Individual home directories
    team_homes:
      type: auto-volume
      dst_path: "/home"
      volume_name: "${PROJECT_NAME:-team-project}-homes"
```

### Example 4: Security-Focused Configuration

For high-security environments, use private keys with proper access controls:

```yaml
# user_config.yml
stage_1:
  image:
    base: ubuntu:24.04
    output: secure-app:stage-1
  
  ssh:
    enable: true
    host_port: "${SECURE_SSH_PORT:-22022}"  # Non-standard port
    users:
      # Primary admin account
      secadmin:
        password: "${ADMIN_PASSWORD:-$(openssl rand -base64 32)}"
        uid: 1000
        privkey_text: "${ADMIN_PRIVATE_KEY}"  # No default - must be provided
      
      # Backup admin account
      backup-admin:
        password: "${BACKUP_PASSWORD:-$(openssl rand -base64 32)}"
        uid: 1001
        privkey_file: "${BACKUP_KEY_FILE}"  # Reference to secure key file
      
      # Application service account (no password, key-only access)
      app-service:
        password: null  # Disable password authentication
        uid: 1002
        pubkey_text: "${SERVICE_PUBLIC_KEY}"

  # Security enhancements
  environment:
    - 'SSH_DISABLE_PASSWORD_AUTH=${DISABLE_PASSWORDS:-true}'
    - 'SSH_MAX_AUTH_TRIES=${MAX_AUTH_TRIES:-3}'
```

### SSH Key Security Best Practices

1. **Use private keys for automated systems**: When configuring CI/CD or automated deployment systems, use `privkey_text` or `privkey_file` to ensure the public key is generated consistently.

2. **Environment variable security**: When using environment variables for private keys, ensure they are properly secured in your deployment environment:
   ```bash
   # Use secret management systems in production
   export SSH_PRIVATE_KEY="$(vault kv get -field=private_key secret/ssh/deploy)"
   ```

3. **Key rotation**: With inline keys, you can easily rotate SSH keys by updating environment variables:
   ```bash
   # Generate new key pair
   ssh-keygen -t ed25519 -f ./new-deploy-key -N ""
   
   # Update environment
   export SSH_PRIVATE_KEY="$(cat ./new-deploy-key)"
   
   # Regenerate configuration
   python -m pei_docker.pei configure -p ./my-project
   ```

4. **Validation**: PeiDocker automatically validates key formats and mutual exclusivity, preventing configuration errors.

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
