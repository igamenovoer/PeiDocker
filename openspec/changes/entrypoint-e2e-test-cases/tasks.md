## 1. Functional Test Harness Setup

- [x] 1.1 Create or extend `tests/functional/entrypoint-non-tty-default-blocking/` with dedicated fixtures/config for stage-1 and stage-2 image build/run flows.
- [x] 1.2 Implement shared helper utilities for container lifecycle, log/transcript capture, `/proc/1/cmdline` assertions, SSH smoke execution, and teardown cleanup.
- [x] 1.3 Ensure the entrypoint E2E suite is manual-trigger only (not part of default `pytest` / `pixi run test`) and provide a stable invocation path.

## 2. Scenario Matrix Implementation

- [x] 2.1 Implement default-mode matrix tests `E01`-`E07` for both stage images, including branch log checks, liveness/exit behavior, and command passthrough semantics.
- [x] 2.2 Implement custom `on_entry` matrix tests `C01`-`C06`, covering stage precedence, baked-arg ordering, runtime arg forwarding, and missing-target hard-failure behavior.
- [x] 2.3 Implement signal-handling test `S01` to verify non-interactive blocking fallback exits promptly after `SIGTERM`.
- [x] 2.4 Add SSH-first assertions for blocking branches to validate login success and minimal smoke commands after container startup.

## 3. Artifacts, Documentation, and Verification

- [x] 3.1 Persist test outputs under `tmp/entrypoint-non-tty-default-blocking-e2e/` with clear `project/`, `logs/`, and optional `images/` structure.
- [x] 3.2 Add or update user-facing test documentation describing prerequisites, manual run commands, case selection, and artifact locations.
- [x] 3.3 Execute the manual entrypoint E2E suite for stage-1 and stage-2 paths, then record verification notes and any known follow-up issues.
  - Executed on 2026-02-13: `bash tests/functional/entrypoint-non-tty-default-blocking/run.bash`
  - Verified passing coverage for `E01`-`E07` (stage-1/stage-2) and `C01`-`C06` (custom wrapper matrix).
  - Known follow-up issue: `S01` fails on both stage images because `docker kill --signal TERM` does not stop PID1 `sleep infinity` within timeout in current runtime behavior.
  - Reproduced follow-up issue with targeted command: `bash tests/functional/entrypoint-non-tty-default-blocking/run.bash --cases S01`.
