# Do this task

## Prerequisites

Read these first:
- Terminololy: `context/design/terminology.md`, to understand the concepts used in this task.
- Coding guide: `context/instructions/debug-code.md`, to understand how to debug the code, and also note that python code should be strongly typed, see `context/instructions/strongly-typed.md` for details.

## The problem

### Data flow from GUI to `user_config.yml` is wrong

The current data flow from GUI setting to `user_config.yml` is not wrong, seeing this in `src\pei_docker\webgui\utils\ui_state_bridge.py`:

```python
# [BUG: the implementation directly map the ui state to user_config.yml format, this is not the way to do it, should go through the `peidocker-data-model` first. Specifically, see the _ui_to_attrs_config() function about how to convert `ui-data-model` to `peidocker-data-model`, and then use the `peidocker-data-model` to generate the `user_config.yml` format, in-memory]
    def _ui_to_user_config_format(self, ui_state: AppUIState) -> Dict[str, Any]:
        """Convert UI state to user_config.yml format."""
        # This method remains largely the same as it's converting to YAML format
        # The previous implementation already handles the conversion correctly
        
        # Convert environment variables to list format
        def env_vars_to_list(env_vars: Dict[str, str]) -> List[str]:
            return [f"{k}={v}" for k, v in env_vars.items()]
        
        # Build stage-1 configuration
        output_name = ui_state.project.image_output_name or ui_state.project.project_name or "pei-image"
        stage_1: Dict[str, Any] = {
            'image': {
                'base': ui_state.project.base_image,
                'output': f"{output_name}:stage-1"
            }
        }
        
        # Add inline scripts metadata if any
        inline_scripts_1: Dict[str, str] = {}
        inline_scripts_2: Dict[str, str] = {}
        
        # Process stage-1 inline scripts
        if ui_state.stage_1.scripts.entry_mode == "inline":
            script_name = ui_state.stage_1.scripts.entry_inline_name
            script_content = ui_state.stage_1.scripts.entry_inline_content
            if script_name and script_content:
                inline_scripts_1[script_name] = script_content
                stage_1['entry_point'] = f"/pei-docker/scripts/{script_name}"
        elif ui_state.stage_1.scripts.entry_mode == "file":
            stage_1['entry_point'] = ui_state.stage_1.scripts.entry_file_path
        
        # Add environment configuration to stage-1
        # Environment tab has separate sections for stage-1 and stage-2, save separately
        if ui_state.stage_1.environment.env_vars:
            stage_1['environment'] = env_vars_to_list(ui_state.stage_1.environment.env_vars)
        
        # Add device configuration to stage-1
        if ui_state.stage_1.environment.device_type != DeviceTypes.CPU:
            stage_1['device'] = {
                'type': ui_state.stage_1.environment.device_type
            }
...

```

It has the following problems:
- the data flow from GUI to `user_config.yml` is should be: GUI state -> `ui-data-model` -> `peidocker-data-model` -> `user_config.yml`. For summary tab preview, the data flow should still be the above, just the `user_config.yml` is not written to disk, but generated in-memory and passed to the summary tab.
- the `_ui_to_user_config_format()` function has too many duplicated code, the processing logic for stage-1 and stage-2 are very similar, so it should be refactored to avoid code duplication.
