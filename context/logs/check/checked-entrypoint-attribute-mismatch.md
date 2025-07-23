# Code Check Report

**Title**: Code Check Report - EntryPoint Attribute Name Mismatch  
**Date**: July 24, 2025  
**Status**: Critical Error Found  

## Description of Symptoms

The PeiDocker GUI application crashes with `AttributeError: 'Stage1Config' object has no attribute 'entrypoint'` when navigating to the Entry Point configuration screen in the wizard. The error occurs at line 93 in `entry_point.py` within the `__init__()` method when attempting to access `project_config.stage_1.entrypoint` to extract the current entry point configuration.

## Problems Found

### 1. Attribute Name Mismatch (Critical)
**Location**: `/Users/igame/code/PeiDocker/src/pei_docker/gui/screens/simple/entry_point.py:93-94`

**Issue**: The `EntryPointScreen` is trying to access `entrypoint` attributes that don't exist in the `Stage1Config` and `Stage2Config` dataclasses.

**Current Code**:
```python
# Lines 93-94
self.stage1_entrypoint = project_config.stage_1.entrypoint or ""
self.stage2_entrypoint = project_config.stage_2.entrypoint or ""
```

**Actual Stage Config Structure** (from `gui/models/config.py`):
```python
@dataclass
class Stage1Config:
    # ... other attributes ...
    custom_entry: Optional[str] = None  # <-- Correct attribute name
    # ... other attributes ...

@dataclass
class Stage2Config:
    # ... other attributes ...
    custom_entry: Optional[str] = None  # <-- Correct attribute name
    # ... other attributes ...
```

The classes have `custom_entry`, not `entrypoint`.

### 2. Consistent Mismatch Throughout the File
**Additional Locations**:
- Line 106-107: `bool(self.stage1_entrypoint)` and `not bool(self.stage1_entrypoint)`
- Line 116: `value=self.stage1_entrypoint`
- Line 131-132: `bool(self.stage2_entrypoint)` and `not bool(self.stage2_entrypoint)`  
- Line 141: `value=self.stage2_entrypoint`
- Line 282-283: `self.project_config.stage_1.entrypoint = ...` and `self.project_config.stage_2.entrypoint = ...`

The entire screen consistently uses the wrong attribute name pattern.

### 3. Save Configuration Method Issues
**Location**: Lines 282-283
```python
def save_configuration(self) -> None:
    """Save current entry point configuration to project config."""
    stage1_entrypoint, stage2_entrypoint = self._get_entry_point_config()
    self.project_config.stage_1.entrypoint = stage1_entrypoint  # Wrong attribute
    self.project_config.stage_2.entrypoint = stage2_entrypoint  # Wrong attribute
```

This will also fail when trying to save the configuration.

### 4. Data Model Naming Inconsistency
**Multi-layered naming confusion**:
1. **User Config Model** (`user_config.py`): Uses `on_entry` as a list
2. **GUI Config Model** (`gui/models/config.py`): Uses `custom_entry` as a string
3. **Screen Implementation** (`entry_point.py`): Expects `entrypoint` as a string

This suggests inconsistent naming conventions across different layers of the application.

### 5. Type Mismatch Between Models
The user config model uses `on_entry: list[str]` (allowing multiple entry points with validation to ensure at most one), while the GUI model uses `custom_entry: Optional[str]` (single string). This indicates a potential impedance mismatch between the CLI and GUI data models.

## Suggestions for Improvement/Bugfix

### 1. Fix Attribute Access (Immediate Fix)
Update all references from `entrypoint` to `custom_entry`:

```python
# Lines 93-94 - Fixed version
self.stage1_entrypoint = project_config.stage_1.custom_entry or ""
self.stage2_entrypoint = project_config.stage_2.custom_entry or ""
```

### 2. Fix Save Configuration Method
```python
def save_configuration(self) -> None:
    """Save current entry point configuration to project config."""
    stage1_entrypoint, stage2_entrypoint = self._get_entry_point_config()
    self.project_config.stage_1.custom_entry = stage1_entrypoint
    self.project_config.stage_2.custom_entry = stage2_entrypoint
```

### 3. Review Variable Naming for Consistency
Consider renaming internal variables to match the data model:

```python
def __init__(self, project_config: ProjectConfig):
    super().__init__()
    self.project_config = project_config
    
    # Use consistent naming with the data model
    self.stage1_custom_entry = project_config.stage_1.custom_entry or ""
    self.stage2_custom_entry = project_config.stage_2.custom_entry or ""
```

### 4. Add Data Model Documentation
Add clear documentation about the naming conventions:

```python
# In gui/models/config.py
@dataclass
class Stage1Config:
    """Stage-1 configuration."""
    # ...
    custom_entry: Optional[str] = None  # Custom entry point script path
    # Note: This corresponds to 'on_entry' in user_config.py (first item if list has items)
```

### 5. Implement Data Model Conversion Utilities
Create utility functions to handle conversion between different data model representations:

```python
def convert_user_config_to_gui_config(user_config_custom_script):
    """Convert user_config CustomScriptConfig.on_entry to GUI custom_entry."""
    if user_config_custom_script.on_entry:
        return user_config_custom_script.on_entry[0]  # Take first entry
    return None

def convert_gui_config_to_user_config(custom_entry_str):
    """Convert GUI custom_entry string to user_config on_entry list."""
    if custom_entry_str:
        return [custom_entry_str]
    return []
```

### 6. Consider Unified Naming Convention
**Long-term architectural improvement**: Standardize naming across all layers:

**Option A**: Use `entry_point` everywhere
**Option B**: Use `custom_entry` everywhere  
**Option C**: Use `on_entry` everywhere

### 7. Add Validation and Type Safety
```python
def __init__(self, project_config: ProjectConfig):
    if not hasattr(project_config.stage_1, 'custom_entry'):
        raise AttributeError("Stage1Config missing required 'custom_entry' attribute")
    if not hasattr(project_config.stage_2, 'custom_entry'):
        raise AttributeError("Stage2Config missing required 'custom_entry' attribute")
    # ... rest of initialization
```

## Root Cause Analysis
This appears to be the result of:
1. **Inconsistent naming conventions** across different layers of the application
2. **Copy-paste error** where the screen was modeled after an interface expecting `entrypoint` attributes
3. **Incomplete refactoring** where data models were updated but screen implementations weren't synchronized
4. **Lack of integration testing** that would have caught this attribute mismatch

## Impact Assessment
- **Severity**: Critical - Application crashes when accessing entry point configuration
- **Scope**: Limited to entry point functionality in the GUI wizard
- **User Experience**: Complete failure of custom entry point configuration workflow
- **Data Integrity**: No corruption risk, but configuration cannot be set or retrieved

## Architecture Pattern Issues
This error reveals a broader pattern where:
1. **CLI layer** uses `on_entry: list[str]` (attrs-based)
2. **GUI data model** uses `custom_entry: Optional[str]` (dataclass-based)  
3. **GUI screen** expects `entrypoint: str` (non-existent)

This three-way mismatch suggests the need for better architectural alignment and data model consistency.

## Testing Recommendations
After implementing the fix:
1. Test navigation to the entry point configuration screen
2. Test both stage 1 and stage 2 entry point input
3. Test empty/None entry point handling
4. Test configuration persistence across wizard steps
5. Test final configuration output generation
6. Add unit tests for data model conversion utilities
7. Add integration tests to catch attribute mismatches

## Priority
**High Priority** - This blocks a key customization feature (custom entry points) which is important for advanced Docker container configurations.
