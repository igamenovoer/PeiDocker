# Web GUI for PeiDocker

This document outlines the design and implementation of a web GUI for PeiDocker, a tool for managing Docker-based projects. The GUI will provide an intuitive interface for users to create, configure, and manage their projects.

## IMPORTANT: Single-User Assumption

The GUI is designed for single-user usage, meaning that it will not support multi-user scenarios, we do not map the user using some kind of session or authentication. If multiple users access the GUI at the same time, they will share the same project directory, and they will even see each other's changes in real-time. This is how `nicegui` works.

## Overview

The web GUI will be built using NiceGUI, a Python framework for creating web applications. The GUI will create a `project dir` on server side, which will be used to store the project files. The GUI will allow users to interact with the project files, configure the project, and download the project as a zip file.

Project can be initialized in 2 ways:

- On top of the GUI, there is a "Create Project" button, which will create a new project with the initial structure defined by `pei-docker-cli create` command, and then the user can interact with the GUI to configure the project.

- There is also a "Load Project" button, which will allow the user to load an existing project from their local machine, and the GUI will create project files structure according to the loaded project, and then the user can interact with the GUI to configure the project further. Note that, the GUI may not simply read the given project files, because it can be incomplete, some files need to be downloaded from the server.

## From scratch

This is when the user creates a new project from scratch using the GUI, clicking the "Create Project" button.

- alongside the "Create Project" button, there is place for user to input the project directory, which is the directory where the project files will be stored. By default, it is empty and will be set to a temporary directory once the user clicks the "Create Project" button, and the project directory will be shown in the textbox, we call this the `project-dir`.
- - Note that, the user can change the `project-dir` to any directory they want, as long as it is writable by the nicegui process.
- - After project is created, the user can still change the `project-dir` to any directory they want, but the GUI will not create a new project, unless the user clicks the "Create Project" button again, which will create a new project in the new `project-dir`, and treat it as a new start, resetting the GUI state.
- - The user specified `project-dir` must be empty or non-existent, otherwise the GUI will display an error message and ask the user to choose a different directory, refusing to create project in non-empty directory.

- the project is created with `pei-docker-cli create`, so the cli command defines the initial structure of the project. The created project files will be stored in `project-dir`.

- then the user will interact with the GUI, the data produced by the GUI will be stored in memory or some temporary storage, not affecting the project files, until the user explicitly click "save" button in the GUI, which changes will be written to the `project-dir` directory, overwriting existing files if necessary.

- if the user creates new scripts (for example, in `custom_scripts` section) in the GUI, the GUI will create new files in the `project-dir`, or update the project files accordingly. This happens when the user clicks "save" button in the GUI, otherwise just store those files in memory or some temporary storage.

- when "save" button is clicked, the GUI will write the current state of the project files to the project directory, overwriting existing files if necessary. Particularly, the `user_config.yml` file will be updated with the user configuration, which is the main configuration file for the project.

- when the user think he is done with the project setting, he can click "configure" button in the GUI, which will run `pei-docker-cli configure` command to update the project files structure according to the user configuration, outputing logs to the user and inform the user of any errors or warnings. This will also update the project files in the `project-dir` directory, overwriting existing files if necessary.

- a project can be `configured` multiple times, and the project files structure will be updated accordingly, overwriting existing files if necessary. GUI will just call `pei-docker-cli configure` command, and the command will determine what to do with the project files, whether to update them or not, and how to handle errors.

- if error occurs during the `configure` command, the GUI will display the error message to the user (look for "[ERROR]" in logging), whatever happens during the `configure` command is determined by the `pei-docker-cli configure` command, whether the project files structure is updated or not, and whether the user configuration is applied or not, is determined by the `pei-docker-cli configure` command, the GUI just runs it as is and DO NOT guarantee anything beyond `pei-docker-cli configure` is run.

- the project is downloadable anytime, after its creation, and when user clicks the "download" button, the GUI will zip the project directory and provide it for download. But, in the following cases, warn the user with a popup dialog:
- - if the project is not yet configured
- - if the project's last `configure` command failed
- - if there is unsaved changes in the GUI, the user can choose to save the changes or discard them before downloading.

## From existing project

NOT YET IMPLEMENTED, just warn the user that this is not implemented yet.