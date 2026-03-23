# Environment Variables

PeiDocker supports two different substitution moments. Mixing them up is the most common source of confusion.

## Configure-Time: `${VAR}`

`${VAR}` and `${VAR:-default}` are resolved when you run `pei-docker-cli configure`.

Use this when the generated files should contain concrete values immediately.

```yaml
image:
  base: "${BASE_IMAGE:-ubuntu:24.04}"
```

## Compose-Time: `{{VAR}}`

`{{VAR}}` and `{{VAR:-default}}` are preserved during PeiDocker parsing and rewritten to `${VAR}` syntax in the generated `docker-compose.yml`.

Use this when Docker Compose should resolve the value later.

```yaml
ports:
  - "{{WEB_HOST_PORT:-18080}}:80"
```

## Comparison

| Syntax | Resolved by | When to use |
| --- | --- | --- |
| `${VAR}` | PeiDocker | Values you want baked into generated output |
| `{{VAR}}` | Docker Compose | Values you want to change without re-running `configure` |

## Mixed-Mode Strings

Mixed strings are supported:

```yaml
output: "${PROJECT_NAME:-demo}:{{TAG:-dev}}"
```

PeiDocker resolves the `${PROJECT_NAME}` part during `configure` and leaves the tag placeholder for Compose.

## Important Limits

- `{{...}}` markers are not allowed in generated script entries such as `custom.on_build`.
- `{{...}}` markers are incompatible with `pei-docker-cli configure --with-merged`.
- If environment baking into `/etc/environment` is enabled for a stage, passthrough markers are rejected for that baked stage environment.
