## 1. Directory Structure Setup

- [ ] 1.1 Delete all existing content in `docs/` (clean wipe)
- [ ] 1.2 Create new docs directory structure: `docs/manual/getting-started/`, `docs/manual/concepts/`, `docs/manual/guides/`, `docs/manual/scripts/`, `docs/developer/`, `docs/developer/diagrams/`, `docs/examples/basic/`, `docs/examples/advanced/`
- [ ] 1.3 Create new repo-root examples directory structure: `examples/basic/`, `examples/advanced/` with slug subdirectories for all planned examples

## 2. Index and Navigation

- [ ] 2.1 Rewrite `docs/index.md` as audience-routed navigation hub (first-time → getting-started, returning → guides/scripts, developer → developer/)
- [ ] 2.2 Create `docs/examples/index.md` with two-tier listing of all basic and advanced examples
- [ ] 2.3 Create `examples/README.md` at repo root — lists all examples with one-line descriptions and links to corresponding doc pages

## 3. Manual: Getting Started

- [ ] 3.1 Write `docs/manual/getting-started/installation.md` — pip/pixi install for Linux, macOS, Windows WSL with prerequisites and verification
- [ ] 3.2 Write `docs/manual/getting-started/quickstart.md` — zero-to-running-container in ≤10 commands using `--quick minimal`
- [ ] 3.3 Write `docs/manual/getting-started/project-structure.md` — explain all generated files and directories from `create`

## 4. Manual: Concepts

- [ ] 4.1 Write `docs/manual/concepts/two-stage-architecture.md` — stage-1 vs stage-2, what belongs where, how they chain
- [ ] 4.2 Write `docs/manual/concepts/storage-model.md` — 4 storage types, 3 fixed keys, storage vs mount, decision matrix
- [ ] 4.3 Write `docs/manual/concepts/script-lifecycle.md` — 5 lifecycle hooks, execution order, context, constraints
- [ ] 4.4 Write `docs/manual/concepts/environment-variables.md` — config-time `${VAR}` vs compose-time `{{VAR}}`, comparison table

## 5. Manual: Guides

- [ ] 5.1 Write `docs/manual/guides/ssh-setup.md` — all auth methods, multi-user, UID/GID, auto-discovery, host port mapping
- [ ] 5.2 Write `docs/manual/guides/gpu-support.md` — enable GPU, NVIDIA prerequisites, verification
- [ ] 5.3 Write `docs/manual/guides/proxy-configuration.md` — proxy setup, host.docker.internal, enable_globally, remove_after_build, HTTPS, APT integration, stage inheritance
- [ ] 5.4 Write `docs/manual/guides/custom-scripts.md` — writing scripts, placement, referencing in config, parameter passing, logging
- [ ] 5.5 Write `docs/manual/guides/storage-and-mounts.md` — configuring storage types, switching, custom mounts, path relationships
- [ ] 5.6 Write `docs/manual/guides/port-mapping.md` — single ports, ranges, Docker format syntax
- [ ] 5.7 Write `docs/manual/guides/networking.md` — APT mirrors (predefined + custom), keep_repo/keep_proxy options
- [ ] 5.8 Write `docs/manual/guides/webgui.md` — launching the GUI, navigating the interface, config mapping to YAML

## 6. Manual: Scripts Catalog

- [ ] 6.1 Write `docs/manual/scripts/index.md` — overview table of all 19 scripts (name, description, stage, complexity)
- [ ] 6.2 Write `docs/manual/scripts/pixi.md` — parameters, common patterns, pixi env creation
- [ ] 6.3 Write `docs/manual/scripts/conda.md` — parameters, repo config, activation
- [ ] 6.4 Write `docs/manual/scripts/ssh.md` — SSH server setup script details
- [ ] 6.5 Write `docs/manual/scripts/ros2.md` — ROS2 installation, workspace setup
- [ ] 6.6 Write `docs/manual/scripts/proxy.md` — proxy helper scripts
- [ ] 6.7 Write `docs/manual/scripts/opengl.md` — OpenGL setup, platform considerations
- [ ] 6.8 Write `docs/manual/scripts/opencv.md` — OpenCV installation
- [ ] 6.9 Write `docs/manual/scripts/simple-installers.md` — grouped page for nodejs, bun, uv, clang, firefox, ngc, litellm, claude-code, codex-cli, magnum, vision-dev

## 7. Manual: CLI Reference and Troubleshooting

- [ ] 7.1 Write `docs/manual/cli-reference.md` — all commands (create/configure/remove/gui), options, defaults, quick templates
- [ ] 7.2 Write `docs/manual/troubleshooting.md` — common errors (create/configure/build/run), known issues from context/issues/known/, FAQ

## 8. Developer Documentation

- [ ] 8.1 Write `docs/developer/architecture.md` — system overview, component diagram (reference diagrams/), source tree mapping
- [ ] 8.2 Write `docs/developer/build-pipeline.md` — full flow from user_config.yml to docker-compose.yml
- [ ] 8.3 Write `docs/developer/config-processing.md` — PeiConfigProcessor section-by-section walkthrough
- [ ] 8.4 Write `docs/developer/contracts.md` — stage interfaces, install script params, flag conventions, wrapper policies (reference openspec specs)
- [ ] 8.5 Write `docs/developer/storage-internals.md` — symlink strategy, /soft vs /hard, mount path resolution
- [ ] 8.6 Write `docs/developer/entrypoint-system.md` — preparation, handoff, logging, SIGTERM handling
- [ ] 8.7 Write `docs/developer/env-var-processing.md` — substitution engine, config-time vs compose-time, passthrough markers
- [ ] 8.8 Write `docs/developer/testing.md` — running tests, e2e framework, adding new tests

