# PeiDocker GUI Testing Strategy

## Overview

This document outlines a focused testing strategy for the PeiDocker GUI based on functional requirements rather than implementation details. The strategy emphasizes **what to test**, **what inputs to provide**, and **what outcomes to expect**.

## Core Functionality Matrix

### 1. Application Lifecycle Testing

**What to Test**: Basic application startup, shutdown, and system integration
**Priority**: Critical

| Scenario | Input | Expected Outcome | Test Type |
|----------|-------|------------------|-----------|
| App startup without Docker | Launch `pei-docker-gui` | Warning about Docker unavailability, but GUI still functional | Integration |
| App startup with Docker | Launch with Docker available | Clean startup, Docker version displayed | Integration |
| App startup with project dir | `pei-docker-gui --project-dir ./test` | Skip directory selection, go to mode selection | Integration |
| App startup with invalid project dir | `pei-docker-gui --project-dir /invalid` | Error message, fallback to directory selection | Integration |
| App shutdown | Press 'q' or Ctrl+C | Clean shutdown, no hanging processes | Integration |

### 2. Simple Mode Wizard Testing

**What to Test**: 12-step wizard flow with validation at each step
**Priority**: Critical (main user workflow)

#### Step-by-Step Flow Testing

| Step | Input | Expected Outcome | Validation Points |
|------|-------|------------------|-------------------|
| Project Info | `name="test-project", base_image="ubuntu:24.04"` | Project name saved, Docker image validated | Name format, image existence |
| SSH Config | `enable=true, port=2222, user="testuser", password="pass123"` | SSH enabled, ports configured | Port conflicts, password format |
| SSH Keys | `pubkey_text="ssh-rsa AAAAB3...", privkey_file="~/.ssh/id_rsa"` | Keys configured, file validation | Key format, file existence |
| Proxy Config | `enable=true, port=8080, build_only=true` | Proxy environment vars set | Port validation, proxy reachability |
| APT Config | `mirror="tuna"` | APT sources updated | Mirror availability |
| Port Mapping | `mappings=["8080:80", "3000-3010:3000-3010"]` | Port forwards configured | Port conflicts, range validation |
| Environment | `vars=["NODE_ENV=production", "DEBUG=false"]` | Environment variables set | Key=value format |
| Device Config | `gpu=true` | GPU runtime enabled | GPU availability warning |
| Stage-1 Mounts | `type="auto-volume", dst="/app/data"` | Volume mounts configured | Path validation, type compatibility |
| Custom Scripts | `on_build=["./setup.sh --verbose"]` | Build scripts added | Script existence, permissions |
| Summary | Review all settings | Complete configuration displayed | All sections populated |
| Save | Save configuration | `user_config.yml` created in project dir | File creation, YAML validity |

#### Navigation Testing

| Action | Input | Expected Outcome |
|--------|-------|------------------|
| Forward navigation | Complete step, press Next | Move to next step, data saved |
| Backward navigation | Press Back | Return to previous step, data preserved |
| Skip optional step | Press Skip on optional step | Jump to next required step |
| Invalid step data | Submit incomplete/invalid data | Error message, remain on step |
| Cancel wizard | Press Cancel/Escape | Return to mode selection, data discarded |

### 3. Advanced Mode Testing

**What to Test**: Tabbed interface with comprehensive form editing
**Priority**: High

#### Form Validation Testing

| Section | Invalid Input | Expected Outcome |
|---------|---------------|------------------|
| Image Config | `base_image=""` | Error: "Base image required" |
| SSH Config | `port=70000` | Error: "Port must be 1-65535" |
| Network Config | `proxy_port="abc"` | Error: "Invalid port number" |
| Environment | `var="INVALID"` | Error: "Format must be KEY=value" |
| Storage | `mount_path="/invalid path"` | Error: "Invalid mount path" |

#### Tab Navigation Testing

| Action | Input | Expected Outcome |
|--------|-------|------------------|
| Switch between Stage-1/Stage-2 | Click tabs | Content changes, data preserved |
| Unsaved changes warning | Edit form, switch tabs | Warning about unsaved changes |
| Auto-save | Edit field, wait 5 seconds | Changes automatically saved |

### 4. Configuration Management Testing

**What to Test**: Save, load, validate, and export functionality
**Priority**: High

| Operation | Input | Expected Outcome |
|-----------|-------|------------------|
| Save valid config | Complete configuration | `user_config.yml` created, valid YAML structure |
| Save invalid config | Incomplete configuration | Validation errors, save blocked |
| Load existing config | Open project with `user_config.yml` | Configuration loaded into forms |
| Load corrupted config | Malformed YAML file | Error message, fallback to defaults |
| Export config | Working configuration | Downloadable YAML file |
| Import config | Valid external config file | Configuration imported, forms populated |

### 5. File System Integration Testing

