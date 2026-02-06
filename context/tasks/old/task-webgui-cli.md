we need to update the implementation of `pei-docker-gui` to launch the NiceGUI web application, discarding the previous `textual` implementation.

# Specification of `pei-docker-gui`

The `pei-docker-gui` should be used to launch the NiceGUI web application, which cli tool is implemented in `src/pei_docker/gui/app.py`, which is for the previous `textual` implementation. You need to create one like this in `src/pei_docker/webgui/cli-launcher.py`, and update `pyproject.toml` to redirect the `pei-docker-gui` command to this new implementation.

Here are the specifications of the `pei-docker-gui` subcommand:

## 'start' subcommand

This subcommand should start the NiceGUI web application. Options include:
- `--port <port>`: specify the port to run the NiceGUI web application, default is `8080`. If the port is already in use, it should show an error message and exit.
- `--project-dir <path>`: specify the project directory to load the user configuration from. 
  - If the directory exists, then the functionality is equivalent to clicking "load project" in the NiceGUI web application. 
  - If the directory does not exist, its functionality is equivalent to clicking "create project" in the NiceGUI web application, which will create a new project using `pei-docker-cli create` to create a new project in the specified directory.
  - If the directory is not legitimate, causing the NiceGUI web application to fail, it should show an error message and exit.
- `--jump-to-page <page_name>`: specify the page to jump to after starting the NiceGUI web application. If the project directory is specified, then load the project and go, otherwise, create the project and go (the gui will have a default project path in tmp dir, so you do not have to worry about that). Page names are defined in the NiceGUI web application (those tab names), with the followings:
  - `home`: the home page of the NiceGUI web application.
  - `project`: the project configuration page, which normally appears after creating or loading a project.
  - `ssh`: the SSH configuration page.
  - `network`: the network configuration page.
  - `environment`: the environment configuration page.
  - `storage`: the storage configuration page.
  - `scripts`: the custom scripts configuration page.
  - `summary`: the summary page, which shows the overall configuration of the project.
  