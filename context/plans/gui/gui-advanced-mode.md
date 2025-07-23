# PeiDocker GUI - Advanced Mode Interaction Design

## Overview

Advanced mode provides a comprehensive form-based interface that exposes all PeiDocker configuration options across both Stage-1 and Stage-2. Unlike simple mode's wizard approach, advanced mode presents a structured, tabbed interface allowing users to navigate freely between configuration sections and have complete control over their Docker container setup.

## Architecture & Enhanced File Structure

```
src/pei_docker/gui/
├── __init__.py
├── app.py                          # Main GUI application entry point
├── screens/
│   ├── __init__.py
│   ├── startup.py                  # Project directory selection and validation
│   ├── mode_selection.py           # Simple vs Advanced mode selection
│   ├── advanced/
│   │   ├── __init__.py
│   │   ├── main_layout.py          # Main advanced mode layout with tabs
│   │   ├── stage1/
│   │   │   ├── __init__.py
│   │   │   ├── image_config.py     # Image settings (base, output)
│   │   │   ├── ssh_config.py       # SSH configuration with all options
│   │   │   ├── network_config.py   # Proxy, ports, network settings
│   │   │   ├── system_config.py    # APT, device, environment vars
│   │   │   ├── storage_config.py   # Mounts and volumes
│   │   │   ├── scripts_config.py   # Custom scripts and entry points
│   │   │   └── review_stage1.py    # Stage-1 configuration review
│   │   ├── stage2/
│   │   │   ├── __init__.py
│   │   │   ├── image_config.py     # Stage-2 image settings
│   │   │   ├── storage_config.py   # Stage-2 storage configuration
│   │   │   ├── pixi_config.py      # Pixi package manager settings
│   │   │   ├── conda_config.py     # Conda/Miniconda settings (legacy)
│   │   │   ├── ros_config.py       # ROS2 development settings
│   │   │   ├── ai_config.py        # AI/ML framework settings
│   │   │   ├── scripts_config.py   # Stage-2 custom scripts
│   │   │   └── review_stage2.py    # Stage-2 configuration review
│   │   ├── yaml_editor.py          # Direct YAML editing interface
│   │   ├── config_validator.py     # Real-time configuration validation
│   │   ├── config_comparison.py    # Compare current vs saved config
│   │   ├── template_manager.py     # Load/save configuration templates
│   │   └── build_monitor.py        # Docker build progress monitor
│   └── common/
│       ├── __init__.py
│       ├── widgets.py              # Advanced custom widgets
│       ├── forms.py                # Form components and layouts
│       ├── validators.py           # Complex input validation
│       ├── yaml_utils.py           # YAML parsing and generation
│       └── config_templates.py     # Configuration template definitions
├── models/
│   ├── __init__.py
│   ├── config.py                   # Enhanced configuration data models
│   ├── validation.py               # Configuration validation rules
│   └── templates.py                # Template configuration structures
└── utils/
    ├── __init__.py
    ├── docker_utils.py             # Enhanced Docker operations
    ├── file_utils.py               # Advanced file operations
    ├── git_utils.py                # Git integration utilities
    └── export_utils.py             # Configuration export/import
```

## Main Interface Architecture

### Tab-Based Navigation Structure

```
╭─ PeiDocker Advanced Configuration ─────────────────────────╮
│                                                             │
│ [Stage-1] [Stage-2] [YAML Editor] [Templates] [Build]      │
│ ═══════════════════════════════════════════════════════════ │
│                                                             │
│ ┌─ Configuration Sections ─────────────────────────────────┐ │
│ │ [Image] [SSH] [Network] [System] [Storage] [Scripts]    │ │
│ │ ═════════════════════════════════════════════════════════ │ │
│ │                                                         │ │
│ │                Main Configuration Area                  │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Status Bar ──────────────────────────────────────────────┐ │
│ │ ✓ Config Valid │ ⚠ 2 Warnings │ Docker: Ready │ Auto-save: On │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Save] [Load] [Reset] [Validate] [Build Images] [Help]     │
╰─────────────────────────────────────────────────────────────╯
```

## Detailed Screen Designs

### 1. Advanced Mode Main Layout

**Layout Structure:**
```
╭─ PeiDocker Advanced Configuration ─────────────────────────╮
│                                                             │
│ Project: my-awesome-project                                 │
│ Path: D:\code\my-project                                    │
│                                                             │
│ ┌─ Main Tabs ───────────────────────────────────────────────┐ │
│ │ [●Stage-1] [○Stage-2] [○YAML] [○Templates] [○Build]     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Section Tabs ───────────────────────────────────────────┐ │
│ │ [●Image] [○SSH] [○Network] [○System] [○Storage] [○Scripts] │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Configuration Form ─────────────────────────────────────┐ │
│ │                                                         │ │
│ │           Dynamic Content Area                          │ │
│ │           (Changes based on selected tabs)             │ │
│ │                                                         │ │
│ │                                                         │ │
│ │                                                         │ │
│ │                                                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Status & Validation ────────────────────────────────────┐ │
│ │ ✓ Configuration Valid │ Last Saved: 2 minutes ago      │ │
│ │ ⚠ Warning: GPU enabled but no CUDA base image          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Save Config] [Load Template] [Build Images] [Help] [Exit] │
│                                                             │
│ Ctrl+S: Save │ Ctrl+L: Load │ Ctrl+B: Build │ F1: Help     │
╰─────────────────────────────────────────────────────────────╯
```

**Key Features:**
- **Dual Tab System**: Main tabs (Stage-1/2, YAML, etc.) and section tabs within each main tab
- **Real-time Validation**: Continuous validation with status indicators
- **Auto-save**: Optional automatic saving of configuration changes
- **Context Help**: Context-sensitive help for current section

### 2. Stage-1 Image Configuration

**Layout:**
```
╭─ Stage-1: Image Configuration ─────────────────────────────╮
│                                                             │
│ ┌─ Base Image Settings ────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Base Docker Image: *                                    │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ ubuntu:24.04                                        │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ [Check Hub] [Browse Popular]                            │ │
│ │                                                         │ │
│ │ ✓ Image exists on Docker Hub (24.04, ~78MB)            │ │
│ │                                                         │ │
│ │ Popular base images:                                    │ │
│ │ • ubuntu:24.04         - Latest Ubuntu LTS             │ │
│ │ • ubuntu:22.04         - Previous LTS (stable)         │ │
│ │ • debian:12            - Debian Bookworm               │ │
│ │ • alpine:3.18          - Alpine Linux (minimal)        │ │
│ │ • nvidia/cuda:12.6.*   - CUDA development              │ │
│ │ • python:3.11          - Python runtime                │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Output Image Settings ──────────────────────────────────┐ │
│ │                                                         │ │
│ │ Output Image Name: *                                    │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ my-awesome-project:stage-1                          │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ ⚠ Image already exists locally - will be overwritten   │ │
│ │ Created: 2 hours ago, Size: 1.2GB                      │ │
│ │                                                         │ │
│ │ Image Naming Convention:                                │ │
│ │ • project-name:stage-1 (recommended)                   │ │
│ │ • Custom tags supported                                 │ │
│ │ • Registry prefixes allowed (e.g., localhost:5000/)    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Advanced Image Options ─────────────────────────────────┐ │
│ │                                                         │ │
│ │ Build Args:                                             │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ ARG1=value1                                         │ │ │
│ │ │ ARG2=value2                                         │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ [+Add] [Clear All]                                      │ │
│ │                                                         │ │
│ │ Labels:                                                 │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ version=1.0.0                                       │ │ │
│ │ │ maintainer=user@example.com                         │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ [+Add] [Clear All]                                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back] [Next: SSH] [Save Section]                          │
╰─────────────────────────────────────────────────────────────╯
```

