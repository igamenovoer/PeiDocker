# PeiDocker GUI - Simple Mode Interaction Design

## Overview

Simple mode provides a guided, wizard-like interface that walks users through creating a PeiDocker project using a series of sequential questions. The interface focuses on the most common configuration options and hides advanced features to reduce complexity.

## Architecture & File Structure

```
src/pei_docker/gui/
├── __init__.py
├── app.py                    # Main GUI application entry point
├── screens/
│   ├── __init__.py
│   ├── startup.py            # Project directory selection and validation
│   ├── mode_selection.py     # Simple vs Advanced mode selection
│   ├── simple/
│   │   ├── __init__.py
│   │   ├── wizard.py         # Main wizard orchestrator
│   │   ├── project_info.py   # Project name and base image
│   │   ├── ssh_config.py     # SSH configuration screen
│   │   ├── proxy_config.py   # Proxy configuration screen
│   │   ├── apt_config.py     # APT mirror configuration
│   │   ├── port_mapping.py   # Additional port mappings
│   │   ├── env_vars.py       # Environment variables
│   │   ├── device_config.py  # GPU/device configuration
│   │   ├── mounts.py         # Additional mount points
│   │   ├── entry_point.py    # Custom entry point scripts
│   │   ├── custom_scripts.py # Custom hook scripts
│   │   └── summary.py        # Configuration summary and save
│   └── common/
│       ├── __init__.py
│       ├── widgets.py        # Reusable custom widgets
│       └── validators.py     # Input validation functions
├── models/
│   ├── __init__.py
│   └── config.py            # Configuration data models
└── utils/
    ├── __init__.py
    ├── docker_utils.py      # Docker command utilities
    └── file_utils.py        # File system utilities
```

## Screen Flow Diagram

```
┌─────────────────┐
│   Application   │
│     Startup     │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐    Docker not found
│  System Check   │ ──────────────────► Warning Dialog
└─────┬───────────┘
      │
      ▼
┌─────────────────┐    --project-dir provided
│ Project Dir     │ ──────────────────► Skip to Mode Selection
│   Selection     │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Mode Selection  │
│ Simple/Advanced │
└─────┬───────────┘
      │ Simple Mode
      ▼
┌─────────────────┐
│ Simple Wizard   │
│   Controller    │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Project Info    │───►│ SSH Config      │───►│ Proxy Config    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
      │                        │                        │
      ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ APT Config      │───►│ Port Mapping    │───►│ Environment     │
└─────────────────┘    └─────────────────┘    │   Variables     │
                                              └─────────────────┘
                                                      │
                                                      ▼
                                              ┌─────────────────┐
                                              │ Device Config   │
                                              └─────┬───────────┘
                                                    │
                                                    ▼
                                              ┌─────────────────┐
                                              │    Mounts       │
                                              └─────┬───────────┘
                                                    │
                                                    ▼
                                              ┌─────────────────┐
                                              │  Entry Point    │
                                              └─────┬───────────┘
                                                    │
                                                    ▼
                                              ┌─────────────────┐
                                              │ Custom Scripts  │
                                              └─────┬───────────┘
                                                    │
                                                    ▼
                                              ┌─────────────────┐
                                              │    Summary      │
                                              │   & Save        │
                                              └─────────────────┘
```

## Detailed Screen Designs

### 1. Application Startup Screen

