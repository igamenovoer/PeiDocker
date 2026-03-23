# 10 Pixi Environment

Use this when you want a simple user-facing Python tooling setup without writing installer scripts yourself.

Source: `examples/basic/pixi-environment/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-pixi:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2231
    users:
      developer:
        password: "dev123"
        uid: 1100
  apt:
    repo_source: tuna

stage_2:
  image:
    output: pei-example-pixi:stage-2
  storage:
    app:
      type: image
    data:
      type: auto-volume
    workspace:
      type: auto-volume
  mount:
    home_developer:
      type: auto-volume
      dst_path: /home/developer
  custom:
    on_build:
      - "stage-1/system/pixi/install-pixi.bash --user developer --pypi-repo tuna --conda-repo tuna"
      - "stage-1/system/pixi/create-env-common.bash"
```

Highlights:

- uses the canonical stage-1 Pixi scripts
- keeps the install simple by letting Pixi use its default per-user location
- persists the developer home directory separately from app/data/workspace

Next reads:

- [Pixi](../../manual/scripts/pixi.md)
- [ML Dev GPU](../advanced/ml-dev-gpu.md)
