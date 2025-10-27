# Fix GUI APT Mirror Mapping Bug

## Bug Description

The GUI APT mirror selection currently stores full URLs instead of short names, which conflicts with the intended design where short names are for predefined mirrors and full URLs are for advanced manual configuration.

## Current Incorrect Behavior

In `src/pei_docker/webgui/tabs/network.py`, the APT mirror select component uses full URLs as values:

```python
apt_select = ui.select(
    options={
        '': 'Default Ubuntu Mirrors',
        'https://mirrors.tuna.tsinghua.edu.cn/ubuntu/': 'Tsinghua University (tuna)',
        'http://mirrors.aliyun.com/ubuntu/': 'Alibaba Cloud (aliyun)',
        'http://mirrors.163.com/ubuntu/': 'NetEase (163)',
        'http://mirrors.ustc.edu.cn/ubuntu/': 'USTC',
        'http://cn.archive.ubuntu.com/ubuntu/': 'Ubuntu CN Mirror'
    },
    value=''
).classes('w-full').bind_value(network_1, 'apt_mirror')
```

**Result**: `NetworkUI.apt_mirror` stores full URLs like `'https://mirrors.tuna.tsinghua.edu.cn/ubuntu/'`

## Correct Expected Behavior

The GUI should store short names for predefined mirrors:

```python
apt_select = ui.select(
    options={
        '': 'Default Ubuntu Mirrors',
        'tuna': 'Tsinghua University (tuna)',
        'aliyun': 'Alibaba Cloud (aliyun)',
        '163': 'NetEase (163)',
        'ustc': 'USTC',
        'cn': 'Ubuntu CN Mirror'
    },
    value=''
).classes('w-full').bind_value(network_1, 'apt_mirror')
```

**Result**: `NetworkUI.apt_mirror` should store short names like `'tuna'`, `'aliyun'`, etc.

## Existing Infrastructure

The project already has the correct infrastructure in place:

### AptMirrors Class (`src/pei_docker/webgui/constants.py`)
```python
class AptMirrors:
    """Constants for known APT mirror shortcuts."""
    
    TUNA: str = 'tuna'  # Tsinghua University mirror
    ALIYUN: str = 'aliyun'  # Alibaba Cloud mirror
    MIRRORS_163: str = '163'  # NetEase mirror
    USTC: str = 'ustc'  # University of Science and Technology of China mirror
    CN_ARCHIVE: str = 'cn'  # China archive mirror
    
    @classmethod
    def get_mirror_urls(cls) -> Dict[str, str]:
        """Get mapping of mirror shortcuts to their URLs."""
        return {
            cls.TUNA: 'http://mirrors.tuna.tsinghua.edu.cn/ubuntu/',
            cls.ALIYUN: 'http://mirrors.aliyun.com/ubuntu/',
            cls.MIRRORS_163: 'http://mirrors.163.com/ubuntu/',
            cls.USTC: 'http://mirrors.ustc.edu.cn/ubuntu/',
            cls.CN_ARCHIVE: 'http://cn.archive.ubuntu.com/ubuntu/'
        }
```

## Why This is a Bug

1. **Design Principle Violation**: 
   - Short names (`'tuna'`, `'aliyun'`) = predefined mirrors for easy selection
   - Full URLs = advanced manual configuration in `user_config.yml`

2. **Inconsistent with CLI/Manual Usage**:
   - CLI and manual YAML editing use short names
   - GUI should follow the same convention

3. **Violates Separation of Concerns**:
   - GUI should use semantic identifiers (short names)
   - URL resolution should happen at build time

4. **Makes Future Maintenance Harder**:
   - If mirror URLs change, they need to be updated in GUI code
   - With short names, URLs are centralized in build scripts

## Impact

- **Current**: GUI users get full URLs in their `user_config.yml`
- **Expected**: GUI users get short names in their `user_config.yml`, same as CLI users
- **Compatibility**: Both approaches work during build, but short names are preferred

## Files to Fix

### 1. GUI Network Tab
**File**: `src/pei_docker/webgui/tabs/network.py`
- Change select options keys from full URLs to short names
- Update any related validation or preview logic

### 2. Use Existing Constants
**File**: `src/pei_docker/webgui/constants.py` 
- Already has `AptMirrors` class with correct short names and URL mappings
- **No changes needed** - just import and use these constants in the GUI

### 3. Config Adapter (if needed)
**File**: `src/pei_docker/webgui/models/config_adapter.py`
- Verify `NetworkConfigAdapter.apt_mirror` property works correctly with short names
- Update any URL-to-shortname conversion logic if present

### 4. UI State Bridge (if needed)
**Files**: `src/pei_docker/webgui/utils/ui_state_bridge/*.py`
- Ensure conversion between UI state and config models works with short names
- Remove any URL-based logic for predefined mirrors

## Testing Required

1. **GUI Selection Test**:
   - Select each mirror option in GUI
   - Verify `NetworkUI.apt_mirror` stores correct short name
   - Verify generated `user_config.yml` contains short names

2. **Build Test**:
   - Create project with each mirror option
   - Build Docker image and verify correct mirror is used
   - Check that `setup-env.sh` processes short names correctly

3. **Compatibility Test**:
   - Ensure existing projects with full URLs still work
   - Test loading YAML files with both short names and full URLs

## Implementation Notes

### Phase 1: Fix GUI Options
The `AptMirrors` class in `constants.py` already provides everything needed:

```python
# Import existing constants
from pei_docker.webgui.constants import AptMirrors

# Use the predefined short names as select option keys
apt_select = ui.select(
    options={
        '': 'Default Ubuntu Mirrors',
        AptMirrors.TUNA: 'Tsinghua University (tuna)',
        AptMirrors.ALIYUN: 'Alibaba Cloud (aliyun)',
        AptMirrors.MIRRORS_163: 'NetEase (163)',
        AptMirrors.USTC: 'USTC',
        AptMirrors.CN_ARCHIVE: 'Ubuntu CN Mirror'
    },
    value=''
)
```

**Note**: The `AptMirrors` class already includes:
- All short names as constants (`TUNA = 'tuna'`, `ALIYUN = 'aliyun'`, etc.)
- A `get_mirror_urls()` method that returns the URL mappings
- A `get_all_mirrors()` method that lists all available mirrors

This means **zero new code** is needed for constants - just import and use the existing `AptMirrors` class.

### Phase 2: Update Build System (if needed)
Verify that `src/pei_docker/project_files/installation/stage-1/internals/setup-env.sh` correctly handles all short names used by GUI.

### Phase 3: Documentation Update
Update any documentation that mentions APT mirror configuration to clarify:
- GUI users: Select from predefined options (short names)
- Advanced users: Edit YAML directly (can use full URLs)

## Priority

**High** - This affects user experience consistency and violates design principles. Should be fixed before next release.

## Related Files

- `src/pei_docker/webgui/tabs/network.py` (main fix)
- `src/pei_docker/webgui/constants.py` (use existing constants)
- `src/pei_docker/project_files/installation/stage-1/internals/setup-env.sh` (verify compatibility)
- `src/pei_docker/user_config/network.py` (model supports both)