**Layout:**
```
╭─ PeiDocker GUI ─────────────────────────────────────────────╮
│                                                             │
│  ██████╗ ███████╗██╗██████╗  ██████╗  ██████╗██╗  ██╗███████╗██████╗ │
│  ██╔══██╗██╔════╝██║██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗│
│  ██████╔╝█████╗  ██║██║  ██║██║   ██║██║     █████╔╝ █████╗  ██████╔╝│
│  ██╔═══╝ ██╔══╝  ██║██║  ██║██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗│
│  ██║     ███████╗██║██████╔╝╚██████╔╝╚██████╗██║  ██╗███████╗██║  ██║│
│  ╚═╝     ╚══════╝╚═╝╚═════╝  ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝│
│                                                             │
│                 Docker Container Configuration GUI           │
│                                                             │
│  System Status:                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ✓ Docker: Available (version 24.0.6)                   │ │
│  │ ✓ Python: 3.11.5                                       │ │
│  │ ✓ PeiDocker: 0.8.0                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Continue] [Quit]                                          │
│                                                             │
│  Press 'q' to quit, Enter to continue                      │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Check for Docker availability on startup
- Show warning dialog if Docker not found
- Display system information
- Auto-continue after 2 seconds or on Enter key

### 2. Project Directory Selection Screen

**Layout:**
```
╭─ Project Directory Setup ──────────────────────────────────╮
│                                                             │
│  Select where to create your PeiDocker project:            │
│                                                             │
│  Project Directory:                                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ D:\code\my-project                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              [Browse...]                    │
│                                                             │
│  ⚠ Directory will be created if it doesn't exist           │
│                                                             │
│  Project Name (for Docker images):                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ my-project                                              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  Docker images will be named:                               │
│  • my-project:stage-1                                      │
│  • my-project:stage-2                                      │
│                                                             │
│  [Back] [Continue]                                          │
│                                                             │
│  Press 'b' for back, Enter to continue                     │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- If `--project-dir` provided, skip this screen
- Auto-suggest project name from directory name
- Check for existing Docker images and warn if found
- Validate directory path and create if needed

### 3. Mode Selection Screen

**Layout:**
```
╭─ Configuration Mode ───────────────────────────────────────╮
│                                                             │
│  Choose how you'd like to configure your project:          │
│                                                             │
│  ┌─ Simple Mode ─────────────────────────────────────────┐  │
│  │ ✓ Guided step-by-step configuration                  │  │
│  │ ✓ Common options only                                 │  │
│  │ ✓ Perfect for beginners                               │  │
│  │ ✓ Quick setup                                         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Advanced Mode ───────────────────────────────────────┐  │
│  │ ✓ Complete control over all options                   │  │
│  │ ✓ Form-based editing                                  │  │
│  │ ✓ Stage-1 and Stage-2 configuration                  │  │
│  │ ✓ Expert features                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Selected: ● Simple Mode  ○ Advanced Mode                  │
│                                                             │
│  [Back] [Continue]                                          │
│                                                             │
│  Use arrow keys to select, Enter to continue               │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Default selection: Simple Mode
- Arrow keys or mouse to select
- Enter to continue with selected mode

### 4. Simple Mode - Wizard Controller

The wizard controller manages the flow between different configuration screens, maintaining state and enabling navigation.

**Navigation Features:**
- Progress indicator showing current step
- Back/Next buttons
- Skip options for optional sections
- Form validation before proceeding

### 5. Project Information Screen

**Layout:**
```
╭─ Project Information ──────────────────────── Step 1 of 12 ╮
│                                                             │
│  Basic project settings:                                    │
│                                                             │
│  Project Name: *                                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ my-awesome-project                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│  Images: my-awesome-project:stage-1, my-awesome-project:stage-2 │
│                                                             │
│  Base Docker Image:                                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ubuntu:24.04                                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  Common base images:                                        │
│  • ubuntu:24.04 (recommended)                              │
│  • ubuntu:22.04                                            │
│  • nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04             │
│                                                             │
│  ✓ Image exists on Docker Hub                              │
│                                                             │
│  [Back] [Next]                                              │
│                                                             │
│  * Required field                                           │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Auto-populate project name from directory
- Validate Docker image name format
- Check Docker Hub for image existence (optional, non-blocking)
- Prevent empty project names

### 6. SSH Configuration Screen

