---
name: pei-docker-cli-workflow
description: Guidance for PeiDocker CLI project workflows. Use when Codex needs to install or verify pei-docker-cli, create projects, choose quick templates or build modes, run configure or remove, inspect generated project structure, or decide which generated project files are durable edit targets.
---

# PeiDocker CLI Workflow

## Start Here

Use this skill for project-level PeiDocker operations, not detailed YAML authoring or runtime container operation.

First determine where the user is working:

- Repository root: source tree contains `src/pei_docker/`, `docs/`, and `pyproject.toml`.
- Generated project root: project contains `user_config.yml`, `compose-template.yml`, Dockerfiles, and `installation/`.

Read the smallest relevant source before advising:

- `docs/manual/getting-started/installation.md`
- `docs/manual/getting-started/build-modes.md`
- `docs/manual/getting-started/quickstart.md`
- `docs/manual/getting-started/project-structure.md`
- `docs/manual/cli-reference.md`
- `src/pei_docker/templates/quick/*.yml`

## CLI Workflow

For install or verification:

```bash
pei-docker-cli --help
docker --version
docker compose version
```

For repository development, prefer:

```bash
pixi run pei-docker-cli --help
```

For a new project:

```bash
pei-docker-cli create -p <project-dir> --quick minimal
cd <project-dir>
pei-docker-cli configure
```

Use quick templates intentionally:

- `minimal`: smallest default two-stage project with SSH.
- `cn-demo`: demo with China mirrors, Pixi, UV, and mixed storage.
- `cn-dev`: CPU-focused China-friendly development setup.
- `cn-ml`: GPU-focused ML setup with China mirrors and vision tooling.

## Build Mode Choice

Use the build-mode docs before telling a first-time user what to run.

| User intent | Mode | Config shape | Configure command |
| --- | --- | --- | --- |
| One SSH-ready/system-base container | stage-1-only | omit `stage_2` | `pei-docker-cli configure` |
| Default PeiDocker development flow | two-stage Compose | keep `stage_1` and `stage_2` | `pei-docker-cli configure` |
| Plain `docker build` / `docker run` flow | merged build | keep both stages | `pei-docker-cli configure --with-merged` |

Do not conflate `stage-1-only` with merged build. `stage-1-only` changes config shape; merged build changes the build/run workflow.

## Durable Edit Targets

Prefer editing:

- `user_config.yml`
- files under `installation/stage-1/custom/`
- files under `installation/stage-2/custom/`
- project-owned support files under `installation/`

Treat these as generated outputs:

- `docker-compose.yml`
- `installation/stage-*/generated/`
- `merged.Dockerfile`
- `merged.env`
- `build-merged.sh`
- `run-merged.sh`

Generated outputs can be inspected, but durable fixes usually belong in `user_config.yml` or source custom scripts.

## Validation

After meaningful config or project workflow changes, run configure when feasible:

```bash
pei-docker-cli configure -p <project-dir>
```

Use `-c <config-file>` only when the user has a non-default config file. Use `--with-merged` only when the project is meant to use generated merged-build artifacts.

Use `pei-docker-cli remove -p <project-dir>` when the user wants PeiDocker-managed image/container cleanup from a generated compose file.
