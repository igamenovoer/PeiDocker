# Bug Report: Unbound Variable Error in SSH Setup

## Summary
Docker build fails with `SSH_PUBKEY_FILE: unbound variable` error when optional SSH key file paths are left empty in `merged.env`.

## Severity
**High** - Blocks all Docker builds when SSH is enabled with default configuration.

## Environment
- Affected files:
  - `dockers/build-merged.sh`
  - `dockers/installation/stage-1/internals/setup-ssh.sh`
  - `dockers/merged.env`
- Build command: `./build-merged.sh`

## Error Message
```
/pei-from-host/stage-1/internals/setup-ssh.sh: line 55: SSH_PUBKEY_FILE: unbound variable
```

## Steps to Reproduce
1. Configure `merged.env` with SSH enabled but empty key file paths:
   ```bash
   WITH_SSH='true'
   SSH_USER_NAME='me'
   SSH_USER_PASSWORD='123456'
   SSH_PUBKEY_FILE=''    # Empty
   SSH_PRIVKEY_FILE=''   # Empty
   SSH_USER_UID='1001'
   ```
2. Run `./build-merged.sh`
3. Build fails at `setup-ssh.sh` execution

## Root Cause Analysis

### The Problem Chain

1. **Configuration Layer (`merged.env:61,64`)**
   ```bash
   SSH_PUBKEY_FILE=''
   SSH_PRIVKEY_FILE=''
   ```
   Variables are intentionally set to empty strings (valid configuration for auto-generated keys).

2. **Build Script Layer (`build-merged.sh:55-57`)**
   ```bash
   [[ -n "${SSH_USER_UID:-}" ]] && cmd+=( --build-arg SSH_USER_UID )
   [[ -n "${SSH_PUBKEY_FILE:-}" ]] && cmd+=( --build-arg SSH_PUBKEY_FILE )
   [[ -n "${SSH_PRIVKEY_FILE:-}" ]] && cmd+=( --build-arg SSH_PRIVKEY_FILE )
   ```
   **ISSUE**: Conditional logic only passes build args when variables are non-empty.
   **RESULT**: These ARG declarations are completely omitted from the Docker build command.

3. **Docker Build Layer (merged.Dockerfile)**
   ```dockerfile
   ARG SSH_PUBKEY_FILE
   ARG SSH_PRIVKEY_FILE
   ARG SSH_USER_UID
   ```
   **RESULT**: ARGs are declared but receive no values from `--build-arg`, leaving them unset.

4. **Execution Layer (`setup-ssh.sh:2,55-57`)**
   ```bash
   set -euo pipefail  # -u flag treats unset variables as errors
   ...
   IFS=',' read -ra pubkey_files <<< "$SSH_PUBKEY_FILE"    # FAILS HERE
   IFS=',' read -ra privkey_files <<< "$SSH_PRIVKEY_FILE"
   IFS=',' read -ra uids <<< "$SSH_USER_UID"
   ```
   **FAILURE**: Variables are completely unset (not even empty), triggering `-u` flag error.

### Key Insight
The bug stems from a **semantic mismatch**:
- `build-merged.sh` treats empty strings as "don't pass this arg"
- `setup-ssh.sh` expects variables to always be defined (even if empty)
- Docker ARG layer drops the variables entirely when not passed

## Impact
- All Docker builds fail when using default SSH configuration with auto-generated keys
- Workaround requires manually setting dummy values for optional parameters
- Affects user experience for common use case (SSH with auto-generated keys)

## Proposed Solutions

### Solution 1: Fix Setup Script (Quick, Defensive)
**File**: `dockers/installation/stage-1/internals/setup-ssh.sh`

**Change lines 55-57**:
```bash
# BEFORE
IFS=',' read -ra pubkey_files <<< "$SSH_PUBKEY_FILE"
IFS=',' read -ra privkey_files <<< "$SSH_PRIVKEY_FILE"
IFS=',' read -ra uids <<< "$SSH_USER_UID"

# AFTER
IFS=',' read -ra pubkey_files <<< "${SSH_PUBKEY_FILE:-}"
IFS=',' read -ra privkey_files <<< "${SSH_PRIVKEY_FILE:-}"
IFS=',' read -ra uids <<< "${SSH_USER_UID:-}"
```

**Pros**:
- Minimal change
- Makes script resilient to unset variables
- Follows defensive programming practices

**Cons**:
- Doesn't fix the root cause (build-merged.sh logic)
- Other scripts may have similar issues

### Solution 2: Fix Build Script (Root Cause)
**File**: `dockers/build-merged.sh`

**Change lines 55-57**:
```bash
# BEFORE
[[ -n "${SSH_USER_UID:-}" ]] && cmd+=( --build-arg SSH_USER_UID )
[[ -n "${SSH_PUBKEY_FILE:-}" ]] && cmd+=( --build-arg SSH_PUBKEY_FILE )
[[ -n "${SSH_PRIVKEY_FILE:-}" ]] && cmd+=( --build-arg SSH_PRIVKEY_FILE )

# AFTER
cmd+=( --build-arg "SSH_USER_UID=${SSH_USER_UID:-}" )
cmd+=( --build-arg "SSH_PUBKEY_FILE=${SSH_PUBKEY_FILE:-}" )
cmd+=( --build-arg "SSH_PRIVKEY_FILE=${SSH_PRIVKEY_FILE:-}" )
```

**Pros**:
- Fixes root cause
- Ensures ARGs are always passed (even if empty)
- Consistent with intent of optional parameters

**Cons**:
- Requires review of all conditional build arg logic

### Recommended Solution: Both
Apply both fixes for defense in depth:
1. Fix `build-merged.sh` to always pass optional ARGs (root cause)
2. Fix `setup-ssh.sh` to handle unset variables gracefully (defensive)

This ensures:
- Normal case: ARGs are passed correctly
- Edge cases: Scripts handle missing vars without crashing

## Testing Checklist
After fix:
- [ ] Build succeeds with empty `SSH_PUBKEY_FILE` and `SSH_PRIVKEY_FILE`
- [ ] Build succeeds with populated key file paths
- [ ] Build succeeds with `WITH_SSH='false'`
- [ ] SSH keys are auto-generated when files not provided
- [ ] User-provided keys are installed when files are specified
- [ ] UID conflicts are handled correctly when `SSH_USER_UID` is empty

## Related Issues
- This pattern may affect other optional build args in `build-merged.sh`
- All scripts using `set -u` should use parameter expansion `${VAR:-}` for optional vars
- Consider audit of all build arg conditional logic

## Status
- **Discovered**: 2025-11-09
- **Status**: Open
- **Priority**: High
- **Assigned**: Pending
