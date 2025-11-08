# Bug Report: User Creation Failure Due to GID Conflict

## Summary
Docker build fails to create user 'me' due to GID 1001 conflict with the 'ssh_users' group, causing subsequent installation scripts to fail with "Error: target user 'me' does not exist".

## Severity
**Critical** - Blocks entire Docker image build process

## Environment
- Base Image: `nvidia/cuda:12.6.3-devel-ubuntu24.04`
- OS: Ubuntu 24.04
- Build Script: `dockers/build-merged.sh`
- Dockerfile: `dockers/merged.Dockerfile`

## Symptoms
Build fails during stage-2 with the following error pattern:
```
#40 0.271 Installing Pixi Python Package Manager...
#40 0.275 Error: target user 'me' does not exist
#40 0.282 Error: target user 'me' does not exist
#40 0.292 Error: target user 'me' does not exist
#40 0.305 Error: target user 'me' does not exist
#40 0.316 Error: target user 'me' does not exist
#40 ERROR: process "/bin/sh -c $PEI_STAGE_DIR_2/internals/custom-on-build.sh" did not complete successfully: exit code: 1
```

## Root Cause Analysis

### Timeline of the Bug

1. **Initial Group Creation** (setup-ssh.sh:41)
   ```bash
   groupadd ssh_users
   ```
   The system assigns GID 1001 to 'ssh_users' group automatically.

2. **User Creation Attempt** (setup-ssh.sh:94)
   ```bash
   adduser --gecos "" --disabled-password --uid "$uid" "$user"
   # Expands to: adduser --gecos "" --disabled-password --uid 1001 me
   ```
   The `adduser` command tries to create:
   - User 'me' with UID 1001
   - Group 'me' with GID 1001 (by default, adduser creates a group with same GID as UID)

3. **Silent Failure**
   ```
   #18 28.03 fatal: The GID 1001 is already in use.
   ```
   The `adduser` command **fails silently** because GID 1001 is already taken by 'ssh_users'.
   The user 'me' is **never created**.

4. **Cascade of Errors**
   - `usermod -aG sudo me` → fails: "usermod: user 'me' does not exist"
   - `usermod -aG ssh_users me` → fails: "usermod: user 'me' does not exist"
   - `chpasswd` → fails: "Authentication token manipulation error"
   - `chown me:me` → fails: "invalid user: 'me:me'"

5. **Stage-2 Failures**
   All installation scripts in stage-2 that reference user 'me' fail:
   - `install-pixi.bash --user me` → "Error: target user 'me' does not exist"
   - `install-uv.sh --user me` → fails
   - `install-nvm-nodejs.sh --user me` → fails
   - `install-codex-cli.sh --user me` → fails
   - `install-claude-code.sh --user me` → fails

### Technical Details

**Why GID 1001 was taken:**
Ubuntu 24.04's `groupadd` command, when called without explicit GID, assigns GIDs starting from the first available GID >= 1000. Since no groups were created yet, 'ssh_users' got GID 1001.

**Why the failure was silent:**
The `adduser` command outputs error to stderr but the script doesn't check exit codes, so execution continues even after the failure.

**Configuration that triggered it:**
```yaml
# user_config.yml
ssh:
  users:
    me:
      uid: 1001
      gid: 1001  # This was not being parsed/used
```

```bash
# merged.env
SSH_USER_UID='1001'
# SSH_USER_GID was missing!
```

## Steps to Reproduce

1. Start with base image `nvidia/cuda:12.6.3-devel-ubuntu24.04`
2. Configure user in `user_config.yml`:
   ```yaml
   ssh:
     users:
       me:
         uid: 1001
         gid: 1001
   ```
3. Run build script:
   ```bash
   cd dockers
   ./build-merged.sh --no-cache
   ```
4. Observe failure at stage-2 custom scripts

## Impact

- **Build Process**: Complete build failure, image cannot be created
- **Development**: Blocks all development work requiring the Docker environment
- **CI/CD**: Would break automated builds if integrated
- **User Experience**: Confusing error messages that don't clearly indicate the root cause

## Solution

### Files Modified

1. **dockers/installation/stage-1/internals/setup-ssh.sh**
2. **dockers/merged.Dockerfile**
3. **dockers/merged.env**
4. **dockers/build-merged.sh**

