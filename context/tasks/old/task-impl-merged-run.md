# Feature Plan: run-merged.sh (Docker run for merged image)

## Goal

Add a generated script `run-merged.sh` that starts the merged image (built by
`build-merged.sh`) using `docker run`. This script should be produced by
`pei-docker-cli configure --with-merged` together with `merged.Dockerfile`,
`merged.env`, and `build-merged.sh`.

The script reads configuration from `merged.env` so users can customize runtime
behavior without editing the script.

## High-Level Design

- Extend the merged artifacts generator to also emit `run-merged.sh`.
- `run-merged.sh`:
  - Sources `merged.env` (set -a; source ...; set +a)
  - Builds a `docker run` command based on values from `merged.env` and resolved
    compose (ports, volumes, extra_hosts, GPU).
  - Accepts minimal CLI overrides for common operations (e.g., `--name`,
    `--detach`, `--no-rm`, extra `-p` and `-v`).
  - Appends any remaining args to `docker run` for advanced customization.

## Inputs from resolved compose

From the fully-resolved compose (the same object used to generate `merged.Dockerfile`):
- Image tag: `services.stage-2.image` → default image for `run-merged.sh`.
- Port mappings: `services.stage-2.ports` (list of `host:container` strings).
- Volume mappings: `services.stage-2.volumes` (list of strings: `<src>:<dst>`)
  - Includes host binds (absolute host paths) and named volumes (auto/manual).
- Extra hosts: `services.stage-2.extra_hosts` → `--add-host` flags.
- GPU/device: If `stage_2.device.type == 'gpu'`, add `--gpus all` by default.
- Environment: `stage_2.environment` (already normalized to dict by processor)
  - Optional; can be emitted as `-e KEY=VALUE` flags (opt-in via env toggle).

## merged.env additions (runtime block)

Augment `merged.env` with runtime variables; defaults filled from compose or
sensible defaults.

- `STAGE2_IMAGE_NAME` (already present) – default image for `docker run`.
- `RUN_CONTAINER_NAME` – default container name (e.g., `pei-stage-2`).
- `RUN_DETACH` – `0|1` (default `0` → interactive `-it`).
- `RUN_REMOVE` – `0|1` (default `1` → `--rm`).
- `RUN_TTY` – `0|1` (default `1` → `-t`).
- `RUN_GPU` – `auto|none|all` (default `auto`; if device is gpu then `--gpus all`).
- `RUN_PORTS` – space-separated port mappings, e.g., `"2323:22 8080:8080"`.
- `RUN_VOLUMES` – space-separated volume/bind mappings, e.g.,
  `"myvol:/hard/volume/app /host/data:/hard/volume/data"`.
- `RUN_EXTRA_HOSTS` – space-separated pairs, e.g.,
  `"host.docker.internal:host-gateway"`.
- `RUN_ENV_ENABLE` – `0|1` (default `0`; if `1`, emit `-e KEY=VALUE` for compose env).
- `RUN_NETWORK` – optional network name (default empty → Docker default bridge).
- `RUN_EXTRA_ARGS` – free-form args appended to `docker run`.

Rationale: These variables give users an ergonomic way to adjust runtime
settings by editing a single env file.

## run-merged.sh behavior

- Parse light CLI flags:
  - `-n, --name <container-name>` → overrides `RUN_CONTAINER_NAME`.
  - `-d, --detach` → sets `RUN_DETACH=1`.
  - `--no-rm` → sets `RUN_REMOVE=0`.
  - `-p, --publish <host:container>` → append to `RUN_PORTS`.
  - `-v, --volume <src:dst[:mode]>` → append to `RUN_VOLUMES`.
  - `--gpus <value>` → override GPU behavior (`all|none`).
  - `--` → stop parsing, pass remainder directly to Docker.
- Build flags:
  - `-it` if `RUN_DETACH=0` and `RUN_TTY=1`; `-d` if `RUN_DETACH=1`.
  - `--rm` if `RUN_REMOVE=1`.
  - One `-p` per token in `RUN_PORTS`.
  - One `-v` per token in `RUN_VOLUMES`.
  - One `--add-host` per item in `RUN_EXTRA_HOSTS`.
  - `--gpus all` if `RUN_GPU=all`, `--gpus all` if `RUN_GPU=auto` and device is gpu; none otherwise.
  - `-e KEY=VALUE` for each env (only if `RUN_ENV_ENABLE=1`).
  - Append `RUN_EXTRA_ARGS` at the end.
- Image:
  - Use `STAGE2_IMAGE_NAME` by default.
  - Allow positional override: if the last arg looks like an image (contains `:` or `/` and no `=`), treat as image override.
