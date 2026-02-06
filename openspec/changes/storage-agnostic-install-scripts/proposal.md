## Why

PeiDocker's curated installation scripts are currently tightly coupled to the stage-2 storage filesystem layout (e.g. `/soft/app`, `/soft/data`, `/soft/workspace`), making them difficult to reuse in single-Dockerfile CI builds or "fully provisioned at build time" images. We want the same installers to work in both stage-2 runtime workflows and plain Dockerfile contexts by taking explicit destination paths rather than assuming `/soft/*` symlinks exist.

## What Changes

- Standardize how installation scripts receive destination paths and runtime inputs via **script-specific flags** (e.g. `--install-dir`, `--cache-dir`, `--tmp-dir`), rather than relying on PeiDocker stage detection or `/soft/*` hardcoding.
- Update stage-2 oriented scripts to:
  - Stop detecting stages by probing `/soft/*`.
  - Stop writing to `/soft/*` directly.
  - Instead, use explicit paths passed by the caller (args and/or documented env vars), with each script owning its own defaults appropriate for that tool (e.g. npm installs to user home, apt installs to system locations, ros2 installs under `/opt`, etc.).
- Make stage-2 prefer calling stage-1 scripts directly. Only keep/add stage-2 wrapper scripts when stage-2 needs to inject stage-2 storage-related behavior or values (e.g. configuring build-time paths under `/hard/image/...` for `on_build`, and runtime paths under `/soft/...` for first-run/every-run/login hooks).
- Ensure stage-2 scripts can be invoked during stage-1 or merged builds (single Dockerfile) without requiring stage-2 runtime storage plumbing.
- Add documentation and representative examples for:
  - Single Dockerfile CI builds that call PeiDocker installers.
  - Stage-2 workflows passing stage-2 resolved prefixes into the same installers.

## Capabilities

### New Capabilities

- `install-script-parameter-interface`: Define a consistent, documented convention for installer scripts to accept explicit path inputs via script-specific CLI flags (e.g. `--install-dir`, `--cache-dir`, `--tmp-dir`) and avoid stage detection and `/soft/*` hardcoding.
- `stage2-wrapper-forwarding`: Stage-2 should use stage-1 scripts directly when possible; only keep/add stage-2 wrapper scripts where stage-2 must inject stage-2 storage values/behavior, and document that build-time hooks use `/hard/image/...` while runtime hooks may use `/soft/...`.
- `single-dockerfile-ci-install-flow`: Provide a documented minimal "single Dockerfile" example showing how to invoke a representative set of installers to produce a fully provisioned image.

### Modified Capabilities

<!-- None -->

## Impact

- Affects installer scripts under `src/pei_docker/project_files/installation/` (especially `stage-2/system/...`) and any wrappers that invoke them.
- Documentation updates: how to use installers in stage-2 vs plain Dockerfile contexts.
- May require small changes in config/template generation so PeiDocker can pass stage-2 resolved prefixes into installers when building images.
