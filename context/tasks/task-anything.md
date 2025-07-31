# Do this task

## Terminology

- `nicegui-web`: the web GUI implemented using `nicegui`, source code is in `src/pei_docker/webgui`
- `static-web`: the static web pages as a mockup of the GUI, used in design phase, source code is in `context/plans/web-gui/demo`
- `design-doc`: the design document for the GUI, located at `context/plans/web-gui/webgui-general-design.md`
- `pei-docker-cli`: the command line interface for PeiDocker, used to create and manage projects, source code is in `src/pei_docker/pei.py`
- `user_config.yml`: the user configuration file for PeiDocker, will be used by `pei-docker-cli configure` to generate docker-compose files, the template is `src/pei_docker/templates/config-template-full.yml`

## Task

In the "project" tab in `nicegui-web`, the placement is OK, but `static-web` has a "Create Project" button, and "Load Project" button (which should replace your "Change Project" button).

Behavior of these buttons:
- "Create Project" button should use `pei-docker-cli create` to create a new project. If the project already exists, it should show an error message.
- "Load Project" button should open a file dialog to select a project directory, and the `user_config.yml` will be loaded from the selected directory. If the file does not exist, it should show an error message. Once loaded, its relevant information should be displayed in the GUI, the mapping is given in the `design-doc`.