**Behavior:**
- **Live Docker Hub Checking**: Real-time verification of base image existence
- **Image Size Display**: Show estimated download size and build time
- **Conflict Detection**: Warn about existing local images
- **Smart Suggestions**: Context-aware suggestions based on project type
- **Build Args/Labels**: Advanced Docker build customization

### 3. Enhanced SSH Configuration

**Layout:**
```
╭─ Stage-1: SSH Configuration ──────────────────────────────╮
│                                                             │
│ ┌─ SSH Server Settings ────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Enable SSH Server: ● Yes  ○ No                          │ │
│ │                                                         │ │
│ │ SSH Port (Container): ┌───────┐  SSH Port (Host): ┌────┐ │ │
│ │                      │ 22    │                   │2222│ │ │
│ │                      └───────┘                   └────┘ │ │
│ │                                                         │ │
│ │ ⚠ Port 2222 is already in use by another container     │ │
│ │ [Scan Ports] [Suggest Alternative]                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ SSH Users ──────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ ┌─ User: me ─────────────────────────────────────────┐   │ │
│ │ │                                                   │   │ │
│ │ │ Password: ┌─────────────────┐ [👁 Show] [🎲 Generate] │   │ │
│ │ │          │ ••••••••••      │                        │   │ │
│ │ │          └─────────────────┘                        │   │ │
│ │ │                                                   │   │ │
│ │ │ UID: ┌─────┐ (Recommended: ≥1100)                 │   │ │
│ │ │     │ 1100│                                       │   │ │
│ │ │     └─────┘                                       │   │ │
│ │ │                                                   │   │ │
│ │ │ Authentication Methods:                           │   │ │
│ │ │ ☑ Password   ☐ Public Key   ☐ Private Key        │   │ │
│ │ │                                                   │   │ │
│ │ │ ┌─ Public Key (when enabled) ─────────────────────│   │ │
│ │ │ │ Source: ● Text  ○ File  ○ System (~)           │   │ │
│ │ │ │                                                │   │ │
│ │ │ │ ┌─────────────────────────────────────────────┐│   │ │
│ │ │ │ │ ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQA... ││   │ │
│ │ │ │ │                                             ││   │ │
│ │ │ │ └─────────────────────────────────────────────┘│   │ │
│ │ │ │ [Validate Key] [Import from File]              │   │ │
│ │ │ └──────────────────────────────────────────────────┘   │ │
│ │ │                                                   │   │ │
│ │ │ ┌─ Private Key (when enabled) ────────────────────│   │ │
│ │ │ │ Source: ● File Path  ○ System (~)              │   │ │
│ │ │ │                                                │   │ │
│ │ │ │ File Path: ┌─────────────────────────────────┐ │   │ │
│ │ │ │           │ /home/user/.ssh/id_rsa          │ │   │ │
│ │ │ │           └─────────────────────────────────┘ │   │ │
│ │ │ │ [Browse] [Test Key]                          │   │ │
│ │ │ │                                                │   │ │
│ │ │ │ ⚠ Key is encrypted - will be copied as-is      │   │ │
│ │ │ └──────────────────────────────────────────────────┘   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ │                                                         │ │
│ │ [+Add User] [Remove User]                               │ │
│ │                                                         │ │
│ │ ┌─ Root User ──────────────────────────────────────────┐ │ │
│ │ │ Enable Root SSH: ○ Yes  ● No                        │ │ │
│ │ │                                                     │ │ │
│ │ │ ┌─ Root Password (when enabled) ──────────────────┐  │ │ │
│ │ │ │ ┌─────────────────┐ [👁 Show] [🎲 Generate]      │  │ │ │
│ │ │ │ │ ••••••••••      │                             │  │ │ │
│ │ │ │ └─────────────────┘                             │  │ │ │
│ │ │ └─────────────────────────────────────────────────┘  │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ SSH Security Options ───────────────────────────────────┐ │
│ │                                                         │ │
│ │ ☐ Disable password authentication (key-only)            │ │
│ │ ☐ Change default SSH port for security                  │ │
│ │ ☐ Enable SSH connection logging                         │ │
│ │ ☑ Use strong cipher suites only                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back: Image] [Next: Network] [Test SSH] [Save Section]    │
╰─────────────────────────────────────────────────────────────╯
```

**Advanced Features:**
- **Port Conflict Detection**: Real-time checking for port availability
- **Password Generator**: Built-in secure password generation
- **Key Validation**: SSH key format validation and testing
- **Multi-user Support**: Add/remove multiple SSH users
- **Security Options**: Advanced SSH hardening options

### 4. Network Configuration

**Layout:**
```
╭─ Stage-1: Network Configuration ──────────────────────────╮
│                                                             │
│ ┌─ Proxy Settings ─────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Enable HTTP Proxy: ○ Yes  ● No                          │ │
│ │                                                         │ │
│ │ ┌─ Proxy Configuration (when enabled) ─────────────────┐ │ │
│ │ │                                                     │ │ │
│ │ │ Proxy Host: ┌─────────────────────┐                 │ │ │
│ │ │            │ host.docker.internal│                 │ │ │
│ │ │            └─────────────────────┘                 │ │ │
│ │ │                                                     │ │ │
│ │ │ Proxy Port: ┌──────┐                               │ │ │
│ │ │            │ 8080 │                               │ │ │
│ │ │            └──────┘                               │ │ │
│ │ │                                                     │ │ │
│ │ │ Proxy URL: http://host.docker.internal:8080         │ │ │
│ │ │                                                     │ │ │
│ │ │ Proxy Usage:                                        │ │ │
│ │ │ ● Build-time only (removed after build)            │ │ │
│ │ │ ○ Build and runtime (persistent)                   │ │ │
│ │ │                                                     │ │ │
│ │ │ Proxy Variables:                                    │ │ │
│ │ │ ☑ HTTP_PROXY   ☑ HTTPS_PROXY   ☐ FTP_PROXY        │ │ │
│ │ │ ☑ NO_PROXY: localhost,127.0.0.1,.local             │ │ │
│ │ │                                                     │ │ │
│ │ │ [Test Connection] [Auto-detect]                     │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Port Mappings ──────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Current Mappings:                                       │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Host Port │ Container Port │ Protocol │ Description │ │ │
│ │ │ ──────────┼────────────────┼──────────┼─────────────│ │ │
│ │ │ 2222      │ 22             │ TCP      │ SSH         │ │ │
│ │ │ 8080      │ 80             │ TCP      │ HTTP        │ │ │
│ │ │ 3000-3010 │ 3000-3010      │ TCP      │ Node.js Dev │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ Add Port Mapping:                                       │ │
│ │ Host: ┌─────┐ Container: ┌─────┐ Protocol: [TCP ▼]      │ │
│ │      │8080 │           │ 80  │                        │ │
│ │      └─────┘           └─────┘                        │ │
│ │                                                         │ │
│ │ Description: ┌─────────────────────────────────────────┐ │ │
│ │             │ Web server                              │ │ │
│ │             └─────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ [Add Mapping] [Remove Selected] [Import from Template] │ │
│ │                                                         │ │
│ │ ⚠ Port 8080 conflicts with existing mapping            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Network Mode ───────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Docker Network Mode:                                    │ │
│ │ ● bridge (default)  ○ host  ○ none  ○ custom           │ │
│ │                                                         │ │
│ │ Custom Network: ┌─────────────────────────────────────┐ │ │
│ │                │ my-custom-network                   │ │ │
│ │                └─────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ Network Aliases: ┌────────────────────────────────────┐ │ │
│ │                 │ web-server, api-backend            │ │ │
│ │                 └────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back: SSH] [Next: System] [Test Network] [Save Section]   │
╰─────────────────────────────────────────────────────────────╯
```

