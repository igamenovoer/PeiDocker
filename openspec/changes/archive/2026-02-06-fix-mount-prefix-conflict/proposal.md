## Why

Users report that `mount` entries with keys that match storage prefixes (app/data/workspace) can override or corrupt the intended `dst_path`, producing incorrect mounts. This breaks expected behavior in real projects and should be fixed before more 2.0 adoption.

## What Changes

- Ensure `mount` keys never collide with storage prefix handling when computing mount destinations.
- Preserve explicit `dst_path` values for mounts even when keys resemble storage prefixes.
- Keep current configuration surface intact (no new required fields).

## Capabilities

### New Capabilities
- `mount-path-resolution`: Define deterministic rules for resolving mount destinations so storage prefixes cannot override explicit `mount` destinations.

### Modified Capabilities
- (none)

## Impact

- Configuration processing in `config_processor.py` (mount/storage resolution logic)
- Possibly GUI/config adapters if they assume prefix-based behavior
- No external API changes expected
