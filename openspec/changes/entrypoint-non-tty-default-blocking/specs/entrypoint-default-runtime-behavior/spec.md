## ADDED Requirements

### Requirement: Non-TTY default entrypoint behavior blocks when no command is provided
When no custom entrypoint is configured and no runtime command arguments are provided, stage entrypoints MUST keep the container alive in non-interactive (non-TTY) contexts by running a blocking foreground process.

#### Scenario: Stage-1 no-command non-TTY runtime
- **WHEN** a stage-1 container starts without runtime command arguments
- **AND** stdin is not a TTY
- **AND** no valid custom entrypoint script is configured
- **THEN** the entrypoint runs a blocking foreground process (`sleep infinity` or equivalent) instead of launching `/bin/bash`

#### Scenario: Stage-2 no-command non-TTY runtime
- **WHEN** a stage-2 container starts without runtime command arguments
- **AND** stdin is not a TTY
- **AND** no valid custom entrypoint script is configured in stage-2 or stage-1
- **THEN** the entrypoint runs a blocking foreground process (`sleep infinity` or equivalent) instead of launching `/bin/bash`

### Requirement: TTY default behavior remains interactive
When no custom entrypoint is configured and no runtime command arguments are provided in an interactive context, entrypoints MUST continue to start an interactive bash shell.

#### Scenario: Interactive runtime with no command
- **WHEN** a stage container starts without runtime command arguments
- **AND** stdin is a TTY
- **AND** no valid custom entrypoint script is configured
- **THEN** the entrypoint starts `/bin/bash` for interactive usage

### Requirement: Runtime command arguments keep highest precedence
Runtime command arguments MUST continue to take precedence over default shell/blocking behavior.

#### Scenario: Runtime command is provided
- **WHEN** a stage container starts with runtime command arguments
- **THEN** the entrypoint executes the provided command arguments
- **AND** it does not fall back to default interactive or blocking behavior

### Requirement: Custom entrypoint behavior is preserved
Existing custom entrypoint selection and argument precedence behavior MUST remain unchanged.

#### Scenario: Custom entrypoint with no runtime args
- **WHEN** a valid custom entrypoint script is configured
- **AND** no runtime command arguments are provided
- **THEN** the configured custom entrypoint executes with existing default-argument precedence rules
