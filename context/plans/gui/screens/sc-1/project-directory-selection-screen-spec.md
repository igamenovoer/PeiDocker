# Screen 1: Project Directory Selection Screen - Technical Specification

## Overview

**Screen ID:** `SC-1`  
**Screen Name:** Project Directory Selection Screen  
**Purpose:** Project location setup and Docker image naming configuration  
**File Location:** `src/pei_docker/gui/screens/project_setup.py`  
**Flow Position:** Second screen after Application Startup (SC-0), before Simple Wizard Controller (SC-2)  
**Figures Directory:** `figures/sc1/` (contains generated UML diagrams)

## Functional Requirements

### Primary Objectives
1. **Directory Selection**: Allow user to select or create project directory
2. **Project Naming**: Generate and validate project name for Docker images (no default value)
3. **Path Validation**: Ensure directory path is valid and accessible
4. **Docker Image Preview**: Show resulting Docker image names
5. **Project Directory Creation**: Create the project directory structure for use by subsequent screens

### Use Cases

![Use Cases Diagram](figures/sc1/use-cases.svg)

<details>
<summary>PlantUML Source</summary>

```plantuml
@startuml
left to right direction
actor "User" as user
actor "File System" as fs
actor "Docker System" as docker

rectangle "Project Directory Selection Screen" {
  usecase "Select Project Directory" as UC1
  usecase "Enter Project Name" as UC2
  usecase "Browse for Directory" as UC3
  usecase "Validate Directory Path" as UC4
  usecase "Create Project Directory" as UC5
  usecase "Check Docker Images" as UC6
  usecase "Preview Image Names" as UC7
}

user --> UC1
user --> UC2
user --> UC3
UC1 --> UC4 : <<include>>
UC4 --> UC5 : <<extend>>
UC2 --> UC7 : <<include>>
UC6 --> docker
UC4 --> fs
UC5 --> fs
@enduml
```
</details>

### Navigation Options
- **Back Button**: Return to Application Startup Screen (SC-0)
- **Continue Button**: Proceed to Simple Wizard Controller (SC-2)
- **Browse Button**: Open directory selection dialog
- **Keyboard Controls**: 'b' for back, Enter to continue

## User Interface Specification

### Layout Structure
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

### Status Display Examples

#### Standard Configuration
```
Project Directory:
┌─────────────────────────────────────────────────────────────┐
│ D:\code\my-project                                          │
└─────────────────────────────────────────────────────────────┘
                             [Browse...]

⚠ Directory will be created if it doesn't exist

Project Name (for Docker images):
┌─────────────────────────────────────────────────────────────┐
│ my-project                                                  │
└─────────────────────────────────────────────────────────────┘

Docker images will be named:
• my-project:stage-1
• my-project:stage-2
```

#### Directory Already Exists
```
Project Directory:
┌─────────────────────────────────────────────────────────────┐
│ D:\code\existing-project                                    │
└─────────────────────────────────────────────────────────────┘
                             [Browse...]

ℹ Directory already exists

Project Name (for Docker images):
┌─────────────────────────────────────────────────────────────┐
│ existing-project                                            │
└─────────────────────────────────────────────────────────────┘

Docker images will be named:
• existing-project:stage-1
• existing-project:stage-2
```


#### Invalid Project Name
```
Project Directory:
┌─────────────────────────────────────────────────────────────┐
│ D:\code\my project with spaces                              │
└─────────────────────────────────────────────────────────────┘
                             [Browse...]

⚠ Directory will be created if it doesn't exist

Project Name (for Docker images):
┌─────────────────────────────────────────────────────────────┐
│ my project with spaces                                      │
└─────────────────────────────────────────────────────────────┘

❌ Invalid project name: 
   • No spaces allowed
   • Use letters, numbers, hyphens, and underscores only
   • Must start with letter
```

## Behavior Specifications

### Screen Initialization Activity

