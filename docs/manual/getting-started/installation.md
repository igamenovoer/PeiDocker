# Installation

PeiDocker needs Python 3.11+ and Docker. The default workflow uses `docker compose`, while the merged-build workflow can use plain `docker build` and `docker run`. The CLI is the supported interface today; the Web GUI command exists but currently exits with a deprecation message in 2.0.

## Prerequisites

- Docker Engine or Docker Desktop
- Docker Compose plugin if you plan to use the default two-stage Compose workflow
- Python 3.11 or newer
- A shell that can run `pei-docker-cli`
- For GPU work: NVIDIA drivers plus a Docker setup that exposes GPUs to containers

## Linux

### `uv` or `pip`

```bash
uv tool install pei-docker
```

```bash
pip install pei-docker
```

### Pixi-managed development environment

```bash
git clone https://github.com/igamenovoer/PeiDocker.git
cd PeiDocker
pixi run pei-docker-cli --help
```

## macOS

Use Docker Desktop plus the same Python installation commands:

```bash
uv tool install pei-docker
```

or:

```bash
pip install pei-docker
```

For local repo work:

```bash
git clone https://github.com/igamenovoer/PeiDocker.git
cd PeiDocker
pixi run pei-docker-cli --help
```

## Windows with WSL

Use WSL2 for the CLI workflow. Install Docker Desktop, enable WSL integration, then install PeiDocker inside your Linux distro:

```bash
uv tool install pei-docker
```

or:

```bash
pip install pei-docker
```

If you are contributing from this repository:

```bash
git clone https://github.com/igamenovoer/PeiDocker.git
cd PeiDocker
pixi run pei-docker-cli --help
```

## Verify The Install

```bash
pei-docker-cli --help
docker --version
docker compose version
```

You should see the `create`, `configure`, and `remove` commands from PeiDocker, plus a working Docker installation. If you plan to use the default two-stage Compose path, confirm that `docker compose version` also works.

## Next Step

Continue with [Build Modes](build-modes.md) to choose among stage-1-only, the default two-stage Compose workflow, and merged build artifacts. If you already know you want the default path, continue straight to [Quickstart](quickstart.md).
