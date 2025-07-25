we are going to setup an automatic test pipeline for the GUI.

- gui source code is located in `src\pei_docker\gui`
- currently usable screens are screen 0 and screen 1
  - screen 0 design doc: `context\plans\gui\screens\sc-0\application-startup-screen-spec.md`
  - screen 1 design doc: `context\plans\gui\screens\sc-1\project-directory-selection-screen-spec.md`
- about how to run the GUI and capture screenshots, refer to `context\hints\howto-test-textual-gui-with-screenshots.md`

your task is to create a test script in `tests\autotest`, which starts up the GUI and take a screenshot of the first screen, then navigate to the second screen and take another screenshot. save both screenshots in `tmp/output/gui-screenshots` directory with appropriate names.