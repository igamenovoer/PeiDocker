# Storage And Mounts Reference

## Source Files

- `docs/manual/concepts/storage-model.md`
- `docs/manual/guides/storage-and-mounts.md`
- `docs/developer/storage-internals.md`
- `src/pei_docker/templates/config-template-full.yml`
- `src/pei_docker/examples/basic/host-mount/user_config.yml`
- `src/pei_docker/examples/basic/docker-volume/user_config.yml`
- `openspec/specs/mount-path-resolution/spec.md`

## Core Model

`stage_2.storage` accepts only three fixed keys:

- `app` -> `/soft/app`
- `data` -> `/soft/data`
- `workspace` -> `/soft/workspace`

At runtime, `/soft/<key>` points to either `/hard/image/<key>` or `/hard/volume/<key>`.

Storage types:

- `image`: keep files inside the image layer
- `auto-volume`: let Docker create a named volume
- `manual-volume`: use an externally managed named volume
- `host`: bind mount a host directory

## Storage Pattern

```yaml
stage_2:
  storage:
    app:
      type: image
    data:
      type: auto-volume
    workspace:
      type: host
      host_path: "${HOST_WORKSPACE:-/tmp/peidocker-workspace}"
```

## Extra Mounts

Use `mount` for arbitrary absolute container destinations:

```yaml
stage_2:
  mount:
    home_dev:
      type: auto-volume
      dst_path: /home/dev
```

Mount keys are names only. `dst_path` determines the container path.

## Build-Time Versus Runtime

During stage-2 `on_build`, use `/hard/image/...` for durable image paths. Do not use `/soft/...` or `/hard/volume/...` in build-time hooks.

Runtime hooks such as `on_first_run` and `on_every_run` may use `/soft/...` after the stage-2 entrypoint creates storage links.
