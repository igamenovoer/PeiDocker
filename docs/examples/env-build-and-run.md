# Env Build and Run Walkthrough

This walkthrough verifies all env tutorial cases under one workspace:

- `tmp/<subdir>/cases/no-passthrough/`
- `tmp/<subdir>/cases/with-passthrough/`
- `tmp/<subdir>/cases/advanced-env-handling/`

The workflow validates both:

- Image build success (`docker compose build`)
- Runtime env values (`docker compose run --rm stage-2 env`)

All cases pin base image to `ubuntu:24.04`.

## Networking note

If package downloads are unstable, use China-based mirrors (for example
`APT_REPO_SOURCE=tuna` in these examples). Do not use proxy setup in this
walkthrough.

## One-pass setup and verification

```bash
ROOT=tmp/env-var-examples
CASES_DIR="$ROOT/cases"
rm -rf "$ROOT"
mkdir -p "$CASES_DIR"

create_case() {
  local case_name="$1"
  local config_path="$2"
  local quick_template="minimal"

  local case_dir="$CASES_DIR/$case_name"
  pixi run pei-docker-cli create -p "$case_dir" --quick "$quick_template"
  cp "$config_path" "$case_dir/user_config.yml"
}

create_case "no-passthrough" "src/pei_docker/examples/envs/01-no-passthrough.yml"
create_case "with-passthrough" "src/pei_docker/examples/envs/02-with-passthrough.yml"
create_case "advanced-env-handling" "src/pei_docker/examples/envs/03-advanced-env-handling.yml"
```

## Case 1: no-passthrough

```bash
CASE_DIR="$CASES_DIR/no-passthrough"
export BASE_IMAGE=ubuntu:24.04
export APT_REPO_SOURCE=tuna
export CASE_PREFIX=pei-env-no-pass-local
export CASE_NAME=no-passthrough-local
export APP_MODE=dev
pixi run pei-docker-cli configure -p "$CASE_DIR"

(
  cd "$CASE_DIR"
  docker compose build stage-1
  docker compose build stage-2
  docker compose run --rm stage-2 env | rg "^(CASE_NAME|APP_MODE|RESOLVED_AT)="
)
```

Expected runtime values:

- `CASE_NAME=no-passthrough-local`
- `APP_MODE=dev`
- `RESOLVED_AT=configure-time`

## Case 2: with-passthrough

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

(
  cd "$CASE_DIR"
  docker compose build stage-1
  docker compose build stage-2
  docker compose run --rm stage-2 env | rg "^(CASE_NAME|RUNTIME_TAG|HOST_WEB_PORT|CONFIG_MODE)="
)
```

Expected runtime values:

- `CASE_NAME=with-passthrough`
- `RUNTIME_TAG=rc1`
- `HOST_WEB_PORT=18081`
- `CONFIG_MODE=compose-time`

## Case 3: advanced-env-handling

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

(
  cd "$CASE_DIR"
  docker compose build stage-1
  docker compose build stage-2
  docker compose run --rm stage-2 env | rg "^(CASE_NAME|MIXED_IMAGE_REF|RESOLVED_HOSTNAME|RUNTIME_PROFILE|STATIC_FLAG)="
)
```

Expected runtime values:

- `CASE_NAME=advanced-env-handling`
- `MIXED_IMAGE_REF=pei-env-advanced-local:v2`
- `RESOLVED_HOSTNAME=lab`
- `RUNTIME_PROFILE=ci`
- `STATIC_FLAG=advanced-case`

## Cleanup

```bash
rm -rf tmp/env-var-examples
```
