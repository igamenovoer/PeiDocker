# Do this task

## Prerequisites

Read these first:
- Terminololy: `context/design/terminology.md`, to understand the concepts used in this task.
- Coding guide: `context/instructions/debug-code.md`, to understand how to debug the code, and also note that python code should be strongly typed, see `context/instructions/strongly-typed.md` for details.

## The problem

The current way of loading `user_config.yml` into the GUI is not optimal, easy to introduce bugs.

### Current Implementation

in `src\pei_docker\webgui\utils\ui_state_bridge.py`

```python
def _load_into_ui(self, config_data: Dict[str, Any], ui_state: AppUIState) -> None:
    """Load YAML configuration into UI state.
    
    Implements mapping rules from gui-to-core-data-mapping.md:
    - SSH: Load from stage-2 if exists in both, otherwise from whichever has it
    - Device: Load from stage-2 if exists in both, otherwise from whichever has it
    - Environment: Merge variables with stage-2 overriding stage-1
    - Network: Load from stage-2 if exists in both, otherwise from whichever has it
    """
    stage_1_data = config_data.get('stage_1', config_data.get('stage-1', {}))
    stage_2_data = config_data.get('stage_2', config_data.get('stage-2', {}))
    
    # Load project configuration
    self._load_project_config(stage_1_data, ui_state.project)
    
    # Load environment configuration (separate for each stage, no merging)
    self._load_environment_config_separate(stage_1_data, stage_2_data, ui_state)
    
    # Load network configuration following default behavior
    self._load_network_config_default(stage_1_data, stage_2_data, ui_state)
    
    ...
```

this `_load_into_ui` try to load the `user_config.yml` manually into the `ui_state`, section-by-section, this is NOT the way to do it. And in each section loading function, you try to manually parse everything, this is error prone and not maintainable.

In fact, what should be done is:

`user_config.yml` -> load into `peidocker-data-model` -> bridge to `ui-data-model`

### Solution

in `src\pei_docker\config_processor.py`, the `process()` function has an implementation as to how to load `user_config.yml` into `peidocker-data-model`.

Also, we prefer to use `omegaconf` to deal with yaml instead of using `yaml` library, as many techniques in `config_processor.py` can be reused with `omegaconf`.

```python
def process(self, remove_extra : bool = True, generate_custom_script_files : bool = True) -> DictConfig:
    """
    Process the full configuration to generate the final Docker Compose object.

    This is the main public method that orchestrates the entire process:
    1. Parses the user configuration.
    2. Applies settings to the pre-resolution compose template.
    3. Resolves the compose template variables.
    4. Applies final settings to the resolved compose object.
    5. Generates all necessary helper scripts.
    6. Cleans up the final compose object.

    Parameters
    ----------
    remove_extra : bool, optional
        If True (default), remove the `x-*` helper keys from the final compose object.
    generate_custom_script_files : bool, optional
        If True (default), generate the custom script files on the host.

    Returns
    -------
    DictConfig
        The final, processed Docker Compose configuration.

    Raises
    ------
    ValueError
        If the compose template is not set before processing.
    """
    # user_cfg = self.m_config
    # compose_cfg = self.m_compose_template.copy()
    
    # read files for test
    # fn_template = r'templates/base-image.yml'
    # fn_config = r'templates/config-template-full.yml'
    # user_cfg = oc.OmegaConf.load(fn_config)
    # compose_cfg = oc.OmegaConf.load(fn_template)
    
    config_dict = oc.OmegaConf.to_container(self.m_config, resolve=True)
    
    # convert environment from list to dict
    if isinstance(config_dict, dict):
        for stage in ['stage_1', 'stage_2']:
            if stage not in config_dict:
                continue
            
            # Handle environment conversion
            if 'environment' in config_dict[stage]:
                env = config_dict[stage]['environment']
                if env is not None and isinstance(env, list):
                    config_dict[stage]['environment'] = env_str_to_dict(env)
            
            # Handle on_entry conversion from string to list
            if 'custom' in config_dict[stage] and config_dict[stage]['custom'] is not None:
                custom = config_dict[stage]['custom']
                if 'on_entry' in custom and custom['on_entry'] is not None:
                    on_entry = custom['on_entry']
                    if isinstance(on_entry, str):
                        # Convert string to single-element list
                        config_dict[stage]['custom']['on_entry'] = [on_entry]
    
    # [!!IMPORTANT: this is the key part, a valid user_config.yml should be able to be parsed into UserConfig]
    # parse the user config
    user_config : UserConfig = cattrs.structure(config_dict, UserConfig)
    
    # apply the user config to the compose template
    if self.m_compose_template is None:
        raise ValueError("compose_template is None")
    compose_template : DictConfig = self.m_compose_template.copy()
```

