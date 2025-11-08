# Bug Report: Bash Array Expansion Errors in run-merged.sh

## Summary

The `run-merged.sh` script fails to execute due to two critical bash syntax errors related to improper array handling, resulting in "bad substitution" errors and "invalid empty volume spec" errors.

## Severity

**CRITICAL** - Script completely unusable; prevents running containers from the built image.

## Status

**FIXED** - 2025-11-09

## Symptoms

### Error 1: Bad Substitution
```bash
$ ./run-merged.sh
./run-merged.sh: line 121: ${#POSITIONAL[@]:-0}: bad substitution
```

### Error 2: Invalid Empty Volume Spec
```bash
$ ./run-merged.sh
docker run -it --rm -p 40012:22 -p '' -v app:/hard/volume/app -v data:/hard/volume/data \
  -v /workspace:/hard/volume/workspace -v home_me:/home/me -v '' \
  --add-host host.docker.internal:host-gateway --gpus all --name pei-stage-2 npu-dev:stage-2
docker: invalid empty volume spec
```

Notice the empty arguments: `-p ''` and `-v ''`

## Root Cause Analysis

### Bug 1: Invalid Array Length with Default Value Operator

**Location**: Line 121 (original)
```bash
[[ ${#POSITIONAL[@]:-0} -gt 0 ]] && cmd+=( "${POSITIONAL[@]}" )
```

**The Problem**: Bash does not allow combining array length syntax `${#array[@]}` with default value operators `${var:-default}`.

**Why It's Wrong**:
- `${#array[@]}` is for getting array length
- `${var:-default}` is for scalar variable default values
- These operators are mutually exclusive in bash syntax

**Why It Seemed Logical**:
Developers often use `${var:-0}` for scalars to provide a default when unset. The author incorrectly assumed this pattern could extend to array lengths to "safely" return 0 if the array is somehow uninitialized.

**Why It's Unnecessary**:
Since `POSITIONAL=()` is explicitly initialized at line 33, `${#POSITIONAL[@]}` will always work correctly, returning `0` for empty arrays without needing a default value operator.

### Bug 2: Empty String Expansion from Array Default Operator

**Location**: Lines 99, 103 (original)
```bash
for p in "${CLI_PORTS[@]:-}"; do cmd+=( -p "$p" ); done
for v in "${CLI_VOLS[@]:-}"; do cmd+=( -v "$v" ); done
```

**The Problem**: Using `"${array[@]:-}"` on an empty array causes it to expand to **one iteration with an empty string** instead of **zero iterations**.

**The Mechanics**:
```bash
# Correct behavior (no :-):
CLI_PORTS=()
for p in "${CLI_PORTS[@]}"; do
  echo "Iteration: [$p]"
done
# Output: (nothing - zero iterations)

# Buggy behavior (with :-):
CLI_PORTS=()
for p in "${CLI_PORTS[@]:-}"; do
  echo "Iteration: [$p]"
done
# Output: Iteration: []  (one iteration with empty string!)
```

**Why It Happens**:
The `:-` operator is designed for scalar variables:
- `${scalar:-default}` - if scalar is unset/empty, use default
- When applied to `"${array[@]:-}"`, bash interprets the empty array as "empty" and substitutes with the default (which is empty string), creating one iteration

**Cascading Effect**:
1. Empty `CLI_PORTS` array → expands to `""`
2. Loop iterates once with `p=""`
3. Command becomes `cmd+=( -p "" )`
4. Final docker command: `docker run ... -p '' ...`
5. Docker rejects: "invalid empty volume spec"

**Defensive Gap**:
The code for `RUN_PORTS` and `RUN_VOLUMES` (unquoted word splitting) includes defensive checks:
```bash
for p in $RUN_PORTS; do [[ -n "$p" ]] && cmd+=( -p "$p" ); done
```

But the CLI array iterations lacked these checks:
```bash
for p in "${CLI_PORTS[@]:-}"; do cmd+=( -p "$p" ); done  # No [[ -n "$p" ]] check!
```

## Files Affected

**File**: `dockers/run-merged.sh`

### Buggy Code (Before Fix)

**Line 121**:
```bash
[[ ${#POSITIONAL[@]:-0} -gt 0 ]] && cmd+=( "${POSITIONAL[@]}" )
```