**Layout:**
```
╭─ SSH Configuration ───────────────────────── Step 2 of 12 ╮
│                                                             │
│  Configure SSH access to your container:                   │
│                                                             │
│  Enable SSH: ● Yes  ○ No                                   │
│                                                             │
│  ⚠ Selecting 'No' means you'll need to use docker exec    │
│    commands to access the container                        │
│                                                             │
│  SSH Container Port:                                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 22                                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  SSH Host Port:                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 2222                                                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  SSH User:                                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ me                                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  SSH Password (no spaces or commas):                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ••••••                                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Extended SSH Configuration (if enabled):**
```
╭─ SSH Keys Configuration ──────────────────────────────────╮
│                                                             │
│  SSH Public Key Authentication: ○ Yes  ● No                │
│                                                             │
│  ┌─ Public Key (when enabled) ───────────────────────────┐  │
│  │ ○ Enter key text  ○ Use system key (~)               │  │
│  │                                                       │  │
│  │ Key Text:                                             │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ...        │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  SSH Private Key: ○ Yes  ● No                               │
│                                                             │
│  Root SSH Access: ○ Yes  ● No                               │
│                                                             │
│  ┌─ Root Password (when enabled) ────────────────────────┐  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ ••••                                              │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Show/hide sections based on selections
- Validate port numbers (1-65535)
- Check for port conflicts
- Password validation (no spaces/commas)
- Toggle password visibility

### 7. Proxy Configuration Screen

**Layout:**
```
╭─ Proxy Configuration ─────────────────────── Step 3 of 12 ╮
│                                                             │
│  Configure HTTP proxy for container networking:            │
│                                                             │
│  Use Proxy: ○ Yes  ● No                                    │
│                                                             │
│  ┌─ Proxy Settings (when enabled) ───────────────────────┐  │
│  │                                                       │  │
│  │ This will set http_proxy and https_proxy environment │  │
│  │ variables in the container.                           │  │
│  │                                                       │  │
│  │ Proxy Port:                                           │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ 8080                                              │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  │                                                       │  │
│  │ Proxy Usage:                                          │  │
│  │ ● Build-time only (remove after build)               │  │
│  │ ○ Build and runtime (persistent)                     │  │
│  │                                                       │  │
│  │ Proxy URL will be: http://host.docker.internal:8080  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Show/hide proxy settings based on selection
- Validate port number
- Preview proxy URL format
- Explain build vs runtime proxy usage

### 8. APT Configuration Screen

**Layout:**
```
╭─ APT Repository Configuration ────────────── Step 4 of 12 ╮
│                                                             │
│  Choose APT repository mirror for faster package downloads:│
│                                                             │
│  Use Custom Mirror: ○ Yes  ● No                            │
│                                                             │
│  ┌─ Mirror Selection (when enabled) ─────────────────────┐  │
│  │                                                       │  │
│  │ Available mirrors:                                    │  │
│  │                                                       │  │
│  │ ○ tuna    - Tsinghua University (China)              │  │
│  │ ○ aliyun  - Alibaba Cloud (China)                    │  │
│  │ ○ 163     - NetEase (China)                          │  │
│  │ ○ ustc    - University of Science and Technology     │  │
│  │ ○ cn      - Ubuntu Official China Mirror             │  │
│  │ ● default - Ubuntu Default (no change)               │  │
│  │                                                       │  │
│  │ Selected mirror provides faster downloads for users  │  │
│  │ in specific geographic regions.                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Radio button selection for mirror
- Geographic information for each mirror
- Preview of mirror benefits

### 9. Port Mapping Screen

**Layout:**
```
╭─ Additional Port Mapping ─────────────────── Step 5 of 12 ╮
│                                                             │
│  Map additional ports from host to container:               │
│  (SSH port is already configured)                          │
│                                                             │
│  Add Port Mappings: ○ Yes  ● No                            │
│                                                             │
│  ┌─ Port Mappings (when enabled) ────────────────────────┐  │
│  │                                                       │  │
│  │ Enter port mapping (host:container) or range:        │  │
│  │ Examples: 8080:80, 3000:3000, 100-200:300-400        │  │
│  │                                                       │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ 8080:80                                           │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  │                                          [Add]        │  │
│  │                                                       │  │
│  │ Current mappings:                                     │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ • 2222:22 (SSH)                                   │ │  │
│  │ │ • 8080:80                                         │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  │                                                       │  │
│  │ Press Enter with empty input to finish               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Dynamic list of port mappings
- Validate port format and ranges
- Prevent duplicate mappings
- Show SSH port as read-only

### 10. Environment Variables Screen

**Layout:**
```
╭─ Environment Variables ───────────────────── Step 6 of 12 ╮
│                                                             │
│  Set custom environment variables for the container:       │
│                                                             │
│  Add Environment Variables: ○ Yes  ● No                    │
│                                                             │
│  ┌─ Environment Variables (when enabled) ─────────────────┐ │
│  │                                                       │  │
│  │ Enter environment variable (KEY=VALUE):               │  │
│  │                                                       │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ NODE_ENV=production                               │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  │                                          [Add]        │  │
│  │                                                       │  │
│  │ Current variables:                                    │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ • NODE_ENV=production                             │ │  │
│  │ │ • DEBUG=true                                      │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  │                                                       │  │
│  │ To delete a variable, set it to an empty value       │  │
│  │ Press Enter with empty input to finish               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Validate KEY=VALUE format
- Allow deletion by setting empty value
- Dynamic list management
- Show current variables list

