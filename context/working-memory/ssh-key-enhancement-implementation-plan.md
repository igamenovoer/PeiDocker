# SSH Key Enhancement Implementation Plan

**Date:** July 1, 2025  
**Objective:** Implement inline SSH key specification features for PeiDocker

## Overview

This plan implements the SSH key enhancement specifications to allow users to:
1. Specify public keys directly as text (`pubkey_text`)
2. Specify private keys directly as text (`privkey_text`) or files (`privkey_file`)
3. Automatically generate public keys from private keys
4. Handle key validation and conflict detection

## Current State Analysis

### Existing SSH Configuration Structure

**User Config (`SSHUserConfig`):**
```python
class SSHUserConfig:
    password: str | None = None
    pubkey_file: str | None = None
    uid: int | None = None
```

**Template Config (`base-image-gen.yml`):**
```yaml
ssh:
  enable: true
  username: 'me,you'
  password: '123456,654321'
  uid: '1000,1001'
  pubkey_file: ''  # comma-separated paths
```

### Current Processing Flow

1. `user_config.yml` → Python config objects
2. Config validation in `SSHUserConfig.__attrs_post_init__`
3. Processing in `PeiConfigProcessor._apply_ssh_to_x_compose()`
4. Writing files and updating template paths

## Implementation Plan

### Phase 1: Data Structure Updates

#### 1.1 Update `SSHUserConfig` class in `user_config.py`

**New fields to add:**
```python
@define(kw_only=True)
class SSHUserConfig:
    password: str | None = field(default=None)
    pubkey_file: str | None = field(default=None)
    pubkey_text: str | None = field(default=None)     # NEW
    privkey_file: str | None = field(default=None)    # NEW
    privkey_text: str | None = field(default=None)    # NEW
    uid: int | None = field(default=None)
```

#### 1.2 Update validation logic in `__attrs_post_init__`

**Validation rules:**
1. Either `password` or one of the key options must be provided
2. `pubkey_file` and `pubkey_text` are mutually exclusive
3. `privkey_file` and `privkey_text` are mutually exclusive
4. SSH key format validation for text fields

**Implementation:**
```python
def __attrs_post_init__(self):
    # Existing password validation
    if self.password is not None:
        assert ' ' not in self.password and ',' not in self.password, \
               f'Password cannot contain space or comma: {self.password}'
    
    # Public key conflict validation
    if self.pubkey_file is not None and self.pubkey_text is not None:
        raise ValueError('Cannot specify both pubkey_file and pubkey_text')
    
    # Private key conflict validation
    if self.privkey_file is not None and self.privkey_text is not None:
        raise ValueError('Cannot specify both privkey_file and privkey_text')
    
    # At least one authentication method required
    has_password = self.password is not None
    has_pubkey = self.pubkey_file is not None or self.pubkey_text is not None
    has_privkey = self.privkey_file is not None or self.privkey_text is not None
    
    if not (has_password or has_pubkey or has_privkey):
        raise ValueError('Must provide at least one authentication method: password, public key, or private key')
    
    # Validate SSH key formats
    if self.pubkey_text is not None:
        self._validate_public_key_format(self.pubkey_text)
    
    if self.privkey_text is not None:
        self._validate_private_key_format(self.privkey_text)
```

#### 1.3 Add SSH key validation methods

**Methods to implement:**
```python
def _validate_public_key_format(self, key_text: str) -> None:
    """Validate SSH public key format"""
    
def _validate_private_key_format(self, key_text: str) -> None:
    """Validate SSH private key format and detect key type"""
    
def _extract_key_type_from_private_key(self, key_text: str) -> str:
    """Extract key type (rsa, ed25519, ecdsa) from private key"""
```

### Phase 2: Configuration Template Updates

#### 2.1 Update `config-template-full.yml`

**Add new SSH key options with documentation:**
```yaml
ssh:
  users:
    me:
      password: '123456'
      
      # Public key options (mutually exclusive)
      pubkey_file: null  # Path to public key file
      pubkey_text: null  # Direct public key content (conflicts with pubkey_file)
      
      # Private key options (mutually exclusive)
      privkey_file: null  # Path to private key file  
      privkey_text: null  # Direct private key content (conflicts with privkey_file)
      
      uid: 1000
```

