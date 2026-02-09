# Implementation Guide: Docs & Examples

**Group**: 6 | **Change**: env-var-passthrough-and-port-strings | **Tasks**: [6.1]–[6.2]

## Goal

Make the new semantics obvious to users:

- `${VAR}` / `${VAR:-default}` = **config-time substitution** (resolved during `pei-docker-cli configure`)
- `{{VAR}}` / `{{VAR:-default}}` = **compose-time passthrough** (preserved and rewritten into `${...}` only in the generated `docker-compose.yml`)

Also document the initial limitations:

- passthrough is compose-only (initial scope)
- `pei-docker-cli configure --with-merged` is incompatible with passthrough markers
- env baking restrictions (`PEI_BAKE_ENV_STAGE_*`) forbid passthrough markers in baked stage env

## Public APIs

### Task 6.1: Update examples + docs for `${...}` vs `{{...}}`

Primary example to update:

- `src/pei_docker/examples/environment-variables.yml`

Docs to update (starting points; adjust based on where the repo currently documents env substitution):

- `docs/examples/advanced.md` (Environment Variable Substitution section)
- `docs/index.md` (if it references env substitution semantics)

Recommended doc pattern:

- A short “two modes” table (config-time vs compose-time).
- One example per mode:
  - config-time: `${BASE_IMAGE:-ubuntu:24.04}`
  - compose-time: `{{TAG:-dev}}` in an image tag or service environment
- A mixed-mode example: `"${PROJECT_NAME:-app}-{{TAG:-dev}}"`

### Task 6.2: Document limitations and guardrails

Document explicitly:

- Compose-only passthrough (initial): markers only supported where Docker Compose interpolates values.
- `--with-merged` incompatibility and the exact error message users will see.
- Baking restrictions:
  - `stage_?.environment` may contain passthrough markers for compose runtime env
  - if baking is enabled, stage env must not contain passthrough markers

## Group Integration

```mermaid
graph LR
    G2[Group 2: No leftover ${...}] --> G6[Group 6: Docs];
    G3[Group 3: Compose emit rewrite] --> G6;
    G4[Group 4: Guardrails] --> G6;
    G5[Group 5: Port strings] --> G6;
```

## Testing

### Test Input

- Updated markdown docs under `docs/`
- Updated example config under `src/pei_docker/examples/environment-variables.yml`

### Test Procedure

```bash
pixi run pytest
pixi run -e dev docs-build
```

### Test Output

- Tests pass.
- Docs build succeeds.
- The example and docs clearly explain which placeholder syntax applies when.

## References

- Proposal: `openspec/changes/env-var-passthrough-and-port-strings/proposal.md`
- Design: `openspec/changes/env-var-passthrough-and-port-strings/design.md`
- Specs: `openspec/changes/env-var-passthrough-and-port-strings/specs/`

## Implementation Summary

(TBD after implementation.)