### 11. Device Configuration Screen

**Layout:**
```
╭─ Device Configuration ────────────────────── Step 7 of 12 ╮
│                                                             │
│  Configure hardware device access:                         │
│                                                             │
│  Enable GPU Support: ○ Yes  ● No                           │
│                                                             │
│  ┌─ GPU Information ──────────────────────────────────────┐ │
│  │                                                       │  │
│  │ ⚠ GPU support requires:                               │  │
│  │   • NVIDIA Docker runtime                             │  │
│  │   • Compatible GPU drivers                            │  │
│  │   • CUDA-compatible base image                        │  │
│  │                                                       │  │
│  │ We do not detect GPU availability automatically.     │  │
│  │ Enable this only if you have the required setup.     │  │
│  │                                                       │  │
│  │ Recommended base images for GPU:                      │  │
│  │ • nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04         │  │
│  │ • nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Warning about GPU requirements
- No automatic GPU detection
- Suggest compatible base images

### 12. Additional Mounts Screen

**Layout:**
```
╭─ Additional Mounts ───────────────────────── Step 8 of 12 ╮
│                                                             │
│  Configure additional volume mounts:                       │
│                                                             │
│  Stage-1 Mounts: ○ Yes  ● No                               │
│                                                             │
│  ┌─ Stage-1 Mount Configuration (when enabled) ──────────┐  │
│  │                                                       │  │
│  │ Mount Type:                                           │  │
│  │ ○ Automatic Docker Volume                             │  │
│  │ ○ Manual Docker Volume                                │  │
│  │ ○ Host Directory                                      │  │
│  │ ○ Done (finish mounting)                              │  │
│  │                                                       │  │
│  │ Destination Path:                                     │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ /app/data                                         │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  │                                                       │  │
│  │ Source (for manual volume/host directory):           │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ my-data-volume                                    │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  │                                          [Add Mount]  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Stage-2 Mounts: ○ Yes  ● No                               │
│  ⚠ Stage-2 mounts will completely replace Stage-1 mounts  │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Show/hide mount configuration sections
- Validate paths and volume names
- Warning about Stage-2 override behavior
- Support for different mount types

### 13. Custom Entry Point Screen

**Layout:**
```
╭─ Custom Entry Point ──────────────────────── Step 9 of 12 ╮
│                                                             │
│  Configure custom entry point scripts:                     │
│                                                             │
│  Stage-1 Entry Point: ○ Yes  ● No                          │
│                                                             │
│  ┌─ Stage-1 Entry Point (when enabled) ──────────────────┐  │
│  │                                                       │  │
│  │ Entry Point Script (.sh):                             │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ /path/to/my-entrypoint.sh                         │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  │                                         [Browse...]   │  │
│  │                                                       │  │
│  │ Script will be copied to project directory and       │  │
│  │ executed when the container starts.                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Stage-2 Entry Point: ○ Yes  ● No                          │
│  ⚠ Stage-2 entry point will override Stage-1 entry point  │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- File browser for script selection
- Validate script file existence
- Warning about Stage-2 override behavior
- Copy script to project directory

### 14. Custom Scripts Screen

**Layout:**
```
╭─ Custom Scripts ──────────────────────────── Step 10 of 12 ╮
│                                                             │
│  Configure custom lifecycle scripts:                       │
│                                                             │
│  Stage-1 Custom Scripts: ○ Yes  ● No                       │
│                                                             │
│  ┌─ Stage-1 Script Configuration (when enabled) ─────────┐  │
│  │                                                       │  │
│  │ Script Type:                                          │  │
│  │ ● on_build    - Run during Docker image build        │  │
│  │ ○ on_first_run - Run on first container startup      │  │
│  │ ○ on_every_run - Run on every container startup      │  │
│  │ ○ on_user_login - Run when user logs in via SSH     │  │
│  │                                                       │  │
│  │ Script Path (with optional arguments):               │  │
│  │ ┌───────────────────────────────────────────────────┐ │  │
│  │ │ stage-1/custom/setup.sh --verbose                 │ │  │
│  │ └───────────────────────────────────────────────────┘ │  │
│  │                                          [Add Script] │  │
│  │                                                       │  │
│  │ Current on_build scripts:                            │  │
│  │ • stage-1/custom/setup.sh --verbose                  │  │
│  │                                                       │  │
│  │ Press Enter with empty path to switch script types   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Stage-2 Custom Scripts: ○ Yes  ● No                       │
│                                                             │
│  [Back] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Cycle through script types
- Show current scripts for each type
- Support command-line arguments
- Validate script paths

