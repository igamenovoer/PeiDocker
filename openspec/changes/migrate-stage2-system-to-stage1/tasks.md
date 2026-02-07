## 1. Inventory and migration plan

- [ ] 1.1 Inventory `src/pei_docker/project_files/installation/stage-2/system/**` and list all tools to migrate to stage-1 (exclude `stage-2/system/conda/**`, explicitly out of scope).
- [ ] 1.2 For each tool to migrate, identify any non-shell assets required at runtime (e.g., `litellm/proxy.py`, opengl JSON/YAML) and confirm they will be moved alongside scripts **to stage-1 canonical** (no stage-2 asset compatibility paths required).
- [ ] 1.3 Identify scripts that reference `$PEI_STAGE_DIR_2` (especially `.../tmp/...`) and decide per-script whether to (a) default to `$PEI_STAGE_DIR_1/tmp`, (b) add `--cache-dir <dir>` overrides, or (c) keep minimal stage-2-only glue in a wrapper.

## 2. Migrate stage-2 system tools to stage-1 canonical

- [ ] 2.1 Migrate `stage-2/system/bun/` → `stage-1/system/bun/` (move scripts + assets) and convert stage-2 scripts into thin wrappers.
- [ ] 2.2 Migrate `stage-2/system/claude-code/` → `stage-1/system/claude-code/` (move scripts + assets) and convert stage-2 scripts into thin wrappers.
- [ ] 2.3 Migrate `stage-2/system/codex-cli/` → `stage-1/system/codex-cli/` (move scripts + assets) and convert stage-2 scripts into thin wrappers.
- [ ] 2.4 Migrate `stage-2/system/litellm/` → `stage-1/system/litellm/` (include `proxy.py` and any related assets) and convert stage-2 scripts into thin wrappers.
- [ ] 2.5 Migrate `stage-2/system/magnum/` → `stage-1/system/magnum/` (move scripts + assets) and convert stage-2 scripts into thin wrappers.
- [ ] 2.6 Migrate `stage-2/system/nodejs/` → `stage-1/system/nodejs/` (move scripts + assets) and convert stage-2 scripts into thin wrappers.
- [ ] 2.7 Migrate `stage-2/system/opencv/` → `stage-1/system/opencv/` (move scripts + assets) and convert stage-2 scripts into thin wrappers.
- [ ] 2.8 Migrate `stage-2/system/opengl/` → `stage-1/system/opengl/` (include non-shell assets) and convert stage-2 scripts into thin wrappers.
- [ ] 2.9 Migrate `stage-2/system/set-locale.sh` → `stage-1/system/set-locale.sh` and add a stage-2 wrapper if any existing config/examples reference the stage-2 path.

## 3. Wrapper policy, tmp-dir policy, and PEI_STAGE_DIR usage

- [ ] 3.1 Ensure each stage-2 wrapper locates stage-1 canonical scripts via `$PEI_STAGE_DIR_1` and forwards arguments verbatim using `"$@"` (no re-tokenizing or re-quoting).
- [ ] 3.2 Ensure **all** stage-2 wrappers are source-safe (use `return` on error when sourced, with `exit` fallback only when executed directly).
- [ ] 3.3 Update migrated installers that used `$PEI_STAGE_DIR_2/tmp` to default to `$PEI_STAGE_DIR_1/tmp` instead; accept `--cache-dir <dir>` as an override. When writing, create the dir, and when reading-only, tolerate the dir missing (treat as cache miss).

## 4. Docs and examples

- [ ] 4.1 Update `src/pei_docker/project_files/installation/README.md` to list the newly canonical stage-1 tool paths and clarify that stage-2 `user_config.yml` can refer to stage-1 scripts directly.
- [ ] 4.2 Update official docs and configs to prefer `stage-1/system/<tool>/...` paths where appropriate:
  - include: `docs/`, `src/pei_docker/examples/`, `src/pei_docker/project_files/installation/`, `src/pei_docker/templates/quick/*.yml`, `contribs/igamenovoer/configs/*.yml`
  - exclude: `magic-context/` (no changes there)

## 5. Verification

- [ ] 5.1 Add lightweight tests to prevent regressions in the migration (file layout invariants + wrapper forwarding shape where feasible).
- [ ] 5.2 Smoke test: run `pei-docker-cli configure` using a config that references a few migrated stage-1 scripts from stage-2 hooks and confirm it completes without error (assume tool prerequisites are met).
