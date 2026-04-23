# Conda Reference

## Source Files

- `docs/manual/scripts/conda.md`
- `docs/examples/basic/11-conda-environment.md`
- `src/pei_docker/examples/basic/conda-environment/user_config.yml`

## Scripts

Canonical path: `stage-1/system/conda/`.

Main scripts:

- `install-miniconda.sh`
- `activate-conda-on-login.sh`
- `configure-conda-repo.sh`
- `configure-pip-repo.sh`

Important install flags:

- `--install-dir=PATH`
- `--tmp-dir=PATH`
- `--installer-url official|tuna|<https-url>`
- `--pip-repo tuna|aliyun`

Activation flag:

- `--conda-dir=PATH`

## Recommended Pattern

Install into image storage during build and activate via the runtime soft path on login:

```yaml
stage_2:
  storage:
    app:
      type: image
  custom:
    on_build:
      - "stage-1/system/conda/install-miniconda.sh --install-dir=/hard/image/app/miniconda3 --pip-repo tuna"
    on_user_login:
      - "stage-1/system/conda/activate-conda-on-login.sh --conda-dir=/soft/app/miniconda3"
```

`on_user_login` is sourced, so it can safely adjust the user's shell environment.
