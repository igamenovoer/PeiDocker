# Storage And Mounts

Use `storage:` for the fixed logical directories and `mount:` for everything else.

## Fixed Storage Keys

```yaml
stage_2:
  storage:
    app:
      type: image
    data:
      type: auto-volume
    workspace:
      type: host
      host_path: /srv/project
```

Those keys back:

- `/soft/app`
- `/soft/data`
- `/soft/workspace`

## Extra Mounts

```yaml
mount:
  home_dev:
    type: auto-volume
    dst_path: /home/dev
```

Every mount entry must set an absolute `dst_path`.

## Switching Strategies

Common transitions:

- `host` during active development, `image` or `auto-volume` later
- `auto-volume` for state you want to keep but do not need to inspect on the host
- `manual-volume` when another service already owns the volume lifecycle

## Path Relationships

- `/hard/image/<key>` is the in-image location.
- `/hard/volume/<key>` is the mounted location when a volume or host bind is used.
- `/soft/<key>` is the stable path your software should use.

## Stage Rule

`storage:` is stage-2 only. `mount:` works in both stages, but runtime-only mounts are still not available during stage-2 build hooks.

See [03 Host Mount](../../examples/basic/03-host-mount.md) and [04 Docker Volume](../../examples/basic/04-docker-volume.md).
