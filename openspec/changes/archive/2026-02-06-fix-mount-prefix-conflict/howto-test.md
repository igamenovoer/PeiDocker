# How To Test: `fix-mount-prefix-conflict`

This change fixes the bug where `mount` entries whose key matches a storage keyword (`app`, `data`, `workspace`) could incorrectly override `mount.dst_path` and/or cause docker-compose volume key conflicts.

## Prerequisites

- Docker installed and working on the host (`docker`, `docker compose`)
- Use Pixi environment for CLI runs: `pixi run ...`

## End-to-End Repro (Project in `tmp/`)

### 1. Create a minimal project

```bash
mkdir -p tmp
pixi run pei-docker-cli create -p tmp/mount-prefix-conflict-test --quick minimal
```

### 2. Edit `user_config.yml` to create the key-collision scenario

Edit `tmp/mount-prefix-conflict-test/user_config.yml`:

- Use unique image names to avoid clobbering any existing images.
- Add `stage_2.storage.data` (fixed storage keyword).
- Add `stage_2.mount.data` (mount key intentionally equals the storage keyword) with an explicit absolute `dst_path`.

Example snippet:

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-mount-prefix-test:stage-1

stage_2:
  image:
    output: pei-mount-prefix-test:stage-2

  storage:
    app: { type: image }
    data: { type: auto-volume }
    workspace: { type: image }

  mount:
    data:
      type: auto-volume
      dst_path: /custom/data
```

### 3. Generate compose

```bash
pixi run pei-docker-cli configure -p tmp/mount-prefix-conflict-test
```

### 4. Verify generated compose has no key conflict

The important assertions are:

- Storage `data` becomes `data:/hard/volume/data`
- Mount `data` becomes `mount_data:/custom/data` (note `mount_` prefix and preserved `dst_path`)

```bash
rg -n "data:/hard/volume/data" tmp/mount-prefix-conflict-test/docker-compose.yml
rg -n "mount_data:/custom/data" tmp/mount-prefix-conflict-test/docker-compose.yml
rg -n "^\\s*mount_data:" tmp/mount-prefix-conflict-test/docker-compose.yml
cd tmp/mount-prefix-conflict-test && docker compose config
```

### 5. Build and check mounts exist in a temporary container

```bash
cd tmp/mount-prefix-conflict-test
docker compose build stage-1
docker compose build stage-2
docker compose run --rm -T stage-2 bash -lc 'set -euo pipefail; ls -ld /hard/volume/data /custom/data; grep -E "(/hard/volume/data|/custom/data)" /proc/mounts || true'
```

## Warning-Only Destination Conflict Check (Optional)

PeiDocker will warn (but not block) if multiple mappings target the same container `dst_path` by simple string matching.

Example: set a mount destination equal to the storage destination:

```yaml
stage_2:
  mount:
    other:
      type: host
      host_path: /host/data
      dst_path: /hard/volume/data
```

Then:

```bash
pixi run pei-docker-cli configure -p tmp/mount-prefix-conflict-test
```

Expected: a `logging.warning` message like `Multiple volume mappings target the same container path ...` but compose generation still succeeds.

## Negative Tests (Expected Errors)

- **Mount `dst_path` must be absolute**: a mount `dst_path` not starting with `/` must fail configuration.
- **Storage keys are fixed**: `storage` only allows `app`, `data`, `workspace`; any other key must fail configuration.
- **Duplicate YAML keys are rejected**: duplicate keys anywhere in YAML (including `mount`) must fail early during YAML loading.

## Unit Test Pattern (pytest)

Reference: `tests/test_mount_path_resolution.py`.

Run in the dev environment:

```bash
pixi run -e dev test
```

## Cleanup

```bash
cd tmp/mount-prefix-conflict-test
docker compose down -v --remove-orphans
docker image rm pei-mount-prefix-test:stage-2 pei-mount-prefix-test:stage-1 || true
```
