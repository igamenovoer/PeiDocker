# How to map GUI data model to core data model

## Terminology

you can find the full terminology in `context/tasks/prefix/prefix-terminology.md`, here is some relevant parts:

- `ui-data-model`: The data model that represents the state of the GUI, source code is in `src\pei_docker\webgui\models\ui_state.py`.

- `ui-data-adapter`: The adapter that converts between the `peidocker-data-model` and the `ui-data-model`, source code in `src\pei_docker\webgui\models\config_adapter.py`

- `peidocker-data-model`: This is the core data model that represents the `user_config.yml` file during the configuration process, mainly used by the `pei-docker-cli` command line interface and `config_processor.py` module.

- `user_config.yml`: This is the configuration file for the PeiDocker project, which contains settings for SSH, environment variables, and other configurations. It is located in the project directory and can be edited to customize the project. Its master template is in `src/pei_docker/templates/config-template-full.yml`.

## Mapping Principle

The GUI represents a simplified version of `user_config.yml`, and when the GUI has a single section for fields that in `user_config.yml` can be configured separately in stages, those fields (call it `simplified-field`) should be mapped according to these principles:

### Default Behavior
- writing to `user_config.yml`: `simplified_field` settings are normally mapped to both stages in `user_config.yml`, just copy the values to both stages.
- reading from `user_config.yml`
  - if `simplified_field` only exists in a single stage, then load it from that stage.
  - if `simplified_field` exists in both stages, then load it from `stage-2`, as it is the most recent configuration.

### Specific Cases

These tabs in the GUI have specific mapping rules:

- `ssh` tab
  - writing to `user_config.yml`: the SSH settings in the GUI should map to `stage-1` ONLY
  - reading from `user_config.yml`: follow the default behavior.
  
- `device` tab: follow the default behavior.

- `environment` tab: the GUI has separate sections for `stage-1` and `stage-2`, so no special mapping is needed. 

- `network` tab: follow the default behavior.
  
- `script` tab: the GUI has separate sections for `stage-1` and `stage-2`, so no special mapping is needed.

- `storage` tab: the GUI has separate sections for `stage-1` and `stage-2`, so no special mapping is needed.