**Add detailed examples and documentation section:**
```yaml
# SSH Key Configuration Examples:
#
# Example 1: Using public key text
# users:
#   developer:
#     password: 'devpass'
#     pubkey_text: |
#       ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDFFy2DpsaaLcixgYgT8+7GxVR5mRGOx7urSe4rKjZ5G user@host
#
# Example 2: Using private key text (auto-generates public key)
# users:
#   developer:
#     privkey_text: |
#       -----BEGIN OPENSSH PRIVATE KEY-----
#       b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABCLeSpkKu
#       ...
#       -----END OPENSSH PRIVATE KEY-----
#
# Example 3: Using both public and private keys (NOT PAIRED)
# users:
#   developer:
#     pubkey_text: |
#       ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDFFy2DpsaaLcixgYgT8+7GxVR5mRGOx7urSe4rKjZ5G user@host
#     privkey_text: |
#       -----BEGIN OPENSSH PRIVATE KEY-----
#       ...different key content...
#       -----END OPENSSH PRIVATE KEY-----
```

#### 2.2 Update `base-image-gen.yml` template

**Add `privkey_file` support:**
```yaml
ssh:
  enable: true
  username: 'me,you'
  password: '123456,654321'
  uid: '1000,1001'
  pubkey_file: ''   # comma-separated public key file paths
  privkey_file: ''  # NEW: comma-separated private key file paths
```

### Phase 3: Configuration Processing Updates

#### 3.1 Create SSH key utility functions in `pei_utils.py`

**Functions to implement:**
```python
def generate_public_key_from_private(private_key_text: str) -> str:
    """Generate SSH public key from private key text"""
    
def detect_ssh_key_type(private_key_text: str) -> str:
    """Detect SSH key type (rsa, ed25519, ecdsa) from private key"""
    
def validate_ssh_public_key(public_key_text: str) -> bool:
    """Validate SSH public key format"""
    
def validate_ssh_private_key(private_key_text: str) -> bool:
    """Validate SSH private key format"""
    
def write_ssh_key_to_temp_file(key_content: str, key_type: str, user_name: str, project_dir: str) -> str:
    """Write SSH key content to temporary file and return relative path"""
```

#### 3.2 Update `_apply_ssh_to_x_compose()` in `config_processor.py`

**Enhanced processing logic:**
1. **Key file generation:** Convert `pubkey_text` and `privkey_text` to temporary files
2. **Public key generation:** Auto-generate public keys from private keys
3. **Path management:** Update file paths in the template
4. **Validation:** Ensure all key files exist

**Implementation approach:**
```python
def _apply_ssh_to_x_compose(self, ssh_config: Optional[SSHConfig], build_compose: DictConfig):
    # ...existing code...
    
    _ssh_pubkeys: list[str] = []
    _ssh_privkeys: list[str] = []
    
    for name, info in ssh_users.items():
        # Handle public key sources
        pubkey_path = self._process_public_key_sources(name, info)
        if pubkey_path:
            _ssh_pubkeys.append(pubkey_path)
        else:
            _ssh_pubkeys.append('')
            
        # Handle private key sources  
        privkey_path = self._process_private_key_sources(name, info)
        if privkey_path:
            _ssh_privkeys.append(privkey_path)
        else:
            _ssh_privkeys.append('')
    
    # Update template
    oc_set(build_compose, 'ssh.pubkey_file', ','.join(_ssh_pubkeys))
    oc_set(build_compose, 'ssh.privkey_file', ','.join(_ssh_privkeys))
```

#### 3.3 Implement key processing helper methods

**Methods to add to `PeiConfigProcessor`:**
```python
def _process_public_key_sources(self, user_name: str, user_info: SSHUserConfig) -> str:
    """Process public key from file or text, return container path"""
    
def _process_private_key_sources(self, user_name: str, user_info: SSHUserConfig) -> str:
    """Process private key from file or text, generate public key, return container path"""
    
def _write_key_content_to_file(self, content: str, file_name: str) -> str:
    """Write key content to temporary file in project directory"""
    
def _generate_temp_file_path(self, user_name: str, key_type: str, is_public: bool) -> str:
    """Generate temporary file path for SSH keys"""
```

### Phase 4: File Management Strategy

#### 4.1 Temporary file structure

