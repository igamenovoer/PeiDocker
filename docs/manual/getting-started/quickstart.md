# Quickstart

This is the shortest path from an empty directory to a running PeiDocker container in the default two-stage Compose workflow. It uses the built-in `minimal` quick template and keeps the generated config close to defaults.

If you want a stage-1-only container or the merged-build workflow instead, read [Build Modes](build-modes.md) first.

## Goal

Create a project, generate `docker-compose.yml`, build the stage-1 and stage-2 images, start the default final container, and confirm SSH is mapped to the host.

## Commands

```bash
mkdir -p ~/peidocker-quickstart
cd ~/peidocker-quickstart
pei-docker-cli create -p demo --quick minimal
cd demo
pei-docker-cli configure
docker compose build stage-1
docker compose build stage-2
docker compose up -d
docker compose ps
ssh me@localhost -p 2222
```

The default password in the `minimal` template is `123456`.

## What Happened

1. `create` copied the project skeleton, template Dockerfiles, installation scripts, and example configs.
2. `configure` read `user_config.yml` and generated `docker-compose.yml` plus wrapper scripts under `installation/stage-*/generated/`.
3. `docker compose build stage-1` built the system base image.
4. `docker compose build stage-2` built the final image on top of stage-1.
5. `docker compose up -d` started the stage-2 service, which also exposes the SSH mapping defined in the config.

## Common First Changes

- Change the SSH host port in `stage_1.ssh.host_port`.
- Rename the output images in `stage_1.image.output` and `stage_2.image.output`.
- Add storage in `stage_2.storage` before you start doing real work in the container.

## Next Step

Read [Project Structure](project-structure.md) if you want to know what each generated file is for, revisit [Build Modes](build-modes.md) if you want stage-1-only or merged-build alternatives, or jump to [01 Minimal SSH](../../examples/basic/01-minimal-ssh.md) for a guided version of the same config.