## 9. Example Configs (repo-root examples/)

- [ ] 9.1 Create `examples/basic/minimal-ssh/user_config.yml` — adapted from legacy/minimal-ubuntu-ssh.yml, ubuntu:24.04 base
- [ ] 9.2 Create `examples/basic/gpu-container/user_config.yml` — nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04 base
- [ ] 9.3 Create `examples/basic/host-mount/user_config.yml` — ubuntu:24.04 base, single host mount
- [ ] 9.4 Create `examples/basic/docker-volume/user_config.yml` — ubuntu:24.04 base, auto-volume storage
- [ ] 9.5 Create `examples/basic/custom-script/user_config.yml` + supporting script — ubuntu:24.04 base, on_build hook
- [ ] 9.6 Create `examples/basic/port-mapping/user_config.yml` — ubuntu:24.04 base, single ports and ranges
- [ ] 9.7 Create `examples/basic/proxy-setup/user_config.yml` — ubuntu:24.04 base, proxy configuration
- [ ] 9.8 Create `examples/basic/env-variables/user_config.yml` — adapted from envs/01-no-passthrough.yml
- [ ] 9.9 Create `examples/basic/env-passthrough/user_config.yml` — adapted from envs/02-with-passthrough.yml
- [ ] 9.10 Create `examples/basic/pixi-environment/user_config.yml` — adapted from legacy/pixi-basic-cpu.yml, ubuntu:24.04 base
- [ ] 9.11 Create `examples/basic/conda-environment/user_config.yml` — ubuntu:24.04 base
- [ ] 9.12 Create `examples/basic/multi-user-ssh/user_config.yml` — ubuntu:24.04 base, multiple users with different auth
- [ ] 9.13 Create `examples/basic/apt-mirrors/user_config.yml` — ubuntu:24.04 base, China mirror
- [ ] 9.14 Create `examples/advanced/ml-dev-gpu/user_config.yml` — adapted from legacy/pixi-ml-gpu.yml
- [ ] 9.15 Create `examples/advanced/web-dev-nodejs/user_config.yml` — ubuntu:24.04 base, Node.js + host mounts + ports
- [ ] 9.16 Create `examples/advanced/team-dev-environment/user_config.yml` — ubuntu:24.04 base, multi-user + shared volumes
- [ ] 9.17 Create `examples/advanced/china-corporate-proxy/user_config.yml` — ubuntu:24.04 base, proxy + APT mirrors
- [ ] 9.18 Create `examples/advanced/ros2-robotics/user_config.yml` — GPU base, ROS2 + OpenGL
- [ ] 9.19 Create `examples/advanced/vision-opengl/user_config.yml` — GPU base, OpenGL + OpenCV

## 10. Example Doc Pages: Basic

- [ ] 10.1 Write `docs/examples/basic/01-minimal-ssh.md` — embed YAML from examples/basic/minimal-ssh/, annotate, show workflow
- [ ] 10.2 Write `docs/examples/basic/02-gpu-container.md` — embed YAML, annotate
- [ ] 10.3 Write `docs/examples/basic/03-host-mount.md` — embed YAML, annotate
- [ ] 10.4 Write `docs/examples/basic/04-docker-volume.md` — embed YAML, annotate
- [ ] 10.5 Write `docs/examples/basic/05-custom-script.md` — embed YAML, annotate
- [ ] 10.6 Write `docs/examples/basic/06-port-mapping.md` — embed YAML, annotate
- [ ] 10.7 Write `docs/examples/basic/07-proxy-setup.md` — embed YAML, annotate
- [ ] 10.8 Write `docs/examples/basic/08-env-variables.md` — embed YAML, annotate
- [ ] 10.9 Write `docs/examples/basic/09-env-passthrough.md` — embed YAML, annotate
- [ ] 10.10 Write `docs/examples/basic/10-pixi-environment.md` — embed YAML, annotate
- [ ] 10.11 Write `docs/examples/basic/11-conda-environment.md` — embed YAML, annotate
- [ ] 10.12 Write `docs/examples/basic/12-multi-user-ssh.md` — embed YAML, annotate
- [ ] 10.13 Write `docs/examples/basic/13-apt-mirrors.md` — embed YAML, annotate

## 11. Example Doc Pages: Advanced

- [ ] 11.1 Write `docs/examples/advanced/ml-dev-gpu.md` — embed YAML, scenario framing, full workflow, cross-refs to concepts/basic
- [ ] 11.2 Write `docs/examples/advanced/web-dev-nodejs.md` — embed YAML, scenario framing, cross-refs
- [ ] 11.3 Write `docs/examples/advanced/team-dev-environment.md` — embed YAML, scenario framing, cross-refs
- [ ] 11.4 Write `docs/examples/advanced/china-corporate-proxy.md` — embed YAML, scenario framing, cross-refs
- [ ] 11.5 Write `docs/examples/advanced/ros2-robotics.md` — embed YAML, scenario framing, cross-refs
- [ ] 11.6 Write `docs/examples/advanced/vision-opengl.md` — embed YAML, scenario framing, cross-refs
- [ ] 11.7 Write `docs/examples/advanced/migrate-from-dockerfile.md` — conceptual mapping guide (no config)

## 12. Legacy Cleanup

- [ ] 12.1 Decide on disposition of `src/pei_docker/examples/legacy/` — remove, keep as archive, or symlink to new locations
- [ ] 12.2 Decide on disposition of `src/pei_docker/examples/envs/` — content migrated to examples/basic/env-*
- [ ] 12.3 Update any internal references that point to old example paths
