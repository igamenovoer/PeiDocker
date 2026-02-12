# Env Tutorial 1: No Passthrough

This tutorial uses configure-time substitution only:

- `${VAR}`
- `${VAR:-default}`

It does not use compose-time passthrough markers (`{{...}}`).

## Case config

- Source config: `src/pei_docker/examples/envs/01-no-passthrough.yml`
- Case directory: `tmp/env-var-examples/cases/no-passthrough/`

## Setup

```bash
CASE_DIR=tmp/env-var-examples/cases/no-passthrough
rm -rf "$CASE_DIR"
pixi run pei-docker-cli create -p "$CASE_DIR" --quick minimal
cp src/pei_docker/examples/envs/01-no-passthrough.yml "$CASE_DIR/user_config.yml"
```

## Configure-time substitution

Set environment variables before `configure`:

```bash
export BASE_IMAGE=ubuntu:24.04
export CASE_PREFIX=pei-env-no-pass-local
export CASE_NAME=no-passthrough-local
export APP_MODE=dev
export APT_REPO_SOURCE=tuna

pixi run pei-docker-cli configure -p "$CASE_DIR"
```

Check the generated compose file values:

```bash
rg -n "CASE_NAME|APP_MODE|RESOLVED_AT|image:" "$CASE_DIR/docker-compose.yml"
```

## Build and runtime verification

```bash
(
  cd "$CASE_DIR"
  docker compose build stage-1
  docker compose build stage-2
  docker compose run --rm stage-2 env | rg "^(CASE_NAME|APP_MODE|RESOLVED_AT)="
)
```

Expected runtime values include:

- `CASE_NAME=no-passthrough-local`
- `APP_MODE=dev`
- `RESOLVED_AT=configure-time`

## Re-configure behavior

Configure-time values are baked into generated files. If you change env vars,
run `configure` again.

```bash
export APP_MODE=prod
(
  cd "$CASE_DIR"
  docker compose run --rm stage-2 env | rg "^APP_MODE="
)
# still APP_MODE=dev

pixi run pei-docker-cli configure -p "$CASE_DIR"
(
  cd "$CASE_DIR"
  docker compose run --rm stage-2 env | rg "^APP_MODE="
)
# now APP_MODE=prod
```

## Cleanup

```bash
rm -rf tmp/env-var-examples
```
