# UC-001: Directory Selection Test Cases

## Test Case: TC-DS-001 - Valid Directory Path Entry
**Objective:** Verify user can enter valid directory paths
**Steps:**
1. Navigate to SC-1
2. Enter valid path: `D:\code\test-project`
3. Verify status shows "Directory will be created if it doesn't exist"
4. Verify Continue button is enabled

**Expected:** Path accepted, status updated, navigation enabled

## Test Case: TC-DS-002 - Existing Directory Detection
**Objective:** Verify existing directories are properly detected
**Steps:**
1. Create temporary directory: `D:\temp\existing-proj`
2. Enter path in directory field
3. Verify status shows "Directory already exists"

**Expected:** Status correctly identifies existing directory

## Test Case: TC-DS-003 - Invalid Directory Path
**Objective:** Verify invalid paths are rejected
**Steps:**
1. Enter invalid path: `Z:\nonexistent\invalid`
2. Verify validation error displayed
3. Verify Continue button is disabled

**Expected:** Path rejected, error shown, navigation blocked

## Test Case: TC-DS-004 - Browse Button Functionality
**Objective:** Verify browse dialog works correctly
**Steps:**
1. Click Browse button
2. Select directory using file picker
3. Verify path field is updated
4. Verify validation is triggered

**Expected:** Directory picker opens, selection updates field

## Test Case: TC-DS-005 - Path Permission Validation
**Objective:** Verify write permission checking
**Steps:**
1. Enter path to read-only location
2. Verify permission error displayed
3. Enter path to writable location
4. Verify validation passes

**Expected:** Permission errors detected, valid paths accepted