**Advanced Features:**
- **Port Conflict Detection**: Check for port conflicts across host system
- **Network Mode Selection**: Support for different Docker network modes
- **Proxy Testing**: Test proxy connectivity during configuration
- **Port Range Support**: Configure port ranges with validation

### 5. System Configuration

**Layout:**
```
╭─ Stage-1: System Configuration ───────────────────────────╮
│                                                             │
│ ┌─ APT Package Management ─────────────────────────────────┐ │
│ │                                                         │ │
│ │ Repository Mirror:                                      │ │
│ │ ● default (Ubuntu official)                             │ │
│ │ ○ tuna (Tsinghua University, China)                     │ │
│ │ ○ aliyun (Alibaba Cloud, China)                         │ │
│ │ ○ 163 (NetEase, China)                                  │ │
│ │ ○ ustc (USTC, China)                                     │ │
│ │ ○ cn (Ubuntu China official)                            │ │
│ │                                                         │ │
│ │ Additional Repositories:                                │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ deb http://ppa.launchpad.net/example/ppa ubuntu     │ │ │
│ │ │                                                     │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ [Add Repository] [Import PPAs]                          │ │
│ │                                                         │ │
│ │ Pre-install Packages:                                   │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ curl, wget, git, vim, htop, build-essential         │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ [Add Package] [Import Package List]                    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Hardware & Device Configuration ────────────────────────┐ │
│ │                                                         │ │
│ │ Device Type:                                            │ │
│ │ ● cpu (CPU only)                                        │ │
│ │ ○ gpu (NVIDIA GPU support)                              │ │
│ │                                                         │ │
│ │ ┌─ GPU Configuration (when enabled) ─────────────────┐   │ │
│ │ │                                                   │   │ │
│ │ │ NVIDIA GPU Runtime:                               │   │ │
│ │ │ ☑ Enable NVIDIA Docker runtime                   │   │ │
│ │ │ ☑ Expose all GPU devices                          │   │ │
│ │ │ ☑ Enable all driver capabilities                  │   │ │
│ │ │                                                   │   │ │
│ │ │ CUDA Version: ┌──────────────────┐                │   │ │
│ │ │              │ 12.6.3 (auto)    │                │   │ │
│ │ │              └──────────────────┘                │   │ │
│ │ │                                                   │   │ │
│ │ │ Specific GPU Devices (optional):                  │   │ │
│ │ │ ┌───────────────────────────────────────────────┐ │   │ │
│ │ │ │ device=0,1  # Use first two GPUs only         │ │   │ │
│ │ │ └───────────────────────────────────────────────┘ │   │ │
│ │ │                                                   │   │ │
│ │ │ [Detect GPUs] [Test CUDA] [Check Compatibility]  │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Environment Variables ──────────────────────────────────┐ │
│ │                                                         │ │
│ │ System Environment Variables:                           │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Variable        │ Value                             │ │ │
│ │ │ ────────────────┼───────────────────────────────────│ │ │
│ │ │ DEBIAN_FRONTEND │ noninteractive                    │ │ │
│ │ │ TZ              │ UTC                               │ │ │
│ │ │ LANG            │ en_US.UTF-8                       │ │ │
│ │ │ NODE_ENV        │ production                        │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ Add Variable:                                           │ │
│ │ Name: ┌────────────┐ Value: ┌─────────────────────────┐ │ │
│ │      │ DEBUG      │       │ true                    │ │ │
│ │      └────────────┘       └─────────────────────────┘ │ │
│ │                                                         │ │
│ │ [Add Variable] [Remove Selected] [Import from File]    │ │
│ │                                                         │ │
│ │ ⚠ Variable DEBUG already exists - will be overwritten  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Locale & Timezone ──────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Timezone: ┌──────────────────┐ [Detect Local]           │ │
│ │          │ America/New_York │                          │ │
│ │          └──────────────────┘                          │ │
│ │                                                         │ │
│ │ Locale: ┌─────────────┐ Encoding: ┌─────────┐           │ │
│ │        │ en_US       │          │ UTF-8   │           │ │
│ │        └─────────────┘          └─────────┘           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back: Network] [Next: Storage] [Validate Config] [Save]   │
╰─────────────────────────────────────────────────────────────╯
```

**Enhanced Features:**
- **GPU Detection**: Attempt to detect local GPU capabilities
- **Package Management**: Pre-install common packages with smart suggestions
- **Environment Templates**: Load common environment variable sets
- **Locale Detection**: Auto-detect system locale and timezone

### 6. Storage Configuration

**Layout:**
```
╭─ Stage-1: Storage Configuration ──────────────────────────╮
│                                                             │
│ ┌─ Default PeiDocker Storage ──────────────────────────────┐ │
│ │                                                         │ │
│ │ /soft/app:       ○ auto-volume  ○ manual-volume         │ │
│ │                 ○ host-dir      ● image-storage         │ │
│ │                                                         │ │
│ │ /soft/data:      ● auto-volume  ○ manual-volume         │ │
│ │                 ○ host-dir      ○ image-storage         │ │
│ │                                                         │ │
│ │ /soft/workspace: ● auto-volume  ○ manual-volume         │ │
│ │                 ○ host-dir      ○ image-storage         │ │
│ │                                                         │ │
│ │ ℹ auto-volume: Docker manages volume automatically      │ │
│ │ ℹ manual-volume: You specify existing volume name       │ │
│ │ ℹ host-dir: Bind mount from host directory              │ │
│ │ ℹ image-storage: Files stored in image (not persistent) │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Volume Configuration Details ───────────────────────────┐ │
│ │                                                         │ │
│ │ ┌─ /soft/data (auto-volume) ─────────────────────────┐   │ │
│ │ │                                                   │   │ │
│ │ │ Docker will create: my-project_data_volume        │   │ │
│ │ │ Mount options: rw,noatime                         │   │ │
│ │ │ Backup strategy: ○ Enable  ● Disable              │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ │                                                         │ │
│ │ ┌─ /soft/workspace (auto-volume) ────────────────────┐   │ │
│ │ │                                                   │   │ │
│ │ │ Docker will create: my-project_workspace_volume   │   │ │
│ │ │ Mount options: rw,noatime                         │   │ │
│ │ │ Backup strategy: ☑ Enable daily backup            │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Additional Mount Points ─────────────────────────────────┐ │
│ │                                                         │ │
│ │ Custom Mounts:                                          │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Source          │ Destination │ Type        │ Options │ │
│ │ │ ────────────────┼─────────────┼─────────────┼─────────│ │
│ │ │ my-db-volume    │ /var/lib/db │ volume      │ rw      │ │
│ │ │ /host/logs      │ /app/logs   │ bind        │ rw      │ │
│ │ │ tmpfs           │ /tmp        │ tmpfs       │ size=1g │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ Add Mount:                                              │ │
│ │ Type: [Volume ▼] Source: ┌─────────────────────────────┐ │ │
│ │                         │ my-new-volume               │ │ │
│ │                         └─────────────────────────────┘ │ │
│ │                                                         │ │
│ │ Destination: ┌──────────────────────────────────────────┐ │ │
│ │             │ /app/data                               │ │ │
│ │             └──────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ Options: ┌─────────────────────────────────────────────┐ │ │
│ │         │ rw,noatime                                  │ │ │
│ │         └─────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ [Add Mount] [Remove Selected] [Import Configuration]    │ │
│ │                                                         │ │
│ │ ⚠ Destination /app/data already mounted                 │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Storage Optimization ───────────────────────────────────┐ │
│ │                                                         │ │
│ │ ☑ Enable volume caching for better performance          │ │
│ │ ☑ Use delegated consistency for host binds (macOS)      │ │
│ │ ☐ Enable volume encryption (requires setup)             │ │
│ │ ☑ Auto-cleanup unused volumes on removal                │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back: System] [Next: Scripts] [Test Mounts] [Save Section]│
╰─────────────────────────────────────────────────────────────╯
```

