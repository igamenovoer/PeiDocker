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
# assuming the project dir is /path/to/project

python -m pei_docker.pei configure --project-dir=/path/to/project

cd /path/to/project
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

[](){#miniconda-in-image}
## Install miniconda in image

**IMPORTANT NOTE**: The following example is for demonstration purposes only. It is **not recommended** to install miniconda (or any other apps) in the image, because it will make the image size larger, and later modifications (such as `conda install xxx`) will get lost when container is removed. It is recommended to install miniconda in the volume storage `/hard/volume/app`, and copy them to the image storage `/hard/image/app` when you decide to bake them into image. However, **external storage only exists in stage-2**.

To install miniconda during build, you can make use of custom scripts. PeiDocker allows you to add your scripts in the `project_dir/installation/stage-<1,2>/custom`, and then specify them in the `user_config.yml` file.

```yaml
# user_config.yml
stage_1:
  image:
    base: nvidia/cuda:12.3.2-runtime-ubuntu22.04
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
      type: image
    data:
      type: image
    workspace:
      type: image
  custom:
    on_build:
    - stage-2/system/conda/auto-install-miniconda.sh
```

In the above example, the script `auto-install-miniconda.sh` is placed in the `project_dir/installation/stage-2/system/conda` directory. The script will be executed during the build of the `stage-2` image. Below is the content of the script. It first checks if the miniconda installation file exists in the `/tmp` directory, and if not, downloads it from the tuna mirror. Then it installs miniconda to `/hard/image/app/miniconda3`, and initializes conda for all users. The conda and pip mirrors are set to the tuna mirror. Important points to note:

- Custom script can be placed anywhere in the project directory, but it is recommended to put them in the `project_dir/installation/stage-<1,2>/custom` directory. Locations like `xxx/system` are managed by official developers, and may be overwritten in future updates.
- The package files are placed in the `project_dir/installation/stage-2/tmp` directory.
- You can access the installation directory of the `stage-2` image using the `PEI_STAGE_DIR_2` environment variable, likewise for `stage-1`. Note it will try to use external storage `\hard\volume\app` first, but because you have not mounted any external storage, it will use the image storage `\hard\image\app`.
- During build, you are root, so you shall execute commands for other users using `su - $user -c`.
- Remember to set DEBIAN_FRONTEND=noninteractive to prevent interactive prompts.

```bash
#!/bin/bash

# prevent interactive prompts
export DEBIAN_FRONTEND=noninteractive

# PEI_STAGE_DIR_2 points to where the installation/stage-2 is inside container
STAGE_2_DIR_IN_CONTAINER=$PEI_STAGE_DIR_2
echo "STAGE_2_DIR_IN_CONTAINER: $STAGE_2_DIR_IN_CONTAINER"

# the installation directory of miniconda3
# first check for volume storage at /hard/volume/app, if not found, use /hard/image/app
if [ -d "/hard/volume/app" ]; then
  # volume storage takes precedence, note that it only exists in stage-2
  CONDA_INSTALL_DIR="/hard/volume/app/miniconda3"
else
  # otherwise, use the image storage
  CONDA_INSTALL_DIR="/hard/image/app/miniconda3"
fi

# already installed? skip
if [ -d $CONDA_INSTALL_DIR ]; then
    echo "miniconda3 is already installed in $CONDA_INSTALL_DIR, skipping ..."
    exit 0
fi

# download the miniconda3 installation file yourself, and put it in the tmp directory
# it will be copied to the container during the build process
CONDA_PACKAGE_NAME="Miniconda3-latest-Linux-x86_64.sh"

# are you in arm64 platform? If so, use the arm64 version of miniconda3
if [ "$(uname -m)" = "aarch64" ]; then
    CONDA_PACKAGE_NAME="Miniconda3-latest-Linux-aarch64.sh"
fi

# download from
CONDA_DOWNLOAD_URL="https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/$CONDA_PACKAGE_NAME"

# download to
CONDA_DOWNLOAD_DST="$STAGE_2_DIR_IN_CONTAINER/tmp/$CONDA_PACKAGE_NAME"

# if the file does not exist, wget it from tuna
if [ ! -f $CONDA_DOWNLOAD_DST ]; then
    echo "downloading miniconda3 installation file ..."
    wget -O $CONDA_DOWNLOAD_DST $CONDA_DOWNLOAD_URL --show-progress
fi

# install miniconda3 unattended
echo "installing miniconda3 to $CONDA_INSTALL_DIR ..."
bash $CONDA_DOWNLOAD_DST -b -p $CONDA_INSTALL_DIR

# make conda installation read/write for all users
echo "setting permissions for $CONDA_INSTALL_DIR ..."
chmod -R 777 $CONDA_INSTALL_DIR

echo "initializing conda for all users, including root ..."

# conda and pip mirror, for faster python package installation
# save the following content to a variable
read -r -d '' CONDA_TUNA << EOM
channels:
  - defaults
show_channel_urls: true
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch-lts: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  deepmodeling: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/
EOM

# tuna pip mirror
read -r -d '' PIP_TUNA << EOM
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple

[install]
trusted-host=pypi.tuna.tsinghua.edu.cn
EOM

# aliyun pypi mirror, use it if tuna is slow
read -r -d '' PIP_ALIYUN << EOM
[global]
index-url = https://mirrors.aliyun.com/pypi/simple

[install]
trusted-host=mirrors.aliyun.com
EOM

# add all user names to USER_LIST
USER_LIST="root"
for user in $(ls /home); do
    USER_LIST="$USER_LIST $user"
done

# remove duplicated user names, preventing install for root twice
USER_LIST=$(echo $USER_LIST | tr ' ' '\n' | sort | uniq | tr '\n' ' ')
echo "conda config for users: $USER_LIST"

# for each user in USERS, initialize conda.
# remember to execute commands in the user context using su - $user -c
# otherwise the file will be owned by root
for user in $USER_LIST; do
    echo "initializing conda for $user ..."
    su - $user -c "$CONDA_INSTALL_DIR/bin/conda init"

    # if user is root, set home_dir to /root, otherwise /home/$user
    if [ "$user" = "root" ]; then
        home_dir="/root"
    else
        home_dir="/home/$user"
    fi

    # to use tuna mirror, replace the .condarc file with the pre-configured CONDA_TUNA
    echo "setting conda mirror for $user ..."    
    su - $user -c "echo \"$CONDA_TUNA\" >> $home_dir/.condarc"

    # to use pip mirror, create a .pip directory and write the PIP_TUNA to pip.conf
    echo "setting pip mirror for $user ..."
    su - $user -c "mkdir -p $home_dir/.pip"
    su - $user -c "echo \"$PIP_ALIYUN\" > $home_dir/.pip/pip.conf"
done
```

## Install miniconda to external storage

To install miniconda to external storage, you can mount external storage ([How to use external storage?][external-storage]) to the `/hard/volume/app`, so that the miniconda installation will be saved there. The following example demonstrates how to install miniconda to the external storage.

First, create a docker volume named `my_app`:

```bash
docker volume create my_app
```

Then, modify the `user_config.yml` file as follows:

```yaml
stage_1:
  image:
    base: nvidia/cuda:12.3.2-runtime-ubuntu22.04
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
      type: manual-volume
      volume_name: my_app
    data:
      type: auto-volume
    workspace:
      type: auto-volume
  custom:
    on_first_run:
    - stage-2/system/conda/auto-install-miniconda.sh
```

The example is based on [Install miniconda in image][miniconda-in-image], with the following changes:
- `app` is a **manual-volume**, which means it is created manually with the name `my_app`, and then mounted to the container. To create it, use `docker volume create my_app`.
- `data` and `workspace` are **auto-volumes**, which means they are created automatically.
- The `install-my-conda.sh` script is executed on the first run of the container, to install miniconda3 and setup conda for all users.

**IMPORTANT**: Here comes the critical part for using `on_first_run` commands. After the commands are run, they modify the **container**, not the **image**. If you want to save the changes to the image, you need to commit the container to the image. If you forgot to do that, changes are not saved, and the first-run commands will be run again when the container is recreated. 

To correct this, commit the container to the image after the first run:

```bash
docker commit <container_id> pei-image:stage-2
```

## Moving external storage to image

After you have installed apps to the external storage, you can move it to the image storage. This is useful when you want to bake the installed apps into the image. To do this, just copy the files from the external storage to the image storage. Inside the container, do the followings:

```bash
# inside container
# just copy /hard/volume/app to /hard/image/app, likewise for other directories
cp -r /hard/volume/app /hard/image/app

# for data and workspace, if you want to bake them into the image
# cp -r /hard/volume/data /hard/image/data
# cp -r /hard/volume/workspace /hard/image/workspace
```

And then, commit your container to image:
  
```bash
docker commit <container_id> pei-image:stage-2
```

[](){#install-pixi}
## Install pixi package manager

**Pixi** is a modern, fast package manager for Python that uses conda-forge packages but with significantly better performance than conda. It's designed for modern Python development workflows and supports creating isolated environments with precise dependency management.

This example demonstrates how to automatically install pixi and set up a common development environment with essential Python packages. The installation uses the tuna mirror for faster downloads in China and configures pixi to persist across container restarts.

```yaml
# user_config.yml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-pixi-example:stage-1
  
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
    output: pei-pixi-example:stage-2
  
  # storage configurations  
  storage:
    app:
      type: auto-volume
    workspace:
      type: auto-volume
    data:
      type: auto-volume
  
  # custom scripts to install and configure pixi
  custom:
    on_first_run:
      - 'stage-2/system/pixi/install-pixi.bash'
      - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'
      - 'stage-2/system/pixi/create-env-common.bash'
```

### What this configuration does:

1. **Base Image**: Uses `ubuntu:24.04` as the base system
2. **Pixi Installation**: Automatically installs pixi to `/hard/volume/app/pixi` (external storage) or `/hard/image/app/pixi` (image storage)
3. **Mirror Configuration**: Sets up tuna mirrors for faster package downloads in China
4. **Common Environment**: Creates a `common` global environment with essential packages:
   - `scipy` - Scientific computing
   - `click` - Command-line interface creation
   - `attrs` - Classes without boilerplate
   - `omegaconf` - Configuration management
   - `rich` - Rich text and beautiful formatting
   - `networkx` - Network analysis

### Build and run process:

```bash
# assuming the project dir is /path/to/project

# generate docker-compose.yml
python -m pei_docker.pei configure --project-dir=/path/to/project

cd /path/to/project

# build stage-1
docker compose build stage-1 --progress=plain --no-cache

# build stage-2 (this installs pixi on first run)
docker compose build stage-2 --progress=plain --no-cache

# start stage-2 container
docker compose up -d stage-2
```

### Verify pixi installation:

After the container starts, you can SSH into it and verify pixi is working:

```bash
# SSH into the container
ssh -p 2222 developer@127.0.0.1

# Check pixi installation
pixi --version

# List global environments
pixi global list

# Verify packages in common environment
python -c "import scipy; print('scipy:', scipy.__version__)"
python -c "import click; print('click:', click.__version__)"
python -c "import rich; print('rich:', rich.__version__)"
```

### Key advantages of pixi over conda:

- **Speed**: Significantly faster package resolution and installation
- **Modern**: Built with Rust, designed for current Python workflows  
- **Cross-platform**: Works consistently across Linux, macOS, and Windows
- **Lock files**: Automatic lock file generation for reproducible environments
- **Global environments**: Easy management of global tool installations

### Important notes:

- **Persistence**: Since pixi is installed to external storage (`/hard/volume/app`), the installation persists across container restarts
- **First run only**: The installation scripts run only on the first container startup using `on_first_run`
- **Commit changes**: If you want to bake pixi into the image permanently, commit the container after first run:
  ```bash
  docker commit <container_id> pei-pixi-example:stage-2
  ```
- **Adding packages**: You can add more packages to the `common` environment by modifying the `create-env-common.bash` script or by running `pixi global install package_name` inside the container

### Custom package lists:

To customize the packages installed in the common environment, you can modify the installation scripts in your project directory under `installation/stage-2/system/pixi/` or create additional environment setup scripts for specific use cases (e.g., machine learning, web development, data science).

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
