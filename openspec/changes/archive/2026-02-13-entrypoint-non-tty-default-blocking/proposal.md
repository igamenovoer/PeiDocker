## Why

PeiDocker entrypoint defaults currently fall back to `/bin/bash` when no command is provided, which exits immediately in non-TTY environments (for example Kubernetes), causing containers to stop unexpectedly. This needs to be fixed now to make default container behavior reliable in both interactive and non-interactive runtimes.

## What Changes

- Define and implement non-interactive-safe default entrypoint behavior for both stage-1 and stage-2 generated images:
  - Interactive (TTY or stdin open): start `/bin/bash`.
  - Non-interactive: run a blocking foreground process (`sleep infinity`).
  - Opt-out: `--no-block` exits after preparation (no fallback blocking).
- Define a minimal entrypoint CLI:
  - If args do not start with `--`, treat them as a user command and `exec "$@"` (existing `docker run image <cmd...>` behavior).
  - If args start with `--`, parse entrypoint options until `--`, then `exec` the command after `--` (if provided).
- Add `--verbose` entrypoint option to control runtime script logging (default quiet; verbose prints "running ..." style logs).
- Rework `custom.on_entry` wiring to use generated wrapper scripts (like other lifecycle hooks):
  - Bake the configured script path and its config-specified args into `generated/_custom-on-entry.sh`.
  - Stage-2 overrides stage-1 if both exist.
  - If custom entrypoint applies, entrypoint passes all runtime args through unchanged (no entrypoint option parsing).
  - Missing custom script is a hard error (non-zero exit).
- Add required heavy functional coverage as manual-trigger tests under:
  - `tests/functional/entrypoint-non-tty-default-blocking/...`
  - Tests must build real Docker images and save logs/artifacts under `tmp/entrypoint-non-tty-default-blocking-e2e/`.
  - Primary validation is SSH-first: start container with no runtime command in non-interactive mode, verify SSH login succeeds, and confirm installed tooling/scripts are usable after login.
- Update documentation/spec coverage for entrypoint default behavior, entrypoint CLI, and non-interactive runtime expectations.

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
