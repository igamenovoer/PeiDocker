# 06 Port Mapping

Use this when you want to expose multiple services and see how stage-1 and stage-2 port lists combine.

Source: `examples/basic/port-mapping/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-port-mapping:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2227
    users:
      dev:
        password: "123456"
  ports:
    - "6006:6006"

stage_2:
  image:
    output: pei-example-port-mapping:stage-2
  ports:
    - "8080:80"
    - "3000-3002:3000-3002"
```

Generated behavior:

- stage-1 gets `6006:6006` plus the SSH mapping
- stage-2 gets stage-1 ports, stage-2 ports, and the SSH mapping

This is why you usually define system-service ports in stage-1 and app-service ports in stage-2.

Read [Port Mapping](../../manual/guides/port-mapping.md) for the full string model.
