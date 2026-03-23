# Pixi

Pixi is the most complete built-in package-manager workflow in PeiDocker.

## Canonical Path

Use `stage-1/system/pixi/...` even from stage-2 hooks. The `stage-2/system/pixi/...` paths are compatibility wrappers.

## Main Scripts

| Script | What it does |
| --- | --- |
| `install-pixi.bash` | Installs Pixi for a target user |
| `create-env-common.bash` | Installs a curated common package set |
| `create-env-ml.bash` | Installs a curated ML-oriented package set |
| `pixi-utils.bash` | Shared helper functions used by the scripts above |

## Important Flags

- `--user <name>`
- `--install-dir=PATH`
- `--cache-dir=PATH`
- `--pypi-repo tuna|aliyun|official`
- `--conda-repo tuna|official`
- `--verbose`

## Build-Time Pattern

Use in-image paths when you need explicit locations during `on_build`:

```yaml
stage_2:
  custom:
    on_build:
      - "stage-1/system/pixi/install-pixi.bash --install-dir=/hard/image/app/pixi --cache-dir=/hard/image/data/pixi-cache"
```

## Runtime Pattern

Use `/soft/...` only in runtime hooks such as `on_first_run`:

```yaml
stage_2:
  custom:
    on_first_run:
      - "stage-1/system/pixi/install-pixi.bash --install-dir=/soft/app/pixi --cache-dir=/soft/data/pixi-cache --user dev"
      - "stage-1/system/pixi/create-env-common.bash"
```

## Common Use Cases

- Basic Python tooling for development containers
- Shared ML toolchains on GPU-enabled images
- China-friendly mirror setup with `tuna`

See [10 Pixi Environment](../../examples/basic/10-pixi-environment.md) and [ML Dev GPU](../../examples/advanced/ml-dev-gpu.md).
