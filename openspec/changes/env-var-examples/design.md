## Context

PeiDocker already has documentation pages under `docs/`, with MkDocs navigation configured in `mkdocs.yml`. The Examples section currently contains two pages (`examples/basic.md`, `examples/advanced.md`). Env handling semantics are nuanced (configure-time substitution vs Compose-time passthrough), and the repo now supports both patterns plus guardrails and failure modes. Users need reproducible, copy/paste-friendly documentation that matches current behavior and is easy to validate by actually building and running containers. For this change, env tutorial configs will be centralized under `src/pei_docker/examples/envs/` instead of adding more unrelated top-level files under `src/pei_docker/examples/`.

Local constraints for this repo/workspace:
- Prefer `ubuntu:24.04` as the base image for testing on this host.
- Use `tmp/<subdir>/cases/<case-name>/` for temporary case-by-case tutorial projects and generated artifacts.
- Downloads may fail due to networking; documentation should guide users to use China-based mirrors.

## Goals / Non-Goals

**Goals:**
- Add three dedicated tutorials for env handling in user config:
  - basic (configure-time substitution only)
  - passthrough (compose-time resolution)
  - advanced (mixed-mode + ports + guardrails + failure modes)
- Add an env-focused build-and-run walkthrough that is reproducible in this repo/workspace.
- Keep the documentation aligned with existing examples and current CLI behavior.

**Non-Goals:**
- Changing env-handling behavior in code (this change is documentation-centric).
- Introducing new MkDocs plugins or a complicated “single source of truth” extraction system for snippets.
- Reorganizing the whole docs site beyond the minimal navigation additions required for discoverability.

## Decisions

### Documentation structure and navigation
- Create four new pages:
  - Three env tutorials (basic / passthrough / advanced env).
  - One env-focused build-and-run walkthrough.
- Update `mkdocs.yml` to add a nested nav group under Examples:
  - Keep existing `Basic` and `Advanced` examples as-is for backwards familiarity.
  - Add an `Environment Variables` group for the three env tutorials.
  - Add a `Build & Run` entry for the walkthrough (also under Examples).

Rationale: A nested group makes the three-tutorial set discoverable and avoids overloading existing pages. Keeping current Basic/Advanced pages intact minimizes churn and broken links.

### Example config location and naming
- Place all tutorial-owned config examples under `src/pei_docker/examples/envs/`.
- Keep one config per tutorial level to make references deterministic across docs and tests.
- Use stable, ordered names so docs can refer to files without ambiguity.

Directory tree for this change:

```text
src/pei_docker/examples/envs/
├── 01-no-passthrough.yml
├── 02-with-passthrough.yml
├── 03-advanced-env-handling.yml
└── README.md
```

Rationale: A dedicated subtree avoids polluting the root examples directory, makes env examples easy to discover, and gives us a clear place for future env-focused variants.

### Case-based verification workspace layout
- Each tutorial case maps to its own temporary project under `tmp/<subdir>/cases/<case-name>/`.
- Verification is done per case by running create/configure/build/run commands in that case directory.
- Validation must include both image build success and runtime environment value checks.

Verification workspace tree:

```text
tmp/<subdir>/
└── cases/
    ├── no-passthrough/
    ├── with-passthrough/
    └── advanced-env-handling/
```

Per-case verification expectations:
- `docker compose build` completes successfully for the case.
- Runtime checks confirm expected env values (for example via `docker compose run --rm stage-2 env` or equivalent container command).

### Tutorial reproducibility conventions
- All tutorials use `tmp/<subdir>/cases/<case-name>/` as the working directory and call out cleanup (`rm -rf tmp/<subdir>`).
- Use `ubuntu:24.04` by default in tutorial examples. Where configuration supports `${BASE_IMAGE:-...}`, tutorials will either:
  - explicitly set default to `ubuntu:24.04`, or
  - instruct setting `BASE_IMAGE=ubuntu:24.04` before `configure` (for configure-time substitution), and/or
  - demonstrate `{{BASE_IMAGE:-ubuntu:24.04}}` where Compose-time resolution is desired.

### Networking / download guidance
- For any steps involving downloads (apt, installers), include a short “networking note” that recommends China-based mirrors.
- Do not include proxy setup commands or proxy variables in tutorial examples.

### Avoid duplication with existing docs/examples
- Prefer referencing canonical env configs under `src/pei_docker/examples/envs/` and reusing small, focused snippets rather than duplicating long configs.
- Keep `docs/examples/advanced.md` unchanged unless a small cross-link improves discoverability; the env tutorials should stand on their own.

## Risks / Trade-offs

- **Risk: Docs drift from real behavior** → Mitigation: include per-case verification steps that run build and runtime env checks, plus recommend running `mkdocs build` in development workflows.
- **Risk: Mirror endpoints vary by user region** → Mitigation: recommend examples that work with default sources and provide mirror guidance as an optional fallback note.
- **Trade-off: Not introducing snippet tooling** → Keeps implementation simple, but requires manual upkeep of code blocks when behavior changes.
