# SSH Key Absolute Path Support Implementation Plan

**Date:** July 3, 2025  
**Objective:** Implement absolute path and ~ expansion support for SSH key files in PeiDocker

## Overview

This implementation adds support for:
1. Absolute paths in `pubkey_file` and `privkey_file` 
2. Special `~` syntax to auto-detect system SSH keys
3. Proper handling to avoid the path bug mentioned in `ssh-key-path-bug.md`

## Current Code Analysis

### Current SSH Key Processing Flow

1. **User Config** (`SSHUserConfig`): Contains `pubkey_file`, `privkey_file`, `pubkey_text`, `privkey_text`
2. **Config Processor** (`_process_public_key_sources`, `_process_private_key_sources`): Processes key sources
3. **Utility Function** (`write_ssh_key_to_temp_file`): Writes keys to `installation/stage-1/generated/`
4. **Container Paths**: Maps to `/pei-from-host/stage-1/generated/`

### Current Limitations

- `pubkey_file` and `privkey_file` only support relative paths within project directory
- No support for absolute paths or system SSH keys
- Path must exist within `./installation/` directory

## Implementation Design

### Phase 1: Utility Functions for Path Handling

**New functions in `pei_utils.py`:**

```python
def resolve_ssh_key_path(key_path: str) -> str:
    """
    Resolve SSH key path, handling absolute paths and ~ expansion.
    
    Args:
        key_path: Path specification (relative, absolute, or ~)
        
    Returns:
        Absolute path to the SSH key file
        
    Raises:
        FileNotFoundError: If key file doesn't exist
        ValueError: If ~ syntax used but no suitable key found
    """

def find_system_ssh_key(key_type: str = 'auto') -> str:
    """
    Find system SSH key with priority order.
    
    Args:
        key_type: 'auto', 'public', or 'private'
        
    Returns:
        Absolute path to the found SSH key
        
    Priority order: id_rsa, id_dsa, id_ecdsa, id_ed25519
    """

def read_ssh_key_content(key_path: str) -> str:
    """
    Read SSH key content from absolute path.
    
    Args:
        key_path: Absolute path to SSH key file
        
    Returns:
        SSH key content as string
    """
```

### Phase 2: Enhanced Config Processing

**Modify `_process_public_key_sources` and `_process_private_key_sources`:**

1. **Path Type Detection**: Determine if path is relative, absolute, or `~`
2. **Content Reading**: For absolute paths, read content and treat like `*_text`
3. **System Key Discovery**: For `~`, find appropriate system key
4. **Existing Logic**: Keep current relative path handling unchanged

**Enhanced logic flow:**

```python
def _process_public_key_sources(self, user_name: str, user_info) -> str:
    if user_info.pubkey_file is not None and len(user_info.pubkey_file) > 0:
        pubkey_file = user_info.pubkey_file
        
        # NEW: Check if absolute path or ~ syntax
        if os.path.isabs(pubkey_file) or pubkey_file == '~':
            # Read content and process as text
            resolved_path = resolve_ssh_key_path(pubkey_file)
            key_content = read_ssh_key_content(resolved_path)
            # Write to temp file (similar to pubkey_text processing)
            relative_path = write_ssh_key_to_temp_file(
                key_content, 'pubkey', user_name, self.m_project_dir, is_public=True
            )
            return self.m_container_dir + '/' + relative_path
        else:
            # EXISTING: Relative path handling (unchanged)
            host_path = f'{self.m_project_dir}/{self.m_host_dir}/{pubkey_file}'
            if not os.path.exists(host_path):
                raise FileNotFoundError(f'Pubkey file {host_path} not found')
            return self.m_container_dir + '/' + pubkey_file
    
    # Handle pubkey_text (existing logic)
    # ...
```

### Phase 3: Path Bug Prevention

**Critical Fix**: Ensure container paths are correctly generated to avoid the bug:

- **Correct**: `/pei-from-host/stage-1/generated/temp-user-pubkey.pub`
- **Wrong**: `/pei-from-host/installation/stage-1/generated/temp-user-pubkey.pub`

The `write_ssh_key_to_temp_file` already returns the correct relative path format.

### Phase 4: System SSH Key Discovery