**Advanced Features:**
- **Visual Mount Management**: Table-based mount point configuration
- **Mount Validation**: Check for conflicts and invalid paths
- **Storage Optimization**: Performance and security options
- **Backup Integration**: Configure automatic volume backups

### 7. Scripts & Hooks Configuration

**Layout:**
```
╭─ Stage-1: Scripts & Hooks Configuration ──────────────────╮
│                                                             │
│ ┌─ Entry Point Configuration ──────────────────────────────┐ │
│ │                                                         │ │
│ │ Custom Entry Point: ○ Yes  ● No                         │ │
│ │                                                         │ │
│ │ ┌─ Entry Point Script (when enabled) ─────────────────┐ │ │
│ │ │                                                     │ │ │
│ │ │ Script Path: ┌─────────────────────────────────────┐ │ │ │
│ │ │             │ /path/to/entrypoint.sh              │ │ │ │
│ │ │             └─────────────────────────────────────┘ │ │ │
│ │ │ [Browse File] [Create New] [Edit Script]           │ │ │
│ │ │                                                     │ │ │
│ │ │ Arguments: ┌──────────────────────────────────────┐ │ │ │
│ │ │           │ --verbose --config=/app/config.yml   │ │ │ │
│ │ │           └──────────────────────────────────────┘ │ │ │
│ │ │                                                     │ │ │
│ │ │ Working Directory: ┌──────────────────────────────┐ │ │ │
│ │ │                   │ /app                         │ │ │ │
│ │ │                   └──────────────────────────────┘ │ │ │
│ │ │                                                     │ │ │
│ │ │ [Test Script] [View Preview]                        │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Custom Lifecycle Scripts ───────────────────────────────┐ │
│ │                                                         │ │
│ │ Script Categories:                                      │ │
│ │ [●on_build] [○on_first_run] [○on_every_run] [○on_login] │ │
│ │                                                         │ │
│ │ ┌─ on_build Scripts ──────────────────────────────────┐ │ │
│ │ │                                                     │ │ │
│ │ │ Execute during Docker image build process           │ │ │
│ │ │                                                     │ │ │
│ │ │ Current Scripts:                                    │ │ │
│ │ │ ┌─────────────────────────────────────────────────┐ │ │ │
│ │ │ │ 1. stage-1/custom/install-deps.sh --update     │ │ │ │
│ │ │ │ 2. stage-1/system/setup-nginx.sh               │ │ │ │
│ │ │ └─────────────────────────────────────────────────┘ │ │ │
│ │ │                                                     │ │ │
│ │ │ Add Script:                                         │ │ │
│ │ │ Path: ┌───────────────────────────────────────────┐ │ │ │
│ │ │      │ stage-1/custom/my-script.sh --arg value   │ │ │ │
│ │ │      └───────────────────────────────────────────┘ │ │ │
│ │ │ [Add Script] [Browse Files] [Remove Selected]      │ │ │
│ │ │                                                     │ │ │
│ │ │ Execution Order: [Move Up] [Move Down]              │ │ │
│ │ │ ⚠ Scripts execute in order shown above             │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ ┌─ Script Templates ──────────────────────────────────┐ │ │
│ │ │                                                     │ │ │
│ │ │ Common Script Templates:                            │ │ │
│ │ │ • System Updates & Security Patches                 │ │ │
│ │ │ • Development Tools Installation                    │ │ │
│ │ │ • Database Setup (MySQL, PostgreSQL, MongoDB)      │ │ │
│ │ │ • Web Server Configuration (Nginx, Apache)         │ │ │
│ │ │ • SSL Certificate Setup                             │ │ │
│ │ │ • User Environment Setup                            │ │ │
│ │ │                                                     │ │ │
│ │ │ [Browse Templates] [Create Custom Template]         │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Script Editor & Validation ─────────────────────────────┐ │
│ │                                                         │ │
│ │ Selected Script: stage-1/custom/install-deps.sh        │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ #!/bin/bash                                         │ │ │
│ │ │ set -e                                              │ │ │
│ │ │                                                     │ │ │
│ │ │ # Install essential development tools               │ │ │
│ │ │ apt-get update                                      │ │ │
│ │ │ apt-get install -y build-essential git curl        │ │ │
│ │ │                                                     │ │ │
│ │ │ # Setup Node.js                                     │ │ │
│ │ │ curl -fsSL https://deb.nodesource.com/setup_18.x   │ │ │
│ │ │                                                     │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ [Save Script] [Validate Syntax] [Test in Container]    │ │
│ │                                                         │ │
│ │ Validation Status: ✓ Syntax OK  ✓ Dependencies OK     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back: Storage] [Next: Review] [Save All Scripts] [Test]   │
╰─────────────────────────────────────────────────────────────╯
```

**Advanced Features:**
- **Script Categories**: Organized by lifecycle phase with explanations
- **Script Editor**: Built-in editor with syntax highlighting
- **Script Templates**: Pre-built templates for common tasks
- **Validation**: Syntax checking and dependency validation
- **Execution Order**: Visual reordering of script execution

### 8. Stage-1 Configuration Review

**Layout:**
```
╭─ Stage-1: Configuration Review ───────────────────────────╮
│                                                             │
│ ┌─ Configuration Summary ──────────────────────────────────┐ │
│ │                                                         │ │
│ │ ✓ Image: ubuntu:24.04 → my-project:stage-1              │ │
│ │ ✓ SSH: Enabled (2222:22) - 2 users configured           │ │
│ │ ✓ Network: Default bridge, 3 port mappings              │ │
│ │ ✓ System: CPU mode, 5 environment variables             │ │
│ │ ✓ Storage: 2 auto-volumes, 1 custom mount               │ │
│ │ ✓ Scripts: 3 build scripts, 1 custom entry point       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Validation Results ─────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Configuration Status: ✓ Valid                           │ │
│ │                                                         │ │
│ │ Warnings:                                               │ │
│ │ ⚠ Port 8080 is commonly used - consider alternatives    │ │
│ │ ⚠ Root SSH access enabled - security risk               │ │
│ │                                                         │ │
│ │ Recommendations:                                        │ │
│ │ ℹ Consider adding health check configuration             │ │
│ │ ℹ GPU base image recommended for better performance     │ │
│ │ ℹ Add log rotation for long-running containers          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Generated Configuration Preview ────────────────────────┐ │
│ │                                                         │ │
│ │ user_config.yml (Stage-1 section):                     │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ stage_1:                                            │ │ │
│ │ │   image:                                            │ │ │
│ │ │     base: ubuntu:24.04                              │ │ │
│ │ │     output: my-project:stage-1                      │ │ │
│ │ │   ssh:                                              │ │ │
│ │ │     enable: true                                    │ │ │
│ │ │     port: 22                                        │ │ │
│ │ │     host_port: 2222                                 │ │ │
│ │ │     users:                                          │ │ │
│ │ │       me:                                           │ │ │
│ │ │         password: '******'                          │ │ │
│ │ │         uid: 1100                                   │ │ │
│ │ │   # ... (truncated for display)                     │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ [View Full YAML] [Export Configuration]                 │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Build Estimation ───────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Estimated Build Time: ~8-12 minutes                     │ │
│ │ Estimated Image Size: ~1.2GB                            │ │
│ │ Required Disk Space: ~2.5GB (including layers)          │ │
│ │                                                         │ │
│ │ Build Dependencies:                                     │ │
│ │ • Base image download: ~78MB                            │ │
│ │ • APT packages: ~400MB                                  │ │
│ │ • Custom scripts: minimal                               │ │
│ │                                                         │ │
│ │ [Start Build] [Schedule Build] [Save & Exit]            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back: Scripts] [Continue to Stage-2] [Save Config] [Build]│
╰─────────────────────────────────────────────────────────────╯
```

