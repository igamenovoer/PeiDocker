you are tasked to do headless testing for application.

# Platform-specific Instructions

Before starting headless testing, find out which platform you are using and follow the corresponding instructions because you need to use CLI tools correctly:
- If you are in Windows, you shall also follow `context/instructions/win32-env.md` instructions.
- If you are in macOS, you shall also follow `context/instructions/mac-env.md` instructions.

# Testing Guidelines

- Focus on testing the application's functionality without a graphical user interface.
- Use automated testing tools that support headless mode.
- For each test, save the test results in `context/logs/testlog-<date>.md` format, which includes:
- - a header, contains the following:
  - **Test Case ID**: Unique identifier for the test case
  - **Test Objective**: Brief description of what the test is verifying
  - **Test Scope**: Components and functions being tested
  - **Test Data**: Input data used in the test
  - **Expected Outputs**: What the test should produce as output
  - **Status**: Pass/Fail
- - a summary of the test results, including pass/fail status and any relevant logs.

IMPORTANT: whenever a test fails twice, try to find online information, and use `context7` to find documentations if this involves a specific library or framework.

# Debugging
If you found a bug and want to debug it, follow the `context/instructions/debug-code.md` instructions, and note that your code should follow `context/instructions/strongly-typed.md` standards.
