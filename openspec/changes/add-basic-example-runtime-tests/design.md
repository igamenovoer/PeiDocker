## Context

PeiDocker's packaged basic examples are the clearest expression of the workflows the project asks users to trust, but the current automated coverage still stops short of proving that the examples remain correct as packaged assets. We have unit and regression tests for config processing plus one heavy Docker-backed entrypoint suite, but we do not yet automatically verify the full example path:

1. the docs page still matches the packaged example assets
2. the example can be copied into a generated project and configured successfully
3. the stage-2 image builds
4. the container starts
5. the documented users can log in and use the capability the example exists to demonstrate

The examples are not uniform smoke tests. Some are user-tooling scenarios (`pixi-environment`, `conda-environment`), some are infrastructure semantics (`host-mount`, `docker-volume`, `port-mapping`), and some are environment-sensitive (`proxy-setup`, `gpu-container`). The solution therefore needs more than "container starts" checks and more than static YAML validation.

## Goals / Non-Goals

**Goals:**
- Add a fast contract test lane that keeps `docs/examples/basic/*.md` aligned with the packaged example assets.
- Add a reproducible, opt-in pytest-driven Docker-backed runtime suite for the packaged basic examples.
- Build and run each example through the same `create` and `configure` workflow used by real users.
- Verify runtime behavior primarily from configured non-root user sessions, including login success, environment/setup correctness, and user-scoped tool availability where relevant.
- Isolate each run with unique project names, image tags, and free host ports so the suite is automatic and robust on real developer machines.
- Preserve the repository's documented configure-time versus compose-time environment semantics in the harness.
- Guarantee teardown of containers, volumes, and built images even after failures, while retaining artifacts for debugging.

**Non-Goals:**
- Changing production PeiDocker runtime behavior or the packaged example semantics.
- Moving Docker-heavy example tests into the default `pytest` / `pixi run test` path.
- Replacing pytest-native reporting with standalone shell-only orchestration.
- Treating root as the primary test subject for tool installation or login verification.
- Rewriting the example catalog or solving all example limitations by changing application code in this change.

## Decisions

1. **Two-lane verification model**
   - The change will introduce:
     - a fast Python test lane for docs/example contract checks
     - a heavy opt-in pytest functional lane for real Docker-backed runtime verification
   - This keeps cheap correctness checks close to the normal test path while preserving a realistic end-to-end suite for build and runtime behavior.
   - Alternative considered: a single heavy lane only. Rejected because docs/example drift is cheaper to catch before Docker work starts.

2. **Opt-in pytest runtime suite under `tests/functional/`**
   - The Docker-backed lane will live beside the existing entrypoint E2E suite, but it will be implemented as pytest tests and fixtures rather than as a standalone shell harness.
   - Execution remains explicit through both a raw pytest command and a dedicated Pixi task.
   - Alternative considered: default execution in normal pytest runs. Rejected because builds, SSH, proxy, and network installers are too slow and environment-sensitive.

3. **Manifest-driven scenario orchestration**
   - The runtime suite will define one explicit manifest entry per packaged basic example.
   - Each entry records:
     - example source path
     - extra files to copy
     - configured user(s) to verify
     - configure-time env inputs
     - compose-time env inputs
     - required capabilities such as proxy or GPU
     - dynamic host ports to allocate
     - scenario-specific assertion callbacks
   - Pytest parameterization will consume this manifest so each example appears as a distinct selectable test case.
   - Alternative considered: ad hoc standalone scripts per example. Rejected because orchestration and teardown would drift.

4. **SSH-first verification for non-root users**
   - User-facing assertions will run primarily through SSH logins to the configured non-root accounts.
   - This is deliberate: the examples already model SSH-driven usage, and SSH is the cleanest way to exercise login-time hooks such as Conda activation.
   - `docker exec` remains acceptable for orchestration and root-owned observability checks, but not as the primary replacement for user sessions.

5. **Run-scoped isolation includes host ports, not only names**
   - Each scenario run will use a unique temp project directory, unique image names, unique Compose project name, and dynamically allocated free host ports.
   - This is required because many examples hardcode host ports such as `2222` through `2234`, `8080`, and `3000-3002`, which would otherwise make the suite flaky on shared or already-in-use developer machines.
   - The harness will apply this isolation only to the copied project or its generated runtime inputs, never to the packaged source examples.

6. **Preserve `${...}` versus `{{...}}` semantics**
   - The harness will not flatten mixed configure-time and compose-time environment behavior by patching generated compose files after `configure`.
   - For mixed-mode examples such as `env-passthrough`, uniqueness and scenario control will come from controlled environment inputs:
     - configure-time values such as `PROJECT_NAME`
     - compose-time values such as `TAG` and `WEB_HOST_PORT`
   - This keeps the test aligned with the documented PeiDocker environment model instead of a harness-specific mutation path.