- Command:
  - Omit command to use image entrypoint (`/entrypoint.sh`). Users may add a command after `--`.

## Generation details

In `merge_build.py`:
- After generating `merged.env`, write `run-merged.sh` with:
  - Shebang and `set -euo pipefail`.
  - `PROJECT_DIR` and `source "$PROJECT_DIR/merged.env"`.
  - Minimal argument parser for overrides.
  - Construction of arrays for ports / volumes / hosts from the env strings
    (split on whitespace; ignore empty tokens).
  - Docker command assembly with proper quoting.
  - `chmod +x`.

## Pseudocode (generator side)

```python
# in generate_merged_build(...)
# 1) existing: merged.Dockerfile, merged.env, build-merged.sh
# 2) NEW: run-merged.sh

run_script = f"""#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
set -a
source "$PROJECT_DIR/merged.env"
set +a

CONTAINER_NAME="${{RUN_CONTAINER_NAME:-pei-stage-2}}"
DETACH="${{RUN_DETACH:-0}}"; RM="${{RUN_REMOVE:-1}}"; TTY="${{RUN_TTY:-1}}"
GPU_MODE="${{RUN_GPU:-auto}}"
IMG="${{STAGE2_IMAGE_NAME}}"

# parse args: -n/--name, -d/--detach, --no-rm, -p/--publish, -v/--volume, --gpus, --
# accumulate extra -p/-v into local arrays; allow image override at the end

cmd=( docker run )
[[ "$DETACH" == 1 ]] && cmd+=( -d ) || {{ [[ "$TTY" == 1 ]] && cmd+=( -it ) }}
[[ "$RM" == 1 ]] && cmd+=( --rm )
[[ -n "${RUN_NETWORK:-}" ]] && cmd+=( --network "$RUN_NETWORK" )

# ports from RUN_PORTS and CLI
for p in $RUN_PORTS; do [[ -n "$p" ]] && cmd+=( -p "$p" ); done
for p in "${CLI_PORTS[@]:-}"; do cmd+=( -p "$p" ); done

# volumes
for v in $RUN_VOLUMES; do [[ -n "$v" ]] && cmd+=( -v "$v" ); done
for v in "${CLI_VOLS[@]:-}"; do cmd+=( -v "$v" ); done

# extra hosts
for h in $RUN_EXTRA_HOSTS; do [[ -n "$h" ]] && cmd+=( --add-host "$h" ); done

# gpus
if [[ "$GPU_MODE" == "all" ]]; then cmd+=( --gpus all );
elif [[ "$GPU_MODE" == "auto" && "${{RUN_DEVICE_TYPE:-}}" == "gpu" ]]; then cmd+=( --gpus all ); fi

# env
if [[ "${RUN_ENV_ENABLE:-0}" == 1 ]]; then
  while IFS='=' read -r k v; do [[ -n "$k" ]] && cmd+=( -e "$k=$v" ); done < <(printenv | grep -E '^PEI_|^APP_|^ENV_' || true)
fi

# container name
cmd+=( --name "$CONTAINER_NAME" )

# extra args
[[ -n "${RUN_EXTRA_ARGS:-}" ]] && cmd+=( $RUN_EXTRA_ARGS )

# image and optional command
cmd+=( "$IMG" )
[[ ${#POSITIONAL[@]:-0} -gt 0 ]] && cmd+=( "${POSITIONAL[@]}" )

printf '%q ' "${cmd[@]}"; echo
exec "${cmd[@]}"
"""
# write to project_dir/run-merged.sh and chmod +x
```

Notes:
- The `RUN_DEVICE_TYPE` can be written to `merged.env` by the generator based on
  the user config (e.g., `gpu` or `cpu`), enabling the `auto` GPU logic.
- To keep things simple, we treat `RUN_PORTS`, `RUN_VOLUMES`, and
  `RUN_EXTRA_HOSTS` as space-separated lists. Users can edit these in the env
  file or extend via CLI flags.

## Documentation updates

- cli_reference.md: Mention run-merged.sh in the `--with-merged` section.
- index.md: Add a short example that runs the merged image via run-merged.sh and
  shows overriding name or detach mode.

## Acceptance Criteria

- `pei-docker-cli configure --with-merged` writes `run-merged.sh` alongside
  other merged artifacts.
- The script runs the merged image with correct ports, volumes, and GPU options
  per the resolved compose.
- Users can override container name / detach / ports / volumes via CLI or by
  editing `merged.env`.
- No docker compose is required at runtime.

