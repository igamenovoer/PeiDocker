# Pixi Reference

## Source Files

- `docs/manual/scripts/pixi.md`
- `docs/examples/basic/10-pixi-environment.md`
- `docs/examples/advanced/ml-dev-gpu.md`
- `src/pei_docker/examples/basic/pixi-environment/user_config.yml`
- `src/pei_docker/examples/advanced/ml-dev-gpu/user_config.yml`

## Scripts

Canonical path: `stage-1/system/pixi/`.

Main scripts:

- `install-pixi.bash`
- `create-env-common.bash`
- `create-env-ml.bash`
- `pixi-utils.bash`

Important flags:

- `--user <name>`
- `--install-dir=PATH`
- `--cache-dir=PATH`
- `--pypi-repo tuna|aliyun|official`
- `--conda-repo tuna|official`
- `--verbose`

## Build-Time Pattern

Use in-image paths:

```yaml
stage_2:
  custom:
    on_build:
      - "stage-1/system/pixi/install-pixi.bash --user developer --pypi-repo tuna --conda-repo tuna"
      - "stage-1/system/pixi/create-env-common.bash"
```

For explicit locations during build, use `/hard/image/...`.

## Runtime Pattern

Use runtime hooks for `/soft/...` or mounted cache paths:

```yaml
stage_2:
  custom:
    on_first_run:
      - "stage-1/system/pixi/install-pixi.bash --install-dir=/soft/app/pixi --cache-dir=/soft/data/pixi-cache --user dev"
      - "stage-1/system/pixi/create-env-common.bash"
```

Use this pattern when persistence or external storage matters more than baking everything into the image.
