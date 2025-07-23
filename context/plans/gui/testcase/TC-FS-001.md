# Test Case: TC-FS-001

## Test Information
- **Title**: Configuration File Operations and Validation
- **Category**: FileSystem
- **Priority**: Medium
- **Test Type**: Manual
- **Estimated Duration**: 12 minutes
- **Prerequisites**: GUI launched, write permissions to project directory
- **Related Requirements**: task-gui-new.md file generation requirements

## Test Objective
Verify user_config.yml file is created correctly with proper structure and content matching wizard inputs

## Test Scope  
- **Components**: Summary screen, save functionality, YAML generation
- **Functions**: save_user_config(), YAML serialization, file validation
- **Data Flow**: Memory configuration → YAML generation → File creation → Content validation

## Test Data
### Input Data
- **project_name**: "file-test-project"
- **base_image**: "ubuntu:24.04"
- **ssh_config**: 
  - enabled: true
  - user: "fileuser"
  - password: "file123"
  - uid: 1100
  - host_port: 2222
  - container_port: 22
- **proxy_config**: 
  - enabled: true
  - port: 8080
  - build_only: true
- **apt_mirror**: "tuna"
- **env_vars**: ["APP_ENV=test", "DEBUG=true"]
- **port_mappings**: ["3000:3000", "8080:80"]
- **gpu_enabled**: false

### Expected Outputs
- **File Creation**: user_config.yml in project directory
- **File Structure**: Valid YAML format with proper indentation
- **Content Accuracy**: All wizard inputs accurately reflected
- **File Permissions**: Readable file with appropriate permissions

## Test Steps
| Step | Action | Input | Expected Result |
|------|--------|-------|-----------------|
| **File Creation Testing** |
| 1 | Complete wizard configuration | Enter all test data through steps | Reach summary screen |
| 2 | Verify pre-save state | Check project directory | No user_config.yml exists |
| 3 | Save configuration | Click Save button | Success message displayed |
| 4 | Verify file creation | Check project directory | user_config.yml file exists |
| 5 | Check file permissions | ls -la user_config.yml | File readable, appropriate permissions |
| **File Content Validation** |
| 6 | Open configuration file | cat user_config.yml | Valid YAML structure |
| 7 | Verify project section | Check project name and base image | Matches wizard input exactly |
| 8 | Verify SSH section | Check stage_1.ssh configuration | All SSH settings correct |
| 9 | Verify proxy section | Check stage_1.proxy configuration | Proxy settings accurate |
| 10 | Verify APT section | Check stage_1.apt_mirror | Mirror selection correct |
| 11 | Verify environment variables | Check stage_1.env section | All env vars present |
| 12 | Verify port mappings | Check stage_1.ports section | Port mappings accurate |
| 13 | Verify device config | Check stage_1.device section | GPU setting correct |
| **File Structure Testing** |
| 14 | Validate YAML syntax | Parse with YAML parser | No syntax errors |
| 15 | Check section hierarchy | Verify stage_1/stage_2 structure | Proper nesting |
| 16 | Verify data types | Check boolean, integer, string types | Correct type preservation |
| 17 | Check indentation | Verify YAML indentation | Consistent spacing |
| **Multiple Save Testing** |
| 18 | Modify configuration | Change a setting and return to summary | Updated summary shown |
| 19 | Save updated config | Click Save button again | File updated successfully |
| 20 | Verify file update | Check file content | New configuration present |
| 21 | Check file backup | Look for backup files | No unnecessary backup files |
| **Error Condition Testing** |
| 22 | Remove write permissions | chmod 444 project directory | Directory not writable |
| 23 | Attempt save | Click Save button | Error message displayed |
| 24 | Verify no partial file | Check directory | No corrupted/partial files |
| 25 | Restore permissions | chmod 755 project directory | Permissions restored |
| 26 | Save successfully | Click Save button | File created successfully |

## Boundary Conditions
- **Large configurations**: All possible options filled
- **Special characters**: Unicode, special chars in strings
- **Empty values**: Optional fields left empty
- **File size**: Large configurations with many entries
- **Long strings**: Maximum length project names, descriptions

## Error Scenarios
- **No write permissions**: Directory not writable → Clear error message
- **Disk full**: Insufficient space → Error handling, no partial files
- **Invalid characters**: Special chars in file path → Proper escaping
- **File exists**: Overwrite existing user_config.yml → Successful update

## Success Criteria
- [ ] user_config.yml created in correct project directory
- [ ] File contains valid YAML syntax
- [ ] All wizard inputs accurately reflected in file
- [ ] Proper section structure (stage_1, stage_2, etc.)
- [ ] Correct data types preserved (strings, booleans, integers)
- [ ] Consistent YAML indentation and formatting
- [ ] File updates correctly on multiple saves
- [ ] No corrupted or partial files on errors
- [ ] Appropriate error messages for file system issues
- [ ] File permissions allow reading by user
- [ ] No unnecessary backup or temporary files created
- [ ] Large configurations handled properly

## Cleanup Requirements
- Remove test user_config.yml file
- Restore original directory permissions
- Clean up any temporary files
- Reset project directory state