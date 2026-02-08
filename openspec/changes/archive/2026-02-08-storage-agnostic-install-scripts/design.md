## Context

PeiDocker ships many curated installation scripts under `installation/stage-*/system/` that users can reference from `user_config.yml` and run at different lifecycle points (build vs runtime). Historically, many stage-2 scripts assumed the stage-2 storage model and its "soft" symlink paths (`/soft/app`, `/soft/data`, `/soft/workspace`), or attempted to detect whether they were running in stage-2 by probing `/soft/*` or choosing between `/hard/volume/*` and `/hard/image/*`.

PeiDocker also supports a "single `docker build` flow" via `pei-docker-cli configure --with-merged`, which generates `merged.Dockerfile` and `build-merged.sh` from the same compose-derived build args. In the current stage-2 image build, `/soft/*` symlinks are *not created during `docker build`*; they are created at runtime in stage-2 `on-entry.sh` by invoking `create-links.sh` before `on-first-run.sh`.

This creates two important constraints:

1. Scripts that run during image build (`custom.on_build`) must not assume `/soft/*` exists.
2. Runtime scripts (first-run/every-run/user-login) can rely on `/soft/*` existing, because `on-entry.sh` creates the symlinks first.

Separately, users want to reuse PeiDocker installers in:

- plain Dockerfile builds (CI platforms that expect a single Dockerfile repo)
- "fully provisioned at build time" images (no first-run installs required)
- stage-2 runtime workflows that still want to benefit from the storage abstraction

## Affected Scripts (Initial Inventory)

This change is expected to touch "almost all" installers under `installation/stage-2/system/` by either:

- moving the canonical implementation to `installation/stage-1/system/`, and updating docs/examples to reference the stage-1 script path, or
- keeping a stage-2 wrapper when stage-2-specific glue is needed.

Current stage-2 system script inventory:

- `stage-2/system/bun/install-bun.sh`
- `stage-2/system/claude-code/install-claude-code.sh`
- `stage-2/system/codex-cli/install-codex-cli.sh`
- `stage-2/system/conda/activate-conda-on-login.sh`
- `stage-2/system/conda/auto-install-miniconda.sh`
- `stage-2/system/conda/auto-install-miniforge.sh`
- `stage-2/system/conda/configure-conda-repo.sh`
- `stage-2/system/conda/configure-pip-repo.sh`
- `stage-2/system/conda/install-miniconda.sh`
- `stage-2/system/litellm/install-litellm.sh`
- `stage-2/system/magnum/install-magnum-gl.sh`
- `stage-2/system/nodejs/install-angular.sh`
- `stage-2/system/nodejs/install-nodejs.sh`
- `stage-2/system/nodejs/install-nvm-nodejs.sh`
- `stage-2/system/nodejs/install-nvm.sh`
- `stage-2/system/opencv/install-opencv-cpu.sh`
- `stage-2/system/opencv/install-opencv-cuda.sh`
- `stage-2/system/opengl/setup-opengl-win32.sh`
- `stage-2/system/pixi/create-env-common.bash`
- `stage-2/system/pixi/create-env-ml.bash`
- `stage-2/system/pixi/install-pixi.bash`
- `stage-2/system/pixi/pixi-utils.bash`
- `stage-2/system/set-locale.sh`

## Goals / Non-Goals

**Goals:**

- Make installation scripts storage-agnostic by default:
  - no stage detection by probing `/soft/*`
  - no hardcoded writes to `/soft/*`
- Standardize installer script interfaces using tool-specific, explicit flags (e.g. `--install-dir`, `--cache-dir`, `--tmp-dir`) with per-tool defaults.
- Preserve all build modes:
  - stage-1 only (ignore stage-2)
  - stage-1 + stage-2 built separately
  - merged build (single `docker build` flow)
