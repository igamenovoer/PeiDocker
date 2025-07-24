# Screen 1: Project Information - Technical Specification

## Overview

**Screen ID:** `SC-1`  
**Screen Name:** Project Information  
**Wizard Step:** 1 of 11  
**File Location:** `src/pei_docker/gui/screens/simple/project_info.py`  
**Purpose:** Collect basic project metadata required to generate Docker images and project structure

## Functional Requirements

### Primary Objectives
1. **Project Name Collection**: Capture user-defined project name for Docker image naming
2. **Base Image Selection**: Allow user to specify Docker base image with validation
3. **Image Conflict Detection**: Check for existing Docker images and warn user of potential overwrites
4. **Input Validation**: Ensure all inputs meet technical requirements before proceeding

### Input Fields

#### 1. Project Name (Required)
- **Field Type:** Text Input (required)
- **Default Value:** None (user must provide)
- **Validation Rules:**
  - Cannot be empty
  - Must be valid Docker image name format: `[a-z0-9]+(?:[._-][a-z0-9]+)*`
  - Length: 1-255 characters
  - No uppercase letters, spaces, or special characters except `-`, `_`, `.`
- **Example Values:** `my-awesome-project`, `web_app_v2`, `ml.pipeline`
- **Error Messages:**
  - Empty: "Project name is required"
  - Invalid format: "Project name must contain only lowercase letters, numbers, hyphens, underscores, and dots"
  - Too long: "Project name must be 255 characters or less"

#### 2. Base Docker Image (Optional)
- **Field Type:** Text Input with suggestions
- **Default Value:** `ubuntu:24.04`
- **Validation Rules:**
  - Must be valid Docker image tag format: `[registry/]repository[:tag]`
  - Optional Docker Hub existence check (non-blocking)
- **Common Suggestions:**
  - `ubuntu:24.04` (recommended)
  - `ubuntu:22.04`
  - `nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04`
  - `python:3.11-slim`
  - `node:18-alpine`
- **Validation Behavior:**
  - Real-time format validation
  - Async Docker Hub availability check (when possible)
  - Display ✓/⚠/❌ status indicator

## User Interface Specification

### Layout Structure
```
╭─ Project Information ──────────────────────── Step 1 of 11 ╮
│                                                             │
│  Basic project settings:                                    │
│                                                             │
│  Project Name: *                                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [user input]                                            │ │
│  └─────────────────────────────────────────────────────────┘ │
│  Images: [project-name]:stage-1, [project-name]:stage-2    │
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
│  [Status indicator area]                                    │
│                                                             │
│  [Prev] [Next]                                              │
│                                                             │
│  * Required field                                           │
╰─────────────────────────────────────────────────────────────╯
```

### Visual Elements

#### Progress Indicator
- **Location:** Top right of header
- **Format:** "Step 1 of 11"
- **Style:** Subtle, non-intrusive

#### Input Fields
- **Project Name Field:**
  - Width: Full width minus padding
  - Height: Single line
  - Required indicator: Red asterisk (*) 
  - Border: Focus highlighting
  - Placeholder: None (force user decision)

- **Base Image Field:**
  - Width: Full width minus padding  
  - Height: Single line
  - Default text: `ubuntu:24.04`
  - Border: Standard input styling

#### Dynamic Image Names Display
- **Location:** Below project name field
- **Format:** `Images: {project-name}:stage-1, {project-name}:stage-2`
- **Update Behavior:** Real-time as user types project name
- **Style:** Muted text, informational

#### Suggestions Section
- **Location:** Below base image field
- **Content:** Bulleted list of common base images
- **Interaction:** Click to populate base image field
- **Style:** Smaller font, clickable links

#### Status Indicators
- **Docker Image Status:**
  - ✓ Green: Image exists and accessible
  - ⚠ Yellow: Image format valid but existence unverified
  - ❌ Red: Invalid image format or connection error
  - 🔄 Blue: Checking availability...

- **Project Name Conflicts:**
  - ⚠ Warning: "Docker images {name}:stage-1 and {name}:stage-2 already exist and will be overwritten"

### Navigation Controls

#### Button Layout
- **Position:** Bottom of screen, right-aligned
- **Buttons:** `[Prev] [Next]`
- **Prev Button:**
  - Always visible but disabled on first screen
  - Returns to previous wizard step or startup screen
- **Next Button:**
  - Enabled only when validation passes
  - Proceeds to SSH Configuration screen
  - Disabled states: Required fields empty, validation errors

#### Keyboard Navigation
- **Tab Order:** Project name → Base image → Prev button → Next button
- **Enter Key:** Submit form (same as Next button)
- **Escape Key:** 
  - Single: Clear current input field
  - Double: Return to main menu
  
## Data Model

### Screen State Structure
```python
@dataclass
class ProjectInfoState:
    project_name: str = ""
    base_image: str = "ubuntu:24.04"
    validation_errors: Dict[str, str] = field(default_factory=dict)
    docker_images_exist: Optional[bool] = None
    base_image_exists: Optional[bool] = None
    is_checking_images: bool = False
```

### Configuration Output
```yaml
# Generated in wizard memory state
project:
  name: "{project_name}"
  base_image: "{base_image}"
  
# Docker images that will be created:
# - {project_name}:stage-1  
# - {project_name}:stage-2
```

## Validation Logic

### Real-time Validation
```python
def validate_project_name(name: str) -> List[str]:
    errors = []
    if not name:
        errors.append("Project name is required")
    elif not re.match(r'^[a-z0-9]+(?:[._-][a-z0-9]+)*$', name):
        errors.append("Invalid project name format")
    elif len(name) > 255:
        errors.append("Project name too long")
    return errors

def validate_base_image(image: str) -> List[str]:
    errors = []
    if not re.match(r'^[a-z0-9._-]+(?:/[a-z0-9._-]+)*(?::[a-z0-9._-]+)?$', image):
        errors.append("Invalid Docker image format")
    return errors
```

### Navigation Validation
```python
def can_proceed_to_next() -> bool:
    return (
        bool(self.project_name) and
        not self.validation_errors and
        not self.is_checking_images
    )
```

## Behavior Specifications

### Form Interactions

#### Project Name Input
1. **On Focus:** Clear any previous validation errors
2. **On Change:** 
   - Update dynamic image names display
   - Run real-time validation
   - Clear "images exist" status
3. **On Blur:** Trigger Docker image existence check (async)

#### Base Image Input  
1. **On Change:** Run format validation, clear existence status
2. **On Blur:** Trigger Docker Hub existence check (async, non-blocking)
3. **Suggestion Click:** Populate field with clicked suggestion

#### Docker Integration
1. **Image Existence Check:**
   ```bash
   docker images --format "table {{.Repository}}:{{.Tag}}" | grep "^{project_name}:"
   ```
2. **Base Image Check:**
   ```bash
   docker manifest inspect {base_image} 2>/dev/null
   ```
3. **Timeout:** 5 seconds for network operations
4. **Error Handling:** Show warning but don't block progression

### State Transitions

#### Entry State
- Auto-populate project name from directory name (if available)
- Set default base image
- Start with clean validation state

#### Exit Conditions
- **To Next Screen:** All validation passes, user clicks Next
- **To Previous Screen:** User clicks Prev (navigate to startup or project selection)
- **To Main Menu:** User presses Escape twice

### Error Handling

#### Network Errors
- **Docker Unavailable:** Show warning, continue with local validation only
- **Docker Hub Timeout:** Show "Unable to verify" message, don't block progress
- **Invalid Network Response:** Graceful fallback to format-only validation

#### Input Errors  
- **Invalid Characters:** Real-time error display with specific guidance
- **Empty Required Fields:** Disable Next button, show requirement message
- **Conflicting Images:** Warning message but allow continuation

## Implementation Requirements

### Dependencies
```python
# Required imports
from textual.screen import Screen
from textual.widgets import Input, Static, Button
from textual.validation import Validator
from textual.reactive import reactive
import docker
import asyncio
import re
```

### Key Methods
```python
class ProjectInfoScreen(Screen):
    project_name = reactive("")
    base_image = reactive("ubuntu:24.04")
    
    async def on_input_changed(self, event)
    def validate_inputs(self) -> bool
    async def check_docker_images_exist(self) -> None
    async def check_base_image_exists(self) -> None
    def generate_config_data(self) -> dict
```

### Configuration Integration
- Store all inputs in wizard memory state
- Generate partial `user_config.yml` structure
- Pass state to next screen in wizard flow

### Docker Integration Points
- Docker client initialization with error handling
- Async image existence checking
- Docker Hub API calls (when available)
- Graceful degradation when Docker unavailable

## Testing Requirements

### Unit Tests
- Input validation logic
- Docker image name generation
- State management and transitions
- Error handling scenarios

### Integration Tests  
- Docker availability checking
- Network connectivity handling
- Cross-platform path handling
- Screen-to-screen state passing

### User Acceptance Criteria
1. ✅ User can enter valid project names
2. ✅ Invalid project names show clear error messages
3. ✅ Base image suggestions are clickable and functional
4. ✅ Docker image conflicts are detected and warned
5. ✅ Navigation is disabled when validation fails
6. ✅ Screen works with and without Docker available
7. ✅ All keyboard navigation functions correctly
8. ✅ Double-escape returns to main menu from any state

## Accessibility Requirements

### Keyboard Navigation
- Full keyboard accessibility with logical tab order
- Enter key submits form
- Escape key behavior clearly defined

### Screen Reader Support
- Proper labeling of all form elements
- Status announcements for validation errors
- Progress indicator accessibility

### Visual Accessibility  
- High contrast validation indicators
- Color-blind friendly status symbols
- Scalable text and interface elements

## Performance Requirements

### Response Times
- **Input Validation:** < 100ms for real-time feedback
- **Docker Image Check:** < 5s with timeout
- **Screen Transitions:** < 200ms between screens

### Resource Usage
- **Memory:** Minimal state storage, cleanup on exit
- **Network:** Optional background checks, non-blocking UI
- **CPU:** Efficient validation algorithms

This specification provides the foundation for implementing Screen 1 of the PeiDocker GUI wizard, ensuring a robust, user-friendly, and technically sound project information collection interface.