### 15. Configuration Summary Screen

**Layout:**
```
╭─ Configuration Summary ───────────────────── Step 11 of 12 ╮
│                                                             │
│  Review your configuration:                                 │
│                                                             │
│  ┌─ Project Settings ─────────────────────────────────────┐ │
│  │ Name: my-awesome-project                               │ │
│  │ Base Image: ubuntu:24.04                               │ │
│  │ Output Directory: D:\code\my-project                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─ SSH Configuration ────────────────────────────────────┐ │
│  │ ✓ Enabled (port 2222:22)                              │ │
│  │ User: me (password auth)                               │ │
│  │ Root access: disabled                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─ Additional Configuration ─────────────────────────────┐ │
│  │ Proxy: disabled                                        │ │
│  │ APT Mirror: default                                    │ │
│  │ GPU Support: disabled                                  │ │
│  │ Port Mappings: 8080:80                                 │ │
│  │ Environment: NODE_ENV=production                       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Back] [Save & Exit] [Save & Configure More]              │
│                                                             │
│  Save actions will create user_config.yml in project dir   │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Comprehensive configuration review
- Organized by logical sections
- Options to save and exit or continue to advanced mode
- Generate user_config.yml file

## Key Features & Behaviors

### Navigation
- **Progress Indicator**: Shows current step and total steps
- **Back/Next Buttons**: Navigate between screens
- **Skip Options**: Optional sections can be skipped
- **Keyboard Shortcuts**: Tab, Enter, Escape, arrow keys

### Validation
- **Real-time Validation**: Input validation as user types
- **Error Messages**: Clear, actionable error messages
- **Required Fields**: Visual indicators for required inputs
- **Format Checking**: Port ranges, key formats, file paths

### State Management
- **Configuration State**: Maintain user choices across screens
- **Undo/Redo**: Allow going back to change previous choices
- **Auto-save**: Temporary state preservation
- **Reset Options**: Clear all and start over

### Accessibility
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels
- **Color Blind Friendly**: Color-independent indicators
- **Responsive Layout**: Adapts to terminal size

### Error Handling
- **Docker Unavailable**: Graceful degradation with warnings
- **File System Errors**: Clear error messages
- **Network Issues**: Timeout and retry mechanisms
- **Invalid Inputs**: Prevent invalid configurations

## Technical Implementation Notes

### Textual Framework Usage
- **Screens**: Each wizard step is a separate Screen class
- **Widgets**: Custom validation widgets for inputs
- **Reactive Variables**: State management with reactive attributes
- **CSS Styling**: Consistent visual theme
- **Message Handling**: Screen-to-screen communication

### Configuration Model
- **Data Classes**: Type-safe configuration structures
- **YAML Generation**: Convert internal model to user_config.yml
- **Validation**: Comprehensive input validation
- **Defaults**: Sensible default values

### File Operations
- **Path Handling**: Cross-platform path management
- **File Copying**: Script files to project directory
- **Directory Creation**: Automatic directory structure setup
- **Permission Handling**: Proper file permissions

This design provides a comprehensive, user-friendly wizard interface that guides users through creating PeiDocker projects while maintaining simplicity and preventing configuration errors.