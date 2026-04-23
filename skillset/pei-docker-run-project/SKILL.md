---
name: pei-docker-run-project
description: Guidance for operating a configured PeiDocker project. Use when Codex needs to build, run, stop, connect to, validate, troubleshoot, or clean up a PeiDocker project using Docker Compose, SSH, exec, GPU checks, or merged-build helper scripts.
---

# PeiDocker Run Project

## Start Here

Use this skill after a PeiDocker project has been configured or when the user asks how to operate generated Docker artifacts.

Primary sources:

- `docs/manual/getting-started/quickstart.md`
- `docs/manual/getting-started/build-modes.md`
- `docs/manual/cli-reference.md`
- `docs/manual/troubleshooting.md`
- `docs/manual/guides/gpu-support.md`
- `docs/manual/guides/ssh-setup.md`
- `docs/developer/entrypoint-system.md`

First identify the project mode:

- Compose path: project has `docker-compose.yml` and no user intent to use merged helpers.
- Merged path: project was configured with `pei-docker-cli configure --with-merged` and has `build-merged.sh`, `run-merged.sh`, `merged.Dockerfile`, and `merged.env`.
- Stage-1-only: `docker-compose.yml` contains only `stage-1`, usually because `stage_2` was omitted.

## Compose Build And Run

Default two-stage flow:

```bash
cd <project-dir>
docker compose build stage-1
docker compose build stage-2
docker compose up -d stage-2
```

Stage-1-only flow:

```bash
cd <project-dir>
docker compose build stage-1
docker compose up -d stage-1
```

Useful inspection:

```bash
docker compose ps
docker compose logs
docker compose config
```

## Merged Build And Run

Only use this path when the project was configured with `--with-merged`:

```bash
cd <project-dir>
./build-merged.sh
./run-merged.sh -d
```

Forward extra build flags after `--`:

```bash
./build-merged.sh -- --no-cache --progress=plain
```

Do not recommend compose-time passthrough markers `{{...}}` with merged build.

## Connect And Validate

SSH, when configured:

```bash
ssh <user>@localhost -p <host-port>
```

Default minimal template uses user `me`, password `123456`, and host port `2222`.

Exec into a running service:

```bash
docker compose exec stage-2 bash
```

GPU validation:

```bash
docker compose exec stage-2 nvidia-smi
```

Port validation:

- Check `docker compose ps`.
- Check generated `docker-compose.yml`.
- Remember stage-2 includes stage-1 port mappings plus stage-2 mappings.

Verbose entrypoint troubleshooting:

```bash
docker compose run --rm stage-2 --verbose
```

Generated wrapper banners are controlled by `PEI_ENTRYPOINT_VERBOSE=1`.

## Stop And Cleanup

Stop services:

```bash
docker compose down
```

Remove volumes only when the user explicitly wants persistent state deleted:

```bash
docker compose down -v
```

Use PeiDocker cleanup for images and containers created by the generated compose file:

```bash
pei-docker-cli remove -p <project-dir>
```

## Runtime Troubleshooting

When run/build behavior is wrong, check in this order:

1. Confirm `pei-docker-cli configure` was run after the latest `user_config.yml` edits.
2. Confirm the requested service exists in `docker-compose.yml`.
3. Inspect `docker compose config` for resolved ports, env, volumes, and image tags.
4. Inspect `installation/stage-*/generated/` for generated wrapper content.
5. Use `docs/manual/troubleshooting.md` for known config and lifecycle mistakes.

Common fixes:

- Missing config path: run from the project root or pass `-p <project-dir>`.
- `/soft/...` in stage-2 `on_build`: move to runtime hook or target `/hard/image/...`.
- Passthrough markers rejected: remove `{{...}}` from script or merged-build contexts.
- SSH key not found: make relative key paths relative to `installation/`, or use absolute paths or `~`.
