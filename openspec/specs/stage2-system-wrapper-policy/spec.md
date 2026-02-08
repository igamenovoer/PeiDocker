# Spec: stage2-system-wrapper-policy

## Purpose

Specify the behavioral contract for stage-2 system wrapper scripts that forward to stage-1 canonical installers, including source-safety and argument forwarding.

## Requirements

### Requirement: Stage-2 system scripts are thin wrappers by default
For migrated tools, `src/pei_docker/project_files/installation/stage-2/system/**` scripts SHALL be thin wrappers whose primary responsibility is to forward to the stage-1 canonical implementation.

#### Scenario: Stage-2 wrapper forwards to stage-1 canonical
- **WHEN** a stage-2 system script exists for a migrated tool
- **THEN** it MUST locate and invoke the stage-1 canonical script via `$PEI_STAGE_DIR_1/system/<tool>/...`
- **AND** it MUST NOT duplicate full installer logic

### Requirement: Wrappers forward arguments verbatim
Wrappers MUST forward user-provided arguments verbatim (including quotes and `$VARS`) and MUST NOT re-tokenize or re-quote arguments.

#### Scenario: Wrapper preserves `$VARS` and explicit quotes
- **WHEN** a wrapper is invoked with arguments like `--cache-dir=$HOME/cache` and `--message="hello world"`
- **THEN** the wrapper MUST forward the arguments using `"$@"` (or equivalent) so `$VARS` can expand at execution time and quoted values remain quoted

### Requirement: Wrapper execution mode matches call site (exec vs source)
Wrappers SHALL use the correct forwarding mode based on how they are used, and MUST be safe to `source` in all cases:

- When executed directly: wrappers for executable installers SHOULD forward via `exec ... "$@"`
- When sourced: wrappers MUST NOT `exec` and MUST NOT hard-`exit` a parent shell

#### Scenario: Source wrapper does not hard-exit a parent shell
- **WHEN** a wrapper is sourced (e.g. from `on_user_login`, which uses `source`)
- **THEN** the wrapper MUST use `return` on error when possible
- **AND** the wrapper MUST invoke stage-1 installer logic in a way that does not terminate or replace the parent shell (e.g., by running `bash "$PEI_STAGE_DIR_1/..." "$@"` inside the wrapper and returning the status)

### Requirement: Wrapper behavior is explicit and minimal
If a wrapper must add stage-2-only glue, it MUST do so in a minimal, explicit way (e.g., default flag injection), and MUST still delegate the bulk of logic to stage-1.

#### Scenario: Wrapper adds only minimal glue
- **WHEN** a wrapper adds stage-2 behavior
- **THEN** that behavior MUST be limited to stage-2-specific concerns
- **AND** the wrapper MUST still invoke the stage-1 canonical implementation as the primary action

### Requirement: Wrappers fail with a clear error when stage dirs are unavailable
Wrappers MUST fail fast with a clear error message if required environment variables (notably `$PEI_STAGE_DIR_1`) are not set.

#### Scenario: PEI_STAGE_DIR_1 is missing
- **WHEN** a stage-2 wrapper is executed or sourced without `$PEI_STAGE_DIR_1` set
- **THEN** it MUST return/exit with a non-zero code (return if sourced, exit if executed) and an error explaining it cannot locate the stage-1 canonical scripts

### Requirement: Wrappers are source-safe unconditionally
All stage-2 system wrappers MUST be safe to `source`, even if they are typically executed as standalone installers.

#### Scenario: Wrapper detects it is sourced
- **WHEN** a wrapper is sourced instead of executed
- **THEN** it MUST avoid `exec` and MUST use `return` for error propagation
- **AND** it SHOULD detect sourcing via shell-native mechanisms (e.g., comparing `${BASH_SOURCE[0]}` with `$0` in bash)
