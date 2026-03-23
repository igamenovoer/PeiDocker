# CLI Reference

PeiDocker exposes two console entry points:

- `pei-docker-cli`
- `pei-docker-gui`

The GUI entry point currently exits with a deprecation message in 2.0, so the CLI is the supported path.

## `pei-docker-cli`

### Commands

| Command | Purpose |
| --- | --- |
| `create` | Create a project skeleton |
| `configure` | Generate `docker-compose.yml` and helper artifacts |
| `remove` | Remove images and containers created by a generated project |

## Build Modes

PeiDocker supports three documented workflows:

- `stage-1-only`: omit `stage_2` from `user_config.yml`, then configure and build/run only `stage-1`
- `two-stage Compose`: keep `stage_1` and `stage_2`, configure normally, and use the default Compose build/run path
- `merged build`: keep `stage_1` and `stage_2`, run `configure --with-merged`, and use `build-merged.sh` plus `run-merged.sh`

See [Build Modes](getting-started/build-modes.md) for the decision table and beginner walkthroughs.

### `create`

```text
pei-docker-cli create -p <project-dir> [-e] [--quick <template>]
```

Options:

- `-p, --project-dir`
- `-e, --with-examples`
- `-q, --quick`

Quick templates:

| Template | Intent |
| --- | --- |
| `minimal` | Smallest working default two-stage project with SSH |
| `cn-demo` | Demo project with China mirrors, Pixi, UV, and mixed storage |
| `cn-dev` | CPU-focused development template with China mirrors and tool installers |
| `cn-ml` | GPU-focused ML template with China mirrors and vision tooling |

### `configure`

```text
pei-docker-cli configure [-p <project-dir>] [-c <config>] [-f] [--with-merged]
```

Options:

- `-p, --project-dir`
- `-c, --config`
- `-f, --full-compose`
- `--with-merged`

Notes:

- `${VAR}` values are resolved during `configure`.
- `{{VAR}}` values are preserved for Docker Compose.
- If `stage_2` is omitted from `user_config.yml`, `configure` writes a compose file with only the `stage-1` service.
- `--with-merged` generates `merged.Dockerfile`, `merged.env`, `build-merged.sh`, and `run-merged.sh`.
- `--with-merged` changes the build/run workflow, not the logical meaning of `stage_1` and `stage_2`.
- `--with-merged` is incompatible with passthrough markers.

### `remove`

```text
pei-docker-cli remove -p <project-dir> [-y]
```

Options:

- `-p, --project-dir`
- `-y, --yes`

The command parses the generated `docker-compose.yml`, removes containers that depend on the images first, then removes the images.

## Generated Helper Scripts

When you run `configure --with-merged`, PeiDocker also writes:

- `build-merged.sh`
- `run-merged.sh`
- `merged.env`
- `merged.Dockerfile`

These are useful when you want a plain `docker build` / `docker run` workflow instead of `docker compose`.

## `pei-docker-gui`

The repository still contains the GUI code, but the current command returns:

- “PeiDocker Web GUI is deprecated in 2.0 and is currently unavailable.”

Use [Web GUI](guides/webgui.md) for the code-level tab mapping, not for an active supported workflow.
