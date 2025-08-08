# Welcome to PeiDocker

Don't keep your docker images around, keep the build files! If you ever want to make reproducible docker images but have no patience to learn Dockerfiles and docker-compose, PeiDocker is for you.

[PeiDocker (配 docker)](https://github.com/igamenovoer/PeiDocker) helps you script and organize your docker image building process without learning too much about Dockerfiles and docker-compose. It provides both CLI and web-based GUI for managing Docker projects with advanced features. With PeiDocker, you can:

- Build images with SSH support and multiple authentication methods
- Configure separate port mappings for system services (stage-1) and applications (stage-2)
- Use the intuitive web GUI for visual project configuration
- Export projects as ZIP files for easy sharing and backup
- Install packages from public repository using proxy
- Easily switch storage between Docker images, host directories, or volumes
- Run custom commands during image building and container lifecycle
- Manage environment variables with Docker Compose-style substitution

## What's New

### Version 2.0 - Major GUI Update (January 2025)

**Web GUI Enhancements:**
- **Modern NiceGUI Framework**: Complete rewrite using NiceGUI for improved performance and user experience
- **Visual Configuration Wizard**: Intuitive step-by-step interface with tab-based navigation
- **Native Desktop Mode**: Optional OS-native window mode with `--native` flag (requires pywebview)
- **Auto-port Selection**: Intelligent port detection automatically finds available ports
- **Jump-to-Page Navigation**: Direct access to specific configuration sections via CLI parameter
- **Real-time Validation**: Instant configuration validation with helpful error messages

**Configuration Features:**
- **Separate Port Mappings**: Independent port configuration for stage-1 (system services) and stage-2 (applications)
- **Enhanced SSH Management**: 
  - Support for multiple authentication methods
  - Inline SSH key input (both public and private)
  - Automatic public key generation from private keys
  - Multi-user configuration with custom UIDs
- **Advanced Storage Options**: Visual configuration for auto-volume, manual-volume, host, and in-image storage
- **Script Parameters**: Support for shell-like parameters in custom scripts
- **Environment Variable Substitution**: Docker Compose-style `${VAR:-default}` syntax support

**Project Management:**
- **ZIP Import/Export**: Complete project backup and sharing via ZIP files
- **Minimal Config Templates**: Quick-start templates for common Docker setups
- **Project Validation**: Pre-startup validation to catch configuration errors early
- **Configuration Generation**: One-click generation of docker-compose.yml and Dockerfiles

**Developer Experience:**
- **Improved Architecture**: Modular codebase with clear separation of concerns
- **Better Error Handling**: Comprehensive error messages and recovery suggestions
- **Enhanced Documentation**: Inline help, tooltips, and contextual documentation links

## Installation

PeiDocker can be installed using pip or pixi (recommended):

### Using Pixi (Recommended)

```sh
# Install pixi if not already installed
curl -fsSL https://pixi.sh/install.sh | bash

# Clone the repository
git clone https://github.com/igamenovoer/PeiDocker.git
cd PeiDocker

# Install project dependencies (this will also install the package in editable mode)
pixi install

# Run commands using pixi
pixi run pei-docker-cli create -p ./build
pixi run pei-docker-gui start
```

### Using pip

```sh
pip install click omegaconf attrs cattrs nicegui
```

## Quick Start

PeiDocker offers two ways to manage projects: via command line (CLI) or web interface (GUI).

### Option 1: Web GUI (Recommended for beginners)

The modern web-based GUI provides a comprehensive interface for managing PeiDocker projects:

```sh
# Start the web GUI on an auto-selected free port
pei-docker-gui start

# Or specify a custom port
pei-docker-gui start --port 8080

# Load an existing project
pei-docker-gui start --project-dir /path/to/my/project

# Create a new project and jump to SSH configuration
pei-docker-gui start --project-dir /tmp/new-project --jump-to-page ssh

# Run in native desktop mode (requires pywebview)
pei-docker-gui start --native
```

The web interface will open at `http://localhost:<port>` (or in a native window with `--native`) and provides:

**Core Features:**
- **Visual Configuration Wizard**: Step-by-step guided setup with organized tabs
- **Real-time Validation**: Instant feedback with error highlighting and suggestions
- **Auto-port Selection**: Automatically finds available ports when defaults are in use
- **Project Import/Export**: ZIP file download/upload for easy project sharing and backup
- **Interactive Help**: Contextual tooltips and inline documentation throughout

**Configuration Capabilities:**
- **Project Settings**: Docker image configuration, base images, and output naming
- **SSH Management**: 
  - Multiple authentication methods (password, public key file, inline keys)
  - Direct private key input with automatic public key generation
  - Multi-user configuration with custom UIDs
- **Network Configuration**:
  - Separate port mappings for stage-1 (system) and stage-2 (application)
  - Proxy settings with global enable/disable options
  - Environment-specific network configurations
- **Storage Management**:
  - Auto-volume, manual-volume, host mount, and in-image storage options
  - Visual volume and bind mount configuration
  - Storage strategy switching without data loss
- **Script Automation**:
  - Custom scripts for build, first-run, every-run, and user-login events
  - Script parameter support with shell-like syntax
  - Stage-specific script organization
- **Environment Variables**:
  - Docker Compose-style variable substitution (`${VAR:-default}`)
  - Stage-specific environment configuration
  - Visual editor with syntax highlighting

**Advanced Features:**
- **Jump-to-Page Navigation**: Direct access to specific configuration sections
- **Minimal Config Templates**: Quick-start templates for common use cases
- **Native Desktop Mode**: OS-native window experience when pywebview is installed
- **Project Validation**: Pre-startup validation to prevent runtime errors
- **Configuration Export**: Generate docker-compose.yml and Dockerfiles with a single click

### Option 2: Command Line Interface

* Create a new project:

```sh
# cd to the root of the git repository
cd /path/to/PeiDocker

# Create a new project in ./build or any other directory
pei-docker-cli create -p ./build

# Optional: Create without examples or contrib files
pei-docker-cli create -p ./build --no-with-examples --no-with-contrib
```

* Edit the configuration file `user_config.yml` in the project directory (e.g.,`./build`) according to your needs.
* Generate the `docker-compose.yml` file in the project directory:

```sh
# From within the project directory
cd ./build
pei-docker-cli configure

# Or specify project directory explicitly
pei-docker-cli configure -p ./build

# Optional: Use a different config file
pei-docker-cli configure -p ./build -c my-custom-config.yml

# Optional: Generate full compose file with extended sections
pei-docker-cli configure -p ./build -f
```

## CLI Commands Reference

### `create` command

Creates a new PeiDocker project with template files and examples.

```sh
pei-docker-cli create [OPTIONS]
```

**Options:**
- `-p, --project-dir DIRECTORY`: Project directory (required)
- `-e, --with-examples`: Copy example files to the project dir (default: enabled)
- `--with-contrib`: Copy contrib directory to the project dir (default: enabled)
- `--help`: Show help message

**Examples:**
```sh
# Create project with all templates and examples
pei-docker-cli create -p ./my-project

# Create minimal project without examples
pei-docker-cli create -p ./minimal-project --no-with-examples --no-with-contrib
```

### `configure` command

Processes the configuration file and generates docker-compose.yml and related files.

```sh
pei-docker-cli configure [OPTIONS]
```

**Options:**
- `-p, --project-dir DIRECTORY`: Project directory (default: current working directory)
- `-c, --config FILE`: Config file name, relative to the project dir (default: `user_config.yml`)
- `-f, --full-compose`: Generate full compose file with extended sections (default: false)
- `--help`: Show help message

**Examples:**
```sh
# Use current directory as project directory with default config
pei-docker-cli configure

# Use default config file (user_config.yml) in specific directory
pei-docker-cli configure -p ./my-project

# Use custom config file
pei-docker-cli configure -p ./my-project -c prod-config.yml

# Generate full compose file with extended sections
pei-docker-cli configure -p ./my-project -f

# Use current directory with custom config file
pei-docker-cli configure -c prod-config.yml
```

For detailed CLI options and advanced usage, see the [CLI Reference](cli_reference.md).

* Build the docker images. There are two images to be built, namely `stage-1` and `stage-2`. `stage-1` is intended to be a base image, installing system apps using `apt install`, `stage-2` is intended to be a final image based on `stage-1`, installing custom apps using downloaded packages like `.deb`. External storage is only available in `stage-2`.

```sh
cd ./build

# Using docker compose to build the images. 
# To see all the output, use --progress=plain
# To cleanly rebuild the images, use --no-cache

# Build the stage-1 image
# By default, the image is named pei-image:stage-1, you can change it in user_config.yml
docker compose build stage-1 --progress=plain

# Build the stage-2 image
# By default, the image is named pei-image:stage-2
docker compose build stage-2 --progress=plain
```

* Run the docker container:

```sh
# inside project directory, such as ./build

# Typically you will run the stage-2 container
# You can also up the stage-1 container as well.
docker compose up stage-2
```

* If you have setup SSH in `user_config.yml`, now you can SSH into the container:

```sh
# by default, it will create a user named `me` with password '123456'
# and map the port 2222 to the container's port 22

ssh me@127.0.0.1 -p 2222
```

* That's it, you are good to go.

For more detailed information:
- [Web GUI Complete Guide](webgui_guide.md) - Comprehensive guide to the web interface
- [Examples](examples/basic.md) - Basic configuration examples
- [Advanced Examples](examples/advanced.md) - Complex configuration scenarios

* If you prefer to run the image using `docker run` instead of `docker compose`, you can convert the `docker-compose.yml` to commands using [Decomposerize](https://www.decomposerize.com/).
* If you have trouble connecting to docker.io when building the image, you can either set the global proxy for docker, or pull the base image manually and tag it with a local name. For detail, see [stack overflow](https://stackoverflow.com/questions/68520864/how-to-disable-loading-metadata-while-executing-docker-build).

```sh
# get the base image manually
docker pull ubuntu:24.04

# tag it with a local name, 
# in user_config.yml, use my-ubuntu:24.04 as the base image 
# to skip checking with docker.io
docker tag ubuntu:24.04 my-ubuntu:24.04
```

## Custom commands

* To run custom commands during build, edit the scripts in `<project_dir>/installation/stage-<1,2>/custom`. You can also run other scripts by adding them in `user_config.yml`.
* **Custom script parameters**: Scripts can accept shell-like parameters using quotes: `'script.sh --param=value --flag'`. Parameters are safely parsed and passed to scripts during execution.
* If you have *on-first-run* commands in `user_config.yml`, after the first run, you shall commit the container to a new image so that the changes are saved, or otherwise those commands will be executed again when the container is recreated.

## Stage-2 storage

The image built in stage-2 have the following directories for user:

- `/soft/app`: the directory to store the installed apps.
- `/soft/data`: the directory to store the data files.
- `/soft/workspace`: the directory to store the workspace files, like code.

These `/soft/xxx` are links to the corresponding directories in `/hard/image/xxx` (in-image storage) or `/hard/volume/xxx` (external storage), where content is actually stored, based on the following rules:

- If `/hard/volume/xxx` is found, then `/soft/xxx` is a link to `/hard/volume/xxx`.
- Otherwise, if `/hard/image/xxx` is found, then `/soft/xxx` is a link to `/hard/image/xxx`.

As such, you can switch between in-image storage and external storage by mounting into `/hard/volume/xxx`, and this behavious is already present in the generated `docker-compose.yml` file based on your `user_config.yml`. Note that only predefined directories (`app`, `data`, `workspace`) are linked, others will be ignored.

## Project directory layout

Inside your project directory, you will find the following files and directories:

    compose-template.yml    # the template for docker-compose.yml, do not modify this file
    stage-1.Dockerfile      # the Dockerfile for stage-1 image, do not modify this file
    stage-2.Dockerfile      # the Dockerfile for stage-2 image, do not modify this file
    user_config.yml         # the configuration file, edit this file to customize
    installation/           # this directory will be copied into the image under /pei-from-host
        stage-1/            # the scripts to run during stage-1 image building
            custom/         # the custom scripts to run during stage-1 image building, you need to explicitly list them in user_config.yml
            tmp/            # the temporary directory to store downloaded packages, like .deb, .whl, etc.
            system/         # the configuration files for system apps, like apt, pip, etc.
            ...
        stage-2/            # the scripts to run during stage-2 image building
            custom/         # the custom scripts to run during stage-2 image building, you need to explicitly list them in user_config.yml
            tmp/            # the temporary directory to store downloaded packages, like .deb, .whl, etc.
            system/         # the configuration files for system apps, like apt, pip, etc.
            ...

## User configuration file

Here are the options you can set in `user_config.yml`:

```yaml
# all paths are relative to /installation directory

stage_1:
  # input/output image settings
  image:
    base: ubuntu:24.04
    output: pei-image:stage-1

  # ssh settings
  ssh:
    enable: true
    port: 22  # port in container
    host_port: 2222  # port in host

    # ssh users, the key is user name, value is user info
    users:
      me:
        password: '123456'
        uid: 1000  # user ID (optional, defaults to auto-assigned)

        # SSH key authentication (optional, choose ONE method):
        # Method 1: Reference a public key file (relative to installation directory)
        pubkey_file: 'stage-1/system/ssh/keys/example-pubkey.pub'
        
        # Method 2: Provide public key text directly inline
        # pubkey_text: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC...'
        
        # Method 3: Provide private key text directly (public key will be generated)
        # privkey_text: |
        #   -----BEGIN OPENSSH PRIVATE KEY-----
        #   b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2g...
        #   -----END OPENSSH PRIVATE KEY-----
        
        # Method 4: Reference a private key file (public key will be generated)
        # privkey_file: 'stage-1/system/ssh/keys/my-private-key'
        
      you:
        password: '654321'
        pubkey_file: null
        uid: 1001
      root: # you can configure root user here
        password: root
        pubkey_file: null
        uid: 0  # root uid, always 0 regardless of what you put here

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
    # replace the default apt source with a custom one, use empty string to disable this
    # repo_source: 'stage-1/system/apt/ubuntu-22.04-tsinghua-x64.list'
    # special values that refer to well known apt sources:
    # 'tuna' : 'http://mirrors.tuna.tsinghua.edu.cn/ubuntu/'
    # 'aliyun' : 'http://mirrors.aliyun.com/ubuntu/'
    # '163' : 'http://mirrors.163.com/ubuntu/'
    # 'ustc' : 'http://mirrors.ustc.edu.cn/ubuntu/'
    # 'cn' : 'http://cn.archive.ubuntu.com/ubuntu/
    repo_source: ''
    keep_repo_after_build: true # keep the apt source file after build?
    use_proxy: false  # use proxy for apt?
    keep_proxy_after_build: false # keep proxy settings after build?

  # additional environment variables
  # Supports Docker Compose-style variable substitution: ${VAR:-default}
  # see https://docs.docker.com/compose/environment-variables/set-environment-variables/
  environment:
    - 'EXAMPLE_VAR_STAGE_1=example env var'
    - 'API_URL=${API_URL:-http://localhost:8080}'

  # port mapping for stage-1 (system-level services)
  # Use this for databases, cache servers, monitoring tools, etc.
  # see https://docs.docker.com/compose/networking/
  ports: 
    - "5432:5432"  # PostgreSQL example
    - "6379:6379"  # Redis example

  # device settings
  device:
    type: cpu # can be cpu or gpu

  # mount external volumes to container
  # the volumes can be given any names, mounted anywhere
  # mount section does NOT transfer to the next stage, so you need to define them again in stage-2
  mount:
    apt_cache:
      type: auto-volume
      dst_path: /var/cache/apt
      host_path: null
      volume_name: null

  # custom scripts
  custom:
    # scripts run during build
    on_build: 
      - 'stage-1/custom/install-dev-tools.sh' # just an example, you can safely remove this
      - 'stage-1/custom/my-build-1.sh'
      - 'stage-1/custom/my-build-2.sh --verbose --config=/tmp/build.conf'

    # scripts run on first run
    on_first_run:
      - 'stage-1/custom/my-on-first-run-1.sh'
      - 'stage-1/custom/my-on-first-run-2.sh --initialize --create-dirs'

    # scripts run on every run
    on_every_run:
      - 'stage-1/custom/my-on-every-run-1.sh'
      - 'stage-1/custom/my-on-every-run-2.sh --check-health'

    # scripts run on user login
    on_user_login:
      - 'stage-1/custom/my-on-user-login-1.sh'
      - 'stage-1/custom/my-on-user-login-2.sh --show-motd --update-prompt'
    
stage_2:

  # input/output image settings
  image:
    base: null  # if not specified, use the output image of stage-1
    output: pei-image:stage-2

  # additional environment variables
  # Supports Docker Compose-style variable substitution: ${VAR:-default}
  # see https://docs.docker.com/compose/environment-variables/set-environment-variables/
  environment:  # use list instead of dict
    - 'EXAMPLE_VAR_STAGE_2=example env var'
    - 'NODE_ENV=${NODE_ENV:-production}'
    - 'APP_PORT=${APP_PORT:-3000}'

  # port mapping for stage-2 (application-level services)
  # Use this for web apps, APIs, microservices, etc.
  # Note: These are independent from stage-1 ports (not appended)
  # see https://docs.docker.com/compose/networking/
  ports: 
    - "8080:8080"  # Web application example
    - "3000:3000"  # Node.js app example    

  # device settings, will override the stage-1 device settings
  device:
    type: cpu # can be cpu or gpu

  # proxy settings
  # inside the container, the proxy will accessed as http://{address}:{port}
  # note that whether the proxy is used or not depends on the applications
  proxy:
    address: null # this means to use the proxy settings of stage-1
    port: null
    enable_globally: null 
    remove_after_build: null 
    use_https: null

  # storage configurations
  storage:
    app:
      type: auto-volume # auto-volume, manual-volume, host, image
      host_path: null # host directory to be mounted, in effect when type=host
      volume_name: null # volume name, in effect when type=manual-volume
    data:
      type: auto-volume
      host_path: null
      volume_name: null
    workspace:
      type: auto-volume
      host_path: null
      volume_name: null

  # mount external volumes to container
  # the volumes can be given any names, mounted anywhere
  # the volume type cannot be 'image', or otherwise it will be ignored
  mount:
    home_me:
      type: auto-volume   # auto-volume, manual-volume, host
      dst_path: /home/me
      host_path: null
      volume_name: null
    apt_cache:
      type: auto-volume
      dst_path: /var/cache/apt
      host_path: null
      volume_name: null

  # custom scripts in stage-2, run after stage-1 custom scripts
  custom:
    # scripts run during build
    on_build: 
      - 'stage-2/custom/install-gui-tools.sh' # just an example, you can safely remove this
      - 'stage-2/custom/my-build-1.sh'
      - 'stage-2/custom/my-build-2.sh --enable-desktop --theme=dark'

    # scripts run on first start
    on_first_run:
      - 'stage-2/custom/my-on-first-run-1.sh'
      - 'stage-2/custom/my-on-first-run-2.sh --setup-workspace --clone-repos'

    # scripts run on every start
    on_every_run:
      - 'stage-2/custom/my-on-every-run-1.sh'
      - 'stage-2/custom/my-on-every-run-2.sh --update-status --log-startup'

    # scripts run on user login
    on_user_login:
      - 'stage-2/custom/my-on-user-login-1.sh'
      - 'stage-2/custom/my-on-user-login-2.sh --welcome-message --check-updates'
```