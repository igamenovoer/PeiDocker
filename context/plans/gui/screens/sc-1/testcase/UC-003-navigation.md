# UC-003: Navigation Test Cases

## Test Case: TC-NAV-001 - Back Button Navigation
**Objective:** Verify Back button returns to SC-0
**Steps:**
1. Navigate to SC-1 from SC-0
2. Click Back button
3. Verify navigation to Startup Screen (SC-0)

**Expected:** Successfully navigates back to SC-0

## Test Case: TC-NAV-002 - Continue Button (Valid Form)
**Objective:** Verify Continue with valid inputs goes to SC-2
**Steps:**
1. Enter valid directory: `D:\code\test-proj`
2. Enter valid project name: `test-proj`
3. Click Continue button
4. Verify navigation to Simple Wizard Controller (SC-2)

**Expected:** Successfully navigates to SC-2, directory created

## Test Case: TC-NAV-003 - Continue Button (Invalid Form)
**Objective:** Verify Continue is disabled with invalid inputs
**Steps:**
1. Enter invalid project name: `invalid name`
2. Verify Continue button is disabled
3. Fix project name: `valid-name`
4. Verify Continue button is enabled

**Expected:** Button state reflects form validation status

## Test Case: TC-NAV-004 - Keyboard Shortcuts
**Objective:** Verify keyboard navigation works
**Steps:**
1. Press 'b' key
2. Verify Back action triggered
3. Return to SC-1
4. Press Enter key with valid form
5. Verify Continue action triggered

**Expected:** Keyboard shortcuts work as mouse clicks

## Test Case: TC-NAV-005 - Directory Creation on Continue
**Objective:** Verify directory is created when continuing
**Steps:**
1. Enter non-existent directory: `D:\temp\new-project`
2. Enter valid project name: `new-project`
3. Click Continue
4. Verify directory was created on filesystem

**Expected:** Directory created before navigating to SC-2

## Test Case: TC-NAV-006 - Form State Preservation
**Objective:** Verify form state is preserved in project config
**Steps:**
1. Enter directory: `D:\code\myapp`
2. Enter project name: `myapp`
3. Click Continue
4. Verify project config contains correct values

**Expected:** Configuration properly updated and passed to next screen