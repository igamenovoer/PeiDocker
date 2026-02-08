# Spec: install-script-parameter-interface

## Purpose

Define a minimal, storage-agnostic parameter interface for installer scripts and PeiDocker custom script invocations.

## Requirements

### Requirement: Installer scripts are storage-agnostic by default
Installer scripts (especially those used by stage-2 flows) MUST NOT hardcode writes to `/soft/app`, `/soft/data`, or `/soft/workspace`, and MUST NOT attempt to infer stage or storage behavior by probing `/soft/*`.

#### Scenario: Script runs in a plain Dockerfile build
- **WHEN** an installer script is executed during a plain `docker build` (without stage-2 runtime entrypoint behavior)
- **THEN** the script does not require `/soft/*` to exist and does not probe `/soft/*` to decide behavior

### Requirement: Path inputs are explicit and tool-specific
If an installer script needs a non-default filesystem location (e.g. for installs, cache, or temp files), it MUST accept explicit CLI flags for those locations using tool-specific semantics (e.g. `--install-dir`, `--cache-dir`, `--tmp-dir`) and MUST document them.

#### Scenario: Script needs a cache directory
- **WHEN** a caller needs the script to use a non-default cache directory
- **THEN** the caller can pass a documented `--cache-dir=<abs-path>` (or equivalent explicit flag) to control the location

### Requirement: Flags accept absolute paths
When a script accepts path flags intended for container filesystem paths (e.g. `--install-dir`, `--cache-dir`, `--tmp-dir`), those flags MUST accept absolute paths.

#### Scenario: Stage-2 caller passes a stage-2 path
- **WHEN** a stage-2 caller passes `--cache-dir=/soft/data/cache`
- **THEN** the script uses that directory path without assuming any stage-specific prefixing rules

### Requirement: Defaults remain per-tool
Scripts MUST retain per-tool defaults appropriate for the tool and context (e.g. apt installs to system locations, nvm installs to user home), and MUST treat explicit flags as overrides.

#### Scenario: No explicit install directory provided
- **WHEN** an installer script is executed without `--install-dir`
- **THEN** it uses its tool-appropriate default location

### Requirement: Custom script arguments may reference environment variables
PeiDocker custom script invocations MUST allow users to reference environment variables in script arguments (e.g. `$PEI_SOFT_DATA`, `$HOME`) so scripts can resolve those values at execution time.

#### Scenario: Argument contains an env var token
- **WHEN** a user configures a custom script invocation with an argument like `--cache-dir=$PEI_SOFT_DATA/cache`
- **THEN** PeiDocker preserves the token so the shell expands it when executing the script
