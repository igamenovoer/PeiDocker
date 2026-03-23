# 08 Env Variables

Use this when you want configure-time substitution only.

Source: `examples/basic/env-variables/user_config.yml`

```yaml
stage_1:
  image:
    base: "${BASE_IMAGE:-ubuntu:24.04}"
    output: "${PROJECT_NAME:-pei-env-basic}:stage-1"
  ssh:
    enable: true
    port: 22
    host_port: "${SSH_HOST_PORT:-2229}"
    users:
      dev:
        password: "123456"
  apt:
    repo_source: "${APT_REPO_SOURCE:-tuna}"

stage_2:
  image:
    output: "${PROJECT_NAME:-pei-env-basic}:stage-2"
  environment:
    CASE_NAME: "${CASE_NAME:-env-variables}"
    APP_MODE: "${APP_MODE:-dev}"
    RESOLVED_AT: "configure-time"
```

Try it:

```bash
export PROJECT_NAME=my-env-demo
export APP_MODE=prod
pei-docker-cli configure -p demo
```

After configuration, those values are concrete in generated output. Changing the host env later does nothing until you run `configure` again.

Read [Environment Variables](../../manual/concepts/environment-variables.md) before moving on to the passthrough example.
