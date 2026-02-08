# Spec: stage1-system-canonical-installers

## Purpose

Define `stage-1/system/**` as the canonical location for system installer implementations and specify how stage-2 flows reference those scripts and assets.

## Requirements

### Requirement: Stage-1 contains canonical system installers
The repository SHALL treat `src/pei_docker/project_files/installation/stage-1/system/**` as the canonical location for system installer implementations, for tools currently present under `src/pei_docker/project_files/installation/stage-2/system/**` (excluding conda; see below).

#### Scenario: Stage-2 tool has a stage-1 canonical equivalent
- **WHEN** a tool exists at `src/pei_docker/project_files/installation/stage-2/system/<tool>/`
- **THEN** a corresponding canonical tool directory MUST exist at `src/pei_docker/project_files/installation/stage-1/system/<tool>/`
- **AND** stage-2 paths MUST remain callable via either (a) a thin wrapper, or (b) an explicit “stage-2-only” implementation with documented justification

### Requirement: Tool assets move with scripts
When migrating a tool from stage-2 to stage-1, the change MUST move any non-shell assets required for correct execution (e.g., Python helpers, JSON/YAML configs) into the stage-1 canonical tool directory, preserving relative paths used by the scripts.

#### Scenario: Tool directory contains required non-shell assets
- **WHEN** a tool installer relies on a non-shell asset located under its tool directory
- **THEN** the same asset MUST exist under the stage-1 canonical tool directory with the same relative path

### Requirement: Non-shell assets do not need stage-2 compatibility paths
For migrated tools, stage-2 does not require separate compatibility paths for non-shell assets under `src/pei_docker/project_files/installation/stage-2/system/**`, because stage-2 hooks/configs can reference stage-1 canonical asset paths directly.

#### Scenario: Stage-2 hook references a stage-1 asset path
- **WHEN** a stage-2 hook or documentation references a non-shell asset under `stage-1/system/<tool>/...`
- **THEN** that reference SHOULD be considered valid, and no stage-2 asset copy is required for compatibility

### Requirement: Stage-2 configs can call stage-1 canonical scripts
Stage-2 `custom.*` hooks in `user_config.yml` SHALL support referencing stage-1 script paths directly (e.g., `stage-1/system/<tool>/install-<tool>.sh`) without requiring stage-2 wrapper indirection.

#### Scenario: stage_2.custom.on_build calls a stage-1 script
- **WHEN** `stage_2.custom.on_build` includes a script entry whose path starts with `stage-1/system/`
- **THEN** `pei-docker-cli configure` MUST generate wrapper scripts that execute that entry without path rewriting or path restrictions beyond existing lifecycle validation

### Requirement: Conda migration is out of scope
This change SHALL NOT migrate or refactor `src/pei_docker/project_files/installation/stage-2/system/conda/**`.

#### Scenario: Conda remains in stage-2
- **WHEN** `src/pei_docker/project_files/installation/stage-2/system/conda/` exists
- **THEN** it MUST remain present after this change and conda migration tasks MUST be explicitly deferred

### Requirement: Referencing migrated scripts in user_config.yml does not error
For any migrated tool, referencing its stage-1 canonical path in `user_config.yml` MUST execute without errors caused by stage-2-only storage mechanics, assuming the tool’s prerequisites are met and the caller provided valid paths for any tool-specific flags.

#### Scenario: Stage-2 hook invokes a migrated stage-1 installer
- **WHEN** a stage-1 canonical installer is invoked from a stage-2 hook (`on_build`, `on_first_run`, `on_every_run`, or `on_user_login`)
- **THEN** the invocation MUST succeed or fail only for tool-prerequisite reasons (not because stage-2 wrappers or stage-2 storage layout are required)
