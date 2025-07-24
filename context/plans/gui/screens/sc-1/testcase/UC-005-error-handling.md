# UC-005: Error Handling Test Cases

## Test Case: TC-ERR-001 - Path Error Recovery
**Objective:** Verify path errors can be corrected
**Steps:**
1. Enter invalid path: `Z:\invalid\path`
2. Verify error state displayed
3. Enter valid path: `D:\code\valid-project`
4. Verify error cleared, Continue enabled

**Expected:** Error states clear when input is corrected

## Test Case: TC-ERR-002 - Name Error Recovery
**Objective:** Verify project name errors can be corrected
**Steps:**
1. Enter invalid name: `123invalid`
2. Verify error message: "Must start with letter"
3. Enter valid name: `valid-project`
4. Verify error cleared

**Expected:** Specific error messages shown and cleared appropriately

## Test Case: TC-ERR-003 - Permission Error Handling
**Objective:** Verify permission errors are handled gracefully
**Steps:**
1. Enter path to protected system directory
2. Verify permission error displayed
3. Enter path to accessible directory
4. Verify error cleared

**Expected:** Permission issues detected and resolved

## Test Case: TC-ERR-004 - Directory Creation Failure
**Objective:** Verify handling of directory creation failures
**Steps:**
1. Enter valid inputs for protected location
2. Click Continue
3. Verify creation failure is handled gracefully
4. Verify user remains on SC-1 with error message

**Expected:** Creation failures don't crash app, show helpful errors

## Test Case: TC-ERR-005 - Multiple Simultaneous Errors
**Objective:** Verify multiple errors are handled correctly
**Steps:**
1. Enter invalid path and invalid project name
2. Verify both errors displayed
3. Fix path, keep invalid name
4. Verify only name error remains
5. Fix name
6. Verify all errors cleared

**Expected:** Multiple errors tracked independently

## Test Case: TC-ERR-006 - Error Message Clarity
**Objective:** Verify error messages are helpful and specific
**Steps:**
1. Test each validation error condition
2. Verify messages are specific and actionable:
   - "No spaces allowed"
   - "Use letters, numbers, hyphens, and underscores only"
   - "Must start with letter"
   - "Directory path is invalid"

**Expected:** Clear, actionable error messages for each validation rule