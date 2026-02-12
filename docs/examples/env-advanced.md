# Env Tutorial 3: Advanced Env Handling

This tutorial covers advanced env handling in one case:

- Mixed-mode strings (`${...}` with `{{...}}`)
- Port mappings as strings with passthrough
- Build and runtime verification
- Guardrails and known failure modes

## Case config

- Source config: `src/pei_docker/examples/envs/03-advanced-env-handling.yml`
- Case directory: `tmp/env-var-examples/cases/advanced-env-handling/`

## Setup

```bash
CASE_DIR=tmp/env-var-examples/cases/advanced-env-handling
rm -rf "$CASE_DIR"
pixi run pei-docker-cli create -p "$CASE_DIR" --quick minimal
cp src/pei_docker/examples/envs/03-advanced-env-handling.yml "$CASE_DIR/user_config.yml"
```

## Configure with mixed inputs

```bash
export PROJECT_NAME=pei-env-advanced-local
export HOST_LABEL=lab
export BASE_IMAGE=ubuntu:24.04
export APT_REPO_SOURCE=tuna
pixi run pei-docker-cli configure -p "$CASE_DIR"

cat > "$CASE_DIR/.env" <<'EOF'
TAG=v2
WEB_HOST_PORT=28081
RUNTIME_PROFILE=ci
EOF
```

Check generated compose content:

```bash
rg -n "MIXED_IMAGE_REF|RUNTIME_PROFILE|WEB_HOST_PORT|ports:|image:" "$CASE_DIR/docker-compose.yml"
```

## Build and runtime verification

```bash
(
  cd "$CASE_DIR"
  docker compose build stage-1
  docker compose build stage-2
  docker compose run --rm stage-2 env | rg "^(CASE_NAME|MIXED_IMAGE_REF|RESOLVED_HOSTNAME|RUNTIME_PROFILE|STATIC_FLAG)="
)
```

Expected runtime values include:

- `CASE_NAME=advanced-env-handling`
- `MIXED_IMAGE_REF=pei-env-advanced-local:v2`
- `RESOLVED_HOSTNAME=lab`
- `RUNTIME_PROFILE=ci`
- `STATIC_FLAG=advanced-case`

## Guardrails and failure modes

The following are intentionally invalid patterns. Keep them out of working
configs used for build verification.

### 1) Passthrough with `--with-merged` is rejected

```bash
pixi run pei-docker-cli configure -p "$CASE_DIR" --with-merged
```

Expected: error about passthrough markers being incompatible with merged mode.

### 2) Passthrough in script-baked contexts is rejected

Invalid example:

```yaml
stage_2:
  custom:
    on_first_run:
      - 'echo "tag={{TAG:-dev}}"'
```

Expected: `configure` fails because custom script contexts are baked during
configure.

### 3) Passthrough in baked env values is rejected

Invalid example pattern:

```yaml
stage_1:
  environment:
    BAKED_VAR: "{{TAG:-dev}}"
```

Combined with a compose build arg enabling env baking (for example
`PEI_BAKE_ENV_STAGE_1=true`), this is rejected.

## Cleanup

```bash
rm -rf tmp/env-var-examples
```
