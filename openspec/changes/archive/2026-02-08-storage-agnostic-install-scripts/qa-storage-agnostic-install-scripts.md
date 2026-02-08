# Q&A: storage-agnostic-install-scripts

## Introduction

This Q&A collects implementation questions for the `storage-agnostic-install-scripts` change in PeiDocker. It is intended for developers (including future maintainers) who need to understand or modify the build-time vs runtime storage rules and installer/script behavior.

**Related docs**
- `openspec/changes/storage-agnostic-install-scripts/proposal.md`
- `openspec/changes/storage-agnostic-install-scripts/design.md`
- `openspec/changes/storage-agnostic-install-scripts/tasks.md`
- `openspec/changes/storage-agnostic-install-scripts/specs/install-script-parameter-interface/spec.md`
- `openspec/changes/storage-agnostic-install-scripts/specs/stage2-wrapper-forwarding/spec.md`
- `openspec/changes/storage-agnostic-install-scripts/specs/single-dockerfile-ci-install-flow/spec.md`
- `openspec/changes/storage-agnostic-install-scripts/impl-guides/impl-integrate-groups.md`

**Key entrypoints and modules**
- `src/pei_docker/config_processor.py`
- `src/pei_docker/pei.py`
- `src/pei_docker/project_files/installation/README.md`
- `src/pei_docker/project_files/installation/stage-1/system/pixi/install-pixi.bash`
- `src/pei_docker/project_files/installation/stage-2/system/pixi/install-pixi.bash`
- `src/pei_docker/project_files/installation/stage-1/system/conda/install-miniconda.sh`
- `src/pei_docker/project_files/installation/stage-2/system/conda/install-miniconda.sh`

## What scripts have been moved to stage-1 from stage-2?
> Last revised at: `2026-02-07T18:14:07Z` | Last revised base commit: `972583f43234afa6d347135050a29dfcefbb91de`

Paths below are relative to `src/pei_docker/project_files/installation/`.

| Before (stage-2) | After (stage-1 canonical) |
| --- | --- |
| `stage-2/system/pixi/install-pixi.bash` | `stage-1/system/pixi/install-pixi.bash` |
| `stage-2/system/pixi/create-env-common.bash` | `stage-1/system/pixi/create-env-common.bash` |
| `stage-2/system/pixi/create-env-ml.bash` | `stage-1/system/pixi/create-env-ml.bash` |
| `stage-2/system/pixi/pixi-utils.bash` | `stage-1/system/pixi/pixi-utils.bash` |
| `stage-2/system/conda/install-miniconda.sh` | `stage-1/system/conda/install-miniconda.sh` |
| `stage-2/system/conda/activate-conda-on-login.sh` | `stage-1/system/conda/activate-conda-on-login.sh` |

- The stage-2 paths remain as thin wrappers for backward compatibility; they forward to stage-1 via `$PEI_STAGE_DIR_1/...`.
- Stage-1 conda also includes copied helper files from stage-2: `stage-1/system/conda/configure-conda-repo.sh`, `stage-1/system/conda/configure-pip-repo.sh`, `stage-1/system/conda/conda-tsinghua.txt`.

## [question title]
> Last revised at: `{{LAST_REVISED_AT}}` | Last revised base commit: `{{LAST_REVISED_BASE_COMMIT}}`

- [answer/code]

## [question title]
> Last revised at: `{{LAST_REVISED_AT}}` | Last revised base commit: `{{LAST_REVISED_BASE_COMMIT}}`

- [answer/code]
