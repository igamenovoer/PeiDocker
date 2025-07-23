# Code Check Report

**Title**: Code Check Report  
**Date**: July 24, 2025  
**Status**: Critical Error Found  

## Description of Symptoms

The PeiDocker GUI application crashes with a `TypeError: 'ProjectConfig' object is not iterable` when navigating to the Port Mapping configuration screen in the wizard. The error occurs at line 219 in `port_mapping.py` within the `_update_port_list()` method when attempting to iterate over `self.current_mappings`.

## Problems Found

### 1. Constructor Parameter Mismatch (Critical)
**Location**: `/Users/igame/code/PeiDocker/src/pei_docker/gui/screens/simple/port_mapping.py:80`

**Issue**: The `PortMappingScreen` constructor signature is inconsistent with other wizard screens:

```python
def __init__(self, current_mappings: list[str] = None, ssh_port: str = "2222:22"):
    super().__init__()
    self.current_mappings = current_mappings or []
    self.ssh_port = ssh_port
```

However, the wizard instantiates all screens with a `ProjectConfig` object:
```python
# From wizard.py line 194
self.step_screens[self.current_step] = step.screen_class(self.project_config)
```

This causes `self.current_mappings` to be assigned a `ProjectConfig` object instead of a list, leading to the iteration error.

### 2. Inconsistent Screen Constructor Pattern
**Comparison with working screens**:
- `SSHConfigScreen`: `def __init__(self, project_config: ProjectConfig)`
- `ProjectInfoScreen`: `def __init__(self, project_config: ProjectConfig)`
- `PortMappingScreen`: `def __init__(self, current_mappings: list[str] = None, ssh_port: str = "2222:22")` ❌

### 3. Missing Configuration Data Extraction
The `PortMappingScreen` doesn't follow the established pattern of extracting needed configuration data from the `ProjectConfig` object like other screens do.

## Suggestions for Improvement/Bugfix

### 1. Fix Constructor Signature (Required)
Update `PortMappingScreen.__init__()` to match the pattern used by other wizard screens:

```python
def __init__(self, project_config: ProjectConfig):
    super().__init__()
    self.project_config = project_config
    
    # Extract current mappings from project config
    self.current_mappings = project_config.stage_1.ports or []
    
    # Extract SSH port configuration
    ssh_config = project_config.stage_1.ssh
    if ssh_config.enable:
        self.ssh_port = f"{ssh_config.host_port}:{ssh_config.port}"
    else:
        self.ssh_port = "2222:22"  # Default fallback
```

### 2. Add Configuration Persistence
Implement methods to save port mapping changes back to the project configuration:

```python
def save_configuration(self) -> None:
    """Save current port mappings to project configuration."""
    self.project_config.stage_1.ports = self.current_mappings.copy()
```

### 3. Follow Textual Screen Constructor Best Practices
According to Textual documentation, screens should have simple constructors that accept configuration data and store it for later use. The current pattern in other screens follows this correctly by accepting a `ProjectConfig` object and extracting needed data.

### 4. Add Validation
Consider adding validation for port mapping format consistency with other screens in the wizard.

## Root Cause Analysis
This appears to be a refactoring oversight where the `PortMappingScreen` was not updated when the wizard infrastructure was changed to pass `ProjectConfig` objects to all screen constructors. All other screens follow the correct pattern, making this an isolated issue.

## Impact Assessment
- **Severity**: Critical - Application crashes when accessing port mapping configuration
- **Scope**: Limited to port mapping functionality in the GUI wizard
- **User Experience**: Complete failure of port mapping configuration workflow

## Testing Recommendations
After fixing the constructor:
1. Test navigation to the port mapping screen
2. Test adding/removing port mappings
3. Test configuration persistence across wizard steps
4. Verify integration with the final configuration output
