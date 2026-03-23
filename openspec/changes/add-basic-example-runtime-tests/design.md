## Context

PeiDocker's packaged basic examples are the closest thing the repository has to an executable contract for core user workflows. The current automated coverage is valuable but narrow: it focuses on specific regressions in config processing plus one manual Docker-backed entrypoint suite. That leaves a gap between "the example config exists" and "the example actually builds, runs, creates the expected users, and makes the expected tools usable from those users' login sessions."

This change adds another heavy functional lane. It must stay out of the default fast test path, but it also must be automatic in structure: pytest should drive collection, fixtures, assertions, and reporting even though execution remains opt-in. The examples still need to be turned into real projects, built into real images, started as real containers, and checked from non-root user sessions. Several examples are also environment-sensitive:

- `conda-environment` relies on login-time activation, so verification must exercise a real login path.
- `proxy-setup` must follow the proxy settings available in the invoking shell rather than a hardcoded local assumption, and must skip when no proxy environment is available.
- `host-mount` and `docker-volume` need observable persistence behavior across the host/container boundary.
- `pixi-environment` and `multi-user-ssh` need user-scoped tool checks rather than root-only checks.

## Goals / Non-Goals

**Goals:**
- Add a reproducible, opt-in pytest-driven Docker-backed runtime suite for the packaged basic examples.
- Build and run each example through the same `create` and `configure` workflow used by real users.
- Verify runtime behavior from configured non-root users, including login success, expected environment/setup, and availability of example-installed tools.
- Add per-example feature assertions for storage, runtime mounts, custom build hooks, env resolution, multi-user access, Pixi, Conda, and mirror/proxy behavior.
- Guarantee teardown of containers, volumes, and built images even after failures.
- Capture logs and generated project artifacts under a dedicated tmp root for debugging.

**Non-Goals:**
- Changing production PeiDocker runtime behavior or example semantics.
- Moving Docker-heavy example tests into the default `pytest` / `pixi run test` path.
- Replacing the suite with standalone shell-only orchestration that bypasses pytest fixtures and reporting.
- Treating root as the primary test subject for tool installation or login verification.
- Replacing narrow unit/regression tests that already validate config-processing edge cases.

## Decisions

1. **Opt-in pytest suite under `tests/functional/`**
   - The new suite will live beside the existing entrypoint E2E lane, but it will be implemented as pytest tests and fixtures rather than only as ad hoc shell scripts.
   - Execution remains explicit: default fast test commands must exclude this suite, while a documented pytest command (and optionally a Pixi task that delegates to pytest) runs it on request.
   - This preserves pytest-native reporting and selective reruns without forcing Docker/network-heavy work into the common local path.
   - Alternative considered: integrate into default pytest runs. Rejected because image builds, SSH sessions, and network-dependent installers are too slow and environment-sensitive.
   - Alternative considered: standalone shell-only harness. Rejected because it weakens fixture reuse, test selection, and pytest-native reporting.

2. **Example-manifest-driven orchestration inside pytest**
   - The suite will define one explicit manifest entry per basic example. Each entry records:
     - example source path
     - selected non-root user(s)
     - required env setup before `configure` or `docker compose up`
     - runtime assertions to execute
     - conditional skip rules (for example proxy-sensitive checks)
   - Pytest parameterization will consume this manifest so each example appears as a distinct selectable test case.
   - This preserves one-to-one traceability with the example catalog and avoids hardcoding scenario logic deep inside generic helper code.
   - Alternative considered: ad hoc per-example standalone scripts. Rejected because shared orchestration, cleanup, and reporting would drift.

3. **SSH-first verification for non-root users**
   - User-facing assertions will be executed primarily through SSH logins to the configured non-root accounts.
   - This is deliberate: all basic examples already configure SSH, and SSH exercises the same login-time behavior that users rely on, including `on_user_login` hooks such as Conda activation.
   - `docker exec` remains acceptable for orchestration or root-owned observability checks, but not as the primary substitute for user-session assertions.
   - Alternative considered: verify everything via `docker exec su - <user> -c ...`. Rejected because it weakens login-path coverage and risks missing shell/session initialization behavior.

4. **Run-scoped project names and image tags**
   - Each example run will create its own temp project directory and rewrite output image names to unique, run-scoped tags before build.
   - Compose project names will likewise be isolated per scenario to prevent container, network, and volume collisions across repeated runs.
   - Alternative considered: reuse the example's fixed image names like `pei-example-pixi:stage-2`. Rejected because stale images and concurrent local runs would contaminate results and teardown.

