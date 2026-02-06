# Do this task

Fix the following issues of the GUI. We use the terminology as said in `context/design/terminology.md`.

## Environment Variables Tab

the mapping between `ui-data-model` and `peidocker-data-model` is changed, see `context\design\gui-to-core-data-mapping.md`, previouly the GUI does not have separate sections for `stage-1` and `stage-2`, but now it does, so the mapping should be updated accordingly.

The GUI has separate sections for `stage-1` and `stage-2`, but its `ui-data-model` does not have separate sections, see the current implementation:

```python

# [BUG: all settings do not separate stage-1 and stage-2, they are all in the same section, this will not map to peidocker-data-model correctly, store them for different stages]

@binding.bindable_dataclass
class EnvironmentUI:
    """UI state for environment configuration - automatically syncs with widgets"""

    # GPU Configuration
    gpu_enabled: bool = False

# [BUG: we ONLY supports "all", so no need to have this field, remove it]
    gpu_count: str = "all"  # "all" or specific number

# [BUG: we do not have cuda version, remove it]
    cuda_version: str = "12.4"

    # Environment Variables  
    env_vars: Dict[str, str] = field(default_factory=dict)
    
    # Device Configuration
    device_type: str = "cpu"  # "cpu", "gpu", "custom"
    
# [BUG: we do not have gpu limit in peidocker-data-model, remove it]
    # GPU specific settings
    gpu_memory_limit: str = ""  # e.g., "4GB"
```

if the data model adapter layer needs change, also change the env settings from single stage to separate stages.