**Review Features:**
- **Comprehensive Summary**: All configuration sections at a glance
- **Validation**: Real-time validation with warnings and recommendations
- **YAML Preview**: Show generated configuration
- **Build Estimation**: Predict build time and resource requirements

### 9. Stage-2 Main Interface

**Layout:**
```
╭─ Stage-2: Advanced Application Configuration ─────────────╮
│                                                             │
│ ┌─ Stage-2 Inheritance ────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Inherits from Stage-1: my-project:stage-1                │ │
│ │                                                         │ │
│ │ Stage-2 Override Behavior:                              │ │
│ │ ☑ Storage mounts completely replace Stage-1 mounts      │ │
│ │ ☑ Entry points completely replace Stage-1 entry points  │ │
│ │ ☑ Custom scripts are additive to Stage-1 scripts       │ │
│ │ ☐ Environment variables merge with Stage-1 variables    │ │
│ │                                                         │ │
│ │ ⚠ Changes here will affect the final application image  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Section Navigation ─────────────────────────────────────┐ │
│ │ [●Image] [○Storage] [○Pixi] [○AI/ML] [○ROS2] [○Scripts] │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Stage-2 Image Configuration ────────────────────────────┐ │
│ │                                                         │ │
│ │ Output Image: *                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ my-project:stage-2                                  │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ Base Image Source: ● Stage-1 Image  ○ Custom Base       │ │
│ │                                                         │ │
│ │ ┌─ Custom Base (when selected) ──────────────────────┐   │ │
│ │ │ Base Image: ┌─────────────────────────────────────┐ │   │ │
│ │ │            │ python:3.11-slim                    │ │   │ │
│ │ │            └─────────────────────────────────────┘ │   │ │
│ │ │                                                   │   │ │
│ │ │ ⚠ Using custom base skips Stage-1 configuration   │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ │                                                         │ │
│ │ Final Image Properties:                                 │ │
│ │ • Working Directory: /workspace                         │ │
│ │ • Default User: developer (UID 1100)                   │ │
│ │ • Exposed Ports: 22, 80, 3000-3010                     │ │
│ │ • Health Check: ○ Enabled  ● Disabled                   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Continue to Storage] [Back to Stage-1] [Save] [Build]     │
╰─────────────────────────────────────────────────────────────╯
```

### 10. Stage-2 Storage Configuration

**Layout:**
```
╭─ Stage-2: Storage Configuration ──────────────────────────╮
│                                                             │
│ ┌─ Storage Override Notice ────────────────────────────────┐ │
│ │                                                         │ │
│ │ ⚠ Stage-2 storage configuration completely replaces     │ │
│ │   Stage-1 mount configuration. Configure all required   │ │
│ │   mounts here.                                          │ │
│ │                                                         │ │
│ │ Stage-1 mounts (for reference):                         │ │
│ │ • /soft/app → auto-volume                               │ │
│ │ • /soft/data → auto-volume                              │ │
│ │ • /soft/workspace → auto-volume                         │ │
│ │                                                         │ │
│ │ [Import Stage-1 Mounts] [Start Fresh]                   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ PeiDocker Standard Storage ─────────────────────────────┐ │
│ │                                                         │ │
│ │ /soft/app (Application files):                          │ │
│ │ ● auto-volume  ○ manual-volume  ○ host-dir  ○ image     │ │
│ │                                                         │ │
│ │ ┌─ Configuration (auto-volume) ──────────────────────┐   │ │
│ │ │ Docker Volume: my-project_app_s2 (auto-generated)  │   │ │
│ │ │ Size Limit: ┌──────┐ GB (optional)                 │   │ │
│ │ │            │ 10   │                                │   │ │
│ │ │            └──────┘                                │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ │                                                         │ │
│ │ /soft/data (Data files):                                │ │
│ │ ○ auto-volume  ● manual-volume  ○ host-dir  ○ image     │ │
│ │                                                         │ │
│ │ ┌─ Configuration (manual-volume) ────────────────────┐   │ │
│ │ │ Volume Name: ┌────────────────────────────────────┐ │   │ │
│ │ │             │ shared-data-volume                 │ │   │ │
│ │ │             └────────────────────────────────────┘ │   │ │
│ │ │ [Create Volume] [Check Exists]                     │   │ │
│ │ │                                                    │   │ │
│ │ │ ✓ Volume exists (2.3GB used, created 3 days ago) │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ │                                                         │ │
│ │ /soft/workspace (Development workspace):                │ │
│ │ ○ auto-volume  ○ manual-volume  ● host-dir  ○ image     │ │
│ │                                                         │ │
│ │ ┌─ Configuration (host-dir) ─────────────────────────┐   │ │
│ │ │ Host Path: ┌──────────────────────────────────────┐ │   │ │
│ │ │           │ D:\code\my-project\workspace          │ │   │ │
│ │ │           └──────────────────────────────────────┘ │   │ │
│ │ │ [Browse] [Create Directory]                        │   │ │
│ │ │                                                    │   │ │
│ │ │ Mount Options: ┌─────────────────────────────────┐ │   │ │
│ │ │               │ rw,cached                       │ │   │ │
│ │ │               └─────────────────────────────────┘ │   │ │
│ │ │                                                    │   │ │
│ │ │ ✓ Directory exists and is writable                │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Additional Mounts ──────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Custom Mount Points:                                    │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Source              │ Destination   │ Type      │ RW │ │ │
│ │ │ ────────────────────┼───────────────┼───────────┼────│ │ │
│ │ │ models-volume       │ /models       │ volume    │ ✓  │ │ │
│ │ │ D:\cache           │ /app/cache    │ bind      │ ✓  │ │ │
│ │ │ tmpfs              │ /tmp/scratch  │ tmpfs     │ ✓  │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ [+Add Mount] [Remove Selected] [Import from Template]   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back: Image] [Next: Pixi] [Validate Mounts] [Save]        │
╰─────────────────────────────────────────────────────────────╯
```

### 11. Pixi Package Manager Configuration

