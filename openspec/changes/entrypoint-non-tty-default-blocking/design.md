## Context

Issue #9 reports that PeiDocker entrypoint fallback behavior is unsafe in non-interactive environments. Both stage-1 and stage-2 entrypoint scripts currently fall back to `/bin/bash` when no command is provided and no custom entrypoint applies. In Kubernetes and similar runtimes, stdin is often non-interactive, so bash exits immediately and PID 1 exits, causing the container to stop unexpectedly even though sshd may have been started as a background service.

Relevant scripts:
- `src/pei_docker/project_files/installation/stage-1/internals/entrypoint.sh`
- `src/pei_docker/project_files/installation/stage-2/internals/entrypoint.sh`

## Goals / Non-Goals

**Goals:**
- Make default no-command behavior safe for non-interactive environments by keeping the container alive.
- Preserve existing `docker run image <cmd...>` passthrough behavior (no need to learn a new CLI).
- Add a minimal entrypoint CLI for default behavior control (`--no-block`, `-- <cmd...>`).
- Treat `docker run -i` as interactive (stdin open) even without a TTY.
- Rework `custom.on_entry` wiring to use generated wrapper scripts under `generated/` and pass all runtime args through unchanged.
- Apply the same policy to both stage-1 and stage-2 entrypoints, including stage-2 override semantics for custom entrypoints.

**Non-Goals:**
- Redesigning entrypoint lifecycle hooks (`on-entry`, `on-first-run`, `on-every-run`).
- Replacing the default model with foreground `sshd -D` in this change.
- Introducing a broad set of entrypoint options beyond what's needed for this bug fix.

## Decisions

### Decision 1: Always prepare before handing off
Entrypoints always:
1) run their `on-entry.sh` tasks (stage-2 runs stage-1 then stage-2),
2) start ssh if installed,
then choose one of: custom entrypoint, user command, or default fallback.

Rationale:
- Ensures consistent initialization regardless of how the container is started.

### Decision 2: Custom `on_entry` uses generated wrapper scripts
Instead of runtime parsing of `custom-entry-path` and `custom-entry-args`, config processing will generate a wrapper script (like other lifecycle hooks):
- Stage-1: `$PEI_STAGE_DIR_1/generated/_custom-on-entry.sh`
- Stage-2: `$PEI_STAGE_DIR_2/generated/_custom-on-entry.sh`

The wrapper script bakes the configured script path and its config-specified args, and forwards runtime args.

Forwarding order:
- Invoke the target as `bash "<target-script>" <baked-config-args> "$@"` (baked args first, runtime args appended).

Unset behavior:
- When `custom.on_entry` is not configured for a stage, the generated wrapper script should be empty (size 0) so entrypoints can reliably detect whether a custom entrypoint applies (for example using `-s`).

Selection:
- Stage-2 wrapper overrides stage-1 wrapper if both exist.
- If a wrapper applies but the target script is missing, treat it as an error (exit non-zero).

Rationale:
- Keeps entrypoint runtime logic simple (no argument precedence semantics in entrypoint).
- Matches how other custom hooks are implemented (generated wrapper scripts).

### Decision 3: Entrypoint options are only parsed in default mode
When no custom entrypoint wrapper applies, entrypoint interprets argv as follows:
- If the first arg does **not** start with `--`, treat the entire argv as a user command and `exec "$@"`.
- If the first arg **does** start with `--`, parse entrypoint options until `--`:
  - Supported now: `--no-block` (flag).
  - Supported now: `--verbose` (flag) to enable verbose logging in runtime hook wrappers and preparation scripts.
  - Future options may use `--key value` and `--flag` form.
  - Unknown `--*` options are errors (exit non-zero).
  - The command to `exec` (if any) is everything after `--`.

Rationale:
- Preserves existing UX while enabling explicit control over default behavior.

### Decision 3.1: `--verbose` controls runtime hook wrapper logging
By default, runtime hook wrappers and preparation scripts SHOULD avoid noisy "Executing ..." logs.

When `--verbose` is specified (in default-mode CLI), entrypoint will export a verbosity environment variable
before running preparation steps so that runtime scripts can print call-site logs.

Implementation notes:
- Prefer a single exported variable (for example `PEI_ENTRYPOINT_VERBOSE=1`) that is checked by:
  - stage `internals/on-entry.sh`
  - generated hook wrapper scripts under `generated/` (including `_custom-on-entry.sh`)
- The entrypoint should set this variable as early as possible, before calling `on-entry.sh`.

### Decision 4: Interactive detection includes `docker run -i`
Default fallback mode (no custom entrypoint and no user command):
- Consider the runtime “interactive” if stdin is a TTY (`[ -t 0 ]`) **or** stdin is open (not `/dev/null`), so `docker run -i` drops into `/bin/bash`.

Implementation note:
- One robust check is `readlink /proc/$$/fd/0` and treating `/dev/null` as closed stdin.

Rationale:
- Matches expected behavior for `-i` (stdin open) even without a terminal.

### Decision 5: Fallback policy and `--no-block`
After preparation, if there is still no command to exec:
- If `--no-block` is set: log and exit 0.
- Else if interactive: `exec /bin/bash`.
- Else: `exec sleep infinity`.

Rationale:
- Minimal fix for K8s non-interactive defaults while providing a clear opt-out.

### Decision 6: Logging
Entrypoint logs the chosen branch (custom entrypoint, exec command, bash fallback, sleep fallback, no-block exit) to make behavior obvious in CI/K8s logs.

## Risks / Trade-offs

- **Risk: `sleep infinity` compatibility on some minimal images** → Mitigation: use Ubuntu base behavior already used by project templates; if needed, document acceptable equivalent blocking command.
- **Risk: subtle divergence between stage-1 and stage-2 scripts** → Mitigation: implement equivalent fallback logic in both scripts and verify both paths.
- **Trade-off: still not running sshd as PID 1** → Accepted to keep fix minimal and focused on issue #9.
- **Trade-off: commands that start with `--` require `-- -- <cmd...>` style in default-mode CLI** → Accepted as an edge case.

## Migration Plan

1. Generate `_custom-on-entry.sh` wrappers (empty when unset) and stop using the `custom-entry-args` file approach.
2. Update stage-1 and stage-2 entrypoint scripts to:
   - prefer custom wrapper (stage-2 overrides stage-1),
   - implement default-mode entrypoint CLI parsing and fallback behavior,
   - use `exec` for all hand-offs and fallback processes.
3. Verify behavior in:
   - interactive run (`docker run -it ...`) → bash
   - stdin-open run (`docker run -i ...`) → bash
   - non-interactive run with no args (`docker run ...`) → sleep infinity
   - runtime command provided (`docker run ... env`) → exec env
   - explicit opt-out (`docker run ... --no-block`) → exit

Rollback:
- Revert the entrypoint script changes if unexpected runtime regressions appear.

## Open Questions

- None.
