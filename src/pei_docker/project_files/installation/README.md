# Installation Directory

This directory contains scripts and configuration files that are copied into the Docker image.

## Usage

Files in this directory are available inside the container at `/pei-from-host`.

## Structure

*   `stage-1/`: Files specific to the Stage 1 build (System layer).
*   `stage-2/`: Files specific to the Stage 2 build (Application layer).

## Canonical System Installers

System installer implementations are **canonical in stage-1**:

- Prefer referencing `stage-1/system/**` paths directly in `user_config.yml` (including from `stage_2.custom.*` hooks).
- `stage-2/system/**` paths (when present) are compatibility wrappers that forward to stage-1.
- Non-shell assets for migrated tools (e.g. `opengl/*.yml`, `litellm/proxy.py`) are canonical in stage-1 and do not require stage-2 compatibility copies.

Selected canonical paths (non-exhaustive):

- `stage-1/system/bun/install-bun.sh`
- `stage-1/system/claude-code/install-claude-code.sh`
- `stage-1/system/codex-cli/install-codex-cli.sh`
- `stage-1/system/litellm/install-litellm.sh` (+ `stage-1/system/litellm/proxy.py`)
- `stage-1/system/magnum/install-magnum-gl.sh`
- `stage-1/system/nodejs/*.sh`
- `stage-1/system/opencv/*.sh`
- `stage-1/system/opengl/setup-opengl-win32.sh` (+ `stage-1/system/opengl/*.json|*.yml`)
- `stage-1/system/pixi/*.bash`
- `stage-1/system/set-locale.sh`

## Installer Script Conventions (v2.0)

PeiDocker “installer” scripts (under `stage-*/system/`) should be **storage-agnostic**:

- Do not hardcode writes to `/soft/app`, `/soft/data`, or `/soft/workspace`.
- Do not probe `/soft/*` to infer “stage” or storage behavior.
- If a non-default path is needed, accept explicit, tool-specific flags (when applicable):
  - `--install-dir=...`
  - `--cache-dir=...`
  - `--tmp-dir=...`
  - `--user <name>`

Lifecycle reminder:

- **Build-time** (`custom.on_build`): `/soft/...` and `/hard/volume/...` are not available; use in-image paths (typically `/hard/image/...`) for any path flags.
- **Runtime** (first-run / every-run / user-login): `/soft/...` paths are allowed (symlinks are created on container start).
