# Two-Stage Architecture

PeiDocker’s default model splits the build into two images because system setup and day-to-day application setup have different change rates.

This page explains that default model. PeiDocker also supports a `stage-1-only` workflow and a `merged build` workflow; see [Build Modes](../getting-started/build-modes.md) for the user-facing choice between them.

## Where This Fits

| Mode | What changes |
| --- | --- |
| `stage-1-only` | You omit `stage_2` from `user_config.yml`, and the generated compose file keeps only the `stage-1` service |
| `two-stage Compose` | You keep both stages and build/run them through the default Compose flow |
| `merged build` | You keep both stages, but `configure --with-merged` also writes merged artifacts so the final image can be built and run without the default Compose build path |

## Stage-1

Stage-1 is the system layer. It is where you usually put:

- Base image selection
- SSH server setup
- APT mirrors and proxy-aware package setup
- Low-level installers and stable dependencies

If you change stage-1, you invalidate everything built on top of it.

## Stage-2

Stage-2 is the working layer. It is where you usually put:

- App, data, and workspace storage
- Additional ports
- Application-specific environment variables
- Runtime-oriented custom scripts
- Built-in installers you want closer to the final image

If `stage_2.image.base` is omitted, PeiDocker automatically uses the output image from stage-1.

## How They Chain

1. `configure` writes compose build arguments for stage-1 and stage-2.
2. Stage-1 builds a reusable foundation image.
3. Stage-2 uses that stage-1 image as its base unless you override it.
4. Runtime storage and `/soft/*` symlinks are created when the final container starts, not during `docker build`.

If `stage_2` is omitted, the chain stops after stage-1 and the generated compose file keeps only the `stage-1` service. If you use merged build artifacts, the logical chain is still stage-1 then stage-2; only the build/run workflow changes.

## What Belongs Where

| Put it in | When |
| --- | --- |
| Stage-1 | You need OS-level setup, SSH, APT, or something reused across many projects |
| Stage-2 | You need storage, app tooling, ports, or project-specific runtime behavior |

## Practical Rule

If a script needs `/soft/...` or mounted volumes, it does not belong in `stage_2.custom.on_build`. Those paths do not exist until container startup. Use runtime hooks such as `on_first_run` or target in-image paths like `/hard/image/...` at build time.
