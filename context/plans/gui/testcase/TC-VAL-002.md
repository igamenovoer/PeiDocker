# Test Case: TC-VAL-002

## Test Information
- **Title**: SSH Configuration Validation and Settings
- **Category**: Validation
- **Priority**: Medium
- **Test Type**: Manual
- **Estimated Duration**: 18 minutes
- **Prerequisites**: GUI launched, wizard at SSH configuration step
- **Related Requirements**: task-gui-new.md SSH Configuration section

## Test Objective
Verify SSH configuration options work correctly with proper validation and conditional display

## Test Scope  
- **Components**: SSH Configuration screen, validation functions, conditional UI
- **Functions**: SSH field validation, public/private key handling, root access config
- **Data Flow**: SSH options → Validation → Conditional display → Configuration storage

## Test Data
### Input Data - Valid Cases
- **ssh_user**: "testuser" (alphanumeric, no spaces)
- **ssh_password**: "validpass123" (no spaces/commas)
- **ssh_uid**: 1100 (avoid system conflicts)
- **container_port**: 22 (standard SSH port)
- **host_port**: 2222 (non-conflicting host port)
- **public_key**: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ..." (valid format)
- **private_key_path**: "/home/user/.ssh/id_rsa" (valid file path)
- **root_password**: "rootpass" (for root access)

### Input Data - Invalid Cases
- **ssh_user**: "", "test user", "user@domain" (empty, spaces, special chars)
- **ssh_password**: "pass,word", "pass word", "" (comma, space, empty when enabled)
- **ssh_uid**: "abc", "-1", "0", "99" (non-numeric, negative, too low)
- **container_port**: "abc", "0", "65536" (non-numeric, out of range)
- **host_port**: "abc", "0", "65536", "22" (invalid, or conflicts)
- **public_key**: "invalid-key", "ssh-dss ABC..." (malformed key)

### Expected Outputs
- **Conditional Display**: SSH settings visible only when SSH enabled
- **Validation Messages**: Clear error messages for invalid inputs
- **Key Options**: Public/private key options work correctly
- **Root Access**: Root SSH configuration conditional display

## Test Steps
| Step | Action | Input | Expected Result |
|------|--------|-------|-----------------|
| **SSH Enable/Disable Testing** |
| 1 | Navigate to SSH config | Go to Step 2 | SSH Configuration screen appears |
| 2 | Verify default state | Check initial settings | SSH disabled by default, settings hidden |
| 3 | Enable SSH | Select "Yes" radio button | SSH settings section becomes visible |
| 4 | Disable SSH | Select "No" radio button | SSH settings section hidden |
| 5 | Re-enable SSH | Select "Yes" again | Settings visible with cleared values |
| **SSH User Configuration** |
| 6 | Test empty username | Clear username field | Error: "SSH username is required" |
| 7 | Test username with spaces | "test user" | Error: "Username cannot contain spaces" |
| 8 | Test username with special chars | "user@domain" | Error: "Invalid characters in username" |
| 9 | Test valid username | "testuser" | Validation passes |
| **Password Configuration** |
| 10 | Test empty password | Clear password field | Error: "Password is required when SSH enabled" |
| 11 | Test password with comma | "pass,word" | Error: "Password cannot contain commas or spaces" |
| 12 | Test password with space | "pass word" | Error: "Password cannot contain commas or spaces" |
| 13 | Test valid password | "validpass123" | Validation passes |
| **UID Configuration** |
| 14 | Test non-numeric UID | "abc" | Error: "UID must be a valid number" |
| 15 | Test negative UID | "-1" | Error: "UID must be positive" |
| 16 | Test system UID | "100" | Warning: "UID may conflict with system users" |
| 17 | Test valid UID | "1100" | Validation passes |
| **Port Configuration** |
| 18 | Test invalid container port | "abc" | Error: "Container port must be a valid number" |
| 19 | Test container port out of range | "65536" | Error: "Port must be between 1 and 65535" |
| 20 | Test invalid host port | "0" | Error: "Host port must be between 1 and 65535" |
| 21 | Test port conflict | "22" for host port | Warning: "Port 22 may conflict with host SSH" |
| 22 | Test valid ports | 22 (container), 2222 (host) | Validation passes |
| **Public Key Configuration** |
| 23 | Enable public key auth | Select "Yes" for public key | Public key options visible |
| 24 | Test system key option | Select "Use system key (~)" | Option selected, no text input needed |
| 25 | Test manual key entry | Select "Enter key text" | Text area appears for key input |
| 26 | Test invalid key format | "invalid-key-format" | Error: "Invalid SSH public key format" |
| 27 | Test valid key | Valid SSH public key | Key accepted |
| 28 | Disable public key auth | Select "No" | Public key options hidden |
| **Private Key Configuration** |
| 29 | Enable private key | Select "Yes" for private key | Private key path input visible |
| 30 | Test empty path | Clear private key path | Error: "Private key path required when enabled" |
| 31 | Test tilde expansion | "~/.ssh/id_rsa" | Path accepted with tilde notation |
| 32 | Test absolute path | "/home/user/.ssh/id_rsa" | Absolute path accepted |
| 33 | Disable private key | Select "No" | Private key input hidden |
| **Root Access Configuration** |
| 34 | Enable root access | Select "Yes" for root SSH | Root password field appears |
| 35 | Test empty root password | Clear root password | Error: "Root password required when enabled" |
| 36 | Test valid root password | "rootpass" | Password accepted |
| 37 | Disable root access | Select "No" | Root password field hidden |
| **Integration Testing** |
| 38 | Configure all SSH options | Fill all fields with valid data | All validations pass |
| 39 | Test navigation with valid config | Click Next | Move to next step successfully |
| 40 | Return and verify persistence | Click Prev, then Next | All SSH settings preserved |

## Boundary Conditions
- **Username**: 1-32 characters, alphanumeric and underscore only
- **Password**: Any characters except space and comma
- **UID**: 1000-65535 recommended, warnings for system UIDs
- **Ports**: 1-65535, warnings for common conflict ports
- **SSH Key**: Valid SSH public key format (ssh-rsa, ssh-ed25519, etc.)
- **File Paths**: Valid system paths, tilde expansion supported

## Error Scenarios
- **Disabled SSH with required fields**: Fields cleared when SSH disabled
- **Invalid combinations**: All validation errors prevent navigation
- **Key format validation**: Only valid SSH key formats accepted
- **Port conflicts**: Warnings for common conflicting ports
- **System UID warnings**: Guidance for avoiding system conflicts

## Success Criteria
- [ ] SSH settings only visible when SSH enabled
- [ ] All input fields validate according to requirements
- [ ] Clear error messages for all invalid inputs
- [ ] Public key authentication options work correctly
- [ ] Private key path handling supports tilde expansion
- [ ] Root access configuration conditional display works
- [ ] Valid configuration allows navigation to next step
- [ ] Invalid configuration prevents navigation
- [ ] SSH disabled state clears all SSH-related configuration
- [ ] Field persistence during navigation back/forth
- [ ] Warning messages for potential conflicts
- [ ] All SSH configuration reflected in final output

## Cleanup Requirements
- Reset SSH configuration to default state
- Clear all input fields
- Return to consistent test state