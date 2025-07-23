# Code Check Report

**Title**: Code Check Report - Multiple Constructor Signature Mismatches  
**Date**: July 24, 2025  
**Status**: Multiple Critical Errors Found  

## Description of Symptoms

The PeiDocker GUI application crashes with `TypeError: 'ProjectConfig' object is not iterable` when navigating to multiple wizard screens including Environment Variables, APT Configuration, Proxy Configuration, Device Configuration, Mounts, Entry Point, and Custom Scripts. The error occurs when these screens attempt to iterate over configuration data that has been incorrectly assigned as a `ProjectConfig` object instead of the expected data types.

## Problems Found

### 1. Systemic Constructor Parameter Mismatch (Critical)
**Affected Files**: Multiple screens in `/Users/igame/code/PeiDocker/src/pei_docker/gui/screens/simple/`

**Issue**: Multiple wizard screens have inconsistent constructor signatures that don't match the wizard's instantiation pattern. The wizard passes `ProjectConfig` objects to all screen constructors, but many screens expect different parameter types.

**Problematic Screens**:
- `EnvironmentVariablesScreen`: expects `current_vars: list[str]` but receives `ProjectConfig`
- `APTConfigScreen`: expects `current_mirror: str` but receives `ProjectConfig`
- `ProxyConfigScreen`: expects `current_config: ProxyConfig` but receives `ProjectConfig`
- `DeviceConfigScreen`: expects `current_config: DeviceConfig` but receives `ProjectConfig`
- `MountsScreen`: expects `stage1_mounts: list[MountConfig], stage2_mounts: list[MountConfig]` but receives `ProjectConfig`
- `EntryPointScreen`: expects `stage1_entrypoint: str, stage2_entrypoint: str` but receives `ProjectConfig`
- `CustomScriptsScreen`: expects `stage1_scripts: Dict[str, List[str]], stage2_scripts: Dict[str, List[str]]` but receives `ProjectConfig`

**Working Screens** (correct pattern):
- `SSHConfigScreen`: `def __init__(self, project_config: ProjectConfig)` ✅
- `SummaryScreen`: `def __init__(self, project_config: ProjectConfig)` ✅
- `ProjectInfoScreen`: `def __init__(self, project_config: ProjectConfig)` ✅
- `PortMappingScreen`: `def __init__(self, project_config: ProjectConfig)` ✅ (apparently fixed)

### 2. Data Type Assignment Errors
When the wrong parameter type is passed to constructors, the following assignments occur:
- `self.current_vars = current_vars or []` → `self.current_vars = ProjectConfig` object
- `self.current_mirror = current_mirror or "default"` → `self.current_mirror = ProjectConfig` object
- Similar pattern for all affected screens

### 3. Runtime Iteration Failures
The misassigned data causes runtime errors when the code attempts operations expecting the correct data types:
- `for env_var in sorted(self.current_vars):` fails because `ProjectConfig` is not iterable
- Similar failures occur in all affected screens when they try to process their configuration data

### 4. Inconsistent Architecture Pattern
The codebase shows a mixed approach where some screens follow the correct pattern (accepting `ProjectConfig`) while others use an older pattern (accepting specific data types). This suggests incomplete refactoring.

## Suggestions for Improvement/Bugfix

### 1. Standardize Constructor Signatures (Required)
Update all problematic screens to follow the established pattern:

```python
def __init__(self, project_config: ProjectConfig):
    super().__init__()
    self.project_config = project_config
    
    # Extract needed data from project_config
    self.current_vars = project_config.stage_1.environment or []
    # ... other data extraction as needed
```

### 2. Implement Data Extraction Pattern
Each screen should extract only the data it needs from the `ProjectConfig`:

**EnvironmentVariablesScreen**:
```python
def __init__(self, project_config: ProjectConfig):
    super().__init__()
    self.project_config = project_config
    self.current_vars = project_config.stage_1.environment or []
```

**APTConfigScreen**:
```python
def __init__(self, project_config: ProjectConfig):
    super().__init__()
    self.project_config = project_config
    self.current_mirror = project_config.stage_1.apt_mirror or "default"
```

### 3. Add Configuration Persistence Methods
Each screen should implement methods to save changes back to the project configuration:

```python
def save_configuration(self) -> None:
    """Save current configuration to project config."""
    self.project_config.stage_1.environment = self.current_vars.copy()
```

### 4. Implement Validation and Error Handling
Add type checking and validation to prevent similar issues:

```python
def __init__(self, project_config: ProjectConfig):
    if not isinstance(project_config, ProjectConfig):
        raise TypeError(f"Expected ProjectConfig, got {type(project_config)}")
    # ... rest of initialization
```

### 5. Architectural Improvements

#### a) Create Base Screen Class
Consider creating a base wizard screen class:

```python
class BaseWizardScreen(Screen):
    def __init__(self, project_config: ProjectConfig):
        super().__init__()
        self.project_config = project_config
        self.extract_config_data()
    
    def extract_config_data(self):
        """Override in subclasses to extract needed data."""
        pass
    
    def save_configuration(self):
        """Override in subclasses to save configuration."""
        pass
```

#### b) Add Type Hints and Documentation
Ensure all constructors have proper type hints and docstrings explaining expected parameters.

## Root Cause Analysis
This appears to be the result of incomplete refactoring where the wizard infrastructure was updated to pass `ProjectConfig` objects to all screens, but many screen constructors were not updated to match. The working screens show the intended pattern, while the broken screens retain the old individual parameter approach.

## Impact Assessment
- **Severity**: Critical - Application crashes when accessing multiple wizard screens
- **Scope**: Wide - Affects 7 out of 11 wizard screens
- **User Experience**: Major workflow disruption - users cannot complete configuration
- **Code Quality**: Indicates systemic architecture inconsistency

## Testing Recommendations
After implementing fixes:
1. Test navigation to each wizard screen
2. Test data input and modification on each screen
3. Test configuration persistence across wizard steps
4. Test final configuration output generation
5. Add unit tests for each screen constructor
6. Add integration tests for the complete wizard flow

## Priority Order for Fixes
1. **EnvironmentVariablesScreen** (currently crashing as shown in traceback)
2. **APTConfigScreen**, **ProxyConfigScreen**, **DeviceConfigScreen** (likely to be accessed soon)
3. **MountsScreen**, **EntryPointScreen**, **CustomScriptsScreen** (later in wizard flow)

This represents a systemic architectural issue that needs comprehensive addressing rather than piecemeal fixes.
