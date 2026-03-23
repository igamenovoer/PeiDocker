# Storage Internals

PeiDocker’s storage abstraction is built around stable soft paths and switchable backing locations.

## Path Model

| Path family | Meaning |
| --- | --- |
| `/soft/*` | Stable paths used by applications |
| `/hard/image/*` | In-image directories created during build |
| `/hard/volume/*` | Runtime-mounted host or Docker-backed storage |

## Stage-2 Build-Time Setup

`create-dirs.sh` prepares:

- `/hard/image/app`
- `/hard/image/data`
- `/hard/image/workspace`
- `/hard/volume`
- `/soft`

This gives runtime scripts a predictable place to link against.

## Runtime Linking

`create-links.sh` removes existing soft links and recreates them using a volume-first policy:

- if `/hard/volume/<key>` exists, `/soft/<key>` points there
- otherwise it points to `/hard/image/<key>`

This lets application code use `/soft/...` regardless of whether the data is image-backed or externally mounted.

## Mount Resolution

`stage_2.storage` is limited to `app`, `data`, and `workspace`. Additional `mount:` entries use explicit `dst_path` values and live in a separate namespace. Name collisions are allowed; destination collisions only emit warnings.

## Developer Implications

- Build-time scripts should target `/hard/image/...` when they need a durable path in the image.
- Runtime hooks may use `/soft/...`.
- A mount key such as `workspace` does not automatically mean `/soft/workspace`; only `stage_2.storage.workspace` has that meaning.