7. **Proxy-sensitive scenarios derive configuration from the invoking shell and assert concrete cleanup observables**
   - The proxy example will read `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and lowercase variants from the invoking shell.
   - If the detected proxy host is `127.0.0.1` or `localhost`, the harness will normalize it to `host.docker.internal` while preserving the port.
   - If no relevant proxy environment exists, the proxy scenario will be skipped with a clear reason.
   - Runtime cleanup will be asserted concretely:
     - non-root login shell does not retain global proxy vars when cleanup is enabled
     - APT proxy configuration file is absent when `keep_proxy_after_build` is false

8. **Per-example assertions prove the example promise, not just container liveness**
   - The suite will assert the smallest observable behavior that proves the example's purpose:
     - `minimal-ssh`: non-root login works
     - `gpu-container`: GPU config is present, and hardware-level visibility is checked only when the host runtime supports it
     - `host-mount`: host/container workspace linkage is observable
     - `docker-volume`: persisted data survives recreation
     - `custom-script`: build-hook side effect exists at runtime
     - `port-mapping`: declared host/container mappings work using temporary in-container listeners started by the harness
     - `proxy-setup`: invoking proxy settings are used for build and removed appropriately at runtime
     - `env-variables`: configure-time substitutions are concrete at runtime
     - `env-passthrough`: compose-time substitutions resolve at container start
     - `pixi-environment`: configured non-root user can run `pixi`, `python`, and the expected installed packages
     - `conda-environment`: configured non-root user gets login-time Conda usability
     - `multi-user-ssh`: multiple non-root users can log in; mixed-auth coverage includes verifying that the configured packaged public key is installed for the user even though the repo does not ship its matching private key
     - `apt-mirrors`: selected mirror configuration is visible in runtime APT files
   - Alternative considered: generic "container started" smoke checks only. Rejected because they do not prove the example's reason for existing.

9. **Hard teardown with artifact retention**
   - Each scenario will register cleanup state up front and use fixture finalizers to:
     - stop and remove compose services
     - remove example-created volumes
     - remove stage-1 and stage-2 images created for the scenario
   - Generated projects, compose files, command transcripts, and logs will be retained under `tmp/basic-example-runtime-e2e/`.
   - Alternative considered: ephemeral tempdirs only. Rejected because post-failure debugging would be much weaker.

10. **Expose both a Pixi task and a raw pytest command**
   - The suite will have a short Pixi task for standard invocation and a raw pytest command for targeted reruns and local debugging.
   - This matches the repo's existing pattern for heavy functional verification and keeps the official path discoverable.

## Risks / Trade-offs

- **[Risk] Long-running suite across 13 examples** → **Mitigation**: keep execution explicit, allow per-example selection, and design manifest-driven reruns.
- **[Risk] Network-installer flakiness** → **Mitigation**: preflight checks, bounded waits, clear skip/fail reasons, and artifact retention.
- **[Risk] Port collision flakiness** → **Mitigation**: dynamically allocate and propagate free host ports for SSH and service-port scenarios.
- **[Risk] Cleanup drift leaves stale images or volumes behind** → **Mitigation**: register resources early, centralize teardown, and make cleanup a required harness behavior.
- **[Risk] SSH readiness timing issues** → **Mitigation**: bounded retry loops with preserved logs and transcripts.
- **[Risk] Current packaged assets do not fully support end-to-end key-auth verification for `multi-user-ssh`** → **Mitigation**: verify packaged public-key installation explicitly and keep password login as the usable access path covered by the runtime suite until matching private-key coverage is intentionally added.

## Migration Plan

1. Add the fast docs/example contract tests.
2. Add the opt-in pytest runtime suite and invocation wiring.
3. Implement shared helpers for project creation, example overlay, env injection, port allocation, SSH readiness, and teardown.
4. Implement scenario assertions in groups: storage/env/tooling first, then proxy/GPU/mixed-auth edge cases.
5. Document invocation, prerequisites, conditional skips, artifact locations, and cleanup expectations.
6. Execute targeted opt-in runs locally and record verification notes and follow-up issues.

## Open Questions

- Should the fast docs/example contract lane validate literal YAML snippet equality for every docs page, or allow normalized semantic equivalence after parsing?
- For `multi-user-ssh`, do we want the current scope to stop at verifying password login plus packaged public-key installation, or should a later change add a dedicated end-to-end key-auth fixture with a matching private key?
