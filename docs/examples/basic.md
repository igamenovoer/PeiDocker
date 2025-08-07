# Examples

[](){#basic-ssh}
## Basic Ubuntu image with SSH support

This is the most basic example of creating an image with SSH support. The image is based on `ubuntu:24.04` and has three users: `me`, `you`, and `root`. The passwords for the users are `123456`, `654321`, and `root` respectively. The SSH server is running on port `22` and mapped to host port `2222`. 

To accelerate apt installation in China, the `apt` source is set to `tuna`. For other options, see the full [config file](../index.md) for documentation. If this option is omitted, the default source will be used.

**Note:** This example uses password-only authentication. For advanced SSH key configuration including inline keys, file-based keys, and environment variable integration, see [Advanced SSH Key Configuration](advanced.md#ssh-keys-advanced).

```yaml
# user_config.yml under project directory

stage_1:
  image:
    base: ubuntu:24.04
    output: pei-image:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '123456'
      you:
        password: '654321'
      root:
        password: root
  apt:
    repo_source: tuna
```

With this `user_config.yml` in side your project dir, do the followings to build and run the image:

```bash
# From within the project directory
cd /path/to/project
pei-docker-cli configure

# Or specify project directory explicitly
pei-docker-cli configure --project-dir=/path/to/project

# Build and run the image
docker compose build stage-1 --progress=plain --no-cache
docker compose up stage-1
```

### With docker run
If you prefer to use `docker run` to run the image, you can copy-paste the `docker-compose.yml` file into [Decomposerize](https://www.decomposerize.com/) to get the `docker run` command. The command will look like this:

```bash
docker run -i -t --add-host host.docker.internal:host-gateway -p 2222:22 pei-image:stage-1 /bin/bash
```

## SSH Key Configuration

While password authentication works well for basic usage, you can also configure SSH keys for more secure access. PeiDocker supports using your existing system SSH keys with the `~` syntax for automatic discovery.

### Using System SSH Keys

When you specify `~` for `pubkey_file` or `privkey_file`, PeiDocker will automatically discover and use your system SSH keys from your home directory (`~/.ssh/`). The discovery follows this priority order: `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`.

```yaml
# user_config.yml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-image:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '123456'
        pubkey_file: '~'        # Auto-discovers your system public key
      admin:
        password: 'admin123'
        privkey_file: '~'       # Auto-discovers your system private key
  apt:
    repo_source: tuna
```

### Important Notes

- **Public keys**: When using `pubkey_file: '~'`, your system public key will be added to the container's `authorized_keys`, allowing passwordless SSH access
- **Private keys**: When using `privkey_file: '~'`, your system private key will be copied to the container using standard SSH filenames (`id_rsa`, `id_ecdsa`, etc.)
- **Encrypted private keys**: If your private key is encrypted, it will be copied as-is without decryption attempts (no passphrase prompts during build)
- **Manual public key generation**: For encrypted private keys, you can manually generate the public key inside the container: `ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub`
- **Absolute paths**: You can also use absolute paths like `/home/user/.ssh/id_rsa.pub` instead of the `~` syntax

With this configuration, you can SSH into the container using your existing SSH keys:

```bash
# Using your private key (if pubkey_file was configured)
ssh -p 2222 me@127.0.0.1

# Or specify your key explicitly
ssh -i ~/.ssh/id_rsa -p 2222 admin@127.0.0.1
```

### SSH Key Methods

PeiDocker supports multiple methods for configuring SSH keys for users, giving you flexibility in how you manage authentication. All SSH key processing (such as public key generation from private keys) happens inside the container during the build process, ensuring cross-platform compatibility.

#### Method 1: Public Key File (Legacy)
Reference an existing public key file relative to the installation directory:

```yaml
users:
  myuser:
    password: 'mypassword'
    pubkey_file: 'stage-1/system/ssh/keys/my-key.pub'
```

#### Method 2: Inline Public Key Text
Provide the public key content directly in the configuration:

```yaml
users:
  myuser:
    password: 'mypassword'
    pubkey_text: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7vbqajDhA... user@host'
```

#### Method 3: Inline Private Key Text
Provide the private key content directly - the public key will be automatically generated inside the container:

```yaml
users:
  myuser:
    password: 'mypassword'
    privkey_text: |
      -----BEGIN OPENSSH PRIVATE KEY-----
      b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2g...
      -----END OPENSSH PRIVATE KEY-----
```

#### Method 4: Private Key File
Reference a private key file - the public key will be automatically generated inside the container:

```yaml
users:
  myuser:
    password: 'mypassword'
    privkey_file: 'stage-1/system/ssh/keys/my-private-key'
```

### Security Model

- **Cross-platform compatibility**: All SSH key operations (including public key generation) happen inside the Linux container during build, not on the host system
- **Mutual exclusivity**: You can only use one SSH key method per user - the configuration will be validated to prevent conflicts
- **Text-based keys**: When using `pubkey_text` or `privkey_text`, the key content is written to temporary files in the project directory and referenced in the docker-compose configuration
- **Container-side processing**: Private key validation and public key extraction are performed by standard SSH tools inside the container

### Example Configurations

#### Basic SSH setup with inline public key:
```yaml
stage_1:
  ssh:
    enable: true
    host_port: 2222
    users:
      developer:
        password: 'devpass123'
        pubkey_text: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7vbqajDhA... dev@laptop'
```

#### Multiple users with different key methods:
```yaml
stage_1:
  ssh:
    enable: true
    host_port: 2222
    users:
      alice:
        password: 'alice123'
        pubkey_file: 'stage-1/system/ssh/keys/alice-key.pub'  # File-based public key
      bob:
        password: 'bob456'
        privkey_text: |  # Inline private key
          -----BEGIN OPENSSH PRIVATE KEY-----
          b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2g...
          -----END OPENSSH PRIVATE KEY-----
      charlie:
        password: 'charlie789'
        pubkey_text: 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... charlie@workstation'  # Inline public key
```

### Usage Tips

1. **Key format validation**: PeiDocker validates that public keys start with recognized prefixes (`ssh-rsa`, `ssh-ed25519`, etc.) and private keys are properly formatted OpenSSH keys
2. **Generated files**: When using text-based keys, PeiDocker automatically creates key files in `installation/stage-1/generated/` and references them in the docker-compose configuration
3. **Example key provided**: PeiDocker includes an example public key at `project_files/installation/stage-1/system/ssh/keys/example-pubkey.pub` that you can use for testing
4. **Complete example**: See `examples/ssh-keys-inline.yml` in your project directory for a comprehensive example using all SSH key methods
5. **Security consideration**: Be careful when storing private keys in configuration files - consider using environment variables or external key files for production deployments

### Troubleshooting

- **Permission errors**: SSH keys in the container are automatically set to the correct permissions (600 for private keys, 644 for public keys)
- **Key validation failures**: Check that your key text is properly formatted and includes the full key content including headers and footers for private keys
- **Connection issues**: Verify that the SSH port mapping is correct and that the SSH service started successfully in the container logs

_For more advanced SSH key configuration including environment variable integration and team development scenarios, see [Advanced SSH Key Configuration](advanced.md#ssh-keys-advanced)._

## GPU image with external storage

This example is based on [the basic ssh image](#basic-ssh), which demonstrates how to use GPU in the container. The image is based on `nvidia/cuda:11.8.0-runtime-ubuntu22.04` that makes use of the GPU. As such, the `device` section is added to the `stage_1` and `stage_2` sections, which are set to `gpu`.

```yaml
stage_1:
  image:
    base: nvidia/cuda:11.8.0-runtime-ubuntu22.04
    output: pei-image:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '123456'
      root:
        password: root
  apt:
    repo_source: tuna
  device:
    type: gpu
stage_2:
  image:
    output: pei-image:stage-2
  device:
    type: gpu
  storage:
    app:
      type: host
      host_path: d:/code/PeiDocker/build/storage/app
    data:
      type: host
      host_path: d:/code/PeiDocker/build/storage/data
    workspace:
      type: host
      host_path: d:/code/PeiDocker/build/storage/workspace
```

### External storage with host directory

The `stage-2` image has three external storage directories: `app`, `data`, and `workspace` (note that the directory names are **NOT CUSTOMIZABLE**, for arbitrary mounts, see [the next section](#mount-additional-volumes)), where specified host directories are mounted. In the container, you can access these directories through `/soft/app`, `/soft/data`, and `/soft/workspace`, which are linked to  `/app`, `/data`, and `/workspace` under the `/hard/volume`. In this example, the host directories are `d:/code/PeiDocker/build/storage/app`, `d:/code/PeiDocker/build/storage/data`, and `d:/code/PeiDocker/build/storage/workspace` (Windows path).

[](){#mount-additional-volumes}
### Mounting arbitrary volumes or directories

You can mount additional volumes or directories to the container by adding them to the `mount` section. The following example demonstrates how to mount the `apt_cache` directory to the container's `/var/cache/apt` directory, in this way, the apt cache will be saved for future use. `home_me` is mounted to `/home/me` to save the home directory to a volume, so that it will not get lost after the container is deleted. 

Unlike `app`, `data`, and `workspace`, the mounted volumes `apt_cache` and `home_me` will not be linked to `/soft`, they are mounted directly to the container and not managed by PeiDocker. You can also use `manual-volume` (with `volume_name` set) or `host` (with `host_path` set) in ther `type` though.

```yaml
# heavy duty cpp development, install a lot of things

stage_1:
  # input/output image settings
  image:
    base: nvidia/cuda:12.3.2-runtime-ubuntu22.04
    output: pei-image:stage-1

  # ssh settings
  ssh:
    port: 22  # port in container
    host_port: 2222  # port in host

    # ssh users, the key is user name, value is user info
    users:
      me:
        password: '123456'
      root: # you can configure root user here
        password: root
        pubkey_file: null

  device:
    type: gpu

  apt:
    repo_source: 'tuna'

  # additional mounts
  mount:
    # save apt cache, to speed up future installations
    apt_cache:
      type: auto-volume
      dst_path: /var/cache/apt
    
stage_2:
  image:
    output: pei-image:stage-2
  device:
    type: gpu

  # additional mounts
  mount:
    # save home directory to volume, so that it will not get lost after container deletion
    home_me:
      type: auto-volume
      dst_path: /home/me

    # mount will not be inherited from stage-1
    # you need to mount it again, or otherwise it will not be mounted
    apt_cache:
      type: auto-volume
      dst_path: /var/cache/apt
```

### With docker-compose

To build and run the image, do the followings:

```bash
# assuming the project dir is /path/to/project

# build stage-1
docker compose -f /path/to/project/docker-compose.yml build stage-1 --progress=plain --no-cache

# build stage-2
docker compose -f /path/to/project/docker-compose.yml build stage-2 --progress=plain --no-cache

# start stage-2
docker compose -f /path/to/project/docker-compose.yml up stage-2
```

After that, you can ssh into the container with the following command:

```bash
ssh -p 2222 me@127.0.0.1
```


### With docker run

If you are using `docker run` to run the image, you can copy-paste the `docker-compose.yml` file into [Decomposerize](https://www.decomposerize.com/) to get the `docker run` command. The command will look like this, note that you need to add `--gpus all` manually:

```bash
# you only need to run stage-2
docker run --gpus all -i -t --add-host host.docker.internal:host-gateway -p 2222:22 -v d:/code/PeiDocker/build/storage/app:/hard/volume/app -v d:/code/PeiDocker/build/storage/data:/hard/volume/data -v d:/code/PeiDocker/build/storage/workspace:/hard/volume/workspace pei-image:stage-2 /bin/bash
```

[](){#external-storage}
## Using docker volume as external storage

Using [docker volumes](https://docs.docker.com/storage/volumes/) is preferred if you run the image locally, because it is more efficient, and will not get lost when the container is removed. Docker volumes can be created automatically, or [manually](https://docs.docker.com/reference/cli/docker/volume/create/) with a given name that can be used to mount the volume to the container. 

This example is based on [the basic ssh image](#basic-ssh), which demonstrates how to use existing docker volumes as external storage. The `stage-2` image has three external storage directories: `app`, `data`, and `workspace` (note that the directory names are **NOT CUSTOMIZABLE**, they are **predefined**), where **docker volumes** are mounted. 


```yaml
# user_config.yml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-image:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '123456'
  apt:
    repo_source: tuna
stage_2:
  image:
    output: pei-image:stage-2
  storage:
    app:
      type: auto-volume
    data:
      type: manual-volume
      volume_name: my_data
    workspace:
      type: manual-volume
      volume_name: my_workspace
```

`app` is an **auto-volume**, which means it will be created automatically. `data` and `workspace` are **manual-volumes**, which means they are created manually with the names `my_data` and `my_workspace` first, and then mounted to the container. To create these volumes, use the following commands

```bash
docker volume create my_data
docker volume create my_workspace
``` 

You can check the volumes with `docker volume ls`.

If you are using the [docker desktop](https://www.docker.com/products/docker-desktop) on Windows, you will see this:

![docker desktop volumes](../images/docker-desktop-volumes.png)

In the container, you can access these directories through `/soft/app`, `/soft/data`, and `/soft/workspace`, which are linked to  `/app`, `/data`, and `/workspace` under the `/hard/volume`.


### With docker run

If you are using `docker run` to run the image, you can copy-paste the `docker-compose.yml` file into [Decomposerize](https://www.decomposerize.com/) to get the `docker run` command. Note that you will have to create all volumes manully. The command will look like this:

```bash
# using docker run, you will have to create all volumes manually
docker volume create app
docker volume create my_data
docker volume create my_workspace
docker run -i -t --add-host host.docker.internal:host-gateway -p 2222:22 -v app:/hard/volume/app -v data:/hard/volume/data -v workspace:/hard/volume/workspace pei-image:stage-2 /bin/bash

# you don't need to run stage-1
# docker run -i -t --add-host host.docker.internal:host-gateway -p 2222:22 pei-image:stage-1 /bin/bash
```

[](){#install-pixi}
## Install pixi package manager

**Pixi** is a modern, fast package manager for Python that uses conda-forge packages but with significantly better performance than conda. It's designed for modern Python development workflows and supports creating isolated environments with precise dependency management.

**Note**: PeiDocker now recommends pixi over conda/miniconda for package management due to its superior performance and modern design. However, if you prefer to use conda/miniconda, the installation scripts are still available in `src/pei_docker/project_files/installation/stage-2/system/conda/` and can be referenced for custom implementations.

### Basic pixi installation

This example demonstrates how to automatically install pixi and set up a common development environment with essential Python packages. The installation uses the tuna mirror for faster downloads in China.

```yaml
# user_config.yml - basic pixi installation
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-pixi-basic:stage-1
  
  ssh:
    enable: true
    port: 22
    host_port: 2222
    
    users:
      developer:
        password: 'dev123'
        uid: 1100
      root:
        password: 'root123'

  apt:
    repo_source: tuna

stage_2:
  image:
    output: pei-pixi-basic:stage-2
  
  # storage configurations - using image storage for this basic example
  storage:
    app:
      type: image
    workspace:
      type: image
    data:
      type: image
  
  # custom scripts to install and configure pixi
  custom:
    on_first_run:
      - 'stage-2/system/pixi/install-pixi.bash'
      - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'
      - 'stage-2/system/pixi/create-env-common.bash'
```

### Pixi with persistent storage

For better persistence and performance, use external volumes to store pixi installation and cache:

```yaml
# user_config.yml - pixi with volumes for persistence
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-pixi-volumes:stage-1
  
  ssh:
    enable: true
    port: 22
    host_port: 2222
    
    users:
      developer:
        password: 'dev123'
        uid: 1100

  apt:
    repo_source: tuna

stage_2:
  image:
    output: pei-pixi-volumes:stage-2
  
  # storage configurations using volumes for persistence
  storage:
    app:
      type: auto-volume
    workspace:
      type: auto-volume
    data:
      type: auto-volume
  
  # additional mounts for persistent user settings
  mount:
    home_developer:
      type: auto-volume
      dst_path: /home/developer
  
  # custom scripts with persistent cache directory
  custom:
    on_first_run:
      # Install pixi with cache directory in external storage
      - 'stage-2/system/pixi/install-pixi.bash --cache-dir=/hard/volume/app/pixi-cache'
      - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'
      - 'stage-2/system/pixi/create-env-common.bash'
```

### Pixi for machine learning (GPU)

For ML development with GPU support and additional packages:

```yaml
# user_config.yml - pixi with ML packages and GPU support
stage_1:
  image:
    base: nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
    output: pei-pixi-ml:stage-1
  
  ssh:
    enable: true
    port: 22
    host_port: 2222
    
    users:
      mldev:
        password: 'ml123'
        uid: 1100

  apt:
    repo_source: tuna
    
  device:
    type: gpu

stage_2:
  image:
    output: pei-pixi-ml:stage-2
  
  device:
    type: gpu
    
  storage:
    app:
      type: auto-volume
    workspace:
      type: auto-volume  
    data:
      type: auto-volume
  
  # additional mounts for ML development
  mount:
    models:
      type: auto-volume
      dst_path: /models
      
    home_mldev:
      type: auto-volume
      dst_path: /home/mldev
  
  environment:
    - 'NVIDIA_VISIBLE_DEVICES=all'
    - 'NVIDIA_DRIVER_CAPABILITIES=all'
  
  custom:
    on_first_run:
      # Install pixi with cache in external storage
      - 'stage-2/system/pixi/install-pixi.bash --cache-dir=/hard/volume/app/pixi-cache'
      - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'
      # Install both common and ML packages
      - 'stage-2/system/pixi/create-env-common.bash'
      - 'stage-2/system/pixi/create-env-ml.bash'
```

### What pixi installation includes:

#### Common packages (`create-env-common.bash`):
- `scipy` - Scientific computing library
- `click` - Command line interface toolkit
- `attrs` - Classes without boilerplate
- `omegaconf` - Configuration management
- `rich` - Rich text and formatting
- `networkx` - Network analysis
- `ipykernel` - Jupyter kernel support

#### ML packages (`create-env-ml.bash`):
- `pytorch`, `torchvision` - Deep learning framework
- `opencv` - Computer vision library
- `open3d` - 3D data processing
- `trimesh` - 3D mesh processing
- `pyvista`, `pyvistaqt` - 3D visualization
- `pyqt` - GUI framework
- `mkdocs-material` - Documentation generator

### Build and run process:

```bash
# generate docker-compose.yml from within project directory
cd /path/to/project
pei-docker-cli configure

# build stage-1
docker compose build stage-1 --progress=plain --no-cache

# build stage-2 (this installs pixi on first run)
docker compose build stage-2 --progress=plain --no-cache

# start stage-2 container
docker compose up -d stage-2
```

### Verify pixi installation:

After the container starts, SSH in and verify pixi is working:

```bash
# SSH into the container
ssh -p 2222 developer@127.0.0.1

# Check pixi installation
pixi --version

# List global environments
pixi global list

# Verify packages are available
python -c "import scipy; print('scipy:', scipy.__version__)"
python -c "import click; print('click:', click.__version__)"
python -c "import rich; print('rich:', rich.__version__)"

# For ML environment, also check:
python -c "import torch; print('pytorch:', torch.__version__)"
python -c "import cv2; print('opencv:', cv2.__version__)"
```

### Key advantages of pixi over conda:

- **Speed**: Significantly faster package resolution and installation
- **Modern**: Built with Rust, designed for current Python workflows  
- **Cross-platform**: Works consistently across Linux, macOS, and Windows
- **Lock files**: Automatic lock file generation for reproducible environments
- **Global environments**: Easy management of global tool installations

### Important notes:

- **Persistence**: When using external storage, pixi installation persists across container restarts
- **First run only**: Installation scripts run only on first container startup using `on_first_run`
- **Custom cache**: Use `--cache-dir` parameter to store package cache in external storage for faster rebuilds
- **Adding packages**: Run `pixi global install package_name` inside the container to add more packages
- **Commit changes**: To bake pixi into the image permanently:
  ```bash
  docker commit <container_id> pei-pixi-ml:stage-2
  ```

### Advanced customization:

You can customize pixi installation by modifying the scripts in `installation/stage-2/system/pixi/` or creating your own environment setup scripts for specific use cases.

### Migration from conda:

If you previously used conda/miniconda, pixi provides a similar but faster experience:
- Global environments replace conda's base environment
- Package installation is significantly faster
- Better dependency resolution and reproducibility
- For legacy conda scripts, see `src/pei_docker/project_files/installation/stage-2/system/conda/`

## Custom script parameters

PeiDocker supports passing parameters to custom scripts using shell-like syntax. This allows you to customize script behavior without modifying the script files themselves.

```yaml
stage_1:
  custom:
    on_build:
      - 'stage-1/custom/my-build.sh --verbose --config=/tmp/build.conf'
    on_first_run:
      - 'stage-1/custom/setup.sh --initialize --create-dirs'
    on_every_run:
      - 'stage-1/custom/health-check.sh --check-services --log-output'

stage_2:
  custom:
    on_build:
      - 'stage-2/custom/install-app.sh --enable-desktop --theme=dark'
    on_user_login:
      - 'stage-2/custom/welcome.sh --show-motd --check-updates'
```

### How it works:

- Parameters are safely parsed using shell-like syntax
- Scripts receive parameters as standard command-line arguments
- Both single and double quotes are supported for complex parameters
- Works across all script lifecycle events (on_build, on_first_run, on_every_run, on_user_login)

### Example script implementation:

```bash
#!/bin/bash
# example script showing parameter handling

# Default values
VERBOSE=false
CONFIG_FILE=""

# Parse parameters
for arg in "$@"; do
    case $arg in
        --verbose)
            VERBOSE=true
            ;;
        --config=*)
            CONFIG_FILE="${arg#*=}"
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

# Use parameters
if [ "$VERBOSE" = true ]; then
    echo "Verbose mode enabled"
fi
```

## Using proxy

You can use proxy when building the image. The following example demonstrates how to use proxy for `stage_1`. The proxy is set to `host.docker.internal:30080`, which refers to `127.0.0.1:30080` in host where the proxy is running. The `apt` is specified to use the proxy, and the proxy is kept after the build.

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-image:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '123456'
      you:
        password: '654321'
      root:
        password: root
  proxy:
    address: host.docker.internal
    port: 30080
    enable_globally: false  # if set to true, the proxy is used during build and run
    remove_after_build: false # if set to true, the proxy is removed after build, not effecting run
    use_https: false  # false means http proxy is used where https proxy is requested
  apt:
    use_proxy: true   # use the proxy for apt
    keep_proxy_after_build: true  # keep apt using the proxy after build
```

### Using proxy during build and run

This example shows how to use proxy during build and run. The key is to set `enable_globally` to `true`. If you set `remove_after_build` to `true`, the proxy will be removed after the build, and not effecting the run, this is useful if you only want to use the proxy during build (e.g., pulling sources from github).

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-image:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '123456'
      you:
        password: '654321'
      root:
        password: root
  proxy:
    address: host.docker.internal
    port: 30080
    enable_globally: true
    remove_after_build: false
    use_https: false
  apt:
    repo_source: tuna
```

### Using proxy across stages

This example shows how to use proxy across stages. The proxy is set in `stage-1`, but only used for `apt`. In `stage-2`, the proxy is enabled globally, affecting all commands after run. 

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-image:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '123456'
      you:
        password: '654321'
      root:
        password: root
  proxy:
    address: host.docker.internal
    port: 30080
    enable_globally: false
    remove_after_build: false
    use_https: false
  apt:
    use_proxy: true
    keep_proxy_after_build: true
stage_2:
  image:
    output: pei-image:stage-2
  proxy:
    enable_globally: true
```

You can verify the proxy is set by running `env` after ssh into the container.

```sh
# inside container
env | grep -i proxy

# you should see the proxy settings
# http_proxy=http://host.docker.internal:30080
# https_proxy=http://host.docker.internal:30080
```

### Using proxy manually

If you specify the proxy, but never use it, it will not automatically affect anything. But you can find the proxy setting in the container, using environment variables `PEI_HTTP_PROXY_1` and `PEI_HTTPS_PROXY_1` (replace `1` with the stage number). 

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-image:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '123456'
      you:
        password: '654321'
      root:
        password: root
  proxy:
    address: host.docker.internal
    port: 30080
  apt:
    repo_source: tuna
```

After ssh into the container, you can find the proxy settings:

```sh
# inside container
env | grep -i proxy

# you should see the proxy settings
# PEI_HTTP_PROXY_1=http://host.docker.internal:30080
# PEI_HTTPS_PROXY_1=http://host.docker.internal:30080
```
