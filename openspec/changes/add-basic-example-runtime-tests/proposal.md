## Why

The packaged basic examples are the most direct expression of PeiDocker's core workflows, but today they are not covered by a systematic post-build runtime verification suite. We need real Docker-backed tests now so regressions in user creation, tool installation, runtime mounts, environment handling, and example-specific behavior are caught against the same examples users are told to copy.

## What Changes

- Add a heavy, pytest-driven functional test suite that builds and runs the packaged basic examples under `src/pei_docker/examples/basic/`, but only when explicitly requested.
- Verify each example from the perspective of the configured non-root user, including user existence, login/shell usability, expected runtime configuration, and availability of example-installed tools.
- Add per-example runtime assertions for the documented feature slices, including storage behavior, custom build hooks, env resolution, multi-user SSH, Pixi, Conda, and mirror/proxy-sensitive examples.
- Require robust teardown so each test run stops containers, removes volumes created by the example project, and removes the stage-1 and stage-2 images built for the scenario.
- Make proxy-sensitive example tests consume proxy settings from the invoking shell environment when present, and skip those tests when no relevant proxy environment is configured.
- Add concise operator documentation for prerequisites, explicit pytest invocation, conditional skips, and artifact/debug locations.

## Capabilities

### New Capabilities

- `basic-example-runtime-tests`: Defines the required Docker-backed runtime test coverage, execution model, environment-sensitive skips, and cleanup guarantees for the packaged basic examples.

### Modified Capabilities

- None.

## Impact

- Affected areas: `tests/functional/`, supporting test helpers/scripts, test fixtures, and developer testing documentation.
- Runtime dependencies for test execution: Docker daemon, Docker Compose plugin, pytest, SSH client tooling, and network access for examples that install tools from external repositories.
- Environment-sensitive dependencies: proxy-backed examples depend on relevant shell proxy variables being set to runnable host-reachable values; otherwise those tests are skipped.
- Test-runner impact: default fast test commands must continue to exclude this new pytest suite unless the developer opts in via an explicit command or marker/path selection.
- No production runtime behavior changes; this change adds verification coverage and execution guidance for the existing example set.
