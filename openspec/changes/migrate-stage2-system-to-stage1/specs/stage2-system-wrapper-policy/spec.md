## ADDED Requirements

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
Wrappers SHALL use the correct forwarding mode based on how they are used:

- executable installers MUST forward via `exec ... "$@"`
- utility scripts intended to be sourced MUST forward via `source ...` and be source-safe

#### Scenario: Source wrapper does not hard-exit a parent shell
- **WHEN** a wrapper is intended to be sourced (e.g., used by another script via `source`)
- **THEN** the wrapper MUST use `return` on error when possible (falling back to `exit` only when executed directly)

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
- **THEN** it MUST return/exit with a non-zero code and an error explaining it cannot locate the stage-1 canonical scripts
