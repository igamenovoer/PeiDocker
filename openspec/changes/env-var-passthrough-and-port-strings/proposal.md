## Why

PeiDocker supports `${VAR}` / `${VAR:-default}` substitution when parsing `user_config.yml`, but this prevents users from generating a project once and later controlling runtime behavior via host env / `.env` passed to `docker compose`. We need a supported way to keep env placeholders in the generated `docker-compose.yml` while still allowing config-time substitution when desired.

## What Changes

- Add a **passthrough** marker syntax `{{VAR}}` and `{{VAR:-default}}` that is preserved through config parsing and emitted into the generated `docker-compose.yml` as Docker Compose-style `${VAR}` / `${VAR:-default}` (instead of being expanded during `pei-docker-cli configure`).
- Keep existing config-time substitution behavior for `${VAR}` / `${VAR:-default}` (expanded at configuration time using the environment running `pei-docker-cli configure`).
- Reject configs that still contain `${...}` after config-time substitution, with a clear error directing users to use `{{...}}` for passthrough or set the env var at configure time.
- **BREAKING**: Change port mapping handling to use string-based representations (instead of int-based parsing/merging) so port mappings can safely contain passthrough markers and remain compatible with Docker Compose variable resolution.
- Define and enforce passthrough scope:
  - Passthrough markers are supported only for values interpreted by Docker Compose (i.e., those that end up in `docker-compose.yml`).
  - Passthrough markers are disallowed in config values consumed by `installation/stage-{1,2}/internals/**` scripts without Docker Compose substitution, and in config values baked into PeiDocker-generated scripts during `configure`.
- Error if `--with-merged` is requested while passthrough markers are present (merged build artifacts are out of scope initially).
- Error if env “baking” into `/etc/environment` is requested while passthrough markers would be written (to avoid silently baking uninterpreted placeholders).
- Update examples/docs to clearly distinguish config-time expansion vs compose-time passthrough, including `src/pei_docker/examples/environment-variables.yml`.

## Capabilities

### New Capabilities
- `compose-env-passthrough-markers`: Define `{{VAR}}` / `{{VAR:-default}}` semantics, supported locations, and the exact mapping to `${...}` in generated artifacts.
- `port-mapping-string-model`: Define the port mapping model/behavior as strings to allow passthrough markers and avoid int parsing failures.
- `config-env-substitution-semantics`: Specify the current `${VAR}` / `${VAR:-default}` config-time substitution behavior and how it composes with passthrough markers.

### Modified Capabilities
- (none)

## Impact

- Code:
  - Config pre-processing (`process_config_env_substitution`) and any new passthrough-preservation step in `src/pei_docker/pei.py`.
  - Port mapping parsing/merging in `src/pei_docker/config_processor.py` and config models under `src/pei_docker/user_config/`.
  - Emission paths that write generated artifacts (`docker-compose.yml`, scripts, and merged build artifacts).
- Docs/examples:
  - Update examples and docs to explain the two modes and show recommended patterns.