- Make stage-2 prefer calling stage-1 scripts directly. Add stage-2 wrapper scripts only when stage-2 needs to inject stage-2-specific behavior/paths.
- Define path behavior by lifecycle:
  - build-time: users MUST target in-image locations (typically under `/hard/image/...`) for tool-specific path flags because mounted volumes and `/soft/*` indirection are not available during `docker build`
  - runtime: users MAY target `/soft/...` paths for tool-specific path flags because `/soft/*` symlinks are created on container start

**Non-Goals:**

- Enforce or validate Docker storage semantics (e.g. whether volume mounts hide in-image content); this is documented behavior.
- Rewrite all existing scripts in one pass if not needed to satisfy the acceptance criteria; focus on a representative set first.
- Create a single universal `--peidocker-*-dir` interface; scripts remain tool-specific.

## Decisions

1. Canonical implementations live in stage-1 where possible

   - Put "real" installers under `installation/stage-1/system/...` whenever they can run without stage-2 storage assumptions.
   - Stage-2 should call stage-1 scripts directly for most installs.
   - Stage-2 wrappers are used only when stage-2 needs to inject stage-2 storage behavior/values.
   - **BREAKING (v2.0)**: Users should update configs/docs to reference stage-1 scripts; existing `stage-2/system/...` paths are not guaranteed to remain stable and may be removed or reduced to wrappers.

   Alternatives considered:
   - Keep everything in stage-2 and retrofit path flags everywhere: rejected because it keeps stage-2 coupling as the default and makes stage-1-only flows harder.

2. Script interfaces are explicit and tool-specific

   - Each script exposes a small set of explicit flags matching its needs (examples: `--install-dir`, `--cache-dir`, `--tmp-dir`, `--user`).
   - Defaults remain per-tool and may already be "system default" (e.g. apt into system paths; npm/nvm into user home).
   - The stage-2 wrapper maps stage-2 storage preferences into those explicit flags, rather than relying on implicit `/soft/*` conventions.

   Alternatives considered:
   - Provide global `--peidocker-app-dir/--peidocker-data-dir/--peidocker-workspace-dir` for all scripts: rejected because many tools do not map cleanly to those categories and stage-1 scripts should not need to interpret prefix semantics.

3. Lifecycle-aware storage path usage (build vs runtime)

   - Build-time installs (scripts executed during image build via `custom.on_build`) must not depend on `/soft/*` (symlinks do not exist during build) and must not assume mounted volumes exist.
   - Users are expected to pass in-image paths (typically under `/hard/image/...`) via tool-specific flags for build-time installs.
   - Users may pass `/soft/...` paths for runtime installs.
   - PeiDocker validates obvious misuses early during configuration parsing (e.g. rejecting `/soft/...`, `$PEI_SOFT_*`, and `/hard/volume/...` in `on_build` arguments).

   Alternatives considered:
   - Make wrappers auto-select `/hard/image/...` for build-time and `/soft/...` for runtime: rejected for v2.0 because script invocations are explicit in config and users can choose paths directly; PeiDocker will reject clearly invalid build-time paths instead.

4. Preserve stage-1, stage-2, and merged Dockerfiles

   - No design change should remove `stage-1.Dockerfile` or `stage-2.Dockerfile`.
   - The merged build remains a generated artifact that stitches these templates together.
   - This supports user choice:
     - (A) stage-1 only
     - (B) stage-1 + stage-2 separate builds
     - (C) merged build (single `docker build`)

## Risks / Trade-offs

- [Risk] Some existing configs/docs reference `stage-2/system/...` script paths directly. → Mitigation: keep wrappers where needed and/or update docs/examples to prefer `stage-1/system/...` paths for storage-agnostic installers.
- [Risk] Tool-specific flags create inconsistent UX across scripts. → Mitigation: document a small set of recommended flag names (`--install-dir`, `--cache-dir`, `--tmp-dir`, `--user`) and apply them consistently when refactoring scripts.
- [Risk] Users expect "installed at build time" content to appear under `/soft/...` at runtime, but runtime storage may point `/soft/...` to `/hard/volume/...` and hide in-image installs. → Mitigation: document that build-time installs should target `/hard/image/...` (and runtime storage choice determines visibility at `/soft/...`).
