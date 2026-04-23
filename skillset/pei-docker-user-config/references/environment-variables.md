# Environment Variables Reference

## Source Files

- `docs/manual/concepts/environment-variables.md`
- `docs/developer/env-var-processing.md`
- `src/pei_docker/examples/basic/env-variables/user_config.yml`
- `src/pei_docker/examples/basic/env-passthrough/user_config.yml`
- `openspec/specs/config-env-substitution-semantics/spec.md`
- `openspec/specs/compose-env-passthrough-markers/spec.md`

## Configure-Time Values

Use `${VAR}` or `${VAR:-default}` when PeiDocker should resolve the value during `pei-docker-cli configure`.

```yaml
stage_1:
  image:
    base: "${BASE_IMAGE:-ubuntu:24.04}"
    output: "${PROJECT_NAME:-pei-env}:stage-1"
```

After configure, generated output contains concrete values. Changing host env later requires another configure run.

## Compose-Time Values

Use `{{VAR}}` or `{{VAR:-default}}` when Docker Compose should resolve the value later.

```yaml
stage_2:
  image:
    output: "${PROJECT_NAME:-pei-env}:{{TAG:-dev}}"
  ports:
    - "{{WEB_HOST_PORT:-18080}}:80"
```

PeiDocker rewrites passthrough markers to Compose `${...}` syntax in compose-emitted values.

## Limits

Do not use `{{...}}` in:

- custom script entries
- merged build artifacts
- baked stage environment values when environment baking is enabled

Do not use merged build with configs that require compose-time passthrough markers.

## Environment Fields

Both list and dictionary-style environment values may appear in existing configs. Follow the style already present unless there is a reason to normalize.
