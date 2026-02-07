## Why

PeiDocker’s installer scripts under `installation/stage-2/system/**` are currently a mix of (a) stage-agnostic installers and (b) stage-2-specific scripts that assume PeiDocker runtime storage mechanics or stage-2 env vars. This makes the “canonical” location of installer behavior unclear, encourages duplication, and complicates build-time / single-Dockerfile usage where stage-2 runtime plumbing (e.g. `/soft/...` symlinks) may not exist.

## What Changes

- Make `installation/stage-1/system/**` the canonical home for system installer implementations for all tools currently present under `installation/stage-2/system/**`, **excluding** `installation/stage-2/system/conda/**` (out of scope for this change).
- Move each tool directory as a unit (scripts **and** non-shell assets) so stage-1 contains the complete runnable tool installer bundle.
- Convert `installation/stage-2/system/**` scripts into minimal wrappers when needed (primarily for backward compatibility), forwarding to the corresponding stage-1 script and preserving CLI flags and behavior.
  - Stage-2 `user_config.yml` MAY refer to stage-1 script paths directly; not every tool needs a stage-2 wrapper.
  - Wrapper scripts may keep *minimal* stage-2 glue where required (e.g., auto-selection logic that depends on stage-2 storage visibility), but must not duplicate full installer logic.
- Standardize installer CLI conventions across all migrated scripts:
  - Prefer explicit tool-specific flags (`--install-dir`, `--cache-dir`, `--tmp-dir`, `--user`) where applicable.
  - Avoid implicit `/soft/*` defaults and avoid probing `/soft/*` to decide behavior; callers must pass explicit paths when storage location matters.
- Update docs/examples so users are guided to stage-1 canonical paths; stage-2 paths remain supported as wrappers for backward compatibility.
- Add/extend tests and a small integration verification matrix to ensure:
  - stage-2 wrappers forward flags without breaking shell expansion/quoting
  - build-time hooks (`stage_2.custom.on_build`) do not depend on runtime-only storage paths

## Capabilities

### New Capabilities

- `stage1-system-canonical-installers`: Define and enforce that stage-1 is the canonical location for system installer implementations; stage-2 system scripts are wrappers.
- `stage2-system-wrapper-policy`: Specify what “minimal wrapper” means for stage-2 system scripts (forward flags, minimal glue only, no re-implementation).
- `installer-flag-conventions`: Specify the common CLI flag conventions for installers (explicit path flags; no implicit `/soft/*` behavior) across all migrated tools.

### Modified Capabilities

<!-- None (no existing installer-related specs in openspec/specs/ at time of writing) -->

## Impact

- Affects the on-disk installer corpus under:
  - `src/pei_docker/project_files/installation/stage-1/system/**`
  - `src/pei_docker/project_files/installation/stage-2/system/**`
  - **Excludes**: `src/pei_docker/project_files/installation/stage-2/system/conda/**` (explicitly deferred)
- Documentation updates in `src/pei_docker/project_files/installation/README.md` and potentially `docs/`.
- Requires coordination with existing “storage-agnostic install scripts” work to avoid diverging conventions between first-batch migrated installers and newly migrated ones.
