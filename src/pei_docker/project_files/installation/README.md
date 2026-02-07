# Installation Directory

This directory contains scripts and configuration files that are copied into the Docker image.

## Usage

Files in this directory are available inside the container at `/pei-from-host`.

## Structure

*   `stage-1/`: Files specific to the Stage 1 build (System layer).
*   `stage-2/`: Files specific to the Stage 2 build (Application layer).

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
