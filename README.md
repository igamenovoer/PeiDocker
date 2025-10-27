<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url] -->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <!-- <a href="https://github.com/github_username/repo_name">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->

<h3 align="center">PeiDocker (配 docker)</h3>

  <p align="center">
   Easily automate docker building process without learning much about Dockerfiles.
    <!-- <br />
    <a href="https://igamenovoer.github.io/PeiDocker"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/github_username/repo_name">Examples</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/github_username/repo_name/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a> -->
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<!-- <details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details> -->



<!-- ABOUT THE PROJECT -->
## About The Project

You don't have time to learn Dockerfiles, we get it. 

But don't keep your docker images around, they will be messed up eventually. If you ever want to make reproducible docker images but have no patience to learn Dockerfiles and docker-compose, PeiDocker is for you.

PeiDocker (配 docker) helps you script and organize your docker image building process with both CLI and modern Web GUI interfaces. It streamlines the building process and allows you to customize the image building and running behaviours using shell scripts. 

With PeiDocker, you can:

- **Custom Script Hooks**: Run custom scripts during image build, first run, each time the container starts or when you SSH into the container, without knowing Dockerfiles

- **Painless Configuration**: Quickly setup SSH configurations for multiple users and authentication methods, changing apt repositories, pip repositories, mounts using docker volumes, system-wide proxy, etc.

- **Dynamic Storage Support**: Use external storage in development, and transparently switch to internal storage in deployment

- **Configure With GUI**: Use the modern web interface to create your reusable docker building files without writing Dockerfiles

### Examples

Given the below `user_config.yml` file, PeiDocker will generate a `docker-compose.yml` file for you, using which you will build two docker images `pei-cn-demo:stage-1` and `pei-cn-demo:stage-2` with many useful features.

```yaml
# pei-docker configuration file as demo
# in-container paths are relative to /installation directory

stage_1:
  # input/output image settings
  image:
    base: ubuntu:24.04
    output: pei-cn-demo:stage-1

  # ssh settings
  ssh:
    enable: true

    # you can configure ssh port in container (default is 22 if not set)
    # useful if you want to use network-mode=host, avoid conflicting with host services
    port: 333

    # mapped port on host machine, if given, this port will be mapped to the container SSH port
    host_port: 2222

    # ssh users, the key is user name
    users:
      me:
        password: '123456'

        # using this will add your public key to the container as authorized key, you can also specify a file path
        # pubkey_file: '~' 

        # you can also use inline public key text
        # pubkey_text: 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC...'
        
      root: # allow you to ssh as root
        password: root

  # apt settings
  apt:
    # use 'tuna' or 'aliyun' apt mirror for faster downloads in China
    repo_source: 'aliyun'
    keep_repo_after_build: true # keep the apt source file after build

  # custom scripts
  custom:
    # scripts run during build
    # Scripts can include parameters: 'script.sh --param1=value1 --param2="value with spaces"'
    on_build: 
      - 'stage-1/custom/install-dev-tools.sh' # just an example, you can safely remove this
    
stage_2:

  # input/output image settings
  image:
    output: pei-cn-demo:stage-2

  # dynamic storage settings
  # they define the physical location of `/soft/app`, `/soft/data` and `/soft/workspace` point to, your these paths can be switched among different storage locations, so that you can use external storage in development, and move them to internal storage in deployment
  storage:
    app:  # /soft/app will be kept as part of the image
      type: image
    data: # mounting /your/data/path to /soft/data in container
      type: host
      host_path: /your/data/path
    workspace: # /soft/workspace will be mounted to a docker automatic volume
      type: auto-volume

  # mount external volumes to container
  mount:
    # mounting docker automatic volume to /home/me
    # so that you do not have to commit your docker image everytime some configuration changes
    home_me:
      type: auto-volume   # auto-volume, manual-volume, host
      dst_path: /home/me

  custom:
    # scripts run during build
    # Scripts can include parameters: 'script.sh --param1=value1 --param2="value with spaces"'
    on_build: 
      # install pixi, a lightweight python package manager
      - 'stage-2/system/pixi/install-pixi.bash'

      # configure pixi to use tuna mirror in China
      - 'stage-2/system/pixi/set-pixi-repo-tuna.bash' # set pixi repo to tuna, a fast mirror in China
```

