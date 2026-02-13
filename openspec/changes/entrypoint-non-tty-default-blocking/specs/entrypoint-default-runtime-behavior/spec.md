## ADDED Requirements

### Requirement: Entrypoint preparation runs before handoff
When a stage container starts, entrypoint MUST run stage preparation steps before handing off to:
- a custom `on_entry` entrypoint,
- a user command, or
- default fallback behavior.

### Requirement: Custom `on_entry` is executed via a generated wrapper script
When `custom.on_entry` is configured for a stage, the system MUST generate a wrapper script:
- Stage-1: `$PEI_STAGE_DIR_1/generated/_custom-on-entry.sh`
- Stage-2: `$PEI_STAGE_DIR_2/generated/_custom-on-entry.sh`

The wrapper script MUST:
- invoke the configured target script,
- include any config-specified args baked into the wrapper,
- forward runtime args (`"$@"`) to the target script,
- and pass baked config args before runtime args.

#### Scenario: Stage-2 overrides stage-1 custom `on_entry`
- **WHEN** a stage-2 container starts
- **AND** stage-2 has a configured custom `on_entry` wrapper script
- **THEN** stage-2 custom `on_entry` MUST be executed
- **AND** stage-1 custom `on_entry` (if present) MUST be ignored

#### Scenario: Custom `on_entry` target script missing is an error
- **WHEN** a stage container starts
- **AND** its selected custom `on_entry` wrapper resolves to a missing target script
- **THEN** entrypoint MUST log an error and exit with a non-zero status

#### Scenario: Entrypoint does not parse default-mode options when custom `on_entry` applies
- **WHEN** a custom `on_entry` wrapper applies
- **THEN** entrypoint MUST pass all runtime args through unchanged
- **AND** it MUST NOT interpret `--no-block` or other default-mode options

### Requirement: Default-mode CLI shape
When no custom `on_entry` applies:
- If argv does **not** start with `--`, entrypoint MUST treat argv as a user command and `exec "$@"`.
- If argv **does** start with `--`, entrypoint MUST parse entrypoint options until `--`, then treat everything after `--` as the user command to `exec` (if provided).

Supported entrypoint options (default-mode) MUST include:
- `--no-block` (flag)
- `--verbose` (flag)

#### Scenario: Default-mode options with command
- **WHEN** a stage container starts with argv beginning with `--`
- **AND** argv contains `--` followed by command args
- **THEN** entrypoint MUST execute the command args after `--`

#### Scenario: Unknown entrypoint option is an error
- **WHEN** a stage container starts with argv beginning with `--`
- **AND** an unrecognized `--*` option is provided before `--`
- **THEN** entrypoint MUST exit non-zero with a helpful error message

### Requirement: `--no-block` disables default fallback blocking
When no custom `on_entry` applies and no user command is provided:
- If `--no-block` is specified, entrypoint MUST exit successfully after preparation (no bash, no sleep).

### Requirement: `--verbose` enables verbose runtime hook wrapper logging
When `--verbose` is specified in default-mode options, entrypoint MUST enable verbose logging for runtime hook wrappers and preparation scripts.

Implementation note:
- Entrypoint SHOULD export a single environment variable (for example `PEI_ENTRYPOINT_VERBOSE=1`) before running stage preparation.

#### Scenario: Default-mode verbose enabled
- **WHEN** a stage container starts with `--verbose`
- **THEN** runtime hook wrappers under `generated/` (including the generated custom `on_entry` wrapper) MUST print a log message when invoked

#### Scenario: Default-mode verbose not enabled
- **WHEN** a stage container starts without `--verbose`
- **THEN** runtime hook wrappers under `generated/` (including the generated custom `on_entry` wrapper) SHOULD avoid noisy "Executing ..." logs

### Requirement: Interactive detection includes stdin-open (`docker run -i`)
When no custom `on_entry` applies and no user command is provided and `--no-block` is not specified:
- If stdin is a TTY OR stdin is open (not `/dev/null`), entrypoint MUST start `/bin/bash`.
- If stdin is not a TTY AND stdin is closed (`/dev/null`), entrypoint MUST run a blocking foreground process (`sleep infinity` or equivalent).

#### Scenario: stdin-open no-command runtime
- **WHEN** a stage container starts without a TTY
- **AND** stdin is open (e.g. `docker run -i`)
- **AND** no custom `on_entry` applies
- **AND** no user command is provided
- **THEN** entrypoint MUST start `/bin/bash`

#### Scenario: non-interactive no-command runtime
- **WHEN** a stage container starts without a TTY
- **AND** stdin is closed (`/dev/null`)
- **AND** no custom `on_entry` applies
- **AND** no user command is provided
- **THEN** entrypoint MUST execute `sleep infinity` (or equivalent) as a blocking foreground process

### Requirement: Logging
Entrypoint MUST log which final action it takes:
- custom `on_entry`
- exec user command
- bash fallback
- sleep fallback
- no-block exit
