# PeiDocker GUI - Simple Mode Only Interaction Design

## Overview

The GUI provides **ONLY a simple mode** - a guided, wizard-like interface that walks users through creating a PeiDocker project using a series of sequential configuration steps. Each step has its own dedicated GUI screen. There is no advanced mode. The interface focuses on the most common configuration options with streamlined navigation and memory-based state management.

## Architecture & File Structure

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
│ Project Dir     │ ──────────────────► Skip to Simple Wizard
│   Selection     │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐
│ Simple Wizard   │ ◄── Double ESC from any step
│   Controller    │
└─────┬───────────┘
      │
      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 1: Project Info │───►│ 2: SSH Config   │───►│ 3: Proxy Config │
└─────────────────┘    └─────────────────┘    └─────────────────┘
      ▲                        ▲                        ▲
      │                        │                        │
      ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 4: APT Config   │───►│ 5: Port Mapping │───►│ 6: Environment  │
└─────────────────┘    └─────────────────┘    │    Variables    │
      ▲                        ▲              └─────────────────┘
      │                        │                        ▲
      ▼                        ▼                        │
┌─────────────────┐    ┌─────────────────┐              ▼
│ 7: Device Config│───►│ 8: Mounts       │    ┌─────────────────┐
└─────────────────┘    └─────────────────┘    │ 9: Entry Point  │
      ▲                        ▲              └─────────────────┘
      │                        │                        ▲
      ▼                        ▼                        │
┌─────────────────┐    ┌─────────────────┐              ▼
│10: Custom       │───►│11: Summary      │    ┌─────────────────┐
│    Scripts      │    │   & Save        │    │ [Persistent     │
└─────────────────┘    │ [Save|Back|     │    │  after save]    │
                       │  Cancel]        │    │ Navigate ←→     │
                       └─────────────────┘    │ Save again      │
                                              └─────────────────┘
```

**Navigation Rules:**
- Each step: `prev` | `next` buttons (bi-directional)
- Final step: `prev` | `save` | `cancel` buttons  
- Double ESC: Return to main menu from any step
- Single ESC: Clear current input or go to previous state
- Memory-only changes until save
- After save: remain on summary page, continue navigation

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
- After completion, proceed directly to Simple Wizard (no mode selection)

### 3. Simple Mode - Wizard Controller

The wizard controller manages the flow between 11 configuration screens, maintaining state in memory until save and enabling unlimited back/forth navigation.

**Navigation Features:**
- Progress indicator showing current step (1-11)
- `prev` | `next` buttons on each step (bi-directional navigation)
- Final step has `prev` | `save` | `cancel` buttons
- Double ESC: Return to main menu from any step
- Single ESC: Clear current input or go to previous state
- Memory-only state until explicit save
- After save: persistent final page with continued navigation ability
- Form validation before proceeding to next step

### 4. Project Information Screen

**Layout:**
```
╭─ Project Information ──────────────────────── Step 1 of 11 ╮
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
│  [Prev] [Next]                                              │
│                                                             │
│  * Required field                                           │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Auto-populate project name from directory
- Validate Docker image name format
- Check Docker Hub for image existence (optional, non-blocking)
- Prevent empty project names

### 5. SSH Configuration Screen

**Layout:**
```
╭─ SSH Configuration ───────────────────────── Step 2 of 11 ╮
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
│  SSH User UID:                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 1100                                                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Prev] [Next]                                              │
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
│  [Prev] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Show/hide sections based on selections
- Validate port numbers (1-65535)
- Check for port conflicts
- Password validation (no spaces/commas)
- Toggle password visibility

### 6. Proxy Configuration Screen

**Layout:**
```
╭─ Proxy Configuration ─────────────────────── Step 3 of 11 ╮
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
│  [Prev] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Show/hide proxy settings based on selection
- Validate port number
- Preview proxy URL format
- Explain build vs runtime proxy usage

### 7. APT Configuration Screen

**Layout:**
```
╭─ APT Repository Configuration ────────────── Step 4 of 11 ╮
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
│  [Prev] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Radio button selection for mirror
- Geographic information for each mirror
- Preview of mirror benefits

### 8. Port Mapping Screen

**Layout:**
```
╭─ Additional Port Mapping ─────────────────── Step 5 of 11 ╮
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
│  [Prev] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Dynamic list of port mappings
- Validate port format and ranges
- Prevent duplicate mappings
- Show SSH port as read-only

