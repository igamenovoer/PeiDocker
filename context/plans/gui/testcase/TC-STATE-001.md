# Test Case: TC-STATE-001

## Test Information
- **Title**: Memory-Only State Management Until Save
- **Category**: StateManagement
- **Priority**: High
- **Test Type**: Manual
- **Estimated Duration**: 15 minutes
- **Prerequisites**: GUI launched, project directory accessible
- **Related Requirements**: task-gui-new.md State Management section, gui-simple-mode.md Memory-Only Changes

## Test Objective
Verify configuration changes are kept in memory only until explicit save, and persistent final page behavior after save

## Test Scope  
- **Components**: SimpleWizardScreen, ProjectConfig, Summary screen, file operations
- **Functions**: Memory state management, save configuration, persistent navigation
- **Data Flow**: User inputs → Memory state → Navigation → Save → File creation → Continued navigation

## Test Data
### Input Data
- **project_name**: "state-test-project"
- **base_image**: "ubuntu:22.04"
- **ssh_user**: "stateuser"
- **ssh_password**: "state123"
- **env_var**: "STATE_TEST=active"
- **port_mapping**: "9090:90"

### Expected Outputs
- **Memory State**: All configuration held in memory until save
- **File System**: No user_config.yml created until explicit save
- **Post-Save State**: Remain on summary page, continue navigation possible
- **File Content**: Accurate reflection of memory state when saved

## Test Steps
| Step | Action | Input | Expected Result |
|------|--------|-------|-----------------|
| **Memory-Only Behavior Testing** |
| 1 | Start wizard | Launch GUI, proceed to wizard | Project Info screen appears |
| 2 | Enter project configuration | Fill project name and base image | Data entered in memory |
| 3 | Check file system | Look for user_config.yml in project dir | File does not exist |
| 4 | Navigate to SSH config | Click Next | SSH Config screen, previous data in memory |
| 5 | Configure SSH | Enter SSH settings | SSH config stored in memory |
| 6 | Check file system again | Look for user_config.yml | File still does not exist |
| 7 | Navigate through more steps | Configure env vars, port mapping | All data accumulated in memory |
| 8 | Check file system repeatedly | Check after each step | No file creation during navigation |
| 9 | Navigate backward | Click Prev multiple times | All previously entered data preserved |
| 10 | Navigate forward again | Click Next to return | Memory state intact, no data loss |
| **Save and Persistent Final Page Testing** |
| 11 | Reach summary screen | Navigate to Step 11 | Summary displays all memory configuration |
| 12 | Verify summary accuracy | Review displayed settings | All entered data correctly shown |
| 13 | Save configuration | Click Save button | Success message appears |
| 14 | Check file system | Look for user_config.yml | File now exists in project directory |
| 15 | Verify file content | Open user_config.yml | Contains all configuration from memory |
| 16 | Verify persistent page | Check current screen | Still on summary screen (Step 11) |
| 17 | Navigate backward post-save | Click Prev button | Can navigate to previous steps |
| 18 | Modify configuration | Change a setting on previous step | Change reflected in memory |
| 19 | Return to summary | Navigate back to Step 11 | Updated configuration shown |
| 20 | Save again | Click Save button again | File updated with new configuration |
| 21 | Check file again | Open user_config.yml | Contains updated configuration |
| **Double ESC Memory Clear Testing** |
| 22 | Enter partial configuration | Fill first few steps | Data in memory |
| 23 | Use double ESC | Press ESC twice quickly | Return to main menu |
| 24 | Check file system | Look for user_config.yml | No file created (memory cleared) |
| 25 | Restart wizard | Enter wizard again | Fresh state, no previous data |

## Boundary Conditions
- **Memory capacity**: Large configurations with all options filled
- **Navigation limits**: Extensive back/forth navigation preserving state
- **Save frequency**: Multiple saves with different configurations
- **Session persistence**: Memory cleared on application exit or double ESC

## Error Scenarios
- **Save failure**: Insufficient permissions → Error message, remain in memory state
- **Corrupted memory state**: Invalid state during navigation → Graceful error handling
- **File system errors**: Directory not writable → Error message, memory preserved
- **Large configuration**: Extensive data → All data preserved in memory and saved

## Success Criteria
- [ ] No user_config.yml created during navigation (memory-only)
- [ ] All configuration data preserved in memory during navigation
- [ ] user_config.yml created only after explicit Save click
- [ ] File content accurately reflects memory state
- [ ] Remain on summary page after save (persistent final page)
- [ ] Can navigate backward/forward after save
- [ ] Can save multiple times with updated configurations
- [ ] Double ESC clears memory state completely
- [ ] Fresh wizard starts with empty memory state
- [ ] Save button only appears on final step (Step 11)
- [ ] Memory state survives all navigation scenarios
- [ ] File updates correctly on subsequent saves

## Cleanup Requirements
- Remove test project directory
- Clear application memory state
- Reset to initial application state