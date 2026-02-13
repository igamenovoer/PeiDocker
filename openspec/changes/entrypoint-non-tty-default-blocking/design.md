## Context

Issue #9 reports that PeiDocker entrypoint fallback behavior is unsafe in non-TTY environments. Both stage-1 and stage-2 entrypoint scripts currently fall back to `/bin/bash` when no command is provided and no custom entrypoint applies. In Kubernetes and similar runtimes, stdin is often non-interactive, so bash exits immediately and PID 1 exits, causing the container to stop unexpectedly even though sshd may have been started.

Relevant scripts:
- `src/pei_docker/project_files/installation/stage-1/internals/entrypoint.sh`
- `src/pei_docker/project_files/installation/stage-2/internals/entrypoint.sh`

## Goals / Non-Goals

**Goals:**
- Make default no-command behavior safe for non-TTY environments by keeping the container alive.
- Preserve interactive (`-it`) behavior for users who expect shell startup.
- Preserve existing command precedence and custom entrypoint behavior.
- Apply the same policy to both stage-1 and stage-2 entrypoints.

**Non-Goals:**
- Redesigning entrypoint lifecycle hooks (`on-entry`, `on-first-run`, `on-every-run`).
- Replacing the default model with foreground `sshd -D` in this change.
- Changing custom entrypoint argument parsing semantics.

## Decisions

### Decision 1: TTY-aware fallback policy
When the entrypoint reaches default fallback mode (no runtime command and no valid custom entrypoint):
- If stdin is a TTY (`[ -t 0 ]`), run `exec /bin/bash`.
- If stdin is not a TTY, run `exec sleep infinity`.

Rationale:
- Keeps current interactive UX unchanged.
- Prevents immediate container exit in non-interactive runtimes.

Alternative considered:
- Always running `sshd -D -e` when SSH is enabled.
  - Rejected for now because it changes the default process model and introduces broader behavioral impact than needed for this bug fix.

### Decision 2: Use `exec` in default terminal/blocking branch
Use `exec` for default fallback commands so PID 1 is replaced directly by the selected process.

Rationale:
- Ensures clean signal handling and consistent container lifecycle behavior.
- Avoids leaving a shell wrapper process as PID 1 in fallback mode.

### Decision 3: Preserve command and custom-entry precedence
No change to precedence rules:
1. Runtime command args (`$@`) if provided.
2. Valid custom entrypoint script with existing argument logic.
3. TTY-aware default fallback policy.

Rationale:
- Minimizes regression risk while addressing the non-TTY exit bug.

## Risks / Trade-offs

- **Risk: `sleep infinity` compatibility on some minimal images** → Mitigation: use Ubuntu base behavior already used by project templates; if needed, document acceptable equivalent blocking command.
- **Risk: subtle divergence between stage-1 and stage-2 scripts** → Mitigation: implement equivalent fallback logic in both scripts and verify both paths.
- **Trade-off: still not running sshd as PID 1** → Accepted to keep fix minimal and focused on issue #9.

## Migration Plan

1. Update stage-1 and stage-2 entrypoint scripts with TTY-aware default fallback logic.
2. Verify behavior in:
   - interactive run (`docker run -it ...`)
   - non-interactive run with no args (`docker run ...`)
   - runtime command provided (`docker run ... env`)
3. Update any user-facing docs/comments that mention unconditional shell fallback.

Rollback:
- Revert the entrypoint script changes if unexpected runtime regressions appear.

## Open Questions

- Should future iterations offer a configurable non-TTY fallback mode (for example `sleep infinity` vs `sshd -D`)?