![Initialization Activity Diagram](figures/sc1/initialization-activity.svg)

<details>
<summary>PlantUML Source</summary>

```plantuml
@startuml
start
:Display screen;
if (CLI override provided?) then (yes)
  :Pre-fill directory path (grayed out);
  :Disable directory path input;
  :Disable browse button;
else (no)
  :Load default directory path;
  :Enable all controls;
endif
:Extract project name from path;
:Validate initial state;
stop
@enduml
```
</details>

### User Interaction Flow

![User Interaction Flow Diagram](figures/sc1/user-interaction-flow.svg)

<details>
<summary>PlantUML Source</summary>

```plantuml
@startuml
start
repeat
  :User enters directory path;
  fork
    :Validate path format;
    :Check permissions;
    :Show existence status;
  fork again
    :Auto-extract project name;
    :Validate project name;
    :Update Docker image preview;
  end fork
  if (Validation passes?) then (yes)
    :Enable Continue button;
  else (no)
    :Disable Continue button;
    :Show error messages;
  endif
  
  :Wait for user action;
  if (User clicks Browse?) then (yes)
    :Open directory dialog;
    :Update path field;
  else if (User clicks Back?) then (yes)
    :Navigate to SC-0;
    stop
  else if (User clicks Continue?) then (yes)
    :Create project directory;
    :Save state for next screens;
    :Navigate to SC-2;
    stop
  endif
repeat while (Continue editing?) is (yes)
@enduml
```
</details>

### Input Validation Rules

**Directory Path**: Non-empty, valid filesystem path, write permissions  
**Project Name**: Alphanumeric + hyphens + underscores, no spaces, 1-50 chars, starts with letter

### Navigation State Machine

![Navigation State Machine Diagram](figures/sc1/navigation-state-machine.svg)

<details>
<summary>PlantUML Source</summary>

```plantuml
@startuml
[*] --> ScreenLoading
ScreenLoading --> InputReady : initialization_complete
InputReady --> ValidatingInput : user_input_change
ValidatingInput --> InputValid : validation_success
ValidatingInput --> InputInvalid : validation_error
InputValid --> InputReady : user_continues_editing
InputInvalid --> InputReady : user_fixes_input
InputValid --> DirectoryCreating : continue_button_clicked
DirectoryCreating --> NavigatingNext : directory_created
DirectoryCreating --> InputInvalid : creation_failed
NavigatingNext --> [*] : navigate_to_sc2
InputReady --> NavigatingBack : back_button_clicked
NavigatingBack --> [*] : navigate_to_sc0

state InputValid {
  [*] --> ContinueEnabled
}

state InputInvalid {
  [*] --> ContinueDisabled
  [*] --> ErrorDisplayed
}
@enduml
```
</details>

### Error Handling States

![Error Handling States Diagram](figures/sc1/error-handling-states.svg)

<details>
<summary>PlantUML Source</summary>

```plantuml
@startuml
[*] --> NoError
NoError --> PathError : invalid_path_entered
NoError --> NameError : invalid_name_entered
NoError --> PermissionError : permission_check_failed
NoError --> CreationError : directory_creation_failed

PathError --> NoError : valid_path_entered
NameError --> NoError : valid_name_entered
PermissionError --> NoError : permission_granted
CreationError --> NoError : creation_successful
@enduml
```
</details>

### Command Line Override Behavior

**CLI Override (--project-dir or --here)**: Screen is displayed with directory input field pre-filled and grayed out (uneditable). Browse button is disabled. Project name is extracted from path and can be modified. 

CLI commands that trigger this behavior:
- `pei-docker-gui start --project-dir <path>`
- `pei-docker-gui start --here`
- `pei-docker-gui dev --project-dir <path>`
- `pei-docker-gui dev --here`

This specification provides comprehensive guidance for implementing the Project Directory Selection Screen as the second step in the PeiDocker GUI application workflow.