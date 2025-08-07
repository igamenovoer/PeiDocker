You are going to use GUI to create such a `user_config.yml` file:

```yaml
# user_config.yml as a test case
# Minimal Ubuntu image with SSH support
# This is the simplest PeiDocker configuration for creating an Ubuntu container with SSH access

stage_1:
  # Base image configuration
  image:
    base: ubuntu:24.04              # Use Ubuntu 24.04 as the base image
    output: <project-name>:stage-1     # Name of the generated stage-1 image
  
  # SSH server configuration
  ssh:
    enable: true                    # Enable SSH server in the container
    port: 22                       # SSH port inside the container (standard SSH port)
    host_port: 2222                # Port on host machine mapped to container SSH port
    
    # Define SSH users with their passwords
    users:
      me:
        password: '123456'          # User 'me' with password '123456'
      you:
        password: '654321'          # User 'you' with password '654321'
      root:
        password: root              # Root user with password 'root'
  
  # Package repository configuration
  apt:
    repo_source: aliyun            # Use Aliyun mirror for faster package downloads in China
                                   # Other options: tuna, ustc, 163, or leave empty for default

stage-2: #DO NOT care, just leave it as default
```

# Steps to Create the Test Case

- go to the GUI, create a new project, the dirname can be any
- in "project information" page
  - set project name as `pei-(uuid)`, we call this as `project-name`.
  - set base image as `ubuntu:24.04`
- in "SSH" page
  - enable SSH server
  - set SSH port as `22`
  - set host port as `2222`
  - add users:
    - user `me` with password `123456`
    - user `you` with password `654321`
    - user `root` with password `root`
- in "Network" page
  - set package repository source as `aliyun`
- click `save` to generate the `user_config.yml` , it will be saved in the project directory, copy it to `<workspace>/tmp`, give it a name, for inspection.

# Expected Result

- the generated `user_config.yml` should match the provided test case in `stage-1`
- extra fields does not matter, they may just take default values, so you can ignore them
