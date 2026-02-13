## Why

The `entrypoint-non-tty-default-blocking` change introduces multiple runtime branches that are hard to validate with unit tests alone. We need reproducible end-to-end Docker tests now to prevent regressions before archiving and future refactors.

## What Changes

- Add a heavy, manually triggered functional test suite for entrypoint runtime behavior under `tests/functional/`.
- Cover stage-1 and stage-2 image behavior for the discussed default-mode matrix (`E01`-`E07`), custom `on_entry` matrix (`C01`-`C06`), and signal handling (`S01`).
- Add reusable test helpers/config fixtures for image build, container orchestration, runtime assertions, and SSH smoke validation.
- Add concise operator documentation for how to run the suite and where runtime artifacts/logs are captured.

## Capabilities

### New Capabilities

- `entrypoint-e2e-functional-tests`: Defines required real-Docker entrypoint test coverage, execution model, and pass/fail expectations.

### Modified Capabilities

- None.

## Impact

- Affected areas: `tests/functional/`, supporting test helpers/scripts, and related docs for manual test execution.
- Runtime dependencies for test execution: Docker daemon, ability to build images, and SSH access tooling used by test harness scripts.
- No production runtime behavior changes; this change adds verification coverage and execution guidance.
