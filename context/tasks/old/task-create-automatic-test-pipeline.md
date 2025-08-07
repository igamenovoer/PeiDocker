we are going to setup an automatic test pipeline for the GUI.

# General Info
- gui source code is located in `src\pei_docker\gui`
- currently usable screens are screen 0 and screen 1
  - screen 0 design doc: `context\plans\gui\screens\sc-0\application-startup-screen-spec.md`
  - screen 1 design doc: `context\plans\gui\screens\sc-1\project-directory-selection-screen-spec.md`
- future screen documents can be found in `context\plans\gui\screens`
- before running the tests, create the directory `tmp/autotest/run-(uuid)` for all outputs of this test run, and this dir is called `run-log-dir`, the `uuid` is called the `run-id` in the following sections.
- your test script should be placed in `tests/autotest`

# Logging

you **HAVE TO log** your actions during automatic test execution, for each key step (before any major state change), in this way

- logging files should be saved in `<run-log-dir>/logs`
- screenshots should be saved in `<run-log-dir>/screenshots`

# Task 1: Be able to take screenshots of the GUI screens in background

The goal is to create a test script that can automatically start the GUI, navigate through the screens, and take screenshots of each screen. This will help in verifying the GUI's layout and functionality without manual intervention.

your task is to create a test script in `tests/autotest`, which starts up the GUI and take a screenshot of the first screen, then navigate to the second screen and take another screenshot. save both screenshots in `<run-log-dir>/screenshots` with appropriate names.

# Task 2: Be able to simulate user input on the GUI and take screenshots, also in background

The goal is to extend the test script to simulate user input, such as button clicks or key presses, and take screenshots after each interaction. This will help in verifying that the GUI responds correctly to user actions.

Now, start the app, navigate to `screen 1`
- input to `project directory` field: `./tmp/autotest/build-autotest`
- input to `project name` field: `autotest-project`
- click `continue` button

