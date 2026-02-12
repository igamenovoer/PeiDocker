## Why

Users need clear, reproducible env-variable examples plus an end-to-end build/run path that demonstrates configure-time substitution and Compose-time passthrough in real workflows. Recent env handling behavior is powerful but easy to misuse without focused examples, leading to confusing failures during `configure`/`docker compose` runs.

## What Changes

- Add three focused tutorials for env usage in user config:
  - Configure-time substitution only (`${VAR}` / `${VAR:-default}`).
  - Compose-time passthrough (`{{VAR}}` / `{{VAR:-default}}`) and how it appears in generated `docker-compose.yml`.
  - Advanced tutorial covering mixed-mode strings, ports, failure modes, and guardrails.
- Add an env-focused build-and-run walkthrough that uses:
  - `ubuntu:24.04` as the base image for testing (available on this host).
  - `tmp/<subdir>/cases/<case-name>/` for disposable per-case projects and generated artifacts.
  - Download guidance: use China-based mirrors.
  - Verification steps that confirm each case can actually build and that environment variables resolve as expected.
- Update docs navigation and link to relevant example configs/commands.

## Capabilities

### New Capabilities

- `env-config-tutorials`: A set of three reproducible tutorials documenting env handling semantics and supported patterns/limitations.
- `env-build-run-walkthrough`: A step-by-step build/run flow (create → configure → build → run → validate) with the repo’s local constraints (base image, case-based tmp dirs, mirror guidance) and explicit runtime env verification.

### Modified Capabilities

<!-- none -->

## Impact

- Documentation: `docs/` content and `mkdocs.yml` navigation.
- Examples: may update/add small example configs to support tutorials.
- Optional helper scripts under `tests/scripts/` (only if needed for reproducible verification).
