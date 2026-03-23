# 05 Custom Script

Use this when you want to see the smallest example that needs an extra file alongside `user_config.yml`.

Source: `examples/basic/custom-script/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-custom-script:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2226
    users:
      dev:
        password: "123456"
  custom:
    on_build:
      - 'stage-1/custom/echo-on-build.sh --message="hello-from-custom-script"'

stage_2:
  image:
    output: pei-example-custom-script:stage-2
```

Supporting file: `examples/basic/custom-script/installation/stage-1/custom/echo-on-build.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

message="custom-script-ran"
for arg in "$@"; do
  case "$arg" in
    --message=*)
      message="${arg#--message=}"
      ;;
  esac
done

printf '%s\n' "$message" >/tmp/peidocker-custom-script.txt
echo "wrote /tmp/peidocker-custom-script.txt"
```

What to copy into a real project:

- `user_config.yml`
- `installation/stage-1/custom/echo-on-build.sh`

This example is intentionally build-time only. If the script needed `/soft/...`, it would belong in a runtime hook instead.
