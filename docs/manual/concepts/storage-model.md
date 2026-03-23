# Storage Model

PeiDocker gives stage-2 three fixed storage keys plus arbitrary extra mounts.

## The Three Fixed Keys

`stage_2.storage` accepts only:

- `app`
- `data`
- `workspace`

These keys represent the logical destinations behind:

- `/soft/app`
- `/soft/data`
- `/soft/workspace`

At runtime, those soft paths are symlinks that point either to `/hard/image/<key>` or `/hard/volume/<key>`.

## The Four Storage Types

| Type | Meaning | Typical use |
| --- | --- | --- |
| `image` | Keep files inside the image layer | Fixed app assets, baked-in tools |
| `auto-volume` | Let Docker create a named volume | Persistent data without host path management |
| `manual-volume` | Use an externally managed Docker volume | Shared state across containers |
| `host` | Bind mount a host directory | Local source trees, datasets, host-visible files |

## Storage vs Mount

Use `storage:` when the destination is one of the three fixed logical locations. Use `mount:` when you need any other container path and will specify `dst_path` yourself.

`mount:` can use user-chosen keys such as `home_dev` or `models`, but every mount entry must set an absolute `dst_path`.

## Decision Matrix

| Need | Best choice |
| --- | --- |
| Reproducible image with no external dependency | `image` |
| Persistent container state, Docker-managed | `auto-volume` |
| Existing named volume you want to reuse | `manual-volume` |
| Live files from the host | `host` |

## Important Constraints

- `stage_1` does not support the `storage` section.
- Mount names do not determine the destination path. `dst_path` does.
- If two entries target the same container destination, PeiDocker warns but still generates compose output.
