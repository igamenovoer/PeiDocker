## 1. Fast Docs/Example Contract Lane

- [x] 1.1 Add Python tests that map each page under `docs/examples/basic/` to its packaged example under `src/pei_docker/examples/basic/`.
- [x] 1.2 Validate that documented example source paths and required supporting files exist for each packaged example.
- [x] 1.3 Add docs/example content checks for the basic catalog, including YAML snippet parity or normalized semantic equivalence for the documented config blocks.

## 2. Runtime Suite Foundation

- [x] 2.1 Create a new pytest-based functional test root for basic example runtime validation under `tests/functional/`.
- [x] 2.2 Register the suite behind explicit pytest selection so default fast test commands do not execute it automatically.
- [x] 2.3 Add a dedicated Pixi task and document the raw pytest command for the heavy suite.
- [x] 2.4 Implement a manifest-driven scenario model that records example source paths, copied extra files, users, env inputs, capabilities, dynamic ports, and assertion callbacks.
- [x] 2.5 Implement shared fixtures/helpers for temp project creation, example overlay, run-scoped image naming, Compose project naming, free host-port allocation, and artifact directory setup.
- [x] 2.6 Implement centralized teardown that always attempts `docker compose down`, volume cleanup, and stage-1/stage-2 image removal for each scenario.

## 3. Runtime Access and Environment Helpers

- [x] 3.1 Implement SSH readiness and login helpers for executing assertions as configured non-root users.
- [x] 3.2 Implement common assertion helpers for shell usability, file persistence, runtime environment inspection, APT config inspection, and host-side connectivity checks.
- [x] 3.3 Implement helper support for temporary in-container listeners used by infrastructure-only scenarios such as `port-mapping`.
- [x] 3.4 Implement proxy-environment discovery from the invoking shell, including loopback-to-host normalization and conditional skip behavior when no relevant proxy env vars are set.
- [x] 3.5 Implement helper support that preserves configure-time `${...}` versus compose-time `{{...}}` behavior through controlled environment injection rather than generated-compose rewrites.

## 4. Example Scenario Coverage

- [x] 4.1 Implement runtime scenarios for `minimal-ssh`, `host-mount`, `docker-volume`, and `custom-script`.
- [x] 4.2 Implement runtime scenarios for `env-variables`, `env-passthrough`, `port-mapping`, and `apt-mirrors`.
- [x] 4.3 Implement runtime scenarios for `pixi-environment` and `conda-environment`, ensuring tool checks run as configured non-root users rather than root.
- [x] 4.4 Implement runtime scenarios for `proxy-setup` and `gpu-container`, including capability-gated behavior and explicit runtime cleanup assertions.
- [x] 4.5 Implement runtime scenarios for `multi-user-ssh`, covering multiple non-root logins and verification that the configured packaged public key is installed for the relevant user.
- [x] 4.6 Ensure scenario selection supports running all examples or a targeted subset for local debugging.

## 5. Documentation and Verification

- [x] 5.1 Update developer testing documentation with prerequisites, explicit pytest and Pixi invocation, conditional proxy/GPU behavior, artifact locations, and cleanup expectations.
- [x] 5.2 Execute targeted opt-in pytest runs for the basic example runtime suite and record verification notes, known skips, or follow-up issues discovered during execution.
