# Code Check Report

**Title**: Code Check Report - DeviceConfig Attribute Mismatch  
**Date**: July 24, 2025  
**Status**: Critical Error Found  

## Description of Symptoms

The PeiDocker GUI application crashes with `AttributeError: 'DeviceConfig' object has no attribute 'gpu'` when navigating to the Device Configuration screen in the wizard. The error occurs at line 87 in `device_config.py` within the `compose()` method when attempting to access `self.current_config.gpu` to set the initial radio button values.

## Problems Found

### 1. Attribute Name Mismatch (Critical)
**Location**: `/Users/igame/code/PeiDocker/src/pei_docker/gui/screens/simple/device_config.py:87-88`

**Issue**: The `DeviceConfigScreen` is trying to access a `gpu` boolean attribute that doesn't exist in the `DeviceConfig` dataclass.

**Current Code**:
```python
# Lines 87-88
yield RadioButton("Yes", value=self.current_config.gpu)
yield RadioButton("No", value=not self.current_config.gpu)
```

**Actual DeviceConfig Structure** (from `gui/models/config.py`):
```python
@dataclass
class DeviceConfig:
    """Device configuration."""
    device_type: str = "cpu"  # "cpu" or "gpu"
```

The class has `device_type` as a string, not `gpu` as a boolean.

### 2. Constructor Parameter Inconsistency in _get_config()
**Location**: `/Users/igame/code/PeiDocker/src/pei_docker/gui/screens/simple/device_config.py:129`

**Issue**: The `_get_config()` method attempts to create a `DeviceConfig` with a `gpu` parameter:
```python
return DeviceConfig(
    gpu=gpu_value  # This parameter doesn't exist
)
```

But the `DeviceConfig` constructor only accepts `device_type`.

### 3. Data Model Confusion
**Multiple DeviceConfig Classes**: There are actually two different `DeviceConfig` classes in the codebase:
1. `src/pei_docker/user_config.py`: `DeviceConfig` with `type: str` (using attrs)
2. `src/pei_docker/gui/models/config.py`: `DeviceConfig` with `device_type: str` (using dataclass)

This suggests a potential architectural inconsistency in how device configuration is handled between the CLI and GUI components.

### 4. Logic-Data Model Mismatch
The screen logic assumes boolean semantics (GPU enabled/disabled) but the data model uses string semantics ("cpu"/"gpu"). This creates an impedance mismatch between the UI representation and the data model.

## Suggestions for Improvement/Bugfix

### 1. Fix Attribute Access (Immediate Fix)
Update the `compose()` method to use the correct attribute and convert between boolean and string representations:

```python
# Lines 87-88 - Fixed version
gpu_enabled = self.current_config.device_type == "gpu"
yield RadioButton("Yes", value=gpu_enabled)
yield RadioButton("No", value=not gpu_enabled)
```

### 2. Fix Constructor in _get_config()
Update the `_get_config()` method to create the `DeviceConfig` with the correct parameter:

```python
def _get_config(self) -> DeviceConfig:
    """Get the current configuration from form."""
    gpu_enabled = self.query_one("#gpu_enabled", RadioSet)
    
    yes_button = gpu_enabled.query_one("RadioButton")  # First button is "Yes"
    gpu_value = yes_button.value if yes_button else False
    
    # Convert boolean to device_type string
    device_type = "gpu" if gpu_value else "cpu"
    
    return DeviceConfig(
        device_type=device_type
    )
```

### 3. Add Helper Methods for Boolean Conversion
Add utility methods to handle the boolean ↔ string conversion cleanly:

```python
def _is_gpu_enabled(self) -> bool:
    """Check if GPU is enabled from current config."""
    return self.current_config.device_type == "gpu"

def _device_type_from_gpu_bool(self, gpu_enabled: bool) -> str:
    """Convert GPU boolean to device_type string."""
    return "gpu" if gpu_enabled else "cpu"
```

### 4. Data Model Consistency Review (Architectural)
Consider standardizing the `DeviceConfig` classes across CLI and GUI components:

**Option A**: Use the same data model for both
**Option B**: Create clear conversion utilities between the two models
**Option C**: Extend the GUI model to include helper properties:

```python
@dataclass
class DeviceConfig:
    """Device configuration."""
    device_type: str = "cpu"  # "cpu" or "gpu"
    
    @property
    def gpu(self) -> bool:
        """Boolean helper for GPU enablement."""
        return self.device_type == "gpu"
    
    @gpu.setter
    def gpu(self, value: bool) -> None:
        """Set GPU enablement via boolean."""
        self.device_type = "gpu" if value else "cpu"
```

### 5. Add Type Safety and Validation
Consider adding validation to ensure `device_type` only accepts valid values:

```python
@dataclass
class DeviceConfig:
    """Device configuration."""
    device_type: str = field(default="cpu")
    
    def __post_init__(self):
        if self.device_type not in ("cpu", "gpu"):
            raise ValueError(f"Invalid device_type: {self.device_type}. Must be 'cpu' or 'gpu'")
```

## Root Cause Analysis
This appears to be either:
1. **Incomplete implementation** - The screen was designed with a boolean `gpu` attribute in mind but the data model was implemented with a string `device_type`
2. **Refactoring oversight** - The data model was changed from boolean to string but the screen logic wasn't updated accordingly
3. **Copy-paste error** - Code was copied from another context where a `gpu` boolean attribute existed

## Impact Assessment
- **Severity**: Critical - Application crashes when accessing device configuration
- **Scope**: Limited to device configuration functionality in the GUI wizard
- **User Experience**: Complete failure of GPU configuration workflow
- **Data Integrity**: No data corruption risk, but configuration cannot be set

## Testing Recommendations
After implementing the fix:
1. Test navigation to the device configuration screen
2. Test both GPU enabled and disabled radio button selections
3. Test configuration persistence across wizard steps
4. Test final configuration output includes correct `device_type` values
5. Verify integration with Docker Compose generation (ensure "gpu" device_type produces correct Docker configuration)
6. Add unit tests for boolean ↔ string conversion utilities

## Priority
**High Priority** - This is a critical path blocking basic GPU configuration functionality in the wizard.
