You are going to use GUI to create such a `user_config.yml` file:

```yaml
# Pixi installation with machine learning packages for GPU development
# This example includes both common and ML packages with CUDA support

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
      root:
        password: 'root123'

  apt:
    repo_source: tuna
    
  device:
    type: gpu

stage_2:
  image:
    output: pei-pixi-ml:stage-2
  
  device:
    type: gpu
    
  # storage configurations using volumes for large ML models and datasets
  storage:
    app:
      type: auto-volume
    workspace:
      type: auto-volume  
    data:
      type: auto-volume
  
  # additional mounts for ML development
  mount:
    # dedicated volume for models (can be large)
    models:
      type: auto-volume
      dst_path: /models
      
    # cache directory for pip and conda packages
    package_cache:
      type: auto-volume
      dst_path: /package-cache
    
    # home directories for user settings
    home_mldev:
      type: auto-volume
      dst_path: /home/mldev
    
    home_root:
      type: auto-volume
      dst_path: /root
  
  # environment variables for CUDA and ML development
  environment:
    - 'NVIDIA_VISIBLE_DEVICES=all'
    - 'NVIDIA_DRIVER_CAPABILITIES=all'
    - 'CUDA_VISIBLE_DEVICES=all'
  
  # custom scripts to install pixi with ML packages
  custom:
    on_first_run:
      # Install pixi with cache in external storage
      - 'stage-2/system/pixi/install-pixi.bash --cache-dir=/package-cache/pixi'
      - 'stage-2/system/pixi/set-pixi-repo-tuna.bash'
      # Install both common and ML packages
      - 'stage-2/system/pixi/create-env-common.bash'
      - 'stage-2/system/pixi/create-env-ml.bash'
```

This is a rather complex example. On GUI, you need to do the following steps.

# Steps to Create the Test Case

- Go to the GUI, create a new project, the dirname can be any.
- In "project information" page:
-  Set project name as `pei-pixi-ml`, we call this as `project-name`.
-  Set base image as `nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04`.
- In "SSH" page:
  - Enable SSH server.
  - Set SSH port as `22`.
  - Set host port as `2222`.
  - Add users:
    - User `mldev` with password `ml123`, UID `1100`.
    - User `root` with password `root123`.
- In "Network" page:
  - In "APT Configuration", set package repository source as `tuna`.
- In "Environment" page:
  - In "Device Configuration", set device type as `GPU`.
- In "Storage" page:
  - In "Stage-2 Dynamic Storage System" section, set `app`, `workspace`, and `data` storage types to `auto-volume`.
  - In "Stage-2 Mounts" section, add the following mounts:
    - `models`: type `auto-volume`, destination path `/models`.
    - `package_cache`: type `auto-volume`, destination path `/package-cache`.
    - `home_mldev`: type `auto-volume`, destination path `/home/mldev`.
    - `home_root`: type `auto-volume`, destination path `/root`.
- In "Scripts" page:
  - In "Stage-2 Image Scripts" section, add the following scripts to "On First Run", by clicking "Add File" and entering the script paths:
    - `stage-2/system/pixi/install-pixi.bash --cache-dir=/package-cache/pixi`
    - `stage-2/system/pixi/set-pixi-repo-tuna.bash`
    - `stage-2/system/pixi/create-env-common.bash`
    - `stage-2/system/pixi/create-env-ml.bash`
- In "Summary" page, review the configuration and click `Save` to generate the `user_config.yml`. It will be saved in the project directory, copy it to `<workspace>/tmp`, give it a name for inspection.