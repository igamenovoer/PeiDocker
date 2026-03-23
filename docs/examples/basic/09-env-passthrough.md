# 09 Env Passthrough

Use this when you want Docker Compose to keep resolving a value after `pei-docker-cli configure` has finished.

Source: `examples/basic/env-passthrough/user_config.yml`

```yaml
stage_1:
  image:
    base: "${BASE_IMAGE:-ubuntu:24.04}"
    output: "${PROJECT_NAME:-pei-env-pass}:stage-1"
  ssh:
    enable: true
    port: 22
    host_port: "${SSH_HOST_PORT:-2230}"
    users:
      dev:
        password: "123456"
  apt:
    repo_source: "${APT_REPO_SOURCE:-tuna}"

stage_2:
  image:
    output: "${PROJECT_NAME:-pei-env-pass}:{{TAG:-dev}}"
  ports:
    - "{{WEB_HOST_PORT:-18080}}:80"
  environment:
    CASE_NAME: "env-passthrough"
    RUNTIME_TAG: "{{TAG:-dev}}"
    HOST_WEB_PORT: "{{WEB_HOST_PORT:-18080}}"
    CONFIG_MODE: "compose-time"
```

What survives into `docker-compose.yml`:

- the tag placeholder
- the port placeholder
- the stage environment placeholders

What does not:

- custom script entries
- merged build artifacts

This example is the cleanest demonstration of the `{{...}}` compose-time path.
