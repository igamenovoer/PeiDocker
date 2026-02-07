## Context

PeiDocker ships curated installation scripts under `src/pei_docker/project_files/installation/stage-*/system/` that users reference from `user_config.yml` (e.g. via `stage_2.custom.*` hooks). Historically, the stage-2 tree has acted as a “default home” for many installers even when they are not actually stage-2-specific, which creates:

- unclear “canonical” implementations (duplicate logic across stages over time)
- difficulty reusing installers in build-time contexts (plain Dockerfile, merged builds)
- a tendency for scripts to rely on stage-2 runtime mechanics (e.g. `$PEI_STAGE_DIR_2`, stage-2 tmp layout, or storage selection logic) even when unnecessary

The completed change `openspec/changes/storage-agnostic-install-scripts/` established the *direction*: stage-1 should be canonical where possible, and stage-2 scripts should become minimal forwarders/wrappers. That change intentionally migrated only a first batch (pixi + conda) to prove the pattern. This change extends that pattern to **all remaining** scripts under `installation/stage-2/system/**`.

## Goals / Non-Goals

**Goals:**

- Make `installation/stage-1/system/**` the canonical location for all system installer implementations currently under `installation/stage-2/system/**`, **excluding** `installation/stage-2/system/conda/**` (out of scope for this change).
- Move tool directories as a unit (scripts **and** non-shell assets) so stage-1 contains the complete runnable installer bundle.
- Convert every `installation/stage-2/system/**` script into one of:
  - a minimal wrapper that `exec`s/sources the stage-1 script and forwards flags verbatim, or
  - an explicitly “stage-2-only” script with documented justification.
- Standardize common installer flag conventions across migrated scripts:
  - `--install-dir`, `--cache-dir`, `--tmp-dir`, `--user` (when applicable)
  - avoid implicit `/soft/*` behavior and avoid probing `/soft/*` to decide behavior
- Update docs/examples to prefer stage-1 canonical paths, keeping stage-2 paths only as compatibility wrappers where appropriate.
- Add tests/verification to prevent regression:
  - wrapper forwarding (including shell quoting and `$VARS` expansion behavior)
  - build-time vs runtime lifecycle constraints (e.g., stage-2 `custom.on_build` path validation)

**Non-Goals:**

- Rewriting the entire installer suite into a uniform framework (keep scripts as shell scripts; keep per-tool defaults).
- Forcing every script to support every flag; flags should exist only where meaningful for that tool.
- Changing stage-1/stage-2 Dockerfile architecture (this is a scripts/layout refactor).
- Migrating `installation/stage-2/system/conda/**` (explicitly deferred to a separate change).

## Decisions

1. Canonical installer logic moves to stage-1; stage-2 becomes wrappers by default

   - For each `installation/stage-2/system/<tool>/...` script, create a corresponding stage-1 implementation under `installation/stage-1/system/<tool>/...`.
   - Stage-2 `user_config.yml` MAY refer to stage-1 script paths directly; wrappers are primarily for backward compatibility.
   - When a stage-2 wrapper exists, replace the stage-2 script body with a thin forwarder that primarily calls stage-1:
     - prefer `exec "$PEI_STAGE_DIR_1/..." "$@"` for executables
     - use `source "$PEI_STAGE_DIR_1/..." "$@"` only when the stage-2 script is meant to be sourced (e.g., login shell setup helpers)
   - Examples (from the completed first-batch migration):
     - exec wrapper: `installation/stage-2/system/pixi/install-pixi.bash`
     - source wrapper: `installation/stage-2/system/pixi/pixi-utils.bash`

   Alternatives considered:
   - Keep the canonical scripts in stage-2 and add stage-1 wrappers: rejected because stage-1 must work in build-only/merged contexts and should not depend on stage-2 assumptions.

2. Stage-2-only scripts remain, but must be explicit and minimal

   - Some scripts genuinely encode stage-2-only behavior (e.g., choosing between `/hard/volume/...` and `/hard/image/...` based on mounted storage visibility).
   - Those scripts remain in stage-2, but:
     - must not probe `/soft/*` as a stage detection mechanism (storage selection should be explicit and/or based on clearly stage-2-only prerequisites),
     - must document why they cannot be stage-1 canonical,
     - should still use tool-specific explicit flags where reasonable.

   Note: conda-related stage-2-only scripts are out of scope for this change; conda is explicitly deferred.

3. Flag conventions are enforced by migration, not by runtime framework

   - We standardize flags in scripts themselves and documentation, but we do not introduce a new shared CLI framework.
   - For migration consistency, each script should:
     - accept a small set of explicit path flags if it meaningfully writes to disk outside the user’s home
     - default to tool-appropriate locations (system vs user scope), without assuming `/soft/*`

4. Backward compatibility approach

   - Stage-2 paths remain callable for a transition period, but are wrappers.
   - Docs/examples should prefer stage-1 paths.
   - Any breaking changes (if unavoidable) must be documented in the script README for that tool and in `installation/README.md`.

5. Stage tmp dir usage (`$PEI_STAGE_DIR_*/tmp`)

   - Stage-1 canonical scripts that need a per-stage scratch/cache directory SHOULD use:
     - `$PEI_STAGE_DIR_1/tmp` (stage-1 canonical)
     - `$PEI_STAGE_DIR_2/tmp` (stage-2-only logic, if any)
   - If a script **writes** into the stage tmp dir, it MUST create it (`mkdir -p`) first.
   - If a script **only reads** from the stage tmp dir, it MUST treat a missing dir as a cache miss and MUST NOT fail.
   - When migrating a script from stage-2 to stage-1, any use of `$PEI_STAGE_DIR_2/tmp` for scratch/caching should become `$PEI_STAGE_DIR_1/tmp`.

## Risks / Trade-offs

- [Risk] Some stage-2 scripts rely on stage-2 env vars (e.g. `$PEI_STAGE_DIR_2`) for caching/tmp; naïvely moving them may reduce caching. → Mitigation: move the cache to stage-1 tmp (`$PEI_STAGE_DIR_1/tmp`) when the installer becomes stage-1 canonical, and/or add `--tmp-dir`/`--cache-dir` flags with safe defaults (`/tmp/...`).
- [Risk] Some scripts use `sudo`, which may not be available/appropriate in all contexts (especially during Docker build). → Mitigation: make stage-1 canonical scripts assume root when intended for Docker build; remove `sudo` usage where possible or clearly document requirement.
- [Risk] Wrapper forwarding can break quoting/variable expansion if wrappers re-parse args. → Mitigation: wrappers forward `"$@"` verbatim; do not re-tokenize.
- [Risk] Large churn touches many scripts and docs. → Mitigation: migrate tool-by-tool with tests and small commits; keep a clear inventory and acceptance criteria.
