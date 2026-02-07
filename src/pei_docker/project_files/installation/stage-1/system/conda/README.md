# Conda Installation

This directory contains **stage-1 canonical** Conda/Miniconda scripts.

- Prefer referencing these scripts as `stage-1/system/conda/...` in `user_config.yml`.
- The `stage-2/system/conda/install-miniconda.sh` and `activate-conda-on-login.sh` paths are wrappers.

## Scripts

### `install-miniconda.sh`

Storage-agnostic Miniconda installer.

- Does **not** write to `/soft/*` and does not probe `/soft/*`.
- Accepts explicit path flags:
  - `--install-dir=PATH` (absolute; default: `/opt/miniconda3`)
  - `--tmp-dir=PATH` (absolute; default: `/tmp/pei-miniconda`)
- Supports installer source selection:
  - `--installer-url official|tuna|<https-url>`
- Optional pip mirror setup inside conda base env:
  - `--pip-repo tuna|aliyun` (default: `aliyun`)

### `activate-conda-on-login.sh`

Activation helper intended for SSH login sessions (typically used in `on_user_login`).

- Accepts `--conda-dir=PATH` (absolute; default: `/opt/miniconda3`)
- Best-effort activation: does not fail the login shell if conda is missing.

## PeiDocker Integration

Build-time vs runtime path rules:

- `custom.on_build`: do **not** use `/soft/...` or `/hard/volume/...`; use `/hard/image/...` (in-image) paths.
- Runtime hooks (`on_first_run` / `on_every_run` / `on_user_login`): `/soft/...` paths are allowed.

Example:

```yaml
stage_2:
  custom:
    on_build:
      - "stage-1/system/conda/install-miniconda.sh --install-dir=/hard/image/app/miniconda3"

    on_first_run:
      # With image storage, /soft/app -> /hard/image/app, so this becomes a no-op if already installed at build time.
      - "stage-1/system/conda/install-miniconda.sh --install-dir=/soft/app/miniconda3"

    on_user_login:
      - "stage-1/system/conda/activate-conda-on-login.sh --conda-dir=/soft/app/miniconda3"
```