**Implementation for `~` syntax:**

```python
def find_system_ssh_key(key_type: str = 'auto') -> str:
    import os
    ssh_dir = os.path.expanduser('~/.ssh')
    
    # Priority order as specified
    key_priorities = ['id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519']
    
    for key_name in key_priorities:
        if key_type == 'auto' or key_type == 'private':
            private_key = os.path.join(ssh_dir, key_name)
            if os.path.exists(private_key):
                return private_key
                
        if key_type == 'auto' or key_type == 'public':
            public_key = os.path.join(ssh_dir, f'{key_name}.pub')
            if os.path.exists(public_key):
                return public_key
    
    raise ValueError(f'No SSH key found in {ssh_dir}')
```

### Phase 5: Enhanced ~ Syntax Logic

**For `~` in `pubkey_file`**: Look for `.pub` files first
**For `~` in `privkey_file`**: Look for private key files first

```python
def resolve_ssh_key_path(key_path: str, prefer_public: bool = True) -> str:
    if key_path == '~':
        key_type = 'public' if prefer_public else 'private'
        return find_system_ssh_key(key_type)
    elif os.path.isabs(key_path):
        if not os.path.exists(key_path):
            raise FileNotFoundError(f'SSH key file not found: {key_path}')
        return key_path
    else:
        # Relative path - let existing logic handle
        return key_path
```

## Testing Strategy

### Test Cases

1. **Absolute Path Public Key**:
   ```yaml
   pubkey_file: '/home/user/.ssh/id_rsa.pub'
   ```

2. **Absolute Path Private Key**:
   ```yaml
   privkey_file: '/home/user/.ssh/id_rsa'
   ```

3. **System SSH Key Discovery**:
   ```yaml
   pubkey_file: '~'
   privkey_file: '~'
   ```

4. **Mixed Usage**:
   ```yaml
   users:
     user1:
       pubkey_file: '~'  # System key
     user2:
       pubkey_file: '/custom/path/key.pub'  # Absolute path
     user3:
       pubkey_file: 'relative/key.pub'  # Relative path (existing)
   ```

### Test Configuration Files

Create test configs in `/workspace/code/PeiDocker/tests/configs/`:
- `ssh-abspath-test.yml` - Absolute path testing
- `ssh-system-keys-test.yml` - ~ syntax testing
- `ssh-mixed-paths-test.yml` - Mixed usage testing

## Implementation Priority

### High Priority
1. Utility functions for path resolution
2. Enhanced config processor logic
3. Basic absolute path support

### Medium Priority
1. System SSH key discovery (~)
2. Validation and error handling
3. Test configurations

### Low Priority
1. Advanced error messages
2. Performance optimizations
3. Documentation updates

## Risk Mitigation

### Path Bug Prevention
- Use existing `write_ssh_key_to_temp_file` function
- Ensure correct relative path generation
- Test container path generation explicitly

### Security Considerations
- Validate file permissions on absolute paths
- Ensure proper error handling for inaccessible files
- Maintain existing security for relative paths

### Backward Compatibility
- Preserve existing relative path behavior
- No changes to existing configurations
- Additive functionality only

## Success Criteria

1. ✅ Support absolute paths in `pubkey_file` and `privkey_file`
2. ✅ Support `~` syntax for system SSH key discovery
3. ✅ Maintain backward compatibility with relative paths
4. ✅ Avoid the container path bug from previous implementation
5. ✅ Proper error handling for missing files
6. ✅ Test cases pass for all scenarios

## Implementation Steps

1. **Create utility functions** in `pei_utils.py`
2. **Enhance config processor** methods for path handling
3. **Add validation** for absolute paths and ~ syntax
4. **Create test configurations** for verification
5. **Test end-to-end** functionality with real SSH keys
6. **Document** the new features

## Dependencies

- Python `os` module for path operations
- Existing `write_ssh_key_to_temp_file` function
- Existing SSH key validation utilities

## Timeline

**Phase 1-2**: 2-3 hours (utility functions + config processor)  
**Phase 3-4**: 1-2 hours (testing + validation)  
**Phase 5**: 1 hour (documentation)  

**Total**: 4-6 hours