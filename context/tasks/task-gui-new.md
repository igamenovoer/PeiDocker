# PeiDocker Terminal GUI - Simple Mode Only

We need to create a terminal GUI for our project using the `textual` library. You can find the docs using `context7` MCP, and some details are in `context/hints/howto-use-textual.md`.

Create a subdir in `src\pei_docker` for this. Do not write the whole GUI in a single file, split it into several files as needed.

## Starting GUI via CLI tool

The GUI is launched with `pei-docker-gui` command, with the following subcommands.

the `start` subcommand will start the GUI application, with the following options:
- empty option, just start the GUI with no project directory specified, will ask user where to output the project later.
- `--project-dir <path>` , to specify the project directory, will launch the GUI for that project. If that project directory does not exist, it will be created with empty content.
- `--here`, to specify the current directory as the project directory, will launch the GUI for that project.

the `dev` subcommand will start the GUI in development mode, with the following options
- all options in `start` subcommand are also valid
- `--screen <screen_name>` to specify the screen to start with, useful for development and testing, `screen_name` can be `sc-0`, `sc-1`, etc. You MUST specify the `--project-dir` or `--here` option when using this `--screen` option, otherwise it will not work.

## Design Philosophy

The GUI provides **ONLY a simple mode** - a guided, wizard-like interface that walks users through creating a PeiDocker project using a series of sequential configuration steps. Each step has its own dedicated GUI screen. There is no advanced mode.

See `src\pei_docker\templates\config-template-full.yml` for what options are possible. This file is called `user_config` in this document.

## Navigation and User Experience Requirements

### Key Navigation Rules:
1. **Step-by-step navigation**: User can go back and forth between configuration steps using `prev`|`next` buttons
2. **Double ESC to main menu**: User can return to main menu anytime by pressing `esc` twice quickly
3. **Single ESC behavior**: `esc` will clear the current input field, or go back to the previous state
4. **Memory-only changes**: Until the final confirmation and save, DO NOT modify any output files - keep all configuration changes in memory only
5. **Persistent final page**: After user confirms and saves, they remain on the final summary page and can still navigate back to make more changes and save again
6. **Button layout**: Each configuration page has buttons at the bottom: `prev`|`next`|`save` (save button only appears on the last page)

### Startup Behavior:
- On startup, ask the user where to output the project (see `src\pei_docker\pei.py` for the `create` command), create the project directory, and work from there. Let's name the project as `my_project` in description.
- On startup, if the GUI is launched with `--project-dir <path>`, use that path as the project directory without asking.
- On startup, look for `docker` command. If not found, show a warning message - some functions will not work without it.
- After project creation, launch directly into the simple mode wizard (no mode selection screen)

## Simple Mode Configuration Steps

The wizard consists of these sequential steps, each with its own GUI screen:

### Step 1: Project Information
Ask for:
- **Project name**: No default, let's call it `my_project_name`. Built docker images will be named `my_project_name:stage-1` and `my_project_name:stage-2`
- **Base image name**: Default `ubuntu:24.04`, this is a docker tag from dockerhub
- If `docker images` command is available, check if the image already exists and warn user it will be overwritten

### Step 2: SSH Configuration
**IMPORTANT**: This will only be set in `stage-1` of `user_config`. For `stage-2` the user needs to edit the config file directly.

Ask whether user wants to use `ssh` for remote access, default is `yes`. If `no`, warn that user needs to use native docker commands to access the container. If `yes`:

- **SSH container port**: Default `22` (useful for host network mode to avoid conflicts)
- **SSH host port**: Default `2222` (port on host machine to access container)
- **SSH user name**: Default `me`
- **SSH user password**: Default `123456`. Warn user not to use `,` or space in password due to implementation details
- **SSH user UID**: Default `1100` (avoid conflicts with system users)
- **Public key option**: Ask if user wants to specify public key for `me`, default `no`. If `yes`, ask for public key string. If user enters `~`, use the `~` functionality in `user_config`
- **Private key option**: Ask if user wants to specify private key for `me`, default `no`. If `yes`, ask for private key file path. If user enters `~`, use the `~` functionality in `user_config`
- **Root SSH access**: Ask if root user should login via ssh, default `no`. If `yes`, ask for root password, default `root`. No ssh keys for root in GUI mode

### Step 3: Proxy Configuration
**IMPORTANT**: This will only be set in `stage-1` of `user_config`.

Ask if user wants to use a proxy on host for the container, default `no`. If `yes`, tell user this sets `http_proxy` and `https_proxy` environment variables:

- **Proxy port**: No default, port on host machine for container internet access
- **Proxy persistence**: Ask if proxy is only used during build process. If `yes`, proxy not available after build. If `no`, proxy available after build in runtime environment. Default `yes`

### Step 4: APT Configuration
**IMPORTANT**: This will only be set in `stage-1` of `user_config`.

Ask if user wants to use different mirror than default, default `no`. If `yes`, ask for mirror name with choices:
- `tuna`: Tsinghua University mirror
- `aliyun`: Aliyun mirror
- `163`: 163 mirror
- `ustc`: University of Science and Technology of China mirror
- `cn`: Ubuntu official China mirror
- `default`: the default Ubuntu mirror (no change)

This sets the `apt` section in user config file.

### Step 5: Port Mapping
**IMPORTANT**: This will only be set in `stage-1` of `user_config`.

Ask if user wants to map additional ports from host to container, default `no` (SSH ports already mapped). If `yes`:

