# Test Case: TC-WIZARD-002

## Test Information
- **Title**: Wizard Navigation Behavior
- **Category**: Wizard
- **Priority**: High
- **Test Type**: Manual
- **Estimated Duration**: 10 minutes
- **Prerequisites**: GUI launched, wizard started
- **Related Requirements**: task-gui-new.md Navigation section, gui-simple-mode.md Navigation Rules

## Test Objective
Verify navigation controls work correctly including double ESC, single ESC, prev/next buttons, and memory state preservation

## Test Scope  
- **Components**: SimpleWizardScreen, all step screens, ESC handling, button navigation
- **Functions**: handle_escape(), prev/next navigation, memory state management
- **Data Flow**: Navigation events → State preservation → Screen transitions

## Test Data
### Input Data
- **test_project_name**: "nav-test-project" (string for testing state preservation)
- **test_input_data**: Various inputs across different steps
- **navigation_sequence**: Forward and backward navigation pattern

### Expected Outputs
- **UI State**: Correct screen transitions, state preservation, input clearing
- **Memory State**: Configuration preserved during navigation
- **Button States**: Correct button visibility and functionality per step

## Test Steps
| Step | Action | Input | Expected Result |
|------|--------|-------|-----------------|
| 1 | Start wizard | Launch GUI and proceed to Step 1 | Project Info screen appears |
| 2 | Enter test data | "nav-test-project" in project name | Input accepted and stored |
| 3 | Navigate forward | Click Next button | Move to Step 2 (SSH Config) |
| 4 | Test backward navigation | Click Prev button | Return to Step 1, data preserved |
| 5 | Verify data preservation | Check project name field | Previously entered data still present |
| 6 | Navigate to middle step | Click Next multiple times | Reach Step 6 (Environment Variables) |
| 7 | Enter test data | Add "TEST_VAR=navigation" | Environment variable added |
| 8 | Test single ESC | Press ESC key once | Input field cleared (TEST_VAR input cleared) |
| 9 | Re-enter data | "TEST_VAR=navigation" again | Data entered successfully |
| 10 | Test double ESC | Press ESC twice quickly | Return to main menu/startup screen |
| 11 | Restart and verify | Re-enter wizard | Fresh wizard state, no previous data |
| 12 | Navigate to final step | Go through all steps to Step 11 | Summary screen appears |
| 13 | Verify final step buttons | Check button layout | Shows [Prev] [Save] [Cancel] buttons |
| 14 | Test backward from final | Click Prev button | Return to Step 10, data preserved |
| 15 | Return to final step | Click Next button | Back to Step 11 (Summary) |

## Boundary Conditions
- **Double ESC timing**: ESC keys pressed within 1-2 seconds
- **Navigation at boundaries**: First step (no Prev), Last step (Save instead of Next)
- **Memory preservation**: State maintained across all navigation scenarios
- **Button states**: Correct buttons shown per step position

## Error Scenarios
- **Single ESC without input**: ESC on empty field → No change
- **Double ESC timing too slow**: Two slow ESC presses → Single ESC behavior only
- **Navigation with validation errors**: Try to navigate with invalid input → Error message, no navigation
- **Rapid navigation clicks**: Quick prev/next clicks → Smooth transitions, no state corruption

## Success Criteria
- [ ] Prev/Next buttons work correctly on all steps
- [ ] Single ESC clears current input field
- [ ] Double ESC returns to main menu from any step
- [ ] Data preservation during forward/backward navigation
- [ ] Correct button layout on each step (Prev/Next vs Prev/Save/Cancel)
- [ ] No navigation allowed with validation errors
- [ ] Smooth transitions without UI glitches
- [ ] Memory state correctly preserved and cleared as expected

## Cleanup Requirements
- Exit wizard cleanly
- Return to main menu
- Clear any temporary state