### 9. Environment Variables Screen

**Layout:**
```
╭─ Environment Variables ───────────────────── Step 6 of 11 ╮
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
│  [Prev] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Validate KEY=VALUE format
- Allow deletion by setting empty value
- Dynamic list management
- Show current variables list

### 10. Device Configuration Screen

**Layout:**
```
╭─ Device Configuration ────────────────────── Step 7 of 11 ╮
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
│  [Prev] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Warning about GPU requirements
- No automatic GPU detection
- Suggest compatible base images

### 11. Additional Mounts Screen

**Layout:**
```
╭─ Additional Mounts ───────────────────────── Step 8 of 11 ╮
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
│  [Prev] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Show/hide mount configuration sections
- Validate paths and volume names
- Warning about Stage-2 override behavior
- Support for different mount types

### 12. Custom Entry Point Screen

**Layout:**
```
╭─ Custom Entry Point ──────────────────────── Step 9 of 11 ╮
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
│  [Prev] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- File browser for script selection
- Validate script file existence
- Warning about Stage-2 override behavior
- Copy script to project directory

### 13. Custom Scripts Screen

**Layout:**
```
╭─ Custom Scripts ──────────────────────────── Step 10 of 11 ╮
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
│  [Prev] [Next]                                              │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Cycle through script types
- Show current scripts for each type
- Support command-line arguments
- Validate script paths

### 14. Configuration Summary Screen

**Layout:**
```
╭─ Configuration Summary ───────────────────── Step 11 of 11 ╮
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
│  [Prev] [Save] [Cancel]                                     │
│                                                             │
│  Save creates user_config.yml in project dir & stays here  │
│  Continue navigating back/forth and save again as needed   │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- Comprehensive configuration review
- Organized by logical sections
- Save: Write user_config.yml and remain on this page
- Prev: Navigate back to any previous step for changes
- Cancel: Return to main menu without saving
- After save: persistent page with continued navigation ability
- Generate user_config.yml file

## Key Features & Behaviors

### Navigation
- **Progress Indicator**: Shows current step (1-11) and total steps
- **Prev/Next Buttons**: Bi-directional navigation between screens
- **Double ESC**: Return to main menu from any step
- **Single ESC**: Clear current input or go to previous state
- **Final Page**: Prev | Save | Cancel buttons
- **Keyboard Shortcuts**: Tab, Enter, Escape, arrow keys
- **Unlimited Navigation**: Go back and forth between steps indefinitely

### Validation
- **Real-time Validation**: Input validation as user types
- **Error Messages**: Clear, actionable error messages
- **Required Fields**: Visual indicators for required inputs
- **Format Checking**: Port ranges, key formats, file paths

### State Management
- **Memory-Only Changes**: All configuration changes kept in memory until save
- **Configuration State**: Maintain user choices across screens during navigation
- **No Auto-save**: Only write user_config.yml when user explicitly saves
- **Persistent Final Page**: After save, remain on summary page for more changes
- **Iterative Workflow**: Navigate, modify, save repeatedly as needed
- **Reset Options**: Clear all and start over from main menu

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

## Key Design Changes from Original

This updated design reflects the new simple-mode-only approach with these critical changes:

### Removed Features
- **Advanced Mode**: Completely removed - only simple mode wizard exists
- **Mode Selection Screen**: No longer needed, go directly to wizard
- **Auto-save**: No automatic file writing during navigation

### Enhanced Features  
- **Memory-First State**: All changes kept in memory until explicit save
- **Persistent Final Page**: After save, stay on summary page for more iterations
- **Enhanced Navigation**: Unlimited back/forth movement with double-ESC to main menu
- **SSH User UID**: Added UID field (default 1100) to avoid system user conflicts
- **Iterative Workflow**: Save multiple times after making changes

### Navigation Behavior
- **Each Step**: [Prev] | [Next] buttons
- **Final Step**: [Prev] | [Save] | [Cancel] buttons  
- **Double ESC**: Return to main menu from anywhere
- **Single ESC**: Clear input or go to previous state
- **Post-Save**: Continue navigation and save again as needed

This design provides a streamlined, single-mode wizard interface that guides users through PeiDocker project creation while maintaining maximum flexibility for configuration changes and iterations.