- Ask for port mapping in format `host_port:container_port`, can be single port like `8080:80` or range like `100-200:300-400`
- User enters valid port mapping and presses Enter to add to list
- Show already added port mappings, no way to delete in GUI mode
- Finish when user enters empty string

### Step 6: Environment Variables
**IMPORTANT**: This will only be set in `stage-1` of `user_config`.

Ask if user wants to set environment variables, default `no`. If `yes`:

- Ask for env variable in format `key=value`
- User enters valid env variable, press Enter to add to list
- Show already added env variables
- To delete, set already-set env variable to empty string

### Step 7: Device Configuration
**IMPORTANT**: This will only be set in `stage-1` of `user_config`.

Ask if user wants to use GPU, default `no`. If `yes`, set `user_config` accordingly. Note: we DO NOT detect if user has GPU - this is user's decision.

### Step 8: Additional Mounts
Ask if user wants to set mounts for `stage-1`, default `no`. If `yes`, present volume type options:
- `automatic docker volume`: use docker volume, mapping to `auto-volume` in `user_config`, volume created automatically
- `manual docker volume`: use docker volume, mapping to `manual-volume` in `user_config`. Ask for volume name
- `host directory`: use host directory, mapping to `host` type volume in `user_config`. Ask for host directory path, handle Windows/Linux paths automatically. Check if path exists, warn if not but accept it
- `done`: finish mount setting

Ask if user wants to set mounts for `stage-2`, default `no`. If `yes`, present same options and warn that `stage-2` mounts will completely replace `stage-1` mounts.

### Step 9: Custom Entry Point
Ask if user wants to set custom entry point for `stage-1`, default `no`. If `yes`:

- Ask for custom entry point script in `.sh` format
- If empty string, no custom entry point set
- If valid path, set `custom.on_entry` in `user_config`, file copied to project directory, path in `user_config` relative to project directory

Ask if user wants to set custom entry point for `stage-2`, default `no`. If `yes`, do same but warn that `stage-2` entry point will completely replace `stage-1` entry point.

### Step 10: Custom Scripts
Ask if user wants to set custom scripts for `stage-1`, default `no`. If `yes`:

We have several kinds: `on_build`, `on_first_run`, `on_every_run`, `on_user_login`. For each kind:
- Explain what it is and what it does
- Let user enter script path, can include cli args like `--arg1 value1 --arg2 value2`
- User enters one script path at a time, show previously entered scripts, no way to delete in GUI mode
- When user enters empty string, finish that script type and go to next

Ask if user wants to set custom scripts for `stage-2`, default `no`. If `yes`, do same and add to `user_config` for `stage-2`.

### Step 11: Configuration Summary and Save
Show comprehensive summary of all project configuration including all user settings. Present options:

- **Save Configuration**: Write the `user_config.yml` to project directory and remain on this page
- **Go Back**: Return to any previous step to make changes
- **Cancel**: Return to main menu without saving

**Important**: After saving, user remains at this summary page and can:
- Navigate back to any previous step to make changes
- Save again with updated configuration
- Continue iterating until satisfied

## File Structure

```
src/pei_docker/gui/
├── __init__.py
├── app.py                    # Main GUI application entry point
├── screens/
│   ├── __init__.py
│   ├── startup.py            # Project directory selection and validation
│   ├── simple/
│   │   ├── __init__.py
│   │   ├── wizard.py         # Main wizard orchestrator
│   │   ├── project_info.py   # Step 1: Project name and base image
│   │   ├── ssh_config.py     # Step 2: SSH configuration
│   │   ├── proxy_config.py   # Step 3: Proxy configuration
│   │   ├── apt_config.py     # Step 4: APT mirror configuration
│   │   ├── port_mapping.py   # Step 5: Additional port mappings
│   │   ├── env_vars.py       # Step 6: Environment variables
│   │   ├── device_config.py  # Step 7: GPU/device configuration
│   │   ├── mounts.py         # Step 8: Additional mount points
│   │   ├── entry_point.py    # Step 9: Custom entry point scripts
│   │   ├── custom_scripts.py # Step 10: Custom hook scripts
│   │   └── summary.py        # Step 11: Configuration summary and save
├── models/
│   ├── __init__.py
│   └── config.py            # Configuration data models
├── widgets/
│   ├── __init__.py
│   ├── inputs.py            # Custom input widgets with validation
│   ├── forms.py             # Reusable form components
│   └── dialogs.py           # Dialog widgets
└── utils/
    ├── __init__.py
    ├── docker_utils.py      # Docker command utilities
    └── file_utils.py        # File system utilities
```

## Implementation Requirements

### State Management:
- Keep all configuration changes in memory until final save
- Allow unlimited back/forth navigation between steps
- Preserve user inputs when navigating between steps
- Only write `user_config.yml` when user explicitly saves

### Navigation:
- Each step screen has `prev`|`next` navigation buttons
- Final step has `prev`|`save` buttons
- Double ESC returns to main menu from any step
- Single ESC clears current input or goes to previous state

### Validation:
- Real-time input validation where possible
- Prevent navigation to next step if current step has validation errors
- Clear error messages and guidance

### Error Handling:
- Graceful handling of missing Docker
- File system permission errors
- Invalid configuration combinations

This design provides a streamlined, single-mode wizard interface that guides users through PeiDocker project creation while maintaining full flexibility for configuration changes and iterations.