# Pixi Support Implementation Strategy

## Overview
This document outlines the implementation strategy for improving pixi support in PeiDocker, focusing on better discovery, reduced code duplication, and proper handling of per-user installations.

## Key Design Decisions

### 1. Installation Approach
- **Always install packages for each user** - no efficiency concerns
- **Skip root if no password** - root without password cannot SSH login
- Support both shared (`/hard/volume/app/pixi`) and per-user (`~/.pixi`) installations

### 2. Centralized Utilities
Created `pixi-utils.bash` with common functions to eliminate code duplication:
- `get_all_users()` - Enumerate users from `/etc/passwd` (UID ≥ 1000, valid shell)
- `find_user_pixi()` - Smart pixi discovery (checks user home first, then shared)
- `setup_pixi_path()` - Configure PATH for current shell
- `root_has_password()` - Check if root has password via `/etc/shadow`
- `install_packages_for_all_users()` - Install packages for all users with pixi

### 3. Simplified Package Installation
Both `create-env-common.bash` and `create-env-ml.bash` now simply:
```bash
packages=(...)
install_packages_for_all_users "${packages[@]}"
```

### 4. Smart Root Handling
- **Critical requirement**: All scripts that install/configure things for users must skip passwordless root
- Check root password via `/etc/shadow` password field using `root_has_password()` function
- Skip if field is empty, `!`, or `*` (indicates no password set)
- Show warning: "WARNING: Skipping root user - no password set (not accessible via SSH)"
- **Rationale**: Root without password cannot SSH login, so configuring pixi for root is wasteful

### 5. PATH Configuration
- Removed reliance on `/etc/profile.d/` (not sourced by non-login SSH shells)
- Add pixi to each user's `.bashrc` directly
- Also update `/etc/bash.bashrc` for system-wide availability in shared mode
- Update `/etc/skel/.bashrc` for future users

## Implementation Files

### Core Files Modified:
1. **`pixi-utils.bash`** (new) - Common utility functions
2. **`install-pixi.bash`** - Updated to add pixi to `.bashrc` files
3. **`set-pixi-repo-tuna.bash`** - Now configures each user's `~/.pixi/config.toml`
4. **`create-env-common.bash`** - Simplified to use utilities
5. **`create-env-ml.bash`** - Simplified to use utilities

### Key Functions:

#### `get_all_users()`
```bash
while IFS=: read -r username password uid gid gecos home shell; do
    if [ "$uid" -ge 1000 ] && [ -d "$home" ] && \
       [[ "$shell" != */nologin ]] && [[ "$shell" != */false ]]; then
        echo "$username:$home:$uid:$gid"
    fi
done < /etc/passwd
```

#### `root_has_password()`
```bash
local root_shadow_entry=$(getent shadow root)
local password_field=$(echo "$root_shadow_entry" | cut -d: -f2)
if [ -z "$password_field" ] || [ "$password_field" = "!" ] || [ "$password_field" = "*" ]; then
    return 1  # No password
fi
```

#### `install_packages_for_all_users()`
- Iterates through all users via `get_all_users()`
- Checks if each user has pixi via `find_user_pixi()`
- Runs `pixi global install` as each user via `su`
- Special handling for root (skip if no password)

## Environment Variables

### `PIXI_INSTALL_AT_HOME`
- If set to `1`, installs pixi to each user's home (`~/.pixi`)
- Downloads once to temp dir, then copies to each user
- Sets permissions to 777 and correct ownership

### No longer used:
- ~~`PIXI_INSTALL_FOR_ALL_USERS`~~ - Always install for all users now

## Root Password Handling Implementation

All scripts that install or configure things for users must properly handle passwordless root:

### Scripts with Root Password Checking:

1. **`install-pixi.bash`** ✅
   - Per-user mode: Checks `root_has_password()` before installing pixi (lines 125-135)
   - Shared mode: Checks `root_has_password()` before modifying root's bashrc (lines 214-219)
   - **Warning messages**: 
     - "WARNING: Skipping root user - no password set (not accessible via SSH)"
     - "WARNING: Skipping root user bashrc - no password set (not accessible via SSH)"

2. **`create-env-common.bash`** ✅
   - Uses `install_packages_for_all_users()` which includes root password checking

3. **`create-env-ml.bash`** ✅  
   - Uses `install_packages_for_all_users()` which includes root password checking

4. **`set-pixi-repo-tuna.bash`** ✅
   - Direct implementation with `root_has_password()` check (lines 108-114)
   - **Warning message**: "WARNING: Skipping root user - no password set (not accessible via SSH)"

### Implementation Details:

The `root_has_password()` function is implemented in two places:
1. **`pixi-utils.bash`** - Primary implementation for scripts that source utilities
2. **`install-pixi.bash`** - Local fallback implementation (lines 58-70) for when utilities aren't available yet

```bash
root_has_password() {
    local root_shadow_entry=$(getent shadow root)
    local password_field=$(echo "$root_shadow_entry" | cut -d: -f2)
    
    # If password field is empty, !, or *, root has no password
    if [ -z "$password_field" ] || [ "$password_field" = "!" ] || [ "$password_field" = "*" ]; then
        return 1  # No password
    else
        return 0  # Has password
    fi
}
```

## Benefits

1. **Reduced Code**: ~70% reduction in script size
2. **No Duplication**: Common logic centralized
3. **Consistent Behavior**: All scripts use same user enumeration and root handling
4. **Better Discovery**: Smart pixi finding that checks all locations
5. **SSH Compatibility**: Direct `.bashrc` modification ensures pixi in PATH
6. **Future-proof**: `/etc/skel` updates for new users
7. **Efficient**: Skips installation/configuration for inaccessible root user

## Testing Notes

When testing with SSH:
- Use `sshpass` with `-o PreferredAuthentications=password`
- Example: `sshpass -p 'admin123' ssh -o PreferredAuthentications=password admin@localhost -p 2222`
- UIDs should be ≥ 1100 to avoid conflicts (see CLAUDE.md)