**Layout:**
```
╭─ Stage-2: Pixi Package Manager ───────────────────────────╮
│                                                             │
│ ┌─ Pixi Installation ──────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Enable Pixi: ● Yes  ○ No                                │ │
│ │                                                         │ │
│ │ Installation Method:                                    │ │
│ │ ● Auto-install during build  ○ Pre-installed in base    │ │
│ │                                                         │ │
│ │ Installation Location:                                  │ │
│ │ ● /hard/volume/app/pixi (persistent)                    │ │
│ │ ○ /hard/image/app/pixi (baked into image)               │ │
│ │ ○ /usr/local/bin/pixi (system-wide)                     │ │
│ │                                                         │ │
│ │ Cache Directory:                                        │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ /hard/volume/app/pixi-cache                         │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ [Test Installation] [Clear Cache]                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Repository Configuration ───────────────────────────────┐ │
│ │                                                         │ │
│ │ Primary Channel: [conda-forge ▼]                        │ │
│ │                                                         │ │
│ │ Additional Channels:                                    │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ • pytorch (for ML packages)                        │ │ │
│ │ │ • bioconda (for bioinformatics)                    │ │ │
│ │ │ • pyviz (for visualization)                         │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ Mirror Configuration:                                   │ │
│ │ ○ Default (conda-forge.org)                            │ │
│ │ ● Tuna Mirror (China) - faster for Asia                │ │
│ │ ○ Custom Mirror                                         │ │
│ │                                                         │ │
│ │ ┌─ Custom Mirror (when selected) ───────────────────┐   │ │
│ │ │ Mirror URL: ┌─────────────────────────────────────┐ │   │ │
│ │ │            │ https://mirrors.example.com/conda   │ │   │ │
│ │ │            └─────────────────────────────────────┘ │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Global Environment Setup ───────────────────────────────┐ │
│ │                                                         │ │
│ │ Create Global Environments:                             │ │
│ │                                                         │ │
│ │ ☑ Common Development Tools                              │ │
│ │   scipy, click, attrs, omegaconf, rich, networkx       │ │
│ │                                                         │ │
│ │ ☑ Machine Learning Stack                                │ │
│ │   pytorch, torchvision, opencv, scikit-learn           │ │
│ │                                                         │ │
│ │ ☐ Data Science Tools                                    │ │
│ │   pandas, numpy, matplotlib, jupyter, seaborn          │ │
│ │                                                         │ │
│ │ ☐ Web Development                                       │ │
│ │   fastapi, flask, requests, httpx, pydantic            │ │
│ │                                                         │ │
│ │ ☐ Computer Vision                                       │ │
│ │   open3d, trimesh, pyvista, pyvistaqt                  │ │
│ │                                                         │ │
│ │ Custom Package List:                                    │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ textual>=0.50.0                                     │ │ │
│ │ │ typer[all]                                          │ │ │
│ │ │ pydantic>2.0                                        │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │                                                         │ │
│ │ [Validate Packages] [Estimate Install Time] [Preview]  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Installation Scripts ───────────────────────────────────┐ │
│ │                                                         │ │
│ │ Generated Scripts (automatically added to custom hooks):│ │
│ │ • on_first_run: install-pixi.bash                       │ │
│ │ • on_first_run: set-pixi-repo-tuna.bash                 │ │
│ │ • on_first_run: create-env-common.bash                  │ │
│ │ • on_first_run: create-env-ml.bash                      │ │
│ │                                                         │ │
│ │ Execution Order: [1] [2] [3] [4]                        │ │
│ │                                                         │ │
│ │ [View Scripts] [Customize Order] [Add Manual Scripts]   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back: Storage] [Next: AI/ML] [Test Pixi] [Save Section]   │
╰─────────────────────────────────────────────────────────────╯
```

**Advanced Features:**
- **Installation Strategy**: Choose between persistent vs baked-in installation
- **Repository Mirrors**: Geographic optimization for package downloads
- **Environment Templates**: Pre-configured package sets for different use cases
- **Script Generation**: Automatic creation of installation scripts

### 12. AI/ML Framework Configuration

**Layout:**
```
╭─ Stage-2: AI/ML Framework Configuration ──────────────────╮
│                                                             │
│ ┌─ Framework Selection ────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Primary AI/ML Framework:                                │ │
│ │ ● PyTorch  ○ TensorFlow  ○ JAX  ○ None                  │ │
│ │                                                         │ │
│ │ Additional Frameworks:                                  │ │
│ │ ☑ Hugging Face Transformers                             │ │
│ │ ☑ OpenCV (Computer Vision)                              │ │
│ │ ☐ Scikit-learn (Classical ML)                           │ │
│ │ ☑ Open3D (3D Processing)                                │ │
│ │ ☐ RAPIDS (GPU-accelerated data science)                 │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ PyTorch Configuration ──────────────────────────────────┐ │
│ │                                                         │ │
│ │ PyTorch Version: [2.1.2 ▼] (Latest Stable)             │ │
│ │                                                         │ │
│ │ CUDA Support: ● Auto-detect  ○ CUDA 11.8  ○ CUDA 12.1  │ │
│ │              ○ CPU Only                                 │ │
│ │                                                         │ │
│ │ Detected Configuration:                                 │ │
│ │ ✓ NVIDIA GPU detected (GTX 4090)                        │ │
│ │ ✓ CUDA 12.1 compatible                                  │ │
│ │ ✓ PyTorch 2.1.2+cu121 will be installed                │ │
│ │                                                         │ │
│ │ Additional PyTorch Packages:                            │ │
│ │ ☑ torchvision (Computer Vision)                         │ │
│ │ ☑ torchaudio (Audio Processing)                         │ │
│ │ ☐ torchtext (NLP)                                       │ │
│ │ ☑ pytorch-lightning (Training Framework)                │ │
│ │                                                         │ │
│ │ [Test CUDA] [Benchmark GPU] [Check Compatibility]       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Model and Data Management ──────────────────────────────┐ │
│ │                                                         │ │
│ │ Model Storage Location:                                 │ │
│ │ ● /models (dedicated mount) - 50GB limit                │ │
│ │ ○ /soft/data/models (in data volume)                    │ │
│ │ ○ ~/.cache/huggingface (user cache)                     │ │
│ │                                                         │ │
│ │ Hugging Face Configuration:                             │ │
│ │ ☑ Pre-download common models during build               │ │
│ │ ☑ Configure model cache location                        │ │
│ │ ☐ Use offline mode (no internet during runtime)        │ │
│ │                                                         │ │
│ │ Pre-download Models:                                    │ │
│ │ ☑ bert-base-uncased (text classification)               │ │
│ │ ☐ gpt2 (text generation)                                │ │
│ │ ☑ clip-vit-base-patch32 (vision-language)               │ │
│ │ ☐ whisper-base (speech recognition)                     │ │
│ │                                                         │ │
│ │ Estimated Download Size: ~2.1GB                         │ │
│ │ [Customize Models] [Check Sizes] [Preview Downloads]    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Development Tools ──────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Jupyter Environment:                                    │ │
│ │ ☑ JupyterLab (modern interface)                         │ │
│ │ ☐ Jupyter Notebook (classic)                            │ │
│ │ ☑ JupyterLab extensions (Git, LSP, etc.)                │ │
│ │                                                         │ │
│ │ Visualization Tools:                                    │ │
│ │ ☑ Matplotlib, Seaborn (plotting)                        │ │
│ │ ☑ Plotly (interactive plots)                            │ │
│ │ ☑ Weights & Biases (experiment tracking)                │ │
│ │ ☐ TensorBoard (PyTorch/TF visualization)                │ │
│ │                                                         │ │
│ │ Development Utilities:                                  │ │
│ │ ☑ Black (code formatting)                               │ │
│ │ ☑ Pytest (testing framework)                            │ │
│ │ ☑ Pre-commit hooks                                      │ │
│ │ ☑ GPU monitoring tools (nvidia-smi, gpustat)            │ │
│ │                                                         │ │
│ │ [Preview Environment] [Generate Requirements]           │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back: Pixi] [Next: ROS2] [Test GPU] [Save Section]        │
╰─────────────────────────────────────────────────────────────╯
```

**Advanced Features:**
- **Hardware Detection**: Attempt to detect GPU capabilities and suggest configurations
- **Model Management**: Configure model storage and pre-download common models
- **Framework Integration**: Intelligent dependency resolution between frameworks
- **Development Environment**: Complete ML development toolchain setup

