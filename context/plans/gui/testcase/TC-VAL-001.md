# Test Case: TC-VAL-001

## Test Information
- **Title**: Input Validation Across All Steps
- **Category**: Validation
- **Priority**: High
- **Test Type**: Manual
- **Estimated Duration**: 20 minutes
- **Prerequisites**: GUI launched, wizard accessible
- **Related Requirements**: task-gui-new.md validation requirements

## Test Objective
Verify input validation works correctly for all input fields across all wizard steps

## Test Scope  
- **Components**: All step screens with input fields, validation functions
- **Functions**: Field validation, error message display, navigation prevention
- **Data Flow**: Invalid input → Validation → Error message → Navigation blocked

## Test Data
### Input Data - Valid Cases
- **project_name**: "valid-project-123" (alphanumeric with hyphens)
- **ssh_port**: 2222 (valid port number)
- **ssh_uid**: 1100 (valid UID)
- **proxy_port**: 8080 (valid port number)
- **port_mapping**: "8080:80" (valid format)
- **env_var**: "NODE_ENV=production" (valid KEY=VALUE)

### Input Data - Invalid Cases
- **project_name**: "", "my project", "a", "a-very-long-project-name-that-exceeds-the-maximum-allowed-length"
- **ssh_port**: "abc", "0", "65536", "-100"
- **ssh_uid**: "abc", "-1", "99" (too low, system conflict)
- **ssh_password**: "pass,word", "pass word" (contains comma/space)
- **proxy_port**: "abc", "0", "65536"
- **port_mapping**: "abc:80", "8080:abc", "8080", "8080:80:90"
- **env_var**: "NODEENV", "NODE_ENV", "=production", "NODE ENV=production"

### Expected Outputs
- **Error Messages**: Clear, descriptive validation error messages
- **Navigation State**: Next button disabled when validation fails
- **Field State**: Invalid fields highlighted or marked

## Test Steps
| Step | Action | Input | Expected Result |
|------|--------|-------|-----------------|
| **Project Information Validation** |
| 1 | Navigate to Step 1 | Launch wizard | Project Info screen appears |
| 2 | Test empty project name | Clear project name field | Error: "Project name is required" |
| 3 | Test invalid characters | "my project!" | Error: "Invalid characters in project name" |
| 4 | Test too short name | "ab" | Error: "Project name must be at least 3 characters" |
| 5 | Test too long name | 60-character string | Error: "Project name too long (max 50 characters)" |
| 6 | Test valid name | "valid-project-123" | Validation passes, Next enabled |
| **SSH Configuration Validation** |
| 7 | Navigate to Step 2 | Click Next | SSH Config screen appears |
| 8 | Enable SSH | Select "Yes" | SSH settings visible |
| 9 | Test invalid SSH port | "abc" | Error: "SSH port must be a valid number" |
| 10 | Test port out of range | "0" | Error: "Port must be between 1 and 65535" |
| 11 | Test port too high | "65536" | Error: "Port must be between 1 and 65535" |
| 12 | Test invalid UID | "abc" | Error: "UID must be a valid number" |
| 13 | Test system UID conflict | "100" | Warning: "UID may conflict with system users" |
| 14 | Test password with comma | "pass,word" | Error: "Password cannot contain commas or spaces" |
| 15 | Test password with space | "pass word" | Error: "Password cannot contain commas or spaces" |
| 16 | Test valid SSH config | Valid test data | Validation passes, Next enabled |
| **Proxy Configuration Validation** |
| 17 | Navigate to Step 3 | Click Next | Proxy Config screen appears |
| 18 | Enable proxy | Select "Yes" | Proxy settings visible |
| 19 | Test invalid proxy port | "abc" | Error: "Proxy port must be a valid number" |
| 20 | Test valid proxy port | "8080" | Validation passes |
| **Port Mapping Validation** |
| 21 | Navigate to Step 5 | Click Next through APT config | Port Mapping screen appears |
| 22 | Enable port mapping | Select "Yes" | Port mapping input visible |
| 23 | Test invalid format | "abc:80" | Error: "Invalid port mapping format" |
| 24 | Test missing container port | "8080:" | Error: "Container port required" |
| 25 | Test invalid container port | "8080:abc" | Error: "Invalid container port" |
| 26 | Test valid mapping | "8080:80" | Mapping added successfully |
| **Environment Variable Validation** |
| 27 | Navigate to Step 6 | Click Next | Environment Variables screen appears |
| 28 | Enable env vars | Select "Yes" | Environment variable input visible |
| 29 | Test missing equals | "NODEENV" | Error: "Invalid format, use KEY=VALUE" |
| 30 | Test empty key | "=production" | Error: "Environment variable key cannot be empty" |
| 31 | Test key with space | "NODE ENV=production" | Error: "Key cannot contain spaces" |
| 32 | Test valid env var | "NODE_ENV=production" | Variable added successfully |

## Boundary Conditions
- **Project name**: 3-50 characters, alphanumeric and hyphens only
- **Port numbers**: 1-65535 range
- **UID values**: Typically 1000+ to avoid system conflicts
- **Password constraints**: No spaces, commas, or special implementation-restricted chars
- **Port mapping format**: "host:container" with valid port numbers
- **Environment variables**: "KEY=VALUE" format, no spaces in KEY

## Error Scenarios
- **Real-time validation**: Errors appear as user types
- **Navigation blocking**: Cannot proceed with invalid inputs
- **Error message clarity**: Messages explain what is wrong and how to fix
- **Error persistence**: Errors clear when input becomes valid

## Success Criteria
- [ ] All invalid inputs trigger appropriate error messages
- [ ] Error messages are clear and actionable
- [ ] Navigation is blocked when validation fails
- [ ] Valid inputs pass validation and enable navigation
- [ ] Real-time validation provides immediate feedback
- [ ] Error states clear when input becomes valid
- [ ] All field types validated according to requirements
- [ ] Boundary conditions properly handled

## Cleanup Requirements
- Clear all input fields
- Return to valid state for subsequent tests
- No persistent error states