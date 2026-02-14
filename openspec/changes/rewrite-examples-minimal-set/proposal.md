## Why

PeiDocker’s shipped example configs have grown large and uneven over time, making
them harder to understand, harder to maintain, and less aligned with the
recommended “create → edit → configure → build/run” workflow.

We want a small, canonical set of examples that are minimal, composable, and
cover the essential PeiDocker features most users need on day 1, plus a few
high-value optional examples (GPU, proxy/APT acceleration, merged build flow).

## What Changes

- Add a new minimal examples set under `src/pei_docker/examples/` intended to be
  the default examples copied by `pei-docker-cli create --with-examples`.
- Keep existing example configs under `src/pei_docker/examples/legacy/` for
  historical reference, but treat them as non-canonical.
- Preserve the focused env tutorial examples under `src/pei_docker/examples/envs/`.
- Update documentation to reference the new canonical examples and to explain
  which examples are “core” vs “optional”.
- (If needed) adjust project creation so `--with-examples` copies canonical
  examples while excluding `legacy/` to avoid user confusion.

## Capabilities

### New Capabilities
- `examples-minimal-set`: Define the required set of canonical example configs,
  their goals, naming, constraints (minimal, cross-platform where possible), and
  how they map to the recommended CLI workflow.

### Modified Capabilities
- (none)

## Impact

- Files/data:
  - `src/pei_docker/examples/` (new canonical example YAMLs and index/README)
  - `src/pei_docker/examples/legacy/` (kept for reference)
  - `src/pei_docker/examples/envs/` (kept as-is, referenced where relevant)
- CLI / project scaffolding:
  - `pei-docker-cli create` and any shared project creation utilities may need
    to exclude `examples/legacy/` from the copied output.
- Docs:
  - `docs/examples/*` and any other pages that refer to shipped examples should
    be updated to point to canonical configs and keep snippets consistent.
