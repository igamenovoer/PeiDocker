# Stage-2 System Installer Audit (v2.0)

This note audits `src/pei_docker/project_files/installation/stage-2/system/**` for:

- hardcoded `/soft/...` paths
- probing `/soft/*` to decide behavior
- general stage-2 storage coupling (e.g. `/hard/image`, `/hard/volume`)

The purpose is to decide which scripts should become **stage-1 canonical installers**
and which should remain **stage-2 wrappers** (or stage-2-only).

Legend:

- **(A) Stage-1 canonical**: real implementation should live under `installation/stage-1/system/...`
- **(B) Stage-2 wrapper**: keep stage-2 path but make it a thin forwarder to stage-1
- **(C) Stage-2-only**: requires stage-2 storage mechanics; keep stage-2 implementation (minimize stage probing)

## Findings (by script)

- `stage-2/system/bun/install-bun.sh` → **A**
  - Uses per-user home defaults and explicit flags; no `/soft` dependency.
- `stage-2/system/claude-code/install-claude-code.sh` → **A**
  - User-scoped install; no `/soft` dependency.
- `stage-2/system/codex-cli/install-codex-cli.sh` → **A**
  - User-scoped install; no `/soft` dependency.
- `stage-2/system/conda/activate-conda-on-login.sh` → **B** (wrapper) + **A** (canonical)
  - **PROBES `/soft/app/miniconda3`** and hardcodes `/soft/...`.
  - Replace with canonical stage-1 script that activates conda via an explicit `--conda-dir` (default per-tool),
    and keep stage-2 path as a thin forwarder.
- `stage-2/system/conda/install-miniconda.sh` → **B** (wrapper) + **A** (canonical)
  - Uses `$PEI_SOFT_APPS` (expands to `/soft/app`) as the install prefix (runtime-only in build context).
  - Replace with canonical stage-1 script taking `--install-dir` (and optional `--tmp-dir`), and keep stage-2 path as a forwarder.
- `stage-2/system/conda/configure-conda-repo.sh` → **A**
  - Can be stage-agnostic (writes to a user’s config).
- `stage-2/system/conda/configure-pip-repo.sh` → **A**
  - Can be stage-agnostic (writes to a user’s config).
- `stage-2/system/conda/auto-install-miniconda.sh` → **C**
  - Chooses between `/hard/volume/...` and `/hard/image/...` based on stage-2 storage presence.
  - Keep for now; ensure docs clarify build vs runtime visibility trade-offs.
- `stage-2/system/conda/auto-install-miniforge.sh` → **C**
  - Same rationale as `auto-install-miniconda.sh`.
- `stage-2/system/litellm/install-litellm.sh` → **A**
  - No `/soft` dependency.
- `stage-2/system/magnum/install-magnum-gl.sh` → **A**
  - Uses a tmp working directory (currently under `$PEI_STAGE_DIR_2/tmp`); can be made stage-agnostic (use `/tmp` or `--tmp-dir`).
- `stage-2/system/nodejs/install-angular.sh` → **A**
  - User-scoped install; no `/soft` dependency.
- `stage-2/system/nodejs/install-nodejs.sh` → **A**
  - User-scoped install; no `/soft` dependency.
- `stage-2/system/nodejs/install-nvm-nodejs.sh` → **A**
  - User-scoped install; no `/soft` dependency.
- `stage-2/system/nodejs/install-nvm.sh` → **A**
  - User-scoped install; no `/soft` dependency.
- `stage-2/system/opencv/install-opencv-cpu.sh` → **A**
  - System install; should not require `/soft`.
- `stage-2/system/opencv/install-opencv-cuda.sh` → **A**
  - System install; should not require `/soft`.
- `stage-2/system/opengl/setup-opengl-win32.sh` → **A**
  - System install; should not require `/soft`.
- `stage-2/system/pixi/install-pixi.bash` → **B** (wrapper) + **A** (canonical)
  - Already uses explicit flags; can live in stage-1.
- `stage-2/system/pixi/create-env-common.bash` → **B** (wrapper) + **A** (canonical)
  - Uses pixi utils; can live in stage-1.
- `stage-2/system/pixi/create-env-ml.bash` → **B** (wrapper) + **A** (canonical)
  - Uses pixi utils; can live in stage-1.
- `stage-2/system/pixi/pixi-utils.bash` → **A**
  - Utility library; keep identical across stages or source stage-1 copy.
- `stage-2/system/set-locale.sh` → **A**
  - System install; no `/soft` dependency.

## Selected “First Batch” for this change

This implementation focuses on a representative set:

- **Conda**: fixes the clearest `/soft` hardcoding/probing issues:
  - canonical: `stage-1/system/conda/install-miniconda.sh` (new)
  - canonical: `stage-1/system/conda/activate-conda-on-login.sh` (new)
  - wrappers: `stage-2/system/conda/install-miniconda.sh` (forwarder)
  - wrappers: `stage-2/system/conda/activate-conda-on-login.sh` (forwarder)
- **Pixi**: demonstrates “already has tool-specific flags” and stage2→stage1 forwarding:
  - canonical: `stage-1/system/pixi/install-pixi.bash` (moved/copied)
  - canonical: `stage-1/system/pixi/create-env-common.bash` (moved/copied)
  - canonical: `stage-1/system/pixi/create-env-ml.bash` (moved/copied)
  - canonical: `stage-1/system/pixi/pixi-utils.bash` (moved/copied)
  - wrappers: `stage-2/system/pixi/*.bash` (forwarders / sources)

