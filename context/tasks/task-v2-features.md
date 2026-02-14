# v2 PeiDocker Features

## Feature revision

- Revise conda-related scripts so they can be moved to the `stage-1` installation directory.
  Affected scripts (for conda revision):
  - `src/pei_docker/project_files/installation/stage-2/system/conda/install-miniconda.sh`
  - `src/pei_docker/project_files/installation/stage-2/system/conda/activate-conda-on-login.sh`
  - `src/pei_docker/project_files/installation/stage-2/system/conda/configure-conda-repo.sh`
  - `src/pei_docker/project_files/installation/stage-2/system/conda/configure-pip-repo.sh`
  - `src/pei_docker/project_files/installation/stage-2/system/conda/auto-install-miniconda.sh`
  - `src/pei_docker/project_files/installation/stage-2/system/conda/auto-install-miniforge.sh`
  - `src/pei_docker/project_files/installation/stage-2/system/conda/conda-tsinghua.txt`
  - `src/pei_docker/project_files/installation/stage-2/system/conda/README.md`
  - `src/pei_docker/project_files/installation/stage-1/system/conda/install-miniconda.sh`
  - `src/pei_docker/project_files/installation/stage-1/system/conda/activate-conda-on-login.sh`
  - `src/pei_docker/project_files/installation/stage-1/system/conda/configure-conda-repo.sh`
  - `src/pei_docker/project_files/installation/stage-1/system/conda/configure-pip-repo.sh`
  - `src/pei_docker/project_files/installation/stage-1/system/conda/conda-tsinghua.txt`
  - `src/pei_docker/project_files/installation/stage-1/system/conda/README.md`
- Clean up logs/prints of generated scripts; do not print runtime status unless the default entrypoint is started with `--verbose`.

## New features

- Revise entrypoint handling logic to be friendly for Kubernetes services and for single-user standalone use on a physical machine.
- Example: Kubernetes service mode where entrypoint runs only the service process as PID 1 (no SSH/login bootstrap), with clean signal handling for `SIGTERM`.
- Example: Single-user standalone mode on a physical machine where entrypoint prepares user environment (home/profile/hooks) and then starts an interactive shell or user command.
- Example: Same image supports both modes via explicit runtime selection (for example env var or command flag) without rebuilding the image.
- Provide `.sh` and `.bat` scripts to build and start containers without using Docker Compose at all.
- Support both Docker and Podman when creating docker compose files, allowing users to choose their preferred container runtime.

## Documentation update

- Improve documentation organization; do not put all examples in a single `.md` file.
