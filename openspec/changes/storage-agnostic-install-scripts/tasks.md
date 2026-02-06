## Implementation Guides

- `openspec/changes/storage-agnostic-install-scripts/impl-guides/grp1-inventory-and-conventions.md`
- `openspec/changes/storage-agnostic-install-scripts/impl-guides/grp2-custom-script-args.md`
- `openspec/changes/storage-agnostic-install-scripts/impl-guides/grp3-on-build-path-validation.md`
- `openspec/changes/storage-agnostic-install-scripts/impl-guides/grp4-stage1-installers-and-wrappers.md`
- `openspec/changes/storage-agnostic-install-scripts/impl-guides/grp5-merged-ci-docs.md`
- `openspec/changes/storage-agnostic-install-scripts/impl-guides/grp6-integration-verification.md`
- `openspec/changes/storage-agnostic-install-scripts/impl-guides/impl-integrate-groups.md`

## 1. Inventory and conventions

- [ ] 1.1 Audit `installation/stage-2/system/**` for `/soft/*` hardcoding and `/soft/*` probing; classify each script as (A) move to stage-1 canonical, (B) keep as stage-2 wrapper, (C) stage-2-only by necessity.
- [ ] 1.2 Document the preferred tool-specific flag names (`--install-dir`, `--cache-dir`, `--tmp-dir`, `--user`) and the rule “no implicit `/soft/*` behavior” in the installation docs.
- [ ] 1.3 Pick a representative “first batch” of installers to refactor (at least one that currently hardcodes `/soft/*`, and one that already has path flags) and record the target script paths (stage-1 canonical + stage-2 wrapper if needed).

## 2. Custom script argument handling (env var-safe)

- [ ] 2.1 Update custom script wrapper generation to preserve user-provided argument text so `$VARS` can expand at execution time (avoid rewriting args into single-quoted tokens).
- [ ] 2.2 Add unit tests covering argument passthrough for: quoted strings with spaces, `$HOME`/`$PEI_SOFT_DATA`-style tokens, and `--flag=value` forms.
- [ ] 2.3 Verify `on_user_login` uses `source` with the same passthrough behavior as `bash`-executed hooks.

## 3. Build-time path validation for `custom.on_build`

- [ ] 3.1 Add config validation that rejects runtime-only paths in stage-2 `custom.on_build` arguments: `/soft/...`, `/hard/volume/...`, `$PEI_SOFT_*`, and `$PEI_PATH_SOFT` (with a clear error pointing to the offending script entry).
- [ ] 3.2 Add unit tests for the validator: accepts `/hard/image/...` and other in-image paths; rejects `/soft/...`, `/hard/volume/...`, and soft-path env var tokens.
- [ ] 3.3 Update user-facing error/help text to explain the lifecycle rule: build-time installs must target in-image paths (typically `/hard/image/...`), runtime may use `/soft/...`.

## 4. Stage-1 canonical installers + stage-2 forwarding wrappers

- [ ] 4.1 Create stage-1 canonical versions of the selected “first batch” installers under `installation/stage-1/system/...` with explicit tool-specific flags and no stage detection.
- [ ] 4.2 Convert the corresponding stage-2 scripts into minimal wrappers that forward user flags to the stage-1 canonical script (only adding stage-2 glue such as choosing `/hard/image/...` vs `/soft/...` where appropriate).
- [ ] 4.3 Remove any remaining `/soft/*` probing from the selected installers and wrappers (e.g. “if `/soft/app/...` exists then …”).
- [ ] 4.4 Update script READMEs/examples to prefer stage-1 script paths; keep stage-2 paths only as wrappers where required.

## 5. Single-Dockerfile (merged) CI example and docs

- [ ] 5.1 Add a minimal “single `docker build`” documentation example that runs installers during build without relying on `/soft/*` (use tool-specific flags targeting `/hard/image/...`).
- [ ] 5.2 Ensure the docs mention the visibility trade-off: build-time installs into `/hard/image/...` may be hidden at runtime if `/soft/...` points at a mounted volume.
- [ ] 5.3 Validate that `pei-docker-cli configure --with-merged` produces `merged.Dockerfile`, `merged.env`, and `build-merged.sh`, and link the doc example to that flow.

## 6. Integration verification

- [ ] 6.1 Add/update an example config that demonstrates (A) build-time install with `/hard/image/...` and (B) runtime install with `/soft/...` using the same installer flags.
- [ ] 6.2 Run pytest and the existing custom-script-params integration flow to confirm: parameter passing works, env var tokens expand, and invalid build-time paths are rejected early.
