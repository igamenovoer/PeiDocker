## Entrypoint E2E Test Cases (Real Docker Images)

Date: 2026-02-13

This note captures an end-to-end test matrix for the change `entrypoint-non-tty-default-blocking`.
These tests are meant to be run against real, freshly-built Docker images (stage-1 and stage-2),
and validate the required entrypoint branches and CLI semantics.

Reference spec:
- `openspec/changes/entrypoint-non-tty-default-blocking/specs/entrypoint-default-runtime-behavior/spec.md`

### Usage Model and Success Criteria (SSH-First)

Assumptions for intended default usage:

- For this project, the image baseline always includes SSH service support (`sshd` managed by entrypoint).
- Images are expected to run long-lived with `sshd` available (started by entrypoint).
- The primary way users interact with the container is SSH login from another host.
- `docker exec` / `docker run image <cmd...>` is considered secondary (mostly for CI/debug).

Therefore the primary success criteria for this change is:

- A container started with no runtime command in a non-interactive context keeps running (does not exit),
  and SSH users can log in successfully.
- After SSH login, users can access and use whatever tools/scripts were installed/configured by the
  stage installation and runtime hooks (as applicable to the chosen test config).

### Tmp Target

Use a dedicated tmp root so artifacts are easy to inspect and clean up:

- `tmp/entrypoint-non-tty-default-blocking-e2e/`
  - `project/`: generated PeiDocker project (create/configure output)
  - `logs/`: captured `docker logs` outputs and command transcripts
  - `images/`: optional `docker image save` tarballs for reproducibility

Suggested layout:

```text
tmp/entrypoint-non-tty-default-blocking-e2e/
  project/
  logs/
  images/
```

### Where To Implement These Tests

These are **heavy functional tests** (they must build real Docker images and run containers), so they
should be implemented as on-demand tests under:

- `tests/functional/<test-case>/...`

Guidance:

- Keep each test case self-contained in its own directory (config, helper scripts, expected outputs).
- Do not run these tests as part of the default unit-test suite (`pytest` / `pixi run test`); run them
  only when explicitly requested (manual trigger).

### Docker Runtime Test Cases (Default Mode)

Run each case against both stage-1 and stage-2 images to catch divergence.

- `E01` Non-interactive, no args, no custom `on_entry`
  - Expected: container stays up; PID1 is blocking (`sleep infinity`); logs include "sleep fallback";
    `sshd` is started and SSH login works.
- `E02` `-i` (stdin open), no TTY, no args, no custom `on_entry`
  - Expected: container stays up; PID1 is `bash`; logs include "bash fallback"; `sshd` is started and
    SSH login works.
- `E03` `--no-block` with no command
  - Expected: container exits quickly with status `0`; logs include "no-block exit".
- `E04` Passthrough command (argv does not start with `--`), e.g. `docker run image env`
  - Expected: exits `0`; entrypoint execs the command unchanged; logs include "exec user command".
- `E05` Default-mode options + command, e.g. `docker run image --verbose -- env`
  - Expected: runs the command after `--`; `PEI_ENTRYPOINT_VERBOSE=1` (or equivalent) is set early;
    verbose hook logs appear.
- `E06` Unknown option in default mode, e.g. `docker run image --wat`
  - Expected: exit non-zero with a clear error message (unknown `--*` option).
- `E07` Preparation runs before handoff
  - Use a short-exit path (e.g. `--no-block` or `env`) and validate stage preparation ran (for example:
    stage signature files in `/pei-init/` if those are still the canonical markers).

Implementation-friendly checks:
- PID1 branch: inspect `/proc/1/cmdline` (works without requiring `ps`).
- Liveness: run detached and assert `docker inspect` shows running for blocking branches.
- SSH-first validation: map a host port and verify login succeeds, then run a minimal smoke command in
  the SSH session (e.g. `whoami`, `env`, `ls`, and a tool expected by the config).

### Custom `on_entry` Test Cases

These assume the new wrapper-based custom `on_entry` wiring:
`$PEI_STAGE_DIR_{1,2}/generated/_custom-on-entry.sh` (empty file when unset).

- `C01` Stage-1 custom `on_entry` set
  - Expected: branch is "custom"; runtime args are forwarded unchanged to wrapper/target; entrypoint does
    not parse default-mode options.
- `C02` Baked args order
  - Expected: target sees `<baked-config-args> <runtime-args>` (baked args first, runtime args appended).
- `C03` Stage-2 overrides stage-1
  - Expected: when both wrappers exist, stage-2 custom runs and stage-1 custom is ignored.
- `C04` Stage-1 fallback on stage-2 image
  - Expected: when stage-2 wrapper is empty/unset and stage-1 wrapper is set, stage-1 custom runs.
- `C05` Missing custom target script
  - Expected: hard error at runtime; logs an error and exits non-zero (no bash/sleep fallback).
- `C06` "No parsing under custom" regression guard
  - Scenario: custom `on_entry` configured; run `docker run image --no-block`
  - Expected: entrypoint does not exit early; `--no-block` is forwarded as a runtime arg to the custom
    script (and may be rejected/handled by that script).

### Signal Handling (Kubernetes Relevance)

- `S01` Non-interactive fallback blocks via `exec`
  - Scenario: start container in sleep-fallback mode; send `SIGTERM`.
  - Expected: container exits promptly (PID1 receives the signal; no signal swallowing).
