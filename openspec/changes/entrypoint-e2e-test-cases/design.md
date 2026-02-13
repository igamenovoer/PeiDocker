## Context

The prior change `entrypoint-non-tty-default-blocking` introduced several runtime branches in stage-1 and stage-2 entrypoints, including default-mode parsing, custom `on_entry` routing, and non-interactive fallback behavior. The agreed validation approach is a real Docker end-to-end matrix (not unit-level mocks) with SSH-first success criteria and explicit branch assertions.

These tests are intentionally heavy: they build images, run containers, inspect runtime state, and exercise SSH login. They must therefore be isolated from the default fast test suite and run only on explicit request.

## Goals / Non-Goals

**Goals:**
- Add reproducible functional tests for the discussed entrypoint matrices: default mode (`E01`-`E07`), custom `on_entry` (`C01`-`C06`), and signal handling (`S01`).
- Validate both stage-1 and stage-2 image behavior, including divergence-sensitive logic around custom wrapper precedence.
- Encode SSH-first liveness expectations for blocking branches and branch-specific log/process assertions.
- Ensure test artifacts (logs and command transcripts) are persisted under a dedicated tmp root for debugging.

**Non-Goals:**
- Changing entrypoint runtime behavior itself.
- Moving these heavy tests into mandatory default CI test paths.
- Reworking unrelated test architecture outside the new entrypoint functional coverage.

## Decisions

1. **Manual-trigger functional suite under `tests/functional/`**
   - We place this work in dedicated `tests/functional/<case>/` paths and gate execution behind explicit invocation so normal `pixi run test` stays fast and deterministic.
   - Alternative considered: integrating into default pytest runs. Rejected due to Docker/SSH dependency and runtime cost.

2. **Matrix-driven scenario implementation**
   - Each scenario ID (`E*`, `C*`, `S*`) maps to explicit setup, runtime invocation, and assertions to preserve traceability with the discussion document.
   - Alternative considered: collapsing scenarios into a small number of broad tests. Rejected because branch coverage would become ambiguous and harder to debug.

3. **Common helper layer for build/run/assert**
   - Shared helpers handle image build, container lifecycle, log capture, `/proc/1/cmdline` checks, and SSH smoke commands.
   - Alternative considered: per-test shell scripts only. Rejected due to duplicated orchestration logic and inconsistent assertions.

4. **Dedicated tmp artifact root**
   - Runtime outputs are written under `tmp/entrypoint-non-tty-default-blocking-e2e/` with subfolders for project outputs and logs to support post-failure diagnosis.
   - Alternative considered: temporary ephemeral directories only. Rejected because reproducibility and debugging are weaker.

5. **Stable, observable assertions over internals**
   - Assertions prioritize externally visible behavior: container running/exited state, expected log branch labels, command passthrough results, and SSH availability.
   - Alternative considered: relying on implementation-private shell details. Rejected to reduce brittleness across refactors.

## Risks / Trade-offs

- **[Risk] Docker environment variability** -> **Mitigation**: explicit preflight checks, bounded timeouts, and robust cleanup in teardown paths.
- **[Risk] SSH timing flakiness after container start** -> **Mitigation**: bounded retry loops with clear failure diagnostics in captured logs.
- **[Risk] Port collisions for SSH tests** -> **Mitigation**: allocate deterministic-but-parameterized host ports per test run and fail fast on conflicts.
- **[Risk] Long execution time** -> **Mitigation**: keep suite manual-triggered and provide targeted case selection for local debugging.

## Migration Plan

1. Add functional test directories, shared helpers, and baseline fixtures/configs.
2. Implement default-mode matrix cases for stage-1 and stage-2 images.
3. Implement custom `on_entry` and signal-handling cases.
4. Add run documentation and expected artifact locations.
5. Execute targeted manual runs and capture sample logs before marking tasks complete.

## Open Questions

- Which host-port allocation approach is preferred for parallel local runs (fixed range per run vs fully dynamic discovery)?
- Should the manual trigger path use a dedicated pytest marker, dedicated script entrypoint, or both for developer ergonomics?
