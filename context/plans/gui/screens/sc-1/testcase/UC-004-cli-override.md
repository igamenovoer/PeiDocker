# UC-004: CLI Override Test Cases

## Test Case: TC-CLI-001 - Directory Pre-filled and Disabled
**Objective:** Verify --project-dir pre-fills and disables directory field
**Steps:**
1. Launch app with: `pei-docker-gui start --project-dir D:\code\cli-project`
2. Navigate to SC-1
3. Verify directory field contains: `D:\code\cli-project`
4. Verify directory field is disabled (grayed out)

**Expected:** Directory field pre-filled and non-editable

## Test Case: TC-CLI-002 - Browse Button Disabled
**Objective:** Verify Browse button is disabled with CLI override
**Steps:**
1. Launch app with: `pei-docker-gui start --project-dir D:\code\cli-project`
2. Navigate to SC-1
3. Verify Browse button is not present or disabled

**Expected:** Browse functionality unavailable in CLI mode

## Test Case: TC-CLI-003 - Project Name Editable
**Objective:** Verify project name remains editable with CLI override
**Steps:**
1. Launch app with: `pei-docker-gui start --project-dir D:\code\cli-project`
2. Navigate to SC-1
3. Verify project name field shows: `cli-project`
4. Change project name to: `different-name`
5. Verify change is accepted

**Expected:** Project name can be modified despite CLI directory

## Test Case: TC-CLI-004 - Docker Preview Updates
**Objective:** Verify Docker preview works with CLI override
**Steps:**
1. Launch app with: `pei-docker-gui start --project-dir D:\code\my-cli-app`
2. Navigate to SC-1
3. Verify preview shows: `my-cli-app:stage-1`, `my-cli-app:stage-2`
4. Change project name to: `custom-name`
5. Verify preview updates: `custom-name:stage-1`, `custom-name:stage-2`

**Expected:** Preview functionality works normally in CLI mode

## Test Case: TC-CLI-005 - Validation Still Active
**Objective:** Verify project name validation works with CLI override
**Steps:**
1. Launch app with: `pei-docker-gui start --project-dir D:\code\cli-project`
2. Navigate to SC-1
3. Enter invalid project name: `invalid name`
4. Verify validation error displayed
5. Verify Continue button disabled

**Expected:** All validation rules still enforced in CLI mode

## Test Case: TC-CLI-006 - Here Option Usage
**Objective:** Verify --here option uses current directory
**Steps:**
1. Navigate to project directory: `cd D:\code\my-current-project`
2. Launch app with: `pei-docker-gui start --here`
3. Navigate to SC-1
4. Verify directory field contains current directory path
5. Verify directory field is disabled (grayed out)

**Expected:** Current directory used as project directory, field disabled

## Test Case: TC-CLI-007 - Dev Mode Screen Selection
**Objective:** Verify dev mode --screen option works
**Steps:**
1. Launch app with: `pei-docker-gui dev --project-dir D:\code\test-project --screen sc-1`
2. Verify app starts directly at SC-1 screen
3. Verify project directory is pre-filled

**Expected:** App starts at specified screen with project directory set

## Test Case: TC-CLI-008 - Dev Mode Validation
**Objective:** Verify dev mode requires project directory for screen option
**Steps:**
1. Try to launch: `pei-docker-gui dev --screen sc-1`
2. Verify error message displayed
3. Verify app does not start

**Expected:** Error message stating screen option requires project directory