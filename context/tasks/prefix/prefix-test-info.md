# Info useful for test tasks

## Useful Files

- readme: `README.md`, this file contains the overview of the PeiDocker project, its purpose and basic usage.
- terminology: `context/tasks/prefix/prefix-terminology.md`, this includes the terminology that is useful for many tasks.
- GUI design document: `context/plans/web-gui/webgui-general-design.md`, this includes the design of the GUI, which is useful for understanding how to use the GUI and what features it supports.
- GUI source code: `src/pei_docker/webgui/`, this is the source code of the GUI, which is useful for understanding how the GUI works and how to extend it.
- CLI commands
    - `pei-docker-cli`: This command creates and manages PeiDocker projects, source code is in `src/pei_docker/pei.py`.
    - `pei-docker-gui`: This command starts the GUI, source code is in `src/pei_docker/webgui/cli_launcher.py`.
- User configuration template: `src/pei_docker/templates/config-template-full.yml`, this is the master template for the project-specific `user_config.yml` file, which contains all the settings that can be configured in the GUI.
  
## Test Project

- you can create test projects using `pei-docker-cli create -p <path>` command, this will create a new project in the specified path, you can then load it in the GUI.
- normally, you will create a new project using `pei-docker-cli create -p <path>` to create temporary project for testing, avoiding corruption of the existing project files, unless you are testing project loading or saving functionality.
- `pei-docker-gui start --project-dir <path>` command will start the GUI with the specified project directory, you can use it to load existing projects.
- temporary projects can be created in `<workspace>/tmp`, or in the system temporary directory (python `tempfile.gettempdir()`).

## Difference between GUI and `user_config.yml`

The GUI does not contain all the functionality of the `user_config.yml` and this PeiDocker project, this is expected, as the GUI aims to provide a user-friendly interface for common tasks, while the `user_config.yml` file contains detailed configurations that can be edited for advanced use cases.

So, some of the settings in `user_config.yml` will be simplified and then reflected in the GUI, for example, the environment variables in `user_config.yml` can be configured for `stage-1` and `stage-2` separately, but in the GUI, they are combined into a single section, so we assume that the GUI will set environment variables for both stages at the same time. When loading the project, you simply combine the environment variables from both stages, if `stage-1` and `stage-2` have the same variable, the value from `stage-2` will be used, the behavior is just like `export` command applied to the environment variables in stage-1 and then stage-2.

This principle applies to all the settings in `user_config.yml` where stage-1 and stage-2 can be configured separately but the GUI has only a single section for them.