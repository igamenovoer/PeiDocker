## Why

The current `docs/` directory has a flat structure mixing user guides, developer internals, and examples as siblings. Most of PeiDocker's 19 system scripts have zero documentation in docs/. There is no progressive learning path for first-time users, no troubleshooting guide, and the examples are heavily skewed toward environment variables while ignoring GPU, storage, SSH multi-user, proxy, and other key features. The documentation needs a complete restructure into audience-oriented sections.

## What Changes

- **New `docs/manual/` section**: User-perspective documentation including getting-started guides, concept explainers (two-stage architecture, storage model, script lifecycle, env vars), task-oriented how-to guides (SSH, GPU, proxy, custom scripts, storage, ports, networking, webgui), a curated scripts catalog (one page per system script), CLI reference, and troubleshooting/FAQ.
- **New `docs/developer/` section**: Internals documentation covering architecture overview, build pipeline, config processing, contracts and interfaces, storage internals, entrypoint system, env var processing engine, testing guide, and diagrams (migrated from existing `internals-diagrams/`).
- **New `docs/examples/` section**: Restructured examples split into `basic/` (single-feature, minimal config, numbered progression) and `advanced/` (scenario-driven, multi-feature, real-world use cases). Doc pages use **embedded YAML** within markdown (Option A) for explanation and annotation.
- **New `<repo-root>/examples/` directory**: Each doc example has a corresponding directory at `examples/<example-slug>/` containing a `user_config.yml` (and any supporting files). Doc pages reference these configs. The existing `src/pei_docker/examples/` (envs/ and legacy/) is migrated and reorganized into this new top-level structure. Runnable verification of these configs is deferred to a future change.
- **Rewritten `docs/index.md`**: Navigation hub with audience-based routing (first-time user → manual/getting-started, returning user → guides/scripts, developer → developer/).
- **Removal of old docs/ content**: All existing files in `docs/` are discarded — this is a clean rewrite, not a migration. No content needs to be preserved or absorbed from existing docs.

## Capabilities

### New Capabilities
- `docs-manual-getting-started`: Installation, quickstart, and project structure guides for first-time users
- `docs-manual-concepts`: Concept explainers for two-stage architecture, storage model, script lifecycle, and environment variables
- `docs-manual-guides`: Task-oriented how-to guides for SSH, GPU, proxy, custom scripts, storage, ports, networking, and webgui
- `docs-manual-scripts-catalog`: Per-script documentation pages for all curated system scripts (pixi, conda, nodejs, uv, opengl, ros2, etc.)
- `docs-manual-cli-reference`: Expanded CLI reference for create/configure/remove/gui commands
- `docs-manual-troubleshooting`: Troubleshooting guide, common errors, known issues, and FAQ
- `docs-developer-internals`: Developer documentation covering architecture, build pipeline, config processing, contracts, storage internals, entrypoint system, env var engine, and testing
- `docs-examples-basic`: Single-feature examples with minimal configs, numbered for progressive learning
- `docs-examples-advanced`: Scenario-driven examples mixing multiple features for real-world use cases
- `docs-index-and-navigation`: Landing page and navigation structure for the documentation site

### Modified Capabilities
<!-- No existing spec-level requirements are changing — this is a documentation-only change -->

## Impact

- **docs/ directory**: Complete wipe and rewrite — all existing content is discarded, not migrated
- **New `examples/` at repo root**: Replaces/reorganizes `src/pei_docker/examples/` (envs/ + legacy/) into a top-level `examples/` directory with slug-named subdirectories
- **`src/pei_docker/examples/`**: Legacy and envs subdirectories are superseded by the new top-level `examples/`; existing files may be removed or symlinked
- **Existing links**: Any external links pointing to current docs paths (e.g., `docs/examples/basic.md`, `docs/cli_reference.md`) will break — redirect strategy may be needed if docs are hosted
- **README.md**: May need updated links to point to new docs structure (not in scope for this change, but noted)
- **Diagram assets**: `docs/internals-diagrams/` moved to `docs/developer/diagrams/`
