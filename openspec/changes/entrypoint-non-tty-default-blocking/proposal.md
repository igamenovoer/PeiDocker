## Why

PeiDocker entrypoint defaults currently fall back to `/bin/bash` when no command is provided, which exits immediately in non-TTY environments (for example Kubernetes), causing containers to stop unexpectedly. This needs to be fixed now to make default container behavior reliable in both interactive and non-interactive runtimes.

## What Changes

- Define and implement non-TTY-safe default entrypoint behavior for both stage-1 and stage-2 generated images.
- Keep interactive behavior for TTY-attached runs while changing non-interactive default behavior to a blocking process.
- Ensure command passthrough remains unchanged (`$@` still takes priority when provided).
- Update documentation/spec coverage for entrypoint default behavior and non-TTY runtime expectations.

## Capabilities

### New Capabilities

- `entrypoint-default-runtime-behavior`: Defines default command behavior for interactive and non-interactive contexts when no custom command is provided.

### Modified Capabilities

<!-- none -->

## Impact

- Entrypoint scripts:
  - `src/pei_docker/project_files/installation/stage-1/internals/entrypoint.sh`
  - `src/pei_docker/project_files/installation/stage-2/internals/entrypoint.sh`
- Related docs/spec artifacts under `openspec/` and possibly `docs/` if runtime behavior is documented there.
