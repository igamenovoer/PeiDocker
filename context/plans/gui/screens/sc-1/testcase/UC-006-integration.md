# UC-006: Integration Test Cases

## Test Case: TC-INT-001 - Complete Flow (New Project)
**Objective:** Verify complete flow for new project creation
**Steps:**
1. Navigate from SC-0 to SC-1
2. Enter new directory: `D:\temp\integration-test`
3. Enter project name: `integration-test`
4. Verify Docker preview: `integration-test:stage-1`, `integration-test:stage-2`
5. Click Continue
6. Verify directory created and navigation to SC-2

**Expected:** Complete flow works end-to-end, directory created

## Test Case: TC-INT-002 - Complete Flow (Existing Directory)
**Objective:** Verify flow with existing directory
**Steps:**
1. Create directory: `D:\temp\existing-proj`
2. Navigate to SC-1
3. Enter existing directory path
4. Verify status: "Directory already exists"
5. Enter project name: `existing-proj`
6. Click Continue to SC-2

**Expected:** Existing directories handled correctly, flow continues

## Test Case: TC-INT-003 - Browse Integration
**Objective:** Verify browse dialog integration
**Steps:**
1. Navigate to SC-1
2. Click Browse button
3. Select directory via file picker
4. Verify directory field updated
5. Verify project name auto-populated
6. Continue to SC-2

**Expected:** Browse functionality fully integrated with form

## Test Case: TC-INT-004 - Back Navigation Preservation
**Objective:** Verify data preserved when navigating back
**Steps:**
1. Navigate to SC-1
2. Enter directory and project name
3. Click Back to SC-0
4. Return to SC-1
5. Verify form is cleared (fresh start)

**Expected:** Form resets on re-entry (stateless behavior)

## Test Case: TC-INT-005 - CLI to Wizard Flow
**Objective:** Verify CLI override flows to wizard correctly
**Steps:**
1. Launch with: `pei-docker-gui start --project-dir D:\code\cli-test`
2. Navigate through SC-0 to SC-1
3. Verify CLI directory pre-filled
4. Modify project name if needed
5. Continue to SC-2 (wizard)
6. Verify project config passed correctly

**Expected:** CLI override seamlessly flows to wizard with correct config

## Test Case: TC-INT-006 - Error Recovery and Continuation
**Objective:** Verify error recovery allows normal flow continuation
**Steps:**
1. Enter invalid inputs (trigger errors)
2. Fix all validation issues
3. Verify Continue button enabled
4. Click Continue
5. Verify successful navigation to SC-2

**Expected:** Error recovery doesn't leave app in broken state

## Test Case: TC-INT-007 - Real-time UI Updates
**Objective:** Verify all UI elements update in real-time
**Steps:**
1. Enter directory path
2. Verify: status message, project name auto-fill, Docker preview
3. Modify project name
4. Verify: Docker preview updates, Continue button state
5. Introduce validation error
6. Verify: error message, Continue button disabled

**Expected:** All UI elements respond immediately to input changes