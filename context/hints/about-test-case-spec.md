# PeiDocker GUI Test Case Specification Template

This document provides a template and guidelines for creating individual test case files for the PeiDocker GUI project. Each test case should be created as a separate file following this structure.

## Purpose

This template helps create consistent, maintainable test cases for the terminal-based user interface built with Textual. Use this as a starting point to create individual test case files like `TC-WIZARD-001.md`, `TC-VAL-002.md`, etc.

## PeiDocker GUI Context

The GUI has multiple interaction modes requiring different test approaches:
- **Simple Mode**: 15-step wizard workflow
- **Advanced Mode**: Form-based configuration
- **File System Operations**: Directory creation, file selection
- **Docker Integration**: Container management, image validation
- **State Management**: Cross-step data dependencies

## Test Case File Template

Create each test case as a separate markdown file using this template:

### File Naming Convention
- **TC-WIZARD-XXX.md**: Wizard flow tests (TC-WIZARD-001.md)
- **TC-VAL-XXX.md**: Input validation tests (TC-VAL-002.md)  
- **TC-FS-XXX.md**: File system operation tests (TC-FS-003.md)
- **TC-DOCKER-XXX.md**: Docker integration tests (TC-DOCKER-004.md)
- **TC-STATE-XXX.md**: State management tests (TC-STATE-005.md)

### Standard Test Case Structure

```markdown
# Test Case: TC-[CATEGORY]-[NUMBER]

## Test Information
- **Title**: [Descriptive test case name]
- **Category**: [Wizard|Validation|FileSystem|Docker|StateManagement]
- **Priority**: [Critical|High|Medium|Low]
- **Test Type**: [Manual|Automated|Both]
- **Estimated Duration**: [X minutes]
- **Prerequisites**: [Required setup conditions]
- **Related Requirements**: [Reference to design docs]

## Test Objective
[Single clear statement of what this test validates]

## Test Scope  
- **Components**: [UI components being tested]
- **Functions**: [Key functions/methods involved]
- **Data Flow**: [Input → Processing → Output]

## Test Data
### Input Data
- **Field1**: [specific value with data type]
- **Field2**: [specific value with constraints]
- **Files**: [required files/configurations]

### Expected Outputs
- **UI State**: [expected screen/widget states]
- **Files Created**: [expected file outputs]
- **Configuration**: [expected config changes]

## Test Steps
| Step | Action | Input | Expected Result |
|------|--------|-------|-----------------|
| 1 | [user action] | [specific input] | [expected response] |
| 2 | [next action] | [input data] | [expected state] |

## Boundary Conditions
- **Valid Boundaries**: [minimum/maximum valid values]
- **Invalid Boundaries**: [values that should fail]
- **Edge Cases**: [special conditions to test]

## Error Scenarios
- **Error Type 1**: [trigger] → [expected error message]
- **Error Type 2**: [trigger] → [expected system behavior]

## Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [System state verification]

## Cleanup Requirements
- [Files to remove]
- [State to reset]
- [Resources to release]
```

## Example Test Cases

### Example 1: TC-WIZARD-001.md
```markdown
# Test Case: TC-WIZARD-001

## Test Information
- **Title**: Complete Simple Mode Wizard Flow
- **Category**: Wizard
- **Priority**: Critical
- **Test Type**: Both
- **Estimated Duration**: 10 minutes
- **Prerequisites**: Docker daemon running, write permissions
- **Related Requirements**: task-gui.md Simple Mode section

## Test Objective
Verify user can complete all 15 wizard steps and generate valid user_config.yml

## Test Scope
- **Components**: SimpleWizardScreen, ProjectConfig
- **Functions**: validate_project_name(), generate_config(), save_file()
- **Data Flow**: User inputs → Validation → Config generation → File creation

## Test Data
### Input Data
- **project_name**: "test-project-123" (string, 3-50 chars)
- **base_image**: "ubuntu:24.04" (string, valid Docker image)
- **ssh_enabled**: true (boolean)
- **ssh_port**: 2222 (integer, 1-65535)

### Expected Outputs
- **UI State**: Summary screen displayed, progress shows 15/15
- **Files Created**: user_config.yml in project directory
- **Configuration**: Valid YAML with all user inputs preserved

## Test Steps
| Step | Action | Input | Expected Result |
|------|--------|-------|-----------------|
| 1 | Launch GUI | --project-dir ./test | Startup screen displays |
| 2 | Select Simple Mode | Click "Simple Mode" | Wizard Step 1 appears |
| 3 | Enter project name | "test-project-123" | Validation passes, Next enabled |
| 4 | Continue through steps | Navigate all 15 steps | Each step accepts input |
| 5 | Save configuration | Click "Save" | Success message, file created |

## Boundary Conditions
- **Valid project names**: alphanumeric, hyphens, underscores, 3-50 chars
- **Invalid project names**: spaces, special chars, empty, >50 chars
- **Valid SSH ports**: 1-65535
- **Invalid SSH ports**: 0, >65535, non-numeric

## Error Scenarios
- **Invalid project name**: "my project!" → "Invalid characters in project name"
- **Port conflict**: SSH port 22 when host port 22 occupied → "Port already in use"

## Success Criteria
- [ ] All 15 wizard steps completed without errors
- [ ] user_config.yml file created with correct structure
- [ ] Configuration contains all user inputs
- [ ] No temporary files left behind

## Guidelines for Test Case Creation

### Input/Output Focus
- **Inputs**: Specify exact values, data types, constraints
- **Outputs**: Define expected UI state, files, configuration changes
- **Boundaries**: Test min/max values, edge cases, invalid inputs
- **Errors**: Define triggers and expected error responses

### Test Structure Principles
- **One objective per test case**: Each test should validate one specific behavior
- **Measurable outcomes**: Use verifiable assertions (file exists, field contains value X)
- **Minimal code examples**: Avoid detailed implementation, focus on input/output contracts
- **Clear data specifications**: Precise input values and expected results

### Common Test Categories

| Category | Purpose | Example |
|----------|---------|---------|
| **TC-WIZARD-XXX** | Wizard navigation and flow | Complete 15-step wizard with valid inputs |
| **TC-VAL-XXX** | Input validation | Port number validation (1-65535) |
| **TC-FS-XXX** | File system operations | Create project directory structure |
| **TC-DOCKER-XXX** | Docker integration | Validate Docker image availability |
| **TC-STATE-XXX** | State management | SSH enabled → SSH user step appears |

### Template Usage
1. Copy the template structure for each new test case
2. Create separate `.md` files (e.g., `TC-WIZARD-001.md`)
3. Fill in specific inputs, outputs, and boundary conditions
4. Focus on **what** to test, not **how** to implement
5. Keep implementation details minimal - test cases describe behavior, not code

### Validation Approach
- **Functional**: Does feature work as designed?
- **Boundary**: What happens at limits (0, 1, max, max+1)?
- **Error**: How does system handle invalid inputs?
- **State**: Are UI and data states consistent?

Remember: Test cases are **specifications**, not implementation guides. They should clearly define expected behavior for developers to implement tests against.
