# SSH Key Advanced Configuration

## Overview

PeiDocker supports advanced SSH key configuration including absolute paths, system SSH key discovery, and proper handling of encrypted private keys.

## Features

### 1. SSH Key Sources

#### Public Key Sources (mutually exclusive)
- `pubkey_file`: Path to public key file
- `pubkey_text`: Inline public key content

#### Private Key Sources (mutually exclusive)
- `privkey_file`: Path to private key file  
- `privkey_text`: Inline private key content

### 2. Path Support

#### Relative Paths (legacy behavior)
```yaml
users:
  developer:
    pubkey_file: 'custom/my-key.pub'    # Relative to installation directory
```

#### Absolute Paths
```yaml
users:
  developer:
    pubkey_file: '/home/user/.ssh/id_rsa.pub'    # Absolute path
    privkey_file: '/home/user/.ssh/id_rsa'       # Absolute path
```

#### System SSH Key Discovery (`~` syntax)
```yaml
users:
  developer:
    pubkey_file: '~'     # Auto-discovers system public key
  admin:
    privkey_file: '~'    # Auto-discovers system private key
```

**Discovery Priority Order**: `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`

### 3. Encrypted Private Key Handling

#### Key Behavior Changes
- **No automatic decryption**: Encrypted private keys are copied as-is without passphrase attempts
- **Standard filenames**: Private keys are installed with standard SSH names:
  - `id_rsa` for RSA and OpenSSH format keys
  - `id_ecdsa` for ECDSA keys  
  - `id_dsa` for DSA keys
- **No public key auto-generation**: When encrypted private keys are provided, no `.pub` files are created

#### Manual Public Key Generation
If you need a public key from an encrypted private key, generate it manually:

```bash
# Inside the container
ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub
```

### 4. Configuration Examples

#### Basic Usage
```yaml
stage_1:
  ssh:
    enable: true
    users:
      developer:
        password: 'dev123'
        pubkey_file: '~'                    # Auto-discover public key
      admin:
        password: 'admin123'  
        privkey_file: '~'                   # Auto-discover private key
```

#### Mixed Configuration
```yaml
stage_1:
  ssh:
    enable: true
    users:
      user1:
        password: 'pass1'
        pubkey_file: '/home/me/.ssh/id_rsa.pub'     # Absolute path
      user2:
        password: 'pass2'
        privkey_file: '~'                           # System discovery
      user3:
        password: 'pass3'
        pubkey_text: |                              # Inline content
          ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB...
```

## Implementation Details

### File Generation
- User-provided keys are copied to `installation/stage-1/generated/`
- Container paths use `/pei-from-host/stage-1/generated/`
- File permissions: 644 for public keys, 600 for private keys

### Key Installation Process
1. **Check for user-provided private key first**
2. **Skip auto-generation if user key provided**
3. **Install with standard filename** (`id_rsa`, `id_ecdsa`, etc.)
4. **Remove conflicting `.pub` files** for encrypted keys
5. **Generate keys only if no user key provided**
6. **Add public keys to authorized_keys**

### Backward Compatibility
- All existing configurations continue to work
- Relative paths still supported
- Auto-generation still happens when no user keys provided

## Security Considerations

### Safe Practices
- Private keys are copied without modification
- No automatic decryption attempts
- Proper file permissions enforced
- No passphrase prompting during build

### Testing
- Repository test keys available for safe testing
- Use UID ≥ 1100 to avoid system conflicts
- Test configurations in `tests/configs/`

## Troubleshooting

### Common Issues

#### "incorrect passphrase supplied to decrypt private key"
- **Cause**: Older versions tried to auto-decrypt
- **Solution**: Update to latest version - no decryption is attempted

#### "SSH key not found"
- **Cause**: Wrong path or missing key
- **Solution**: Verify file exists and use absolute path

#### "Permission denied (publickey)"
- **Cause**: No public key available for authentication
- **Solution**: Either provide a public key or generate one manually from your private key

### Manual Public Key Generation
```bash
# Extract public key from encrypted private key (requires passphrase)
ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub

# Verify the key
cat ~/.ssh/id_rsa.pub
```

## Status: ✅ COMPLETED

All features implemented and documented:
- [x] Absolute path support
- [x] System SSH key discovery (`~` syntax)
- [x] Encrypted private key handling without decryption
- [x] Standard SSH filename usage
- [x] Comprehensive testing suite
- [x] Updated documentation