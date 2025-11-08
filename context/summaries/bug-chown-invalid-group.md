# Bug Report: chown Invalid Group Error in User Installation Scripts

## Summary

Docker build fails during stage-2 custom application installations with `chown: invalid group: 'me:me'` errors, causing cascading failures in NVM, Node.js, and subsequent tool installations.

## Severity

**HIGH** - Blocks entire Docker build process at stage-2, preventing successful image creation.

## Status

**FIXED** - 2025-11-09

## Symptoms

Build fails with the following error sequence:

```
5.835 chown: invalid group: 'me:me'
5.835 Pixi installation completed successfully!
...
13.12 chown: invalid group: 'me:me'
13.12 [uv] Successfully installed uv at /home/me/.local/bin/uv
...
13.17 chown: invalid group: 'me:me'
13.86 /home/me/.nvm/.git: Permission denied
13.86 Failed to clone nvm repo. Please report this!
13.90 sh: 1: npm: not found
...
ERROR: failed to build: process "/bin/sh -c $PEI_STAGE_DIR_2/internals/custom-on-build.sh" did not complete successfully: exit code: 127
```

## Root Cause Analysis

### The Assumption Bug

Multiple installation scripts incorrectly assumed that a user's primary group name would always match their username. This manifests in chown commands like:

```bash
chown "${TARGET_USER}:${TARGET_USER}" /path/to/file
```

This assumes `TARGET_USER` is both the username AND the group name.

### Why This Fails

In `installation/stage-1/internals/setup-ssh.sh`, user creation follows this logic:

1. **User "me" is requested** with UID=1001, GID=1001 (from `user_config.yml`)

2. **GID conflict handling** (lines 153-164):
   ```bash
   if [ -n "${gid:-}" ]; then
     if ! gid_exists "$gid"; then
       grp_name="$user"
       if groupname_exists "$grp_name"; then
         grp_name="${user}_${gid}"  # ← Creates group "me_1001" instead of "me"
       fi
       echo "Creating group '$grp_name' with gid $gid"
       groupadd -g "$gid" "$grp_name"
     fi
   fi
   ```

3. **Result**: If GID 1001 is available but group name "me" already exists (from a previous layer or system group), the script creates group "me_1001" with GID 1001.

4. **User creation** (line 171):
   ```bash
   adduser --uid "$uid" --gid "$gid" "$user"
   ```
   Creates user "me" with primary group GID 1001 (which has name "me_1001", not "me").

5. **Consequence**: When installation scripts later run `chown me:me`, they fail because:
   - User "me" exists ✓
   - Group "me" does NOT exist ✗
   - User "me"'s actual primary group is "me_1001"

### Cascading Failures

1. **Permission errors**: Files/directories owned by root aren't transferred to user
2. **NVM clone failure**: `~/.nvm/.git` has wrong permissions → clone fails
3. **Missing npm**: NVM installation incomplete → npm not available
4. **Codex/Claude Code fail**: Depend on npm → installation fails
5. **Build exit 127**: Command not found in final custom-on-build.sh step

## Files Affected

### Buggy Files (Before Fix)

1. **installation/stage-2/system/pixi/install-pixi.bash**
   - Lines 253, 285, 342, 360, 418
   - Used: `chown -R "${TARGET_USER}:${TARGET_USER}"`

2. **installation/stage-1/system/uv/install-uv.sh**
   - Lines 130, 168, 179, 252
   - Used: `chown "${TARGET_USER}:${TARGET_USER}"`

3. **installation/stage-2/system/nodejs/install-nvm-nodejs.sh**
   - Lines 133, 141, 211
   - Used: `chown "${TARGET_USER}:${TARGET_USER}"`

### Correct Reference Implementation

**installation/stage-1/internals/setup-ssh.sh** (line 256) already uses the correct approach:
```bash
primary_group=$(id -gn "$user")
chown -R "$user":"$primary_group" $ssh_dir
```

## The Fix

Replace all instances of `chown "${TARGET_USER}:${TARGET_USER}"` with:

```bash
primary_group=$(id -gn "$TARGET_USER" 2>/dev/null || echo "$TARGET_USER")
chown -R "${TARGET_USER}:${primary_group}" /path/to/dir
```

### Why This Works

- `id -gn "$TARGET_USER"` queries the actual primary group name from the system
- Falls back to `$TARGET_USER` if the id command fails
- Always uses the correct group regardless of naming conflicts

## Reproduction Steps

1. Start with base image: `nvidia/cuda:12.6.3-devel-ubuntu24.04`
2. Configure user with specific GID in `user_config.yml`:
   ```yaml
   users:
     me:
       password: '123456'
       uid: 1001
       gid: 1001
   ```
3. Run build: `./build-merged.sh`
4. Observe failure during stage-2 custom installations

## Environment

- Base Image: `nvidia/cuda:12.6.3-devel-ubuntu24.04` (Ubuntu 24.04)
- Docker Build Context: Multi-stage Dockerfile
- User Config: UID=1001, GID=1001, username="me"
- Installation Scripts: Pixi, uv, NVM/Node.js, Codex, Claude Code

## Impact Analysis

### Before Fix
- ❌ Build fails at stage-2
- ❌ No development tools installed (pixi, uv, node, npm)
- ❌ Cannot use codex or claude-code in container
- ❌ File ownership corrupted (root-owned files in user home)

### After Fix
- ✅ Build completes successfully
- ✅ All tools installed with correct permissions
- ✅ User "me" can access all installed tools
- ✅ Proper file ownership throughout user directories

## Testing Verification

After applying the fix, verify:

```bash
# Build succeeds
./build-merged.sh

# In running container, check:
docker run -it npu-dev:stage-2 bash

# Verify user and group
id me
# Expected: uid=1001(me) gid=1001(me_1001) groups=1001(me_1001),...

# Verify tool ownership
ls -la /home/me/.pixi
ls -la /home/me/.local/bin
ls -la /home/me/.nvm

# All should be owned by: me:me_1001 (or whatever the actual group is)

# Verify tools work
su - me
pixi --version
uv --version
node --version
npm --version
```

## Related Issues

- `bug-gid-conflict-user-creation-failure.md` - Documents GID conflict handling
- `bug-unbound-ssh-variables.md` - Documents SSH variable issues

## Prevention

### For Future Development

1. **Never assume group name = username**
   - Always query: `id -gn "$username"`
   - Do not hardcode: `username:username`

2. **Follow the pattern in setup-ssh.sh**
   - Lines 252-258 demonstrate correct implementation
   - Copy this pattern for consistency

3. **Test with non-standard GIDs**
   - Use GID values that commonly conflict (1001, 1000, 100)
   - Ensure group creation logic handles edge cases

4. **Add validation checks**
   ```bash
   # After user creation, verify group exists
   if ! getent group "$expected_group" >/dev/null 2>&1; then
     echo "Warning: Expected group '$expected_group' not found"
     echo "User's actual primary group: $(id -gn $username)"
   fi
   ```

## Code Review Checklist

When reviewing scripts that create users or change ownership:

- [ ] Uses `id -gn "$user"` to get primary group name
- [ ] Does NOT assume username equals group name
- [ ] Handles cross-user installs (root installing for another user)
- [ ] Falls back gracefully if id command fails
- [ ] Tests with GID conflicts in environment

## References

- POSIX User/Group Management: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/id.html
- Docker Multi-User Best Practices
- Linux File Ownership and Permissions

## Resolution Timeline

- **Discovered**: 2025-11-09 (build failures reported)
- **Diagnosed**: 2025-11-09 (root cause identified)
- **Fixed**: 2025-11-09 (all three scripts patched)
- **Verified**: 2025-11-09 (build succeeds)

## Fix Commits

Files modified:
- `installation/stage-2/system/pixi/install-pixi.bash` (3 locations)
- `installation/stage-1/system/uv/install-uv.sh` (4 locations)
- `installation/stage-2/system/nodejs/install-nvm-nodejs.sh` (3 locations)

Total: 10 chown commands corrected across 3 files.
