# Config Processing

`PeiConfigProcessor` is the main transformation layer between the typed config model and emitted artifacts.

## Main Phases

### 1. Load And Normalize

- `pei.py` loads YAML with duplicate-key rejection.
- `pei_utils.py` performs config-time `${VAR}` substitution.
- legacy list-form environment values are normalized to dictionaries.
- string `custom.on_entry` values are normalized to single-item lists.

### 2. Pre-Resolution Compose Updates

`_process_config_and_apply_x_compose()` writes build-oriented values into `x-cfg-stage-1` and `x-cfg-stage-2`, including:

- image names
- SSH settings
- proxy settings
- APT settings
- device selection

### 3. Resolve Template

The compose template is converted to a container structure with OmegaConf resolution enabled, then re-created as a resolved config object.

### 4. Post-Resolution Service Updates

`_apply_config_to_resolved_compose()` fills service-level fields:

- cumulative environment
- port strings
- storage and mount volume mappings
- service `volumes:` lists

### 5. Generate Files

The processor writes:

- custom lifecycle wrappers
- custom `on_entry` wrappers
- stage environment shell fragments

## Important Helper Methods

| Method | Role |
| --- | --- |
| `_parse_script_entry()` | Splits script path from argument text while preserving shell syntax |
| `_validate_stage2_on_build_script_entries()` | Rejects runtime-only storage paths in build hooks |
| `_reject_passthrough_markers_in_script_entries()` | Rejects `{{...}}` in generated-script contexts |
| `_generate_etc_environment_with_bake_flags()` | Writes environment files and enforces bake-time restrictions |

## Why The Two-Pass Approach Exists

Some values belong in build args before the template resolves. Others depend on resolved service structure. The processor therefore applies config once before resolution and again after resolution.
