# UC-002: Project Name Validation Test Cases

## Test Case: TC-PN-001 - Valid Project Names
**Objective:** Verify valid project names are accepted
**Steps:**
1. Test valid names: `test-project`, `myapp123`, `app_name`
2. Verify each passes validation
3. Verify Docker preview updates: `name:stage-1`, `name:stage-2`

**Expected:** All valid names accepted, preview updates correctly

## Test Case: TC-PN-002 - Invalid Characters
**Objective:** Verify invalid characters are rejected
**Steps:**
1. Enter names with spaces: `my project`
2. Enter names with symbols: `project@123`, `app.name`
3. Verify validation errors displayed
4. Verify Continue button disabled

**Expected:** Invalid characters rejected, detailed error messages shown

## Test Case: TC-PN-003 - Length Validation
**Objective:** Verify name length limits
**Steps:**
1. Enter empty name: ``
2. Enter 51-character name: `a` * 51
3. Enter valid 50-character name: `a` * 50
4. Verify validation results

**Expected:** Empty and too-long names rejected, 50-char limit enforced

## Test Case: TC-PN-004 - Starting Character Rules
**Objective:** Verify names must start with letter
**Steps:**
1. Enter name starting with number: `123project`
2. Enter name starting with hyphen: `-project`
3. Enter name starting with letter: `project123`
4. Verify validation results

**Expected:** Only letter-starting names accepted

## Test Case: TC-PN-005 - Auto-Population from Directory
**Objective:** Verify project name auto-extracts from directory
**Steps:**
1. Enter directory path: `D:\code\my-awesome-app`
2. Verify project name field auto-fills: `my-awesome-app`
3. Change directory path to: `D:\code\another-project`
4. Verify project name updates: `another-project`

**Expected:** Project name automatically extracted and updated

## Test Case: TC-PN-006 - Docker Image Preview
**Objective:** Verify Docker image names preview correctly
**Steps:**
1. Enter project name: `testapp`
2. Verify preview shows: `testapp:stage-1`, `testapp:stage-2`
3. Change name to: `new-name`
4. Verify preview updates: `new-name:stage-1`, `new-name:stage-2`

**Expected:** Preview updates in real-time with correct format