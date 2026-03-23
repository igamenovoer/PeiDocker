# Troubleshooting

This page focuses on failures you are likely to hit while creating, configuring, building, or running PeiDocker projects.

## Common Errors

### `Config file ... does not exist`

Cause: `pei-docker-cli configure` could not find the config path you passed.

Fix:

- Run from the project root, or
- pass `-p <project-dir>` and optionally `-c <config-file>`

### Duplicate keys in YAML

Cause: PeiDocker rejects duplicate YAML keys instead of silently keeping the last one.

Fix:

- Remove the duplicate key
- Re-run `configure`

### Stage-2 `on_build` uses `/soft/...` or `/hard/volume/...`

Cause: runtime-only storage paths do not exist during `docker build`.

Fix:

- Use `/hard/image/...` for build-time installs
- Move the script to `on_first_run` if it must target `/soft/...`

### Passthrough markers rejected

Cause: `{{...}}` markers only work in values that are emitted into `docker-compose.yml`.

Fix:

- Do not use `{{...}}` inside custom script entries
- Do not use `--with-merged` with passthrough markers
- Avoid passthrough markers in stage environments that are baked into `/etc/environment`

### SSH key file not found

Cause: relative key paths are resolved from the installation directory, not from the repo root.

Fix:

- Move the key file under `installation/`, or
- use an absolute path, or
- use `~` for host key discovery where appropriate

## Known Constraints

### Compose-time env passthrough has a limited scope

Current behavior:

- `{{VAR}}` works for compose-emitted values such as image tags, environment values, and port strings.
- It does not work in generated helper scripts.
- It does not work with merged build artifacts.

### Historical signal-handling caveat

Older entrypoint revisions used `exec sleep infinity` as PID 1, which could ignore `SIGTERM`. Current entrypoints keep Bash as PID 1 in the sleep fallback and trap `TERM`, so this specific issue is no longer the expected behavior.

## FAQ

### Do I edit `docker-compose.yml` directly?

You can, but `pei-docker-cli configure` will overwrite it. Prefer editing `user_config.yml` and custom scripts.

### Why does stage-2 include stage-1 ports?

That is how the compose generation model works. Stage-2 is the final service image, so it carries forward the stage-1 port mappings plus any stage-2 additions.

### Where should I install tools so they survive rebuilds?

- Into the image: `/hard/image/...`
- Into persistent runtime storage: `/soft/...` via runtime hooks
- Into a Docker-managed volume: `auto-volume` or `manual-volume`

### How do I debug startup hooks?

Start the container with verbose entrypoint mode so the generated wrapper banners are printed, and inspect `installation/stage-*/generated/` to see exactly what `configure` wrote.
