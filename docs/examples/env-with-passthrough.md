# Env Tutorial 2: With Passthrough

This tutorial uses compose-time passthrough markers:

- `{{VAR}}`
- `{{VAR:-default}}`

PeiDocker rewrites these markers into Docker Compose `${...}` when writing
`docker-compose.yml`.

## Case config

- Source config: `src/pei_docker/examples/envs/02-with-passthrough.yml`
- Case directory: `tmp/env-var-examples/cases/with-passthrough/`

## Setup

```bash
CASE_DIR=tmp/env-var-examples/cases/with-passthrough
rm -rf "$CASE_DIR"
pixi run pei-docker-cli create -p "$CASE_DIR" --quick minimal
cp src/pei_docker/examples/envs/02-with-passthrough.yml "$CASE_DIR/user_config.yml"
```

## Configure

`PROJECT_NAME` is configure-time, `TAG`/`WEB_HOST_PORT` are passthrough:

```bash
export PROJECT_NAME=pei-env-pass-local
export BASE_IMAGE=ubuntu:24.04
export APT_REPO_SOURCE=tuna
pixi run pei-docker-cli configure -p "$CASE_DIR"
```

Verify passthrough markers were emitted as Compose expressions:

```bash
rg -n "TAG|WEB_HOST_PORT|image:|ports:" "$CASE_DIR/docker-compose.yml"
```

## Compose-time resolution via `.env`

```bash
cat > "$CASE_DIR/.env" <<'EOF'
TAG=rc1
WEB_HOST_PORT=18081
EOF

(
  cd "$CASE_DIR"
  docker compose config | rg -n "image:|18081:80|RUNTIME_TAG|HOST_WEB_PORT"
)
```

## Build and runtime verification

```bash
(
  cd "$CASE_DIR"
  docker compose build stage-1
  docker compose build stage-2
  docker compose run --rm stage-2 env | rg "^(CASE_NAME|RUNTIME_TAG|HOST_WEB_PORT|CONFIG_MODE)="
)
```

Expected runtime values include:

- `CASE_NAME=with-passthrough`
- `RUNTIME_TAG=rc1`
- `HOST_WEB_PORT=18081`
- `CONFIG_MODE=compose-time`

## Cleanup

```bash
rm -rf tmp/env-var-examples
```
