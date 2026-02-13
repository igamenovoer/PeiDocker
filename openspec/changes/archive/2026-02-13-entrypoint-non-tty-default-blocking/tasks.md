## 1. Entrypoint Behavior and CLI

- [x] 1.1 Implement default-mode entrypoint CLI parsing in stage-1 entrypoint:
  - `--no-block` flag
  - `--verbose` flag to enable verbose hook logging
  - export `PEI_ENTRYPOINT_VERBOSE=1` (or equivalent) early when verbose is enabled
  - `-- <cmd...>` separator
  - unknown `--*` options are errors
  - if argv does not start with `--`, `exec "$@"` unchanged
  (`src/pei_docker/project_files/installation/stage-1/internals/entrypoint.sh`)
- [x] 1.2 Implement the same default-mode CLI parsing and fallback behavior in stage-2 entrypoint
  (`src/pei_docker/project_files/installation/stage-2/internals/entrypoint.sh`)
- [x] 1.3 Implement interactive detection that treats `docker run -i` as interactive (stdin open) even without a TTY
- [x] 1.4 Implement fallback behavior when no command remains after parsing:
  - with `--no-block`: exit 0 after preparation
  - interactive: `exec /bin/bash`
  - non-interactive: `exec sleep infinity`
- [x] 1.5 Add explicit log lines for each branch (custom entrypoint, exec command, bash fallback, sleep fallback, no-block exit)
- [x] 1.6 Make internal runtime hook scripts quiet by default and verbose when enabled:
  - `src/pei_docker/project_files/installation/stage-1/internals/on-entry.sh`
  - `src/pei_docker/project_files/installation/stage-1/internals/on-first-run.sh`
  - `src/pei_docker/project_files/installation/stage-1/internals/on-every-run.sh`
  - `src/pei_docker/project_files/installation/stage-2/internals/on-entry.sh`
  - `src/pei_docker/project_files/installation/stage-2/internals/on-first-run.sh`
  - `src/pei_docker/project_files/installation/stage-2/internals/on-every-run.sh`

## 2. Custom `on_entry` Wrapper Generation

- [x] 2.1 Generate `generated/_custom-on-entry.sh` for each stage (empty when unset) and bake:
  - the configured script path
  - the config-specified args
  - forwarding of runtime args
  - quiet-by-default logging (print only when entrypoint verbose flag is enabled)
  (`src/pei_docker/config_processor.py`)
- [x] 2.2 Update stage-2 override selection:
  - stage-2 wrapper overrides stage-1 wrapper when both exist
  (`src/pei_docker/project_files/installation/stage-2/internals/entrypoint.sh`)
- [x] 2.3 Remove usage/generation of `internals/custom-entry-path` and `internals/custom-entry-args`
- [x] 2.4 Treat missing custom on-entry target scripts as hard errors (non-zero exit)
- [x] 2.5 Update all runtime hook wrapper scripts (generated via `_generate_script_text`) to be quiet by default and log only when verbose is enabled

## 3. Tests and Verification

- [x] 3.1 Add automated functional tests (manual trigger; heavy Docker build/run) under `tests/functional/<test-case>/...` covering:
  - tests are implemented under `tests/functional/entrypoint-non-tty-default-blocking/...`
  - tests MUST be opt-in/manual-trigger and are not executed by default `pytest` / `pixi run test`
  - tests build real stage-1/stage-2 Docker images and write artifacts under `tmp/entrypoint-non-tty-default-blocking-e2e/`
  - non-interactive no-command default → blocks (`sleep infinity`) and remains SSH-usable
  - SSH-first success criteria: users can log in via SSH and run installed tooling smoke commands
  - `--no-block` → exits
  - `--verbose` toggles runtime hook wrapper logging (default quiet)
  - `docker run -i` no-command → interactive bash fallback
  - `docker run image env` passthrough unchanged
  - custom entrypoint points to missing script → non-zero exit
- [x] 3.2 Manually verify stage-1 and stage-2 container behavior in:
  - `docker run -it ...` (bash)
  - `docker run -i ...` (bash)
  - `docker run ...` with no args (sleep)
  - `docker run ... env` (exec env)
  - `docker run ... --no-block` (exit)
- [x] 3.3 Run project checks (`pixi run test`, plus any targeted lint/type-check commands used in CI)
  - `pixi run test` executed and passed
  - `pixi run lint` executed; failed due to pre-existing repository-wide issues unrelated to this change
  - `pixi run type-check` executed; failed in this environment (`mypy: command not found`)

## 4. Documentation and Follow-up

- [x] 4.1 Update any user-facing docs/comments that mention unconditional bash fallback
- [x] 4.2 Ensure specs match final implementation behavior before archiving the change
