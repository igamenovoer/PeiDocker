# Pixi (Stage-1 Canonical)

This directory contains the **canonical** Pixi installer + helper scripts.

- Prefer referencing these scripts as `stage-1/system/pixi/...` in `user_config.yml`.
- The `stage-2/system/pixi/...` paths remain as thin wrappers for compatibility.

## Scripts

### `install-pixi.bash`

Installs [Pixi](https://pixi.sh) for a target user (default: current user).

Common options (see `--help` in the script for full details):

- `--user <name>`: install for a specific user (root required for cross-user installs)
- `--install-dir=PATH`: override default install dir (`~/.pixi`)
- `--cache-dir=PATH`: set `PIXI_CACHE_DIR` (persisted in the target user’s `.bashrc`)
- `--pypi-repo <tuna|aliyun|official>`: configure default PyPI index for pixi
- `--conda-repo <tuna|official>`: configure conda-forge mirror mapping for pixi
- `--verbose`: enable verbose output

### `create-env-common.bash` / `create-env-ml.bash`

Installs a curated set of packages globally (via `pixi global install`) for all
users who can SSH login (password-aware filtering is implemented in `pixi-utils.bash`).

### `pixi-utils.bash`

Shared helper functions used by the scripts above.

## PeiDocker Integration

### Runtime hooks (first-run / every-run / user-login)

Runtime hooks may target `/soft/...` paths because `/soft/*` symlinks are created
on container start (stage-2 `on-entry.sh`).

```yaml
stage_2:
  custom:
    on_first_run:
      - "stage-1/system/pixi/install-pixi.bash --pypi-repo tuna --conda-repo tuna"
      - "stage-1/system/pixi/create-env-common.bash"

    # Example: keep cache on data storage and install into app storage
    on_first_run:
      - "stage-1/system/pixi/install-pixi.bash --cache-dir=/soft/data/pixi-cache --install-dir=/soft/app/pixi --verbose"
      - "stage-1/system/pixi/create-env-common.bash"
```

### Build hooks (`custom.on_build`)

Build-time hooks must **not** reference `/soft/...` or `/hard/volume/...` because
those are runtime-only. Use in-image paths (typically under `/hard/image/...`) for
any tool-specific path flags.

```yaml
stage_2:
  custom:
    on_build:
      - "stage-1/system/pixi/install-pixi.bash --cache-dir=/hard/image/data/pixi-cache --install-dir=/hard/image/app/pixi"
      - "stage-1/system/pixi/create-env-common.bash"
```

## Notes

- If you install at build time into `/hard/image/...`, those files are baked into the image layer.
- At runtime, if `/soft/...` points to a mounted volume (`/hard/volume/...`), the in-image
  content under `/hard/image/...` may be hidden by the mount. Plan your install locations
  accordingly.