### 13. YAML Editor Interface

**Layout:**
```
╭─ Direct YAML Configuration Editor ────────────────────────╮
│                                                             │
│ ┌─ Editor Controls ────────────────────────────────────────┐ │
│ │ [Load] [Save] [Validate] [Format] [Undo] [Redo] [Find]  │ │
│ │                                                         │ │
│ │ Validation: ✓ Valid  │  Line: 45  │  Col: 12  │  Size: 2.1KB │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Configuration File (user_config.yml) ──────────────────┐ │
│ │                                                         │ │
│ │   1│ # PeiDocker Configuration                          │ │
│ │   2│ # Generated by PeiDocker GUI Advanced Mode        │ │
│ │   3│ # Date: 2024-07-23 14:30:00                       │ │
│ │   4│                                                   │ │
│ │   5│ stage_1:                                          │ │
│ │   6│   image:                                          │ │
│ │   7│     base: ubuntu:24.04                            │ │
│ │   8│     output: my-project:stage-1                    │ │
│ │   9│                                                   │ │
│ │  10│   ssh:                                            │ │
│ │  11│     enable: true                                  │ │
│ │  12│     port: 22                                      │ │
│ │  13│     host_port: 2222                               │ │
│ │  14│     users:                                        │ │
│ │  15│       me:                                         │ │
│ │  16│         password: '******'                        │ │
│ │  17│         uid: 1100                                 │ │
│ │  18│         pubkey_text: null                         │ │
│ │  19│         privkey_file: null                        │ │
│ │  20│       root:                                       │ │
│ │  21│         password: 'root123'                       │ │
│ │  22│                                                   │ │
│ │  23│   proxy:                                          │ │
│ │  24│     enable: false                                 │ │
│ │  25│                                                   │ │
│ │  26│   apt:                                            │ │
│ │  27│     repo_source: tuna                             │ │
│ │  28│                                                   │ │
│ │  29│   ports:                                          │ │
│ │  30│     - "8080:80"                                   │ │
│ │  31│     - "3000-3010:3000-3010"                       │ │
│ │  32│                                                   │ │
│ │  33│   environment:                                    │ │
│ │  34│     - "NODE_ENV=production"                       │ │
│ │  35│     - "DEBUG=false"                               │ │
│ │  36│                                                   │ │
│ │  37│   device:                                         │ │
│ │  38│     type: gpu                                     │ │
│ │  39│                                                   │ │
│ │  40│   mount:                                          │ │
│ │  41│     models:                                       │ │
│ │  42│       type: auto-volume                           │ │
│ │  43│       dst_path: /models                           │ │
│ │  44│                                                   │ │
│ │█45│   custom: ▌                                       │ │
│ │  46│     on_build:                                     │ │
│ │  47│       - stage-1/custom/install-deps.sh           │ │
│ │  48│       - stage-1/system/setup-nginx.sh            │ │
│ │  49│                                                   │ │
│ │  50│ stage_2:                                          │ │
│ │                                                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Context Help & Validation ──────────────────────────────┐ │
│ │                                                         │ │
│ │ Current Context: stage_1.custom.on_build                │ │
│ │                                                         │ │
│ │ Field Description:                                      │ │
│ │ Custom scripts executed during Stage-1 build process.  │ │
│ │ Scripts run as root user with full system access.      │ │
│ │                                                         │ │
│ │ Validation Issues:                                      │ │
│ │ • Line 45: Missing value after 'custom:'              │ │
│ │ • Line 47: Script file does not exist                  │ │
│ │                                                         │ │
│ │ Suggestions:                                            │ │
│ │ • Press Ctrl+Space for auto-completion                 │ │
│ │ • Use Tab for proper indentation                       │ │
│ │                                                         │ │
│ │ [Fix Issues] [Show Examples] [Import Template]         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back to Forms] [Save & Exit] [Validate & Build] [Help]    │
╰─────────────────────────────────────────────────────────────╯
```

**Advanced Editor Features:**
- **Syntax Highlighting**: YAML syntax highlighting with error indicators
- **Auto-completion**: Context-aware suggestions for configuration keys
- **Real-time Validation**: Immediate feedback on configuration errors
- **Context Help**: Dynamic help based on cursor position
- **Search & Replace**: Find and replace functionality across the file

### 14. Template Management Interface

**Layout:**
```
╭─ Configuration Templates ─────────────────────────────────╮
│                                                             │
│ ┌─ Template Categories ────────────────────────────────────┐ │
│ │ [●Built-in] [○User] [○Shared] [○Import] [○Export]       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Built-in Templates ─────────────────────────────────────┐ │
│ │                                                         │ │
│ │ ┌─ Web Development ──────────────────────────────────┐   │ │
│ │ │ Node.js + Express Development Environment           │   │ │
│ │ │ • Base: node:18-alpine                             │   │ │
│ │ │ • Includes: npm, yarn, nodemon, pm2                │   │ │
│ │ │ • Ports: 3000, 3001 (dev server, debug)           │   │ │
│ │ │ • Storage: Auto-volumes for code and data          │   │ │
│ │ │                                       [Use Template] │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ │                                                         │ │
│ │ ┌─ Machine Learning ─────────────────────────────────┐   │ │
│ │ │ PyTorch + CUDA Development Environment             │   │ │
│ │ │ • Base: nvidia/cuda:12.1-cudnn8-devel-ubuntu22.04  │   │ │
│ │ │ • Includes: PyTorch, Jupyter, OpenCV, Weights&Biases │   │ │
│ │ │ • GPU: Full NVIDIA support enabled                 │   │ │
│ │ │ • Storage: Large model volume (100GB)              │   │ │
│ │ │                                       [Use Template] │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ │                                                         │ │
│ │ ┌─ Data Science ─────────────────────────────────────┐   │ │
│ │ │ Python Data Science with Jupyter                   │   │ │
│ │ │ • Base: python:3.11-slim                           │   │ │
│ │ │ • Includes: Pandas, NumPy, Matplotlib, Seaborn     │   │ │
│ │ │ • Jupyter: Lab + Notebook with extensions          │   │ │
│ │ │ • Storage: Persistent notebooks and datasets       │   │ │
│ │ │                                       [Use Template] │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ │                                                         │ │
│ │ ┌─ Robotics Development ─────────────────────────────┐   │ │
│ │ │ ROS2 Humble Development Environment                │   │ │
│ │ │ • Base: ros:humble-desktop                         │   │ │
│ │ │ • Includes: ROS2 tools, Gazebo, RViz              │   │ │
│ │ │ • Display: X11 forwarding for GUI apps            │   │ │
│ │ │ • Storage: Workspace and simulation files          │   │ │
│ │ │                                       [Use Template] │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ │                                                         │ │
│ │ ┌─ Database Development ─────────────────────────────┐   │ │
│ │ │ Full Stack Database Development                    │   │ │
│ │ │ • Base: ubuntu:22.04                               │   │ │
│ │ │ • Includes: PostgreSQL, Redis, pgAdmin            │   │ │
│ │ │ • Ports: 5432 (Postgres), 6379 (Redis), 8080 (Web) │   │ │
│ │ │ • Storage: Persistent database volumes             │   │ │
│ │ │                                       [Use Template] │   │ │
│ │ └─────────────────────────────────────────────────────┘   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Template Preview ───────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Selected: Machine Learning Template                     │ │
│ │                                                         │ │
│ │ This template will configure:                           │ │
│ │ ✓ NVIDIA CUDA 12.1 development environment             │ │
│ │ ✓ PyTorch 2.1.2 with GPU support                       │ │
│ │ ✓ JupyterLab with ML extensions                         │ │
│ │ ✓ Common ML libraries (OpenCV, scikit-learn, etc.)     │ │
│ │ ✓ Model storage volume (100GB limit)                   │ │
│ │ ✓ Weights & Biases integration                          │ │
│ │ ✓ SSH access with GPU monitoring tools                  │ │
│ │                                                         │ │
│ │ Estimated Build Time: 15-20 minutes                    │ │
│ │ Estimated Image Size: 8.5GB                            │ │
│ │                                                         │ │
│ │ Override Settings:                                      │ │
│ │ ☑ Keep current project name                             │ │
│ │ ☑ Keep current SSH configuration                        │ │
│ │ ☐ Merge with existing configuration                     │ │
│ │ ☑ Replace entire configuration                          │ │
│ │                                                         │ │
│ │ [Apply Template] [Customize First] [View YAML]         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back to Config] [Save as Template] [Share Template] [Help]│
╰─────────────────────────────────────────────────────────────╯
```

