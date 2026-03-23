# Env Var Processing

PeiDocker has two separate env-processing layers:

- config-time substitution in Python
- compose-time passthrough in emitted compose YAML

## Config-Time Substitution

`pei_utils.py` implements `${VAR}` and `${VAR:-default}` processing before the config reaches the main processor.

Properties:

- recursive through nested dicts and lists
- string-only
- errors if unresolved `${...}` tokens remain after processing

## Passthrough Markers

`{{VAR}}` and `{{VAR:-default}}` are preserved during config parsing, then rewritten to `${VAR}` syntax only in compose-emitted values.

This is handled by:

- passthrough marker validation helpers in `pei_utils.py`
- compose emission rewriting before `docker-compose.yml` is written

## Restricted Contexts

Passthrough markers are rejected in:

- custom script entries
- merged build artifact generation
- baked `/etc/environment` stage env when baking is enabled

## Stage Environment Files

The processor writes `_etc_environment.sh` files under both generated stage directories. The stage `setup-env.sh` scripts optionally append those values into `/etc/environment` based on `PEI_BAKE_ENV_STAGE_1` or `PEI_BAKE_ENV_STAGE_2`.

## Developer Rule

If a value ends up in a generated shell script, do not allow compose-time markers there unless the shell-runtime contract is extended explicitly. Today the compose-only boundary is deliberate.