**Directory layout:**
```
project_dir/
├── installation/
│   └── stage-1/
│       └── system/
│           └── ssh/
│               └── keys/
│                   ├── temp-{user}-pubkey.pub
│                   ├── temp-{user}-privkey
│                   └── temp-{user}-generated-pubkey.pub
```

#### 4.2 File naming convention

**Template:**
- Public key files: `temp-{username}-pubkey.pub`
- Private key files: `temp-{username}-privkey`
- Generated public keys: `temp-{username}-generated-pubkey.pub`

### Phase 5: Docker Integration

#### 5.1 Update Dockerfile templates

**Add private key handling to Dockerfile generation:**
```dockerfile
# Copy private keys if specified
COPY ${privkey_file} /home/{user}/.ssh/id_{keytype}
RUN chmod 600 /home/{user}/.ssh/id_{keytype}
RUN chown {user}:{user} /home/{user}/.ssh/id_{keytype}

# Generate and append public key to authorized_keys
RUN ssh-keygen -y -f /home/{user}/.ssh/id_{keytype} >> /home/{user}/.ssh/authorized_keys
```

### Phase 6: Testing Strategy

#### 6.1 Unit tests

**Test cases for `user_config.py`:**
- Validation of mutually exclusive options
- SSH key format validation
- Error handling for invalid keys

**Test cases for `config_processor.py`:**
- Key file generation from text
- Public key generation from private key
- Path resolution and file creation

#### 6.2 Integration tests

**Test scenarios:**
1. Single user with `pubkey_text`
2. Single user with `privkey_text`
3. Single user with both `pubkey_text` and `privkey_text` (unpaired)
4. Multiple users with mixed key types
5. Error scenarios (conflicts, invalid formats)

#### 6.3 End-to-end tests

**Full workflow tests:**
1. Create project with new SSH key features
2. Configure with test data from specifications
3. Build and run container
4. Verify SSH access with generated keys

### Phase 7: Documentation Updates

#### 7.1 Configuration documentation

**Update `docs/index.md`:**
- Add SSH key specification section
- Include examples with new features
- Document security considerations

#### 7.2 Example configurations

**Create new example files:**
- `ssh-keys-inline.yml` - Demonstrates inline key specification
- `ssh-keys-mixed.yml` - Mixed file and inline keys
- `ssh-keys-private-auto.yml` - Auto-generated public keys

## Implementation Priority

### High Priority (Core Functionality)
1. Data structure updates (`SSHUserConfig`)
2. Basic validation logic
3. Key file generation from text
4. Public key generation from private key

### Medium Priority (Integration)
1. Configuration processor updates
2. Template updates
3. Docker integration
4. Basic testing

### Low Priority (Polish)
1. Comprehensive documentation
2. Advanced validation
3. Error message improvements
4. Performance optimizations

## Security Considerations

1. **Temporary file security:** Ensure proper permissions (600) on generated key files
2. **Key validation:** Validate SSH key formats to prevent injection
3. **File cleanup:** Consider cleanup strategies for temporary files
4. **Key separation:** Maintain clear separation between public and private keys

## Dependencies

**Required Python packages:**
- `cryptography` - For SSH key validation and generation
- `paramiko` - Alternative for SSH key operations

**Installation:**
```bash
pip install cryptography paramiko
```

## Risk Assessment

**Low Risk:**
- Configuration validation changes
- Template updates
- Documentation

**Medium Risk:**
- SSH key generation logic
- File path management
- Docker integration

**High Risk:**
- Private key handling security
- Key format validation
- Compatibility with existing configurations

## Success Criteria

1. ✅ Users can specify SSH keys inline using `pubkey_text` and `privkey_text`
2. ✅ Automatic public key generation from private keys works correctly
3. ✅ Validation prevents conflicting configurations
4. ✅ Generated containers have proper SSH access with new keys
5. ✅ Existing configurations continue to work unchanged
6. ✅ Documentation clearly explains new features with examples

## Timeline Estimate

**Phase 1-2 (Data structures & templates):** 2-3 days  
**Phase 3-4 (Processing logic):** 3-4 days  
**Phase 5 (Docker integration):** 2-3 days  
**Phase 6-7 (Testing & documentation):** 2-3 days  

**Total estimated time:** 9-13 days

## Next Steps

1. Start with Phase 1: Update `SSHUserConfig` data structure
2. Implement basic validation logic
3. Create SSH key utility functions
4. Test with provided test data
5. Iterate and refine based on testing results
