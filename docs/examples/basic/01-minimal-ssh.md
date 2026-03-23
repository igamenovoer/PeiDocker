# 01 Minimal SSH

Use this when you want the smallest practical default two-stage Compose project: Ubuntu, one SSH user, and a final `stage-2` image that inherits from `stage-1`.

Source: `examples/basic/minimal-ssh/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-minimal-ssh:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      dev:
        password: "123456"

stage_2:
  image:
    output: pei-example-minimal-ssh:stage-2
```

What it shows:

- the minimum required `image` definitions
- SSH configured in stage-1
- stage-2 inheriting the stage-1 output image automatically in the default two-stage Compose workflow

Workflow:

1. `pei-docker-cli create -p demo --quick minimal`
2. Replace `demo/user_config.yml` with this file.
3. `cd demo && pei-docker-cli configure`
4. `docker compose build stage-2 && docker compose up -d stage-2`
5. `ssh dev@localhost -p 2222`

Alternatives:

- If you want the same kind of minimal SSH container without `stage_2`, see [Build Modes](../../manual/getting-started/build-modes.md) for the runnable `stage-1-only` variant.
- If you want to keep both stages but build with a plain `docker build` workflow, use the merged-build walkthrough on [Build Modes](../../manual/getting-started/build-modes.md).

Read [Two-Stage Architecture](../../manual/concepts/two-stage-architecture.md) if you want to understand why the default model keeps stage-1 and stage-2 separate.
