# Do this task

Fix the following issues of the GUI. We use the terminology as said in `context/design/terminology.md`.

## Project Information Tab

the current layout has wrong hierarchy, it should be like this:

- project information
  - project name
    - input text field
  - base docker image
    - input text field
    - generated docker images info
      - stage-1: (docker image name)
      - stage-2: (docker image name)
- two-stage architecture overview
  - helper text

and the "project information" and "two-stage architecture overview" should be vertically aligned.

and we do not need the "Generated Docker Images" as a separate section (or card).


