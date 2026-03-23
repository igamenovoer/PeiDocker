## Why

The current docs mostly teach PeiDocker as a two-stage Compose workflow, even though the system also supports stage-1-only usage and merged-build artifacts. First-time users can easily conclude that `stage_2` is mandatory or confuse a merged build with a single-stage config, which makes onboarding harder than it needs to be.

## What Changes

- Add a first-time-user build-modes explanation to the published docs so users can clearly choose among stage-1-only, default two-stage Compose, and merged-build workflows.
- Introduce terminology and decision guidance that explicitly distinguishes:
  - omitting `stage_2` from the config
  - keeping both stages and building them separately with Compose
  - keeping both stages and generating merged artifacts with `--with-merged`
- Update the home/getting-started flow, concept docs, project-structure docs, and CLI reference so those modes are introduced consistently instead of only being mentioned as isolated details.
- Add concrete documentation examples or walkthroughs for beginner-facing stage-1-only usage and merged-build usage so readers can see the commands and outcomes, not just the concepts.

## Capabilities

### New Capabilities
- `docs-build-mode-onboarding`: First-time-user documentation covers the supported build modes, where they differ, and how to choose the right one.
- `docs-build-mode-examples`: Example and workflow docs provide concrete stage-1-only and merged-build guidance without conflating the two models.

### Modified Capabilities

None.

## Impact

- Affected docs under `docs/manual/`, `docs/examples/`, and `docs/index.md`
- `mkdocs.yml` navigation updates if a new getting-started page is added
- Repo-root `examples/README.md` and possibly a new example config if stage-1-only is represented as a runnable basic example
- No runtime code, API, or dependency changes