After you build the images, if you start `pei-cn-demo:stage-1` or `pei-cn-demo:stage-2` with `docker compose`, you will have fully functional docker containers with the following features:

#### pei-cn-demo:stage-1 container features

- SSH server running on port 333 inside container, mapped to port 2222 on host, with a user `me` and password `123456`, you can also login as root with password `root`
- `apt` source is switched to `aliyun` mirror for faster downloads in China
- development tools installed via `install-dev-tools.sh` script, into system dirs

#### pei-cn-demo:stage-2 container features

- includes all features of `stage-1`
- `/soft/data` is mounted to `/your/data/path` on host, so you can use external storage in development
- `/soft/workspace` is mounted to a docker automatic volume, so you can use it as a persistent workspace
- `/home/me` is mounted to a docker automatic volume, so during use of the container you can persist your user-specific settings without committing the image
- `pixi` package manager installed, with `tuna` mirror configured, so you can install python packages easily, via the `on_build` scripts

You can further customize the `user_config.yml` file to add more features, mainly using the `custom` section to run your own scripts during build, first run, container starts or login, so you ONLY need to master bash scripting to maintain your docker images build process, no need to learn Dockerfiles!

_For details, please refer to the [Documentation](https://igamenovoer.github.io/PeiDocker/)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ### Built With

* [![Next][Next.js]][Next-url]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- GETTING STARTED -->
## Getting Started

### Installation

#### Option 1: Install from PyPI (Recommended)

```sh
# for ordinary python users, or conda users
pip install pei-docker

# if you are using pixi, you need to install via pipx
pixi global install pipx  # install pipx if you haven't done so
pipx install pei-docker # then install pei-docker
```

#### Option 2: Install from Source

```sh
git clone https://github.com/igamenovoer/PeiDocker.git
cd PeiDocker
pip install -e .
```

### Prerequisites

- Docker and docker-compose installed on your machine
- Python 3.11 or higher

<!-- USAGE EXAMPLES -->
## Usage

### Web GUI (Experimental)

The modern web interface provides an intuitive way to manage PeiDocker projects:

```sh
# Start GUI on auto-selected port, in browser
pei-docker-gui start

# Or specify a custom port
pei-docker-gui start --port 8080

# Load an existing project
pei-docker-gui start --project-dir /path/to/my/project

# Run in native desktop mode (requires pywebview)
# You need this to use the "Browse" feature to locate directories
pei-docker-gui start --native
```

### Command Line Interface

Create a new project:

```sh
# Create a new project in ./build or any other directory
pei-docker-cli create -p /your/build/dir
```

Edit the configuration file `user_config.yml` in the project directory (e.g.,`/your/build/dir`) according to your needs. Generate the `docker-compose.yml` file in the project directory:

```sh
# From within the project directory
cd /your/build/dir
pei-docker-cli configure

# Or specify project directory explicitly
pei-docker-cli configure -p /your/build/dir

# Optional: Use a different config file
pei-docker-cli configure -p /your/build/dir -c my-custom-config.yml
```

Build the docker images. There are two images to be built, namely `stage-1` and `stage-2`. `stage-1` is intended to be a base image, installing system apps using `apt install`, `stage-2` is intended to be a final image based on `stage-1`, installing custom apps using downloaded packages like `.deb`. External storage is only available in `stage-2`.

```sh
cd /your/build/dir

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

Run the docker container:

```sh
# inside project directory, such as /your/build/dir

# Typically you will run the stage-2 container
# You can also up the stage-1 container as well.
docker compose up stage-2
```

If you have setup SSH in `user_config.yml`, now you can SSH into the container:

```sh
# by default, it will create a user named `me` with password '123456'
# and map the port 2222 to the container's port 22

ssh me@127.0.0.1 -p 2222
```

That's it, you are good to go.

_For more examples, please refer to the [Documentation](https://igamenovoer.github.io/PeiDocker/)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>