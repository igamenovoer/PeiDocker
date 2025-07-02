# SSH Key Path Bug Fix

## Problem Description

There is a bug in PeiDocker's configuration processor where SSH key file paths are incorrectly generated in the docker-compose.yml file, causing SSH user creation to fail during image build.

## Issue Details

### Symptoms
- SSH user creation fails during stage-1 build
- Build logs show errors like:
  ```
  cat: /pei-from-host/installation/stage-1/generated/temp-admin-pubkey.pub: No such file or directory
  chown: invalid user: 'admin:admin'
  ```
- SSH login fails because users are never created

### Root Cause
The configuration processor generates incorrect container paths for SSH key files in docker-compose.yml:

**Current (Wrong):**
```yaml
SSH_PUBKEY_FILE: /pei-from-host/installation/stage-1/generated/temp-admin-pubkey.pub
SSH_PRIVKEY_FILE: /pei-from-host/installation/stage-1/generated/temp-admin-privkey
```

**Should Be:**
```yaml
SSH_PUBKEY_FILE: /pei-from-host/stage-1/generated/temp-admin-pubkey.pub
SSH_PRIVKEY_FILE: /pei-from-host/stage-1/generated/temp-admin-privkey
```

### Investigation Findings
1. **Host files exist correctly** at `/workspace/code/PeiDocker/build-pixi-test/installation/stage-1/generated/`
2. **Container mount is correct** - `/pei-from-host/stage-1/` maps to host `./installation/stage-1/`
3. **Generated paths are wrong** - include extra `/installation/` prefix that doesn't exist in container
4. **SSH key files are accessible** at `/pei-from-host/stage-1/generated/` in container

## Required Fix

### Location
The bug is likely in the config processor code that handles SSH key file path generation, specifically:
- `pei_docker/config_processor.py` - SSH processing methods
- Functions that process `pubkey_text` and `privkey_text` inline keys

### Expected Behavior
When inline SSH keys (`pubkey_text`, `privkey_text`) are specified:
1. Temporary files are created in `{project_dir}/installation/stage-1/generated/`
2. Container paths should be `/pei-from-host/stage-1/generated/{filename}`
3. SSH setup script should find the files at the correct container paths

### Testing
1. Use the test configuration `tests/configs/simple-pixi-test.yml`
2. Run `configure` command and verify docker-compose.yml has correct paths
3. Build stage-1 image and verify SSH user creation succeeds
4. Test SSH login with password authentication

## Technical Context

### File Path Mapping
- **Host**: `./installation/stage-1/` → **Container**: `/pei-from-host/stage-1/`
- **Host**: `./installation/stage-2/` → **Container**: `/pei-from-host/stage-2/`

### SSH Key Processing Flow
1. User specifies `pubkey_text`/`privkey_text` in config
2. Config processor creates temp files in `installation/stage-1/generated/`
3. Config processor generates container paths for docker-compose.yml
4. SSH setup script reads files at container paths during build

### Related Files
- `pei_docker/config_processor.py` - Config processing logic
- `pei_docker/pei_utils.py` - SSH key file creation utilities
- `pei_docker/project_files/installation/stage-1/internals/setup-ssh.sh` - SSH setup script

## Priority
**High** - This prevents SSH functionality from working with inline keys, which is a core feature of PeiDocker.