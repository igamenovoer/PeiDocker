# Spec: stage2-wrapper-forwarding

## Purpose

Define how stage-2 prefers stage-1 installers and the forwarding rules for any stage-2 wrapper scripts, including build-time vs runtime path constraints.

## Requirements

### Requirement: Stage-2 prefers stage-1 installers
For installation functionality that does not require stage-2 storage mechanics, stage-2 flows SHOULD call the corresponding stage-1 installer script directly rather than maintaining a duplicated stage-2 copy.

#### Scenario: Installer is independent of stage-2 storage
- **WHEN** an installer script can run without stage-2-specific storage logic
- **THEN** stage-2 usage prefers invoking the stage-1 script path

### Requirement: Stage-2 wrapper scripts are minimal forwarders
If a stage-2 wrapper script exists, it MUST primarily forward to a stage-1 script and MUST NOT re-implement the installer logic beyond parameter mapping and stage-2-specific glue.

#### Scenario: Wrapper forwards explicit flags
- **WHEN** a stage-2 wrapper is invoked
- **THEN** it forwards the user-provided tool-specific flags to the stage-1 script (and MAY add minimal stage-2 glue), without re-implementing the installer logic

### Requirement: Build-time paths are image-based, runtime paths may use /soft
When stage-2 users configure build-time script invocations (`custom.on_build`), they MUST target in-image paths (typically under `/hard/image/...`) for any tool-specific path flags. For runtime script invocations (first-run/every-run/user-login/entrypoint command), users MAY target `/soft/...` paths for tool-specific path flags.

Rationale: `/soft/*` symlinks and mounted volumes are only available after the container has started (stage-2 `on-entry.sh`), not during `docker build`.

#### Scenario: on_build uses /soft path
- **WHEN** a user configures a build-time script invocation that passes a `/soft/...` path, or uses a PeiDocker-defined env var token that expands to `/soft/...` (e.g. `$PEI_SOFT_DATA`, `$PEI_PATH_SOFT`) as a tool-specific path flag
- **THEN** PeiDocker rejects the configuration during parsing with a clear error message

#### Scenario: runtime uses /soft path
- **WHEN** a user configures a runtime script invocation that passes `/soft/...` paths as tool-specific path flags
- **THEN** the configuration is accepted

### Requirement: Wrapper interfaces use tool-specific flags
Stage-2 wrappers MUST pass storage-related paths via the stage-1 script's tool-specific flags (e.g. `--cache-dir`, `--tmp-dir`, `--install-dir`) rather than relying on implicit stage-2 conventions or hardcoded `/soft/*` paths.

#### Scenario: Stage-2 wants cache on data storage
- **WHEN** stage-2 wants a tool's cache to live under data storage
- **THEN** stage-2 passes an explicit `--cache-dir` pointing at `/soft/data/<tool-cache>` for runtime hooks, rather than having the stage-1 script hardcode `/soft/data`
