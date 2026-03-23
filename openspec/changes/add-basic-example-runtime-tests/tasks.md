## 1. Functional Suite Foundation

- [ ] 1.1 Create a new pytest-based functional test root for basic example runtime validation under `tests/functional/`.
- [ ] 1.2 Register the suite behind explicit pytest selection so default fast test commands do not execute it automatically.
- [ ] 1.3 Implement shared pytest fixtures/helpers for temp project creation, example overlay, run-scoped image tag rewriting, compose project naming, and artifact directory setup.
- [ ] 1.4 Implement centralized teardown that always attempts `docker compose down`, volume cleanup, and stage-1/stage-2 image removal for each scenario.
- [ ] 1.5 Add a stable explicit-request invocation path (documented pytest command and, if chosen, Pixi task) without wiring the suite into the default fast test command.

## 2. Runtime Access and Environment Helpers

- [ ] 2.1 Implement SSH readiness and login helpers for executing assertions as configured non-root users.
- [ ] 2.2 Implement common assertion helpers for user existence, shell usability, file persistence, host-side port checks, and runtime environment inspection.
- [ ] 2.3 Implement proxy-environment discovery from the invoking shell, including conditional skip behavior when no relevant proxy env vars are set.
- [ ] 2.4 Implement proxy host normalization so loopback proxy env values are rewritten to a host-reachable address for container builds and runtime checks.

## 3. Example Scenario Coverage

- [ ] 3.1 Implement runtime scenarios for `minimal-ssh`, `gpu-container`, `host-mount`, `docker-volume`, `custom-script`, and `port-mapping`.
- [ ] 3.2 Implement runtime scenarios for `env-variables`, `env-passthrough`, `proxy-setup`, and `apt-mirrors`.
- [ ] 3.3 Implement runtime scenarios for `pixi-environment`, `conda-environment`, and `multi-user-ssh`, ensuring tool checks run as configured non-root users rather than root.
- [ ] 3.4 Ensure scenario selection supports running all examples or a targeted subset for local debugging.

## 4. Documentation and Verification

- [ ] 4.1 Update developer testing documentation with prerequisites, explicit pytest run commands, conditional proxy behavior, artifact locations, and cleanup expectations.
- [ ] 4.2 Execute targeted opt-in pytest runs for the basic example runtime suite and record verification notes, known skips, or follow-up issues discovered during execution.
