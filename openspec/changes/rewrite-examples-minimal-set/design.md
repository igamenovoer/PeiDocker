## Context

PeiDocker ships a set of example configuration files that are copied into new
projects via `pei-docker-cli create --with-examples`. Over time, these examples
have become a mix of “kitchen-sink” configs, platform-specific paths, and
historical patterns that no longer represent the simplest recommended usage.

This change introduces a small canonical set of minimal examples that:

- teach the mental model (Stage-1 vs Stage-2)
- demonstrate the `create → edit user_config.yml → configure → build/run` loop
- cover essential knobs (ports, persistence, customization hooks, env semantics)
- remain stable and maintainable

Existing examples are retained under `src/pei_docker/examples/legacy/` for
reference but should no longer be presented as the default entry point.

## Goals / Non-Goals

**Goals:**
- Provide a canonical set of **core** example configs that are minimal and cover
  essential PeiDocker features.
- Provide a small set of **optional** example configs for common advanced needs
  (GPU, proxy/APT acceleration, merged build flow).
- Keep examples **cross-platform by default**:
  - avoid host-specific absolute paths where possible
  - prefer Docker volumes (`auto-volume` / `manual-volume`) over bind mounts in
    the core set
- Keep env tutorial examples under `src/pei_docker/examples/envs/` as the
  dedicated place for env deep-dives.
- Update docs to point users to canonical examples and clearly distinguish core
  vs optional.
- Ensure `pei-docker-cli create --with-examples` copies canonical examples
  without copying `legacy/` (to avoid user confusion).

**Non-Goals:**
- Redesign the configuration schema or add new runtime features.
- Rework the env tutorial set (`examples/envs/*`) beyond small consistency edits.
- Guarantee that every example runs identically on all platforms (e.g., GPU
  example requires NVIDIA runtime; OpenGL example is platform-specific).

## Decisions

1) **Examples are “configs-first”, not doc-first**

- Canonical examples live as real YAML files in `src/pei_docker/examples/`.
- Docs reference the examples by filename and recommend copying them into
  `user_config.yml` in a created project, reducing doc/config drift.

2) **Naming and layout**

- Core examples use a stable, ordered naming convention:
  - `01-minimal.yml`
  - `02-persistence.yml` (Stage-2 storage + one mount)
  - `03-ports.yml`
  - `04-ssh.yml` (or equivalent primary access method)
  - `05-env-basics.yml` (minimal `${...}` vs `{{...}}` illustration)
- Optional examples are explicit and grouped:
  - `optional-gpu.yml`
  - `optional-proxy-apt.yml`
  - `optional-merged-build.yml`
- Keep `envs/` as the env tutorial namespace.
- Keep historical examples under `legacy/`.

Rationale: numeric prefixes make it obvious “where to start” and keep diffs
readable as examples evolve.

3) **Core example constraints**

- Target ~20–40 lines per core config; prefer a single “new concept” per example.
- Prefer volume-based persistence (`stage_2.storage` + `auto-volume`) and a
  single `mount.*.dst_path` example using volumes. Avoid bind-mount host paths
  in the core set.
- Use only one primary access pattern in the core set. If SSH is the primary
  story, keep it minimal and safe-by-default (key-based where possible, avoid
  encouraging password-only configs as the first example).

4) **Optional examples are allowed to be conditional**

- GPU example: clearly marked as requiring NVIDIA container runtime and GPU
  drivers; config demonstrates `device: gpu` in both stages.
- Proxy/APT example: demonstrates proxy and CN mirror usage; still runnable
  without proxy if defaults are set appropriately.
- Merged build example: demonstrates a config that is compatible with the
  `configure --with-merged` flow; avoid `/soft/*` in `on_build` commands and use
  `/hard/image/*` install targets.

5) **Project creation excludes `legacy/` by default**

Implement the copy behavior such that:

- `pei-docker-cli create --with-examples` copies:
  - canonical core examples
  - optional examples
  - env tutorial examples (`envs/`)
- and does **not** copy `legacy/` unless a future explicit flag is introduced.

Implementation approach: use `shutil.copytree(..., ignore=...)` to ignore
`legacy/` while keeping the rest of `examples/` intact.

## Risks / Trade-offs

- [Docs/config drift] → Prefer referencing filenames and “copy this file into
  user_config.yml” workflows; keep per-example README/index and minimal docs
  snippets.
- [Cross-platform mounts are tricky] → Core examples avoid host bind mounts;
  provide bind-mount guidance only in optional docs/examples.
- [Users still want legacy examples] → Keep legacy shipped in-repo, but exclude
  from default project creation output to reduce confusion.
- [Optional examples expand scope] → Keep optional count small (3) and isolate
  conditional requirements in their README notes.