**Lines 99, 103**:
```bash
for p in "${CLI_PORTS[@]:-}"; do cmd+=( -p "$p" ); done
for v in "${CLI_VOLS[@]:-}"; do cmd+=( -v "$v" ); done
```

## The Fix

### Fix 1: Remove Invalid Default Operator from Array Length

**Line 121** (fixed):
```bash
[[ ${#POSITIONAL[@]} -gt 0 ]] && cmd+=( "${POSITIONAL[@]}" )
```

**Why This Works**:
- `POSITIONAL=()` is always initialized (line 33)
- `${#POSITIONAL[@]}` safely returns `0` for empty arrays
- No default value operator needed

### Fix 2: Remove Default Operator and Add Empty Checks

**Lines 99, 103** (fixed):
```bash
for p in "${CLI_PORTS[@]}"; do [[ -n "$p" ]] && cmd+=( -p "$p" ); done
for v in "${CLI_VOLS[@]}"; do [[ -n "$v" ]] && cmd+=( -v "$v" ); done
```

**Why This Works**:
- `"${array[@]}"` without `:-` correctly expands to zero iterations when empty
- Added `[[ -n "$p" ]]` / `[[ -n "$v" ]]` for defensive programming (matches pattern used for `RUN_PORTS`/`RUN_VOLUMES`)
- Even if somehow an empty string gets into the array, it won't be added to the command

## Reproduction Steps

1. Build the Docker image successfully
2. Attempt to run the container:
   ```bash
   cd /workspace/code/npu-design-tutorial/dockers
   ./run-merged.sh
   ```
3. Observe "bad substitution" error at line 121
4. If line 121 is fixed in isolation, observe "invalid empty volume spec" error

## Environment

- Shell: bash (with `set -euo pipefail`)
- Arrays initialized: `CLI_PORTS=()`, `CLI_VOLS=()`, `POSITIONAL=()`
- Docker version: Any

## Impact Analysis

### Before Fix
- ❌ Script fails immediately with syntax error
- ❌ Cannot run containers even with successful builds
- ❌ CLI port/volume options would add empty specs to docker command
- ❌ Complete blocker for using the built images

### After Fix
- ✅ Script executes without errors
- ✅ Containers run with correct port/volume mappings
- ✅ Empty arrays handled correctly (zero iterations)
- ✅ Defensive checks prevent empty values from reaching docker command

## Testing Verification

### Test 1: Basic Execution
```bash
./run-merged.sh
# Should produce clean docker command without empty specs
```

### Test 2: With CLI Arguments
```bash
./run-merged.sh -p 8080:80 -v /tmp:/mnt/tmp
# Should add ports and volumes correctly
```

### Test 3: With Empty Arrays (Edge Case)
```bash
# In the script, CLI_PORTS and CLI_VOLS start empty
# Verify they don't create -p '' or -v '' in the command
./run-merged.sh
# Check output doesn't contain: -p '' or -v ''
```

### Expected Docker Command
```bash
docker run -it --rm \
  -p 40012:22 \
  -v app:/hard/volume/app \
  -v data:/hard/volume/data \
  -v /workspace:/hard/volume/workspace \
  -v home_me:/home/me \
  --add-host host.docker.internal:host-gateway \
  --gpus all \
  --name pei-stage-2 \
  npu-dev:stage-2
```

## Bash Array Best Practices

### DO: Use Correct Array Expansion

```bash
# Declare array
myarray=()

# Check if array has elements
if [[ ${#myarray[@]} -gt 0 ]]; then
  echo "Array has ${#myarray[@]} elements"
fi

# Iterate over array (empty array = zero iterations)
for item in "${myarray[@]}"; do
  echo "$item"
done

# Iterate with defensive check
for item in "${myarray[@]}"; do
  [[ -n "$item" ]] && process "$item"
done
```

### DON'T: Use Invalid Syntax Combinations

```bash
# ❌ WRONG: Cannot combine array length with default operator
[[ ${#array[@]:-0} -gt 0 ]]

# ❌ WRONG: Creates empty string iteration on empty arrays
for item in "${array[@]:-}"; do

# ❌ WRONG: Missing defensive check when values might be empty
for item in "${array[@]}"; do
  cmd+=( -p "$item" )  # Could add -p '' if item is empty
done
```

### Array vs Scalar Default Values