5. **Hard teardown with artifact retention**
   - Each scenario will register cleanup state up front and use trap/finalizer paths to:
     - stop and remove compose services
     - remove example-created volumes
     - remove stage-1 and stage-2 images created for the scenario
   - Pytest finalizers/fixture teardown will be the primary cleanup path, with shell traps only where subprocess wrappers need them.
   - Logs, generated project files, and host-side test directories will be retained under `tmp/basic-example-runtime-e2e/` so failures remain inspectable.
   - Alternative considered: ephemeral tempdirs only. Rejected because post-failure debugging would be much weaker.

6. **Proxy-sensitive examples derive configuration from the invoking shell**
   - The proxy example will not trust a baked local assumption like `127.0.0.1:7890`. Instead, the harness will inspect the invoking shell's proxy environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, lowercase variants), derive the runtime proxy address/port, and inject that into the copied example project.
   - If the detected proxy host is `127.0.0.1` or `localhost`, the harness will rewrite it to `host.docker.internal` while preserving the port, because the generated compose already provides the required host-gateway mapping.
   - If no relevant proxy environment exists, proxy-sensitive scenarios will be skipped with a clear reason.
   - Alternative considered: always use the example's checked-in proxy address. Rejected because it would not reflect the user's requested test semantics and would fail on hosts without that exact setup.

7. **Per-example assertions focus on example promises**
   - The suite will assert the smallest runtime behavior that proves the example's documented feature:
     - `minimal-ssh`: non-root login works
     - `gpu-container`: container starts and exposes expected GPU-related runtime configuration to the non-root user; hardware-specific checks can be gated on host capability
     - `host-mount`: host/container workspace linkage is observable
     - `docker-volume`: persisted data survives container recreation
     - `custom-script`: build hook side effect exists at runtime
     - `port-mapping`: declared service ports are observable from the host
     - `proxy-setup`: build uses invoking proxy settings, runtime proxy cleanup behavior is observable
     - `env-variables`: configure-time substitutions are concrete at runtime
     - `env-passthrough`: compose-time values resolve at container start
     - `pixi-environment`: configured non-root user can run `pixi` and use installed packages
     - `conda-environment`: configured non-root user gets login-time Conda usability
     - `multi-user-ssh`: multiple non-root users can log in and use their sessions
     - `apt-mirrors`: configured mirror selection is visible in container APT configuration
   - Alternative considered: generic "container started" smoke checks only. Rejected because they do not prove the example's reason for existing.

8. **Explicit pytest opt-in instead of default collection execution**
   - The suite will be marked and documented so developers can run it explicitly via pytest selection, such as a dedicated marker, path, or Pixi task that invokes pytest for the functional example suite.
   - Default fast test commands must continue to exclude this marker/path by default.
   - Alternative considered: relying only on naming patterns that avoid default collection. Rejected because marker/path-based explicit invocation is clearer and easier to document.

## Risks / Trade-offs

- **[Risk] Long-running suite across 13 examples** → **Mitigation**: keep execution manual-triggered, allow per-example selection, and keep helper reuse high so local reruns can target only failing scenarios.
- **[Risk] Network-installer flakiness** → **Mitigation**: preflight checks, clear logging, bounded waits, and explicit skip/fail reasons for proxy-sensitive or host-sensitive scenarios.
- **[Risk] Cleanup drift leaves stale images/volumes behind** → **Mitigation**: register run-scoped image/container names early, centralize teardown, and make image removal part of the required success criteria for the harness.
- **[Risk] SSH timing and login readiness flakiness** → **Mitigation**: use bounded retry loops for SSH readiness and preserve container logs/transcripts when retries fail.
- **[Risk] Host-dependent behavior for proxy and GPU scenarios** → **Mitigation**: derive proxy behavior from shell env, document skip behavior clearly, and gate hardware-specific GPU checks behind host capability detection.

## Migration Plan

1. Add a new pytest functional test root for basic example runtime validation plus marker/task wiring that keeps it opt-in.
2. Implement the example manifest and common project/build/run/SSH/cleanup helpers.
3. Add per-example runtime assertions, starting with SSH/storage/env/tooling coverage and then proxy-sensitive handling.
4. Document pytest invocation, prerequisites, conditional skips, and artifact locations.
5. Execute targeted opt-in pytest runs locally and record verification notes before implementation is considered complete.

## Open Questions

- Should explicit invocation be exposed as both a dedicated Pixi task and a raw pytest marker/path command, or is one documented path sufficient?
- For the GPU example, should hardware-specific checks be optional capability-gated assertions, or should the suite require an NVIDIA-capable host whenever that scenario is selected?
