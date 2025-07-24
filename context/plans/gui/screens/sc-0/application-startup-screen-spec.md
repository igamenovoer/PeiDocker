# Screen 0: Application Startup Screen - Technical Specification

## Overview

**Screen ID:** `SC-0`  
**Screen Name:** Application Startup Screen  
**Purpose:** Initial application launch screen with system validation and branding  
**File Location:** `src/pei_docker/gui/screens/startup.py`  
**Flow Position:** Entry point for GUI application

## Functional Requirements

### Primary Objectives
1. **Branding Display**: Show PeiDocker ASCII logo and application identity
2. **Status Reporting**: Display system component versions and availability
3. **User Onboarding**: Provide clear next steps and controls

### System Checks Required

#### 1. Docker Availability Check
- **Command:** `docker --version`
- **Success Criteria:** Command executes without error and returns version
- **Error Handling:** Show warning but allow continuation
- **Display Format:** `Docker: Available (version X.X.X)` or `Docker: Not found`

#### 2. Python Version Check
- **Source:** `sys.version_info`
- **Success Criteria:** Python 3.11+ detected
- **Display Format:** `Python: X.X.X`

#### 3. PeiDocker Version Check
- **Source:** Package metadata or version file
- **Display Format:** `PeiDocker: X.X.X`

#### 4. Project Directory Validation (when CLI override provided)
- **Source:** Command line arguments:
  - `pei-docker-gui start --project-dir <path>`
  - `pei-docker-gui start --here`
  - `pei-docker-gui dev --project-dir <path>`
  - `pei-docker-gui dev --here`
- **Success Criteria:** Directory path is valid and accessible
- **Error Handling:** Show warning if directory doesn't exist, create if possible
- **Display Format:** `Project Directory: <path>` or `Project Directory: <path> (will be created)`

### Navigation Options
- **Continue Button**: Proceed to project directory selection (or directly to wizard if CLI override provided)
- **Quit Button**: Exit application
- **Keyboard Controls**: 'q' to quit, Enter to continue
- **Project Directory Display**: Show project directory path when CLI override provided

## User Interface Specification

### Layout Structure
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
│  │ Docker: Available (version 24.0.6)                     │ │
│  │ Python: 3.11.5                                         │ │
│  │ PeiDocker: 0.8.0                                       │ │
│  │ Project Directory: D:\code\my-project (existing)       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  [Continue] [Quit]                                          │
│                                                             │
│  Press 'q' to quit, Enter to continue                      │
╰─────────────────────────────────────────────────────────────╯
```

### Status Display Examples

#### All Systems Available (without CLI override)
```
┌─────────────────────────────────────────────────────────┐
│ Docker: Available (version 24.0.6)                     │
│ Python: 3.11.5                                         │
│ PeiDocker: 0.8.0                                       │
└─────────────────────────────────────────────────────────┘
```

#### Existing Project (with CLI override)
```
┌─────────────────────────────────────────────────────────┐
│ Docker: Available (version 24.0.6)                     │
│ Python: 3.11.5                                         │
│ PeiDocker: 0.8.0                                       │
│ Project Directory: D:\code\my-project (existing)       │
└─────────────────────────────────────────────────────────┘
```

#### New Project (with CLI override)
```
┌─────────────────────────────────────────────────────────┐
│ Docker: Available (version 24.0.6)                     │
│ Python: 3.11.5                                         │
│ PeiDocker: 0.8.0                                       │
│ Project Directory: D:\code\new-project (new)           │
└─────────────────────────────────────────────────────────┘
```

#### Config Load Error (with CLI override)
```
┌─────────────────────────────────────────────────────────┐
│ Docker: Available (version 24.0.6)                     │
│ Python: 3.11.5                                         │
│ PeiDocker: 0.8.0                                       │
│ Project Directory: D:\code\broken-proj (config load    │
│    failed - will recreate)                             │
└─────────────────────────────────────────────────────────┘
```

#### System Check in Progress
```
┌─────────────────────────────────────────────────────────┐
│ Checking system components...                           │
│                                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```


## Behavior Specifications

### Startup Sequence
1. **Screen Initialize:** Display logo and "Checking system components..."
2. **Process Command Line Args:** Check for CLI override arguments (--project-dir or --here)
3. **Run System Checks:** Execute all component checks concurrently (including project directory if provided)
4. **Update Display:** Show results as checks complete

5. **Enable Controls:** Activate Continue/Quit buttons
6. **Wait for User:** Accept user input

This specification provides guidance for implementing the Application Startup Screen as the entry point for the PeiDocker GUI application.