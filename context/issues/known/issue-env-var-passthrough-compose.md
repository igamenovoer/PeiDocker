# Issue: No Stable Env Var Passthrough Into Generated `docker-compose.yml`

## Summary

PeiDocker supports **config-time** environment variable substitution inside `user_config.yml` (e.g. `${VAR}` / `${VAR:-default}`), but it does **not** provide a robust mechanism to **preserve** those env-var references so they can be resolved later by `docker compose` at runtime.

In other words: the current system tends to **materialize** env vars during `pei-docker-cli configure`, rather than emitting a compose file that references env vars.

## Why This Matters

Some users want to:

- generate a project once (compose + scripts)
- later run `docker compose up` multiple times with different host env vars (or `.env` files)
- without re-running `pei-docker-cli configure`

This currently does not work reliably.

## Evidence In Code

### Config-time substitution happens before compose generation

`pei-docker-cli configure` loads `user_config.yml`, then eagerly substitutes `${...}` tokens using the current process environment:

- `src/pei_docker/pei.py:406` → `src/pei_docker/pei.py:408` calls `process_config_env_substitution(in_config)`
- `src/pei_docker/pei_utils.py:241` implements `substitute_env_vars`
  - `${VAR:-default}` becomes either `os.environ["VAR"]` or the literal `default`
  - `${VAR}` becomes `os.environ["VAR"]` if set; otherwise it is left as `${VAR}`

Result: if the env var is set at configure time, the generated compose will contain **literal values**, not `${VAR}` placeholders.

### `stage_?.environment` becomes a compose `environment:` map

When composing the final services, PeiDocker writes stage environment variables into the compose `environment:` section as a **dictionary**:

- `src/pei_docker/config_processor.py:625`–`src/pei_docker/config_processor.py:631`

This is fine for fixed values, but it does not support a first-class “passthrough” mechanism like Compose’s list form (`environment: ["FOO"]`) or `FOO:` with no value.

### Current env parsing assumes `KEY=VALUE` only

Legacy env lists are converted via a split on `=`:

- `src/pei_docker/user_config/utils.py:168` (`env_str_to_dict`)

This representation cannot express “provide `KEY` only, value comes from runtime environment”.

## Impact / Symptoms

Using the example config `src/pei_docker/examples/legacy/environment-variables.yml:1`:

- `${BASE_IMAGE:-ubuntu:24.04}` is resolved during `configure`
- users cannot reliably keep `${BASE_IMAGE}` inside the generated `docker-compose.yml` so that `docker compose` resolves it later

Practical consequence:

- changing host env vars (or `.env`) after project generation does **not** reliably affect runtime behavior
- users must re-run `pei-docker-cli configure` whenever they want different resolved values

## Workarounds (Imperfect)

- Re-run `pei-docker-cli configure` with the desired env vars set each time.
- Manually edit the generated `docker-compose.yml` to reintroduce `${VAR}` placeholders.

## Potential Directions (Not Implemented Here)

- Add an explicit “passthrough env” concept in user config (e.g. `stage_?.environment_passthrough: [FOO, BAR]`) and emit compose env entries that defer to `docker compose`.
- Allow per-field/per-section control over config-time substitution (or a configure flag to disable it).
- Support a Compose-like env list format where items can be either `KEY=VALUE` or `KEY` (passthrough), without forcing conversion into a dict.
