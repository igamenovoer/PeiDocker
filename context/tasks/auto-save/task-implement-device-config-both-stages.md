# Task: Implement Device Configuration for Both Stages

## Command Summary
Implement enhancement to copy device configuration to both stage-1 and stage-2 when saving from GUI, following the principle that GUI's single section values should map to both stages.

## Key Points
- Stage-2 should have device configuration copied from GUI's single device setting
- GUI represents a simplified version of `user_config.yml`
- When GUI has single section for fields that can be configured separately in stages, map to both stages
- Just copy the values to both stages
- Do not modify the CLI data model yet

## Referenced Files
- `@context\tasks\prefix\prefix-test-info.md` - Explains GUI to YAML mapping principle
- `@context\instructions\write-code.md` - Code writing guidelines
- `@context\instructions\strongly-typed.md` - Type safety requirements  
- `@context\instructions\win32-env.md` - Windows environment considerations
- `@context\instructions\save-command.md` - Command saving instructions

## Implementation Notes
- The principle from prefix-test-info.md states: "if something is not separated by stage in GUI, then those things are normally mapped to both stages"
- Current issue: Stage-2 device configuration is not being saved to YAML
- Solution: Modify UI state bridge to copy device settings from single GUI field to both stages