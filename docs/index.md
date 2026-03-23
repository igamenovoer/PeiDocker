# PeiDocker Docs

PeiDocker is for people who want reproducible Docker-based development environments without hand-writing large Dockerfiles and `docker-compose.yml` files. You describe the environment in `user_config.yml`, and PeiDocker turns that into staged Docker builds, runtime scripts, and a ready-to-run compose project.

This documentation is organized by audience so you can start in the shortest path that matches what you need.

## Why PeiDocker Exists

Many teams end up with containers that are configured interactively, drift over time, or rely on undocumented manual steps. PeiDocker exists to make those setups repeatable without forcing every user to become a Dockerfile expert.

It is especially useful when you want to:

- keep image setup reproducible instead of modifying containers by hand
- express build and runtime behavior with shell hooks you already understand
- split system-image work from user-facing development setup with stage-1 and stage-2 images
- switch storage strategies between development and deployment without rewriting the whole setup
- standardize SSH users, proxy settings, APT mirrors, mounts, ports, and installer scripts in one config

## Feature Highlights

- **Custom script hooks** for image build, first run, container start, and login flows
- **Two-stage builds** that separate base-system preparation from final development environment setup
- **Storage abstraction** for image-backed, host-mounted, manual-volume, and auto-volume paths
- **Built-in installer scripts** for common tools such as Pixi, Conda, ROS2, proxy helpers, OpenGL, OpenCV, and more
- **Reusable examples** you can copy directly instead of starting from a blank config
- **CLI-first workflow** that works today; the Web GUI code remains documented but is currently deprecated and unavailable in 2.0

## Intended Audience

PeiDocker is a good fit if you are:

- a developer who wants an SSH-ready dev container quickly
- an ML or robotics user who needs GPU, OpenGL, ROS2, or heavy setup scripts
- a team maintaining reusable container setups across multiple machines or users
- working behind China mirrors or corporate proxies and need those settings applied consistently
- more comfortable maintaining Bash scripts than maintaining complex Dockerfiles

If you prefer to hand-author every Dockerfile and Compose detail yourself, PeiDocker may be too opinionated. The project is designed for repeatable setups driven by configuration plus script hooks.

## Motivating Examples

If you want a concrete starting point, begin with one of these:

- [Minimal SSH container](examples/basic/01-minimal-ssh.md): the smallest end-to-end example for a reusable container with SSH enabled
- [GPU development container](examples/basic/02-gpu-container.md): a compact CUDA-based example for validating GPU-enabled builds
- [Custom script workflow](examples/basic/05-custom-script.md): shows how to keep image customization in shell instead of baking logic into a Dockerfile
- [ML development environment](examples/advanced/ml-dev-gpu.md): combines GPU, storage, and tool installation into a more realistic daily-use setup
- [Team development environment](examples/advanced/team-dev-environment.md): shows how shared storage and multi-user access fit into one config
- [China or corporate proxy setup](examples/advanced/china-corporate-proxy.md): demonstrates proxy and mirror-aware configuration for restricted networks

## Start Here

### First time with PeiDocker

- Read [Installation](manual/getting-started/installation.md) to install the CLI and check Docker prerequisites.
- Read [Build Modes](manual/getting-started/build-modes.md) to choose among stage-1-only, the default two-stage Compose workflow, and merged build artifacts.
- Follow [Quickstart](manual/getting-started/quickstart.md) if you want the default two-stage Compose path.
- Read [Project Structure](manual/getting-started/project-structure.md) if you want to understand the files `create` generated.

### Returning user

- Use the [Guides](manual/guides/ssh-setup.md) section for focused tasks such as SSH, GPU, proxy, mounts, ports, and Web GUI mapping.
- Use the [Scripts catalog](manual/scripts/index.md) when you want to reuse PeiDocker’s built-in installers instead of writing shell from scratch.
- Keep [CLI Reference](manual/cli-reference.md) and [Troubleshooting](manual/troubleshooting.md) nearby when iterating on configs.

### Learn by example

- Browse [Examples](examples/index.md) for copyable `user_config.yml` files.
- Start with the numbered [basic examples](examples/basic/01-minimal-ssh.md) for single features in the default two-stage Compose workflow.
- Use [Build Modes](manual/getting-started/build-modes.md) first if you want a stage-1-only container or the merged-build workflow instead.
- Move to the [advanced examples](examples/advanced/ml-dev-gpu.md) when you want complete scenarios.

### Contributing or debugging internals

- Start in [Developer Architecture](developer/architecture.md).
- Follow [Build Pipeline](developer/build-pipeline.md) and [Config Processing](developer/config-processing.md) to trace config to compose output.
- Use [Contracts](developer/contracts.md), [Storage Internals](developer/storage-internals.md), and [Entrypoint System](developer/entrypoint-system.md) when changing behavior.
