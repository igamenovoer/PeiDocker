# Conda

The Conda family is stage-1 canonical and intentionally storage-agnostic.

## Main Scripts

| Script | Purpose |
| --- | --- |
| `install-miniconda.sh` | Install Miniconda to an explicit path |
| `activate-conda-on-login.sh` | Best-effort activation in SSH login shells |
| `configure-conda-repo.sh` | Configure conda repository behavior |
| `configure-pip-repo.sh` | Configure pip repository behavior |

## Important Flags

`install-miniconda.sh` supports:

- `--install-dir=PATH`
- `--tmp-dir=PATH`
- `--installer-url official|tuna|<https-url>`
- `--pip-repo tuna|aliyun`

`activate-conda-on-login.sh` supports:

- `--conda-dir=PATH`

## Recommended Layout

- Build-time install into `/hard/image/app/miniconda3`
- Runtime shell activation via `/soft/app/miniconda3`

```yaml
stage_2:
  storage:
    app:
      type: image
  custom:
    on_build:
      - "stage-1/system/conda/install-miniconda.sh --install-dir=/hard/image/app/miniconda3"
    on_user_login:
      - "stage-1/system/conda/activate-conda-on-login.sh --conda-dir=/soft/app/miniconda3"
```

## Why This Split Matters

The install script writes files into the image. The activation script is sourced in the user shell, so it can safely modify `PATH` and activate the environment when the user logs in.
