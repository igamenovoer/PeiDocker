# 04 Docker Volume

Use this when you want persistent stage-2 state without binding to a host path.

Source: `examples/basic/docker-volume/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-docker-volume:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2225
    users:
      dev:
        password: "123456"

stage_2:
  image:
    output: pei-example-docker-volume:stage-2
  storage:
    app:
      type: image
    data:
      type: auto-volume
    workspace:
      type: auto-volume
```

This is the cleanest way to keep data and workspace persistent while leaving the installed app layer in the image.

Good fit:

- personal dev environments
- local caches you do not need to inspect on the host
- quick persistence without volume-name management

Compare it with [03 Host Mount](03-host-mount.md) if you are deciding between host binds and Docker-managed volumes.