```bash
# ✅ Scalars: use :- for defaults
count=${count:-0}
name=${name:-"default"}

# ✅ Arrays: no :- needed for expansions
array=()
for item in "${array[@]}"; do  # Zero iterations when empty - no :- needed
  echo "$item"
done

# ✅ Array length: no :- needed
if [[ ${#array[@]} -gt 0 ]]; then  # Always works - no :- needed
  echo "Has elements"
fi
```

## Related Bash Pitfalls

### The Word Splitting vs Array Quoting Dichotomy

Notice the inconsistency in the original code:

```bash
# Unquoted (word splitting) - works fine with spaces in values
for p in $RUN_PORTS; do [[ -n "$p" ]] && cmd+=( -p "$p" ); done

# Quoted array (preserves elements) - was missing defensive check
for p in "${CLI_PORTS[@]:-}"; do cmd+=( -p "$p" ); done
```

**Why Different?**
- `$RUN_PORTS` is a space-separated string from merged.env
- `${CLI_PORTS[@]}` is a true bash array from CLI parsing
- Arrays need quotes to preserve elements; strings need word splitting
- Both should have `[[ -n "$item" ]]` checks for safety

## Prevention Guidelines

### For Code Review

When reviewing bash scripts with arrays:

- [ ] Array length checks use `${#array[@]}` without `:-` operator
- [ ] Array expansions use `"${array[@]}"` without `:-` suffix
- [ ] Loops over arrays include `[[ -n "$var" ]]` checks when values might be empty
- [ ] Arrays are always initialized before use (e.g., `myarray=()`)
- [ ] No mixing of array syntax with scalar default operators

### For Development

When writing bash array code:

1. **Initialize arrays explicitly**
   ```bash
   myarray=()  # Start with empty array
   ```

2. **Check length correctly**
   ```bash
   if [[ ${#myarray[@]} -gt 0 ]]; then
   ```

3. **Iterate safely**
   ```bash
   for item in "${myarray[@]}"; do
     [[ -n "$item" ]] && use "$item"
   done
   ```

4. **Never use `:-` with array expansions**
   - `"${array[@]}"` ✅
   - `"${array[@]:-}"` ❌

## References

- Bash Manual: Arrays - https://www.gnu.org/software/bash/manual/html_node/Arrays.html
- Bash Pitfalls: Array Expansion - https://mywiki.wooledge.org/BashPitfalls
- ShellCheck: Bash array best practices
- Stack Overflow: "Why does ${array[@]:-} create an empty element?"

## Resolution Timeline

- **Discovered**: 2025-11-09 (user attempted to run container)
- **Error 1 Found**: Line 121 "bad substitution"
- **Error 2 Found**: Lines 99, 103 "invalid empty volume spec"
- **Root Cause**: Misuse of `:-` operator with arrays
- **Fixed**: 2025-11-09 (both errors corrected)
- **Verified**: Script executes successfully

## Fix Summary

| Line | Buggy Code | Fixed Code | Reason |
|------|------------|------------|--------|
| 121 | `${#POSITIONAL[@]:-0}` | `${#POSITIONAL[@]}` | Cannot combine array length with `:-` |
| 99 | `"${CLI_PORTS[@]:-}"` | `"${CLI_PORTS[@]}"` + check | `:-` creates empty iteration |
| 103 | `"${CLI_VOLS[@]:-}"` | `"${CLI_VOLS[@]}"` + check | `:-` creates empty iteration |

**Total**: 3 fixes across 1 file

## Lessons Learned

1. **Bash array syntax is not intuitive**: Operators that work for scalars don't always work for arrays
2. **Default operators are for scalars**: `:-` is specifically for undefined/empty scalar variables
3. **Empty arrays are not "unset"**: An initialized empty array `myarray=()` doesn't need default values
4. **Always test with empty arrays**: Edge cases with zero elements often reveal bugs
5. **Consistency matters**: If one loop has defensive checks (`[[ -n "$p" ]]`), all should
6. **ShellCheck is your friend**: Static analysis tools would catch `${#array[@]:-0}`

## See Also

- `bug-chown-invalid-group.md` - Another example of assumption-based bugs
- `bug-gid-conflict-user-creation-failure.md` - User/group handling issues
- `bug-unbound-ssh-variables.md` - Variable handling in SSH setup
