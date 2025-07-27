# How to test Textual GUI Screens Given a Test Case

This guide provides an overview of how to test Textual GUI Screens using predefined test cases, like a unit test for GUI components. 

## Prerequisites

- create a test project using `pei-docker-cli create --project-dir (test_project_dir)`, the test project directory should be created in `<workspace>/tmp/projs`. Denote this directory as `test_project_dir`.

- ALWAYS start the GUI app in background, simulate user input, and take screenshots for debugging.

- You must have a test case specification for each test, in `context\plans\gui\screens\sc-1\testcase`

## Workflow

- check the design documentation first, in `context\plans\gui\screens` for each screen

### Per-screen Degugging

given a screen `sc-(xx)` for testing:

- verify it is runable using `pei-docker-gui dev --project-dir ./test --screen sc-(xx)`

- make sure you can take a screenshot of that screen.

- then do as the test case specification said.