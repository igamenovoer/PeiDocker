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

- **Use the intuitive Web GUI** with visual configuration wizard, real-time validation, and auto-port selection
- **Native desktop mode** for OS-native window experience (optional, requires pywebview)
- Build images with SSH support including multiple authentication methods (password, public/private keys)
- Configure separate port mappings for system services (stage-1) and applications (stage-2)
- Install packages from public repository mirrors, or via proxy
- Install apps for your container, during or after building, into places such as docker volumes, bind mounts or in-image directory
- Run custom commands during image building, when the container starts, or when you SSH into the container
- **Use environment variables with fallback values** in configuration files for flexible deployments across different environments
- Export/import projects as ZIP files for easy sharing and backup
- **Advanced template system** with minimal config mode for quick setups

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
pip install pei-docker
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

### Web GUI (Recommended for beginners)

The modern web interface provides an intuitive way to manage PeiDocker projects:

```sh
# Start GUI on auto-selected port
pei-docker-gui start

# Or specify a custom port
pei-docker-gui start --port 8080

# Load an existing project
pei-docker-gui start --project-dir /path/to/my/project

# Jump directly to specific configuration page
pei-docker-gui start --jump-to-page ssh

# Run in native desktop mode (requires pywebview)
pei-docker-gui start --native
```

**Key Features:**
- **Visual Configuration Wizard**: Step-by-step interface with organized tabs for all settings
- **Real-time Validation**: Instant feedback on configuration errors and warnings
- **Auto-port Selection**: Automatically finds available ports if default is in use
- **Multiple SSH Auth Methods**: Support for password, public key files, inline keys, and private keys
- **Project Import/Export**: Download/upload projects as ZIP files for easy sharing
- **Jump-to-Page**: Quick navigation to specific configuration sections for debugging
- **Minimal Config Mode**: Streamlined templates for quick project setup
- **Native Desktop Mode**: Optional OS-native window experience (when pywebview is installed)
- **Interactive Help**: Contextual tooltips and documentation links throughout the interface

**Available Pages:**
- `home` - Welcome page with project management
- `project` - Basic project settings and Docker image configuration
- `ssh` - SSH server and user authentication setup
- `network` - Port mappings and proxy configuration
- `environment` - Environment variables with Docker Compose-style substitution
- `storage` - Volume and bind mount configuration
- `scripts` - Custom script management for build and runtime
- `summary` - Complete project overview with export functionality

### Command Line Interface

Create a new project:

```sh
# Create a new project in ./build or any other directory
pei-docker-cli create -p ./build

# Optional: Create without examples or contrib files
pei-docker-cli create -p ./build --no-with-examples --no-with-contrib
```

Edit the configuration file `user_config.yml` in the project directory (e.g.,`./build`) according to your needs. Generate the `docker-compose.yml` file in the project directory:

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

Build the docker images. There are two images to be built, namely `stage-1` and `stage-2`. `stage-1` is intended to be a base image, installing system apps using `apt install`, `stage-2` is intended to be a final image based on `stage-1`, installing custom apps using downloaded packages like `.deb`. External storage is only available in `stage-2`.

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

Run the docker container:

```sh
# inside project directory, such as ./build

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