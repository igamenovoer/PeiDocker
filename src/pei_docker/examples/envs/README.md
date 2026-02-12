# Environment Variable Example Configs

This directory contains canonical example configs for the `env-var-examples`
OpenSpec change.

- `01-no-passthrough.yml`: Configure-time substitution only (`${...}`)
- `02-with-passthrough.yml`: Compose-time passthrough (`{{...}}`)
- `03-advanced-env-handling.yml`: Mixed-mode usage and advanced patterns

These files are referenced by docs pages under `docs/examples/` and are
designed to be copied into per-case projects under:

- `tmp/<subdir>/cases/no-passthrough/`
- `tmp/<subdir>/cases/with-passthrough/`
- `tmp/<subdir>/cases/advanced-env-handling/`

## Prerequisites

- Docker + Docker Compose installed.
- `pixi` available (examples below use `pixi run pei-docker-cli ...`).
- Working from repository root.

## Recommended workspace layout

Use one disposable project per case:

```text
tmp/env-var-examples/
└── cases/
    ├── no-passthrough/
    ├── with-passthrough/
    └── advanced-env-handling/
```

## Common workflow

For each case:

1. Create a project skeleton.
2. Copy one of the `envs/*.yml` files to `user_config.yml`.
3. Export env vars needed for configure-time values (`${...}`).
4. Run `pei-docker-cli configure`.
5. Build `stage-1` first, then `stage-2`.
6. Verify runtime env values from inside `stage-2`.

`stage-2` depends on the image produced by `stage-1`, so build order matters.

## Quick start (all three cases)

```bash
ROOT=tmp/env-var-examples
CASES_DIR="$ROOT/cases"
rm -rf "$ROOT"
mkdir -p "$CASES_DIR"

create_case() {
  local case_name="$1"
  local config_path="$2"
  local case_dir="$CASES_DIR/$case_name"
  pixi run pei-docker-cli create -p "$case_dir" --quick minimal
  cp "$config_path" "$case_dir/user_config.yml"
}

create_case "no-passthrough" "src/pei_docker/examples/envs/01-no-passthrough.yml"
create_case "with-passthrough" "src/pei_docker/examples/envs/02-with-passthrough.yml"
create_case "advanced-env-handling" "src/pei_docker/examples/envs/03-advanced-env-handling.yml"
```

## Per-config usage notes

### `01-no-passthrough.yml`

- Uses configure-time substitution only.
- Example configure:

```bash
CASE_DIR="$CASES_DIR/no-passthrough"
export BASE_IMAGE=ubuntu:24.04
export APT_REPO_SOURCE=tuna
export CASE_PREFIX=pei-env-no-pass-local
export CASE_NAME=no-passthrough-local
export APP_MODE=dev
pixi run pei-docker-cli configure -p "$CASE_DIR"
```

### `02-with-passthrough.yml`

- Uses compose-time passthrough markers (`{{TAG:-...}}`, `{{WEB_HOST_PORT:-...}}`).
- Configure-time and compose-time inputs are split:

```bash
CASE_DIR="$CASES_DIR/with-passthrough"
export BASE_IMAGE=ubuntu:24.04
export APT_REPO_SOURCE=tuna
export PROJECT_NAME=pei-env-pass-local
pixi run pei-docker-cli configure -p "$CASE_DIR"

cat > "$CASE_DIR/.env" <<'EOF'
TAG=rc1
WEB_HOST_PORT=18081
EOF
```

### `03-advanced-env-handling.yml`

- Demonstrates mixed `${...}` + `{{...}}`, string ports, and advanced env fields.

```bash
CASE_DIR="$CASES_DIR/advanced-env-handling"
export BASE_IMAGE=ubuntu:24.04
export APT_REPO_SOURCE=tuna
export PROJECT_NAME=pei-env-advanced-local
export HOST_LABEL=lab
pixi run pei-docker-cli configure -p "$CASE_DIR"

cat > "$CASE_DIR/.env" <<'EOF'
TAG=v2
WEB_HOST_PORT=28081
RUNTIME_PROFILE=ci
EOF
```

## Build and verify

Run this for any case:

```bash
(
  cd "$CASE_DIR"
  docker compose build stage-1
  docker compose build stage-2
  docker compose run --rm stage-2 env
)
```

Suggested checks:

- `no-passthrough`: `CASE_NAME`, `APP_MODE`, `RESOLVED_AT`
- `with-passthrough`: `CASE_NAME`, `RUNTIME_TAG`, `HOST_WEB_PORT`, `CONFIG_MODE`
- `advanced-env-handling`: `CASE_NAME`, `MIXED_IMAGE_REF`, `RESOLVED_HOSTNAME`, `RUNTIME_PROFILE`, `STATIC_FLAG`

## Cleanup

```bash
rm -rf tmp/env-var-examples
```

## Related docs

- `docs/examples/env-no-passthrough.md`
- `docs/examples/env-with-passthrough.md`
- `docs/examples/env-advanced.md`
- `docs/examples/env-build-and-run.md`