### Changes Applied

#### 1. Parse SSH_USER_GID Parameter
**File**: `setup-ssh.sh` (lines 48, 55)

```bash
# Before
IFS=',' read -ra uids <<< "$SSH_USER_UID"

# After
IFS=',' read -ra uids <<< "$SSH_USER_UID"
IFS=',' read -ra gids <<< "${SSH_USER_GID:-}"
```

```bash
# Before
for i in "${!users[@]}"; do
  user=${users[$i]}
  password=${passwords[$i]}
  pubkey_file=${pubkey_files[$i]}
  privkey_file=${privkey_files[$i]}
  uid=${uids[$i]}

# After
for i in "${!users[@]}"; do
  user=${users[$i]}
  password=${passwords[$i]}
  pubkey_file=${pubkey_files[$i]}
  privkey_file=${privkey_files[$i]}
  uid=${uids[$i]}
  gid=${gids[$i]:-}
```

#### 2. Add GID Conflict Detection and Resolution
**File**: `setup-ssh.sh` (lines 93-105)

```bash
# Handle GID conflicts
# If a GID is specified and already in use by another group, remove the conflicting group
if [ -n "$gid" ]; then
  conflict_group=$(awk -F: -v gid="$gid" '$3==gid{print $1}' /etc/group | head -n1)
  if [ -n "$conflict_group" ] && [ "$conflict_group" != "$user" ] && [ "$conflict_group" != "root" ]; then
    echo "WARNING: GID $gid already used by group '$conflict_group'. Removing that group to create user '$user'." >&2
    # Remove the conflicting group
    groupdel "$conflict_group" 2>/dev/null || true
  elif [ -n "$conflict_group" ] && [ "$conflict_group" = "root" ]; then
    echo "WARNING: Requested GID $gid conflicts with root group; creating '$user' with system-assigned GID instead." >&2
    gid=""
  fi
fi
```

#### 3. Create Group Before User
**File**: `setup-ssh.sh` (lines 112-140)

```bash
# Create the user with specified UID/GID
if [ -n "$uid" ] && [ -n "$gid" ]; then
  echo "Creating user '$user' with uid $uid and gid $gid"
  # Create the group first if it doesn't exist
  if ! getent group "$user" >/dev/null 2>&1; then
    groupadd -g "$gid" "$user" || {
      echo "ERROR: Failed to create group '$user' with gid $gid" >&2
      exit 1
    }
  fi
  # Now create the user and add to the existing group
  adduser --gecos "" --disabled-password --uid "$uid" --gid "$gid" "$user"
elif [ -n "$uid" ]; then
  echo "Creating user '$user' with uid $uid"
  adduser --gecos "" --disabled-password --uid "$uid" "$user"
elif [ -n "$gid" ]; then
  echo "Creating user '$user' with gid $gid"
  # Create the group first if it doesn't exist
  if ! getent group "$user" >/dev/null 2>&1; then
    groupadd -g "$gid" "$user" || {
      echo "ERROR: Failed to create group '$user' with gid $gid" >&2
      exit 1
    }
  fi
  adduser --gecos "" --disabled-password --gid "$gid" "$user"
else
  echo "Creating user '$user' with system-assigned uid and gid"
  adduser --gecos "" --disabled-password "$user"
fi
```

#### 4. Defer ssh_users Group Creation
**File**: `setup-ssh.sh` (lines 38-40, 72-75, 139-143)

```bash
# Before (line 41)
groupadd ssh_users

# After - Removed from early initialization

# For root user (lines 72-75)
if [ "$user" = "root" ]; then
  echo "root:$password" | chpasswd
  # Create ssh_users group if it doesn't exist yet
  if ! getent group ssh_users >/dev/null 2>&1; then
    groupadd ssh_users
  fi
  usermod -aG ssh_users root
  ssh_dir="/root/.ssh"

# For non-root users (lines 139-143)
usermod -aG sudo $user
# Create ssh_users group if it doesn't exist yet
if ! getent group ssh_users >/dev/null 2>&1; then
  groupadd ssh_users
fi
usermod -aG ssh_users $user
echo "$user:$password" | chpasswd
```

