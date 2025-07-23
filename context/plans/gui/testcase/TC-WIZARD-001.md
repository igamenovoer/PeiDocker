# Test Case: TC-WIZARD-001

## Test Information
- **Title**: Complete Simple Mode Wizard Flow
- **Category**: Wizard
- **Priority**: High
- **Test Type**: Manual
- **Estimated Duration**: 15 minutes
- **Prerequisites**: Docker daemon running, write permissions to project directory
- **Related Requirements**: task-gui-new.md Simple Mode section, gui-simple-mode.md

## Test Objective
Verify user can complete all 11 wizard steps with valid inputs and generate valid user_config.yml file

## Test Scope  
- **Components**: SimpleWizardScreen, ProjectConfig, all 11 step screens
- **Functions**: validate inputs, navigate between steps, save configuration
- **Data Flow**: User inputs → Memory state → Navigation → Configuration generation → File creation

## Test Data
### Input Data
- **project_name**: "test-project-gui" (string, alphanumeric with hyphens)
- **base_image**: "ubuntu:24.04" (string, valid Docker image)
- **ssh_enabled**: true (boolean)
- **ssh_port**: 2222 (integer, 1-65535)
- **ssh_user**: "testuser" (string, no spaces)
- **ssh_password**: "testpass123" (string, no spaces or commas)
- **ssh_uid**: 1100 (integer, avoid system conflicts)
- **proxy_enabled**: false (boolean)
- **apt_mirror**: "default" (string)
- **port_mappings**: "8080:80" (string, host:container format)
- **env_vars**: "NODE_ENV=test" (string, KEY=VALUE format)
- **gpu_enabled**: false (boolean)
- **stage1_mounts**: none (empty list)
- **stage1_entrypoint**: none (empty string)
- **stage1_scripts**: none (empty list)

### Expected Outputs
- **UI State**: Summary screen displayed, progress shows Step 11 of 11
- **Files Created**: user_config.yml in project directory
- **Configuration**: Valid YAML with all user inputs preserved
- **Memory State**: All configuration held in memory until save

## Test Steps
| Step | Action | Input | Expected Result |
|------|--------|-------|-----------------|
| 1 | Launch GUI | pei-docker-gui --project-dir ./test-project | Startup screen displays |
| 2 | Continue from startup | Press Continue button | Project Info screen (Step 1) appears |
| 3 | Enter project name | "test-project-gui" | Validation passes, Next enabled |
| 4 | Enter base image | "ubuntu:24.04" | Input accepted, Next remains enabled |
| 5 | Navigate to SSH config | Click Next button | SSH Configuration screen (Step 2) appears |
| 6 | Enable SSH | Select "Yes" radio button | SSH settings section becomes visible |
| 7 | Configure SSH settings | Fill all SSH fields with test data | All fields validate, Next enabled |
| 8 | Navigate through remaining steps | Click Next on each step | Each step appears in sequence (3-11) |
| 9 | Configure each step | Enter appropriate test data | Each step accepts input and validates |
| 10 | Reach summary screen | Click Next from Step 10 | Summary screen (Step 11) displays all config |
| 11 | Verify configuration summary | Review displayed settings | All entered data matches input |
| 12 | Save configuration | Click Save button | Success message, user_config.yml created |
| 13 | Verify file creation | Check project directory | user_config.yml file exists |
| 14 | Verify file content | Open user_config.yml | Valid YAML with all test data |

## Boundary Conditions
- **Valid project names**: alphanumeric, hyphens, underscores, 3-50 chars
- **Valid SSH ports**: 1-65535
- **Valid SSH UIDs**: typically 1000-65535, avoid system UIDs
- **Valid port mappings**: host:container format, 1-65535 range
- **Valid environment variables**: KEY=VALUE format, no spaces in KEY

## Error Scenarios
- **Empty project name**: "" → "Project name is required"
- **Invalid SSH port**: "abc" → "SSH port must be a valid number"
- **Invalid port mapping**: "abc:80" → "Invalid port mapping format"
- **Invalid environment variable**: "KEY VALUE" → "Invalid format, use KEY=VALUE"

## Success Criteria
- [ ] All 11 wizard steps completed without errors
- [ ] user_config.yml file created with correct structure
- [ ] Configuration contains all user inputs accurately
- [ ] YAML file is valid and parseable
- [ ] Project directory structure created correctly
- [ ] No temporary files left behind
- [ ] Memory state maintained throughout navigation
- [ ] Save button only appears on final step

## Cleanup Requirements
- Remove test project directory
- Clean up any temporary files
- Reset application state