**Template Features:**
- **Categorized Templates**: Organized by use case for easy discovery
- **Template Preview**: Show what will be configured before applying
- **Merge Options**: Choose how to apply templates to existing configurations
- **Custom Templates**: Save and share user-created configurations

### 15. Build Monitor Interface

**Layout:**
```
╭─ Docker Build Monitor ────────────────────────────────────╮
│                                                             │
│ ┌─ Build Progress ─────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Building: my-project:stage-1                            │ │
│ │ Started: 14:35:20  │  Elapsed: 02:15  │  ETA: 03:45     │ │
│ │                                                         │ │
│ │ Progress: ████████████████░░░░░░░░ 65% (13/20 steps)    │ │
│ │                                                         │ │
│ │ Current Step: Installing Python packages               │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ Step 13/20: RUN pip install -r requirements.txt    │ │ │
│ │ │ ████████████████████████████████████████░░░░░░░░ 80% │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Build Log ──────────────────────────────────────────────┐ │
│ │                                                         │ │
│ │ [Info] [Warnings] [Errors] [●All] | [Clear] [Export]    │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ [14:35:20] Step 1/20: FROM ubuntu:24.04            │ │ │
│ │ │ [14:35:21] ---> Using cache a1b2c3d4e5f6            │ │ │
│ │ │ [14:35:21] Step 2/20: RUN apt-get update            │ │ │
│ │ │ [14:35:22] ---> Running in temp-container-id        │ │ │
│ │ │ [14:35:25] Get:1 http://archive.ubuntu.com...       │ │ │
│ │ │ [14:35:28] Reading package lists... Done            │ │ │
│ │ │ [14:35:28] ---> b2c3d4e5f6g7                        │ │ │
│ │ │ [14:35:29] Step 3/20: RUN apt-get install...        │ │ │
│ │ │ [14:35:30] ---> Running in temp-container-id2       │ │ │
│ │ │ [14:35:33] Reading package lists... Done            │ │ │
│ │ │ [14:35:35] ⚠  Warning: Package xyz has no candidate │ │ │
│ │ │ [14:35:40] The following NEW packages will be...    │ │ │
│ │ │ [14:37:10] ● Currently installing: tensorflow==2.13 │ │ │
│ │ │ [14:37:15] Processing dependencies... (15/47)       │ │ │
│ │ │ [14:37:20] Downloading package data... (256/400 MB) │ │ │
│ │ │                                                     │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Build Statistics ───────────────────────────────────────┐ │
│ │                                                         │ │
│ │ Image Layers: 13 created, 7 cached                     │ │
│ │ Download Size: 1.2GB  │  Compressed: 450MB             │ │
│ │ Build Context: 15MB   │  Final Size: 3.8GB             │ │
│ │                                                         │ │
│ │ Network Usage: ▲ 15MB/s ▼ 45MB/s                       │ │
│ │ Disk Usage: 📁 2.1GB temporary, 🗂️ 3.8GB final        │ │
│ │ CPU Usage: ████████░░░░ 67%                             │ │
│ │ Memory Usage: ██████░░░░░░ 2.4GB / 8GB                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ Build Control ──────────────────────────────────────────┐ │
│ │ [Pause Build] [Cancel Build] [Build Stage-2 Next]      │ │
│ │                                                         │ │
│ │ Auto Actions:                                           │ │
│ │ ☑ Start Stage-2 build when Stage-1 completes           │ │
│ │ ☑ Test SSH connection after build                       │ │
│ │ ☐ Push image to registry after successful build        │ │
│ │ ☑ Clean up intermediate containers                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Back to Config] [Open Container] [View Images] [Help]     │
╰─────────────────────────────────────────────────────────────╯
```

**Advanced Build Features:**
- **Real-time Progress**: Live build progress with step-by-step tracking
- **Resource Monitoring**: CPU, memory, network, and disk usage during build
- **Log Filtering**: Filter logs by severity level or content
- **Build Statistics**: Detailed metrics about image size, layers, and performance
- **Auto Actions**: Configurable post-build actions

## Key Features & Advanced Behaviors

### Navigation & Usability
- **Persistent State**: Remember user choices across sessions
- **Multi-level Undo**: Comprehensive undo/redo system
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Context-sensitive Help**: Dynamic help based on current section
- **Configuration Comparison**: Compare current vs saved configurations

### Validation & Error Handling
- **Real-time Validation**: Continuous validation with immediate feedback
- **Cross-section Validation**: Check compatibility between different sections
- **Dependency Resolution**: Automatic detection and resolution of package conflicts
- **Resource Estimation**: Predict build time and resource requirements
- **Conflict Detection**: Port, mount point, and naming conflicts

### Advanced Configuration Features
- **Template System**: Save, load, and share configuration templates
- **Environment Variable Substitution**: Support for Docker Compose-style variables
- **Conditional Configuration**: Show/hide options based on other selections
- **Bulk Operations**: Apply changes to multiple items simultaneously
- **Configuration Versioning**: Track and revert configuration changes

### Integration & Automation
- **Docker Integration**: Direct interaction with Docker daemon
- **Build Monitoring**: Real-time build progress and resource monitoring
- **SSH Testing**: Test SSH connectivity during configuration
- **Git Integration**: Track configuration changes in version control
- **CI/CD Integration**: Export configurations for automation pipelines

### Performance & Scalability
- **Lazy Loading**: Load configuration sections on demand
- **Background Validation**: Non-blocking validation processes
- **Caching**: Cache validation results and Docker Hub queries
- **Responsive UI**: Adaptive interface based on terminal size
- **Memory Efficiency**: Optimized for long-running sessions

## Technical Implementation Notes

### State Management
- **Reactive State**: Use Textual's reactive variables for state management
- **Configuration Model**: Type-safe data models with validation
- **Change Tracking**: Track all configuration changes for undo/redo
- **Auto-save**: Configurable automatic saving of changes

### UI Components
- **Custom Widgets**: Advanced form controls and validation widgets
- **Layout Management**: Responsive layouts that adapt to content
- **Theme System**: Consistent visual theming across all screens
- **Accessibility**: Full keyboard navigation and screen reader support

### Docker Integration
- **Docker API**: Direct integration with Docker Engine API
- **Image Management**: Query and manipulate Docker images
- **Container Operations**: Start, stop, and inspect containers
- **Build Streaming**: Real-time build log streaming and progress tracking

This advanced mode design provides comprehensive control over all PeiDocker features while maintaining usability through intelligent organization, validation, and helpful guidance throughout the configuration process.