**What to Test**: Project directory creation, file operations, path validation
**Priority**: High

| Operation | Input | Expected Outcome |
|-----------|-------|------------------|
| Create new project | Non-existent directory path | Directory created, template files copied |
| Open existing project | Existing PeiDocker project | Files loaded, configuration restored |
| Invalid permissions | Read-only directory | Error message, alternative suggested |
| SSH key selection | Browse for SSH key file | File path populated, key validated |
| Script file selection | Browse for build script | Script added to configuration |
| Template file copy | Copy project templates | All required files present in project |

### 6. Docker Integration Testing

**What to Test**: Docker command detection, image validation, build monitoring
**Priority**: Medium (functionality should work without Docker)

#### Docker Availability Testing

| Docker State | Expected Outcome |
|--------------|------------------|
| Docker available | Version displayed, full functionality |
| Docker unavailable | Warning shown, limited functionality |
| Docker permission denied | Error message, suggestions provided |

#### Image Validation Testing

| Image Input | Expected Outcome |
|-------------|------------------|
| `ubuntu:24.04` | Valid, exists on Docker Hub |
| `nonexistent:tag` | Warning: "Image not found" |
| `invalid@image#name` | Error: "Invalid image name format" |

### 7. Error Handling Testing

**What to Test**: Graceful error handling and user feedback
**Priority**: High

| Error Scenario | Expected Outcome |
|----------------|------------------|
| Network timeout | Retry option, graceful degradation |
| File permission error | Clear error message, alternative paths |
| Invalid input format | Field-specific error, correction hints |
| System resource exhaustion | Warning message, reduced functionality |
| Unexpected application crash | Error report, recovery options |

## Testing Methodology

### Test Data Strategy

**Valid Test Configurations**:
- Minimal: Basic project with SSH only
- Standard: Typical development environment with common options
- Complex: Full-featured configuration with all options enabled
- Edge Cases: Boundary values, special characters, unusual combinations

**Invalid Test Inputs**:
- Empty/null values for required fields
- Out-of-range numeric values
- Malformed strings (ports, environment variables, image names)
- Non-existent file paths
- Conflicting configurations

### Automated Test Execution

**Unit Testing Approach**:
```
Input: Project name "test-project"
Action: Validate project name
Expected: True (valid format)

Input: Project name "test project" (with space)
Action: Validate project name  
Expected: False (invalid format), Error: "No spaces allowed"
```

**Integration Testing Approach**:
```
Input: Complete simple mode wizard with valid data
Action: Execute full workflow
Expected: user_config.yml created with correct structure

Input: Navigate back/forward through wizard steps
Action: Test data persistence
Expected: All form data preserved across navigation
```

**End-to-End Testing Approach**:
```
Input: pei-docker-gui --project-dir ./test-project
Action: Complete configuration, save, and verify
Expected: Working PeiDocker project ready for docker build
```

### Mock Testing Strategy

**Docker Mocking**:
- Mock Docker availability check (available/unavailable states)
- Mock Docker image existence checks (exists/not found)
- Mock Docker build process (success/failure scenarios)

**File System Mocking**:
- Mock directory creation (success/permission denied)
- Mock file operations (read/write/copy scenarios)
- Mock SSH key file validation

**Network Mocking**:
- Mock proxy connectivity tests
- Mock Docker Hub image checks
- Mock mirror availability checks

### Performance Testing

**Responsiveness Testing**:
- UI response time < 100ms for form interactions
- Screen transitions < 500ms
- Configuration save < 2 seconds
- Large configuration load < 5 seconds

**Resource Usage Testing**:
- Memory usage < 100MB during normal operation
- CPU usage < 10% during idle
- Disk usage only for configuration files

## Test Environment Setup

### Required Dependencies
```bash
pip install pytest pytest-asyncio textual pytest-mock
```

### Test Data Preparation
- Sample project directories (valid/invalid)
- Test SSH keys (passwordless for automation)
- Sample configuration files (valid/corrupted)
- Mock Docker responses

### CI/CD Integration
- Run tests on code changes
- Test across different Python versions (3.11+)
- Test on different platforms (Windows, Linux, macOS)
- Generate test coverage reports

## Success Criteria

### Functional Requirements
- All core workflows complete successfully
- Error handling provides helpful feedback
- Configuration files are valid and usable
- No data loss during navigation/editing

### Quality Requirements
- 90%+ test coverage on core functionality
- Zero critical bugs in happy path scenarios
- Graceful degradation when external dependencies fail
- Consistent behavior across platforms

### User Experience Requirements
- Intuitive navigation without training
- Clear validation messages for invalid inputs
- Responsive interface (< 500ms interactions)
- No configuration corruption or data loss

This strategy focuses on verifying that the PeiDocker GUI correctly implements its core purpose: guiding users through creating valid Docker container configurations while preventing common mistakes and providing a smooth user experience.