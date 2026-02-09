## 1. Passthrough Marker Utilities

- [ ] 1.1 Implement `{{VAR}}` / `{{VAR:-default}}` marker parsing + validation (trim whitespace, validate `VAR`, reject `}}` in default)
- [ ] 1.2 Implement plain-container tree-walk rewrite for compose output (`{{...}}` → `${...}`) with clear errors on invalid markers
- [ ] 1.3 Add unit tests for marker validation + rewrite (valid, invalid, mixed-mode strings, whitespace cases)

## 2. Config-Time Substitution Hard Errors

- [ ] 2.1 Add post-substitution scan that rejects any remaining `${...}` in the processed user config with a friendly message (use `{{...}}` or set env at configure time)
- [ ] 2.2 Add unit tests for leftover `${...}` errors (undefined var, nested defaults, and mixed-mode strings)

## 3. Compose Emission Integration

- [ ] 3.1 Integrate passthrough rewrite into `docker-compose.yml` emission only (after OmegaConf resolution, before YAML write)
- [ ] 3.2 Add regression tests ensuring compose output contains `${...}` placeholders and does not trigger OmegaConf interpolation errors

## 4. Unsupported Context Guardrails

- [ ] 4.1 Reject `pei-docker-cli configure --with-merged` when any `{{...}}` passthrough markers are present
- [ ] 4.2 Reject env baking (`PEI_BAKE_ENV_STAGE_1` / `PEI_BAKE_ENV_STAGE_2`) when stage environment contains passthrough markers that would be baked into `/etc/environment`
- [ ] 4.3 Reject passthrough markers in config values baked into generated scripts during `configure` (and values consumed by `installation/stage-{1,2}/internals/**` without Docker Compose substitution)

## 5. Port Mapping String Model (BREAKING)

- [ ] 5.1 Update config model/parsing so `stage_1.ports` and `stage_2.ports` are ordered lists of port mapping strings (no int parsing)
- [ ] 5.2 Update port merge logic to concatenate stage-1 ports + stage-2 ports and include SSH mapping as a port mapping string when configured
- [ ] 5.3 Add tests and update sample configs to reflect the new port model (including passthrough markers in port strings)

## 6. Docs & Examples

- [ ] 6.1 Update `src/pei_docker/examples/environment-variables.yml` and docs to explain `${...}` (config-time) vs `{{...}}` (compose-time) semantics
- [ ] 6.2 Document limitations: compose-only passthrough (initial), `--with-merged` incompatibility, and baking restrictions
