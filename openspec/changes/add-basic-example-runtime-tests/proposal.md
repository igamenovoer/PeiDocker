## Why

The packaged basic examples are the closest thing PeiDocker has to executable user-facing contracts, but right now they are not verified end-to-end in an automatic way. We have narrow regression tests and one heavy entrypoint suite, but we still do not automatically prove that:

- the example docs stay aligned with the packaged example assets
- each example can be turned into a real project and built successfully
- the documented users can actually log in and use the capability the example exists to demonstrate

That leaves a gap between "the repo contains an example" and "the example still works as a user would run it."

## What Changes

- Add a fast Python test lane that checks `docs/examples/basic/*.md` against the packaged example assets under `src/pei_docker/examples/basic/`, including extra supporting files where applicable.
- Add a heavy, pytest-driven Docker-backed functional suite that creates projects from the packaged basic examples, builds them, starts them, and verifies runtime behavior.
- Verify example behavior primarily from configured non-root user sessions over SSH, including login shell usability, user-scoped tool availability, and example-specific runtime observables.
- Make the runtime harness fully automatic once invoked: it allocates run-scoped project names, image tags, and free host ports, applies environment inputs, captures artifacts, and performs teardown even on failure.
- Make proxy-sensitive scenarios derive proxy settings from the invoking shell environment and assert concrete runtime cleanup behavior for both shell proxy env vars and APT proxy files.
- Preserve the documented `${...}` versus `{{...}}` semantics in mixed environment examples instead of flattening or rewriting generated compose artifacts after configuration.
- Add explicit operator documentation and invocation paths, including a raw pytest command and a dedicated Pixi task for the heavy suite.

## Capabilities

### New Capabilities

- `basic-example-runtime-tests`: Defines the required example-verification coverage, including docs/example contract checks, Docker-backed runtime coverage, environment-sensitive handling, and cleanup guarantees for the packaged basic examples.

### Modified Capabilities

- None.

## Impact

- Affected areas: `tests/`, `tests/functional/`, supporting helpers/fixtures, `docs/developer/testing.md`, and the OpenSpec artifacts for example verification.
- Runtime dependencies for the heavy suite: Docker daemon, Docker Compose plugin, pytest, OpenSSH client tooling, `sshpass`, and network access for examples that install tools from external repositories.
- Environment-sensitive dependencies: proxy-backed examples depend on relevant shell proxy variables being set to reachable values; GPU hardware assertions are capability-gated on host runtime availability.
- Test-runner impact: default fast test commands must continue to exclude the Docker-heavy suite, while the docs/example contract lane may remain in the normal Python test path.
- No production runtime behavior changes; this change adds verification coverage and execution guidance for the existing packaged examples.