#### 5. Add GID to Dockerfile
**File**: `merged.Dockerfile` (line 34)

```dockerfile
# Before
ARG SSH_USER_NAME
ARG SSH_USER_PASSWORD
ARG SSH_USER_UID
ARG SSH_CONTAINER_PORT

# After
ARG SSH_USER_NAME
ARG SSH_USER_PASSWORD
ARG SSH_USER_UID
ARG SSH_USER_GID
ARG SSH_CONTAINER_PORT
```

#### 6. Add GID to Environment Configuration
**File**: `merged.env` (lines 57-58)

```bash
# SSH user UIDs (comma-separated)
SSH_USER_UID='1001'

# SSH user GIDs (comma-separated)
SSH_USER_GID='1001'

# SSH port inside container
SSH_CONTAINER_PORT='22'
```

#### 7. Pass GID as Build Argument
**File**: `build-merged.sh` (line 56)

```bash
[[ -n "${SSH_USER_NAME:-}" ]] && cmd+=( --build-arg SSH_USER_NAME )
[[ -n "${SSH_USER_PASSWORD:-}" ]] && cmd+=( --build-arg SSH_USER_PASSWORD )
[[ -n "${SSH_USER_UID:-}" ]] && cmd+=( --build-arg SSH_USER_UID )
[[ -n "${SSH_USER_GID:-}" ]] && cmd+=( --build-arg SSH_USER_GID )
[[ -n "${SSH_PUBKEY_FILE:-}" ]] && cmd+=( --build-arg SSH_PUBKEY_FILE )
```

## Verification

After applying the fix, the build succeeds with the following output:

```
#18 28.18 Configuring user me, password 123456, uid 1001, gid 1001, pubkey , privkey
#18 28.19 Creating user 'me' with uid 1001 and gid 1001
#18 28.25 info: Adding user `me' ...
#18 28.25 info: Adding new user `me' (1001) with group `me (1001)' ...
#18 28.30 info: Creating home directory `/home/me' ...
#18 28.34 info: Adding new user `me' to supplemental / extra groups `users' ...
#18 28.35 info: Adding user `me' to group `users' ...

#40 6.196 ✓ Pixi successfully installed for me at /home/me/.pixi
#40 6.207 Pixi installation completed successfully!
#40 13.71 [uv] Successfully installed uv at /home/me/.local/bin/uv
#40 29.54 [nvm+node] Done.

[merge] Done. Final image: npu-dev:stage-2
```

User verification:
```bash
docker run --rm npu-dev:stage-2 id me
# Output: uid=1001(me) gid=1001(me) groups=1001(me),27(sudo),1002(ssh_users)
```

## Lessons Learned

1. **Always validate GID in addition to UID** when creating users with specific IDs
2. **Check command exit codes** for critical operations like user creation
3. **Defer group creation** until after primary user groups are established
4. **Parse all user configuration parameters** (uid, gid, etc.) from config files
5. **Test with --no-cache** to avoid masking build failures with cached layers

## Prevention

To prevent similar issues in the future:

1. **Enhanced Error Handling**
   ```bash
   adduser ... || {
     echo "ERROR: Failed to create user '$user'" >&2
     exit 1
   }
   ```

2. **Pre-flight Validation**
   ```bash
   # Validate all required parameters are set and consistent
   if [ -n "$uid" ] && [ -n "$gid" ]; then
     # Check for conflicts before proceeding
     ...
   fi
   ```

3. **Comprehensive Testing**
   - Test with various UID/GID combinations
   - Test with system-assigned vs. explicit IDs
   - Test group creation order dependencies

4. **Documentation**
   - Document GID requirements in user_config.yml
   - Add comments explaining group creation order
   - Include troubleshooting guide for user creation failures

## Related Issues

- None known at time of writing

## References

- Ubuntu adduser man page: `man adduser`
- Group management: `man groupadd`, `man groupdel`
- User configuration: `dockers/user_config.yml`
- Build logs: `/tmp/docker-build-final.log`

## Reported By
Investigation triggered by Docker build failure on 2025-11-09

## Fixed By
Commits updating:
- setup-ssh.sh
- merged.Dockerfile
- merged.env
- build-merged.sh

## Status
**RESOLVED** - Fix verified and tested successfully
