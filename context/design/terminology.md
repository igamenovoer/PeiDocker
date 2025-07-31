
# Terminology of PeiDocker Project

- `nicegui-web`: the web GUI implemented using `nicegui`, source code is in `src/pei_docker/webgui`
- `static-web`: the static web pages as a mockup of the GUI, used in design phase, source code is in `context/plans/web-gui/demo`
- `design-doc`: the design document for the GUI, located at `context/plans/web-gui/webgui-general-design.md`
- `pei-docker-cli`: the command line interface for PeiDocker, used to create and manage projects, source code is in `src/pei_docker/pei.py`
- `user_config.yml`: the user configuration file for PeiDocker, will be used by `pei-docker-cli configure` to generate docker-compose files, the template is `src/pei_docker/templates/config-template-full.yml`