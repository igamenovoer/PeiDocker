# Issue: SIGTERM Does Not Stop PID1 `sleep infinity` (S01 Failure)

## Summary

In this environment, containers whose PID1 is `sleep infinity` do not exit after
receiving `SIGTERM` via `docker kill --signal TERM <container>`. This breaks the
expected behavior for the entrypoint E2E test case `S01` (sleep-fallback should
exit promptly on `SIGTERM`).

This is not specific to PeiDocker images: a minimal `ubuntu:24.04` container
shows the same behavior.

## Why This Matters

- Kubernetes-style termination relies on a graceful `SIGTERM` path before a
  later `SIGKILL`.
- Our entrypoint "sleep fallback" branch currently uses `exec sleep infinity`
  (making `sleep` PID1), so graceful termination depends on that PID1 exiting.
- The functional suite has an explicit scenario (`S01`) intended to guard this,
  and it currently fails.

## Evidence / Reproduction

### EntryPoint E2E: `S01` fails

From repo root:

```bash
bash tests/functional/entrypoint-non-tty-default-blocking/run.bash --cases S01
```

Observed failure:

- The container remains running after `docker kill --signal TERM <cid>` for
  longer than the test timeout (20s).

### Minimal reproduction (no PeiDocker)

```bash
cid=$(docker run -d ubuntu:24.04 sleep infinity)
docker exec "$cid" sh -lc 'tr "\0" " " </proc/1/cmdline'  # shows: sleep infinity

docker kill --signal TERM "$cid"
sleep 10
docker inspect -f '{{.State.Running}}' "$cid"             # remains: true
```

`docker stop` does terminate the container, but that does not prove a graceful
`SIGTERM` path since Docker will send `SIGKILL` after the stop timeout:

```bash
cid=$(docker run -d ubuntu:24.04 sleep infinity)
docker stop -t 2 "$cid"
docker rm "$cid"
```

### Environment

- Docker: `Docker version 28.2.2`
- Kernel: `Linux 6.8.0-90-generic` (Ubuntu)

## Impact / Symptoms

- `S01` (sleep fallback exits promptly on `SIGTERM`) is not currently achievable
  with `sleep` as PID1 in this environment.
- Any runtime mode that results in PID1 being `sleep` may ignore/never act on
  `SIGTERM`, so shutdown can depend on a forced `SIGKILL`.

## Workarounds (Imperfect)

- Use `docker stop` (or orchestrator stop) which eventually forces `SIGKILL`
  after a grace period.
- Use `docker kill --signal KILL <cid>` in ad-hoc scripts to force termination.
- Keep `S01` as a known-failing scenario until runtime signal handling is fixed.

## Root Cause Analysis

The problem is a fundamental Linux kernel behavior, not a Docker or coreutils bug.

### PID 1 signal immunity

The Linux kernel deliberately protects PID 1 (the init process) from signals it
has not explicitly registered a handler for. When a signal arrives at PID 1, the
kernel checks whether PID 1 has called `sigaction()` to install a handler for
that signal. If it has not, the kernel **silently discards** the signal — it is
not queued, deferred, or applied with default disposition.

For any normal process (PID > 1), the default disposition for `SIGTERM` is to
terminate. But PID 1 is exempt from default dispositions; only explicitly
registered handlers are honoured.

### How the entrypoint triggers this

Both stage-1 (`entrypoint.sh:127`) and stage-2 (`entrypoint.sh:141`) end with:

```bash
exec sleep infinity
```

The `exec` replaces the shell process with `sleep`, so `sleep` **becomes PID 1**
inside the container. The `sleep` command from coreutils does not install a
`SIGTERM` handler — it relies on the default disposition. For PID 1 that means
the kernel drops the signal entirely:

```
docker kill --signal TERM <cid>
     │
     ▼
Docker runtime delivers SIGTERM to container PID 1 (sleep)
     │
     ▼
Kernel: "PID 1 has no handler for SIGTERM → discard"
     │
     ▼
sleep keeps sleeping — container stays running
```

### Why `docker stop` appears to work

`docker stop` is a two-phase operation:

1. Send `SIGTERM`
2. Wait a grace period (default 10 s)
3. Send `SIGKILL`

`SIGKILL` cannot be caught, blocked, or ignored — not even by PID 1. So the
container terminates, but via brute force, not graceful shutdown.

### Why `exec` is the trigger

Without `exec`, bash remains PID 1 and `sleep` runs as a child. Bash registers
signal handlers by default, so `SIGTERM` would reach bash, bash would die, and
`sleep` would be orphaned and reaped. The `exec` removes bash from the picture,
leaving `sleep` (which has no handler) as PID 1.

## Fix Suggestions

### Option A — Bash trap wrapper (lightweight, no extra binary)

Replace `exec sleep infinity` with a bash loop that traps `SIGTERM`:

```bash
# Instead of: exec sleep infinity
_sleep_forever() {
    trap 'exit 0' TERM
    while :; do sleep infinity & wait $!; done
}
_sleep_forever
```

Key points:
- Bash stays as PID 1 and registers a `SIGTERM` handler via `trap`.
- `sleep infinity` runs as a background child; `wait` is interruptible by
  signals, so when `SIGTERM` arrives the trap fires immediately.
- No extra binary needed.

Trade-off: Bash as PID 1 does not automatically reap zombie children. If any
process inside the container forks and its parent exits, zombies may accumulate.
For typical PeiDocker usage (SSH server + user sessions) this is unlikely to be
a practical problem, but it is a theoretical gap.

### Option B — Use `tini` or `dumb-init` as PID 1

Install a minimal init (`tini` is ~20 KB) and make it PID 1:

```bash
exec tini -- sleep infinity
```

Or at the Docker level:

```dockerfile
RUN apt-get install -y tini
ENTRYPOINT ["tini", "--"]
```

Key points:
- `tini` registers signal handlers and forwards them to children.
- Also handles zombie reaping (PID 1 responsibility).
- Well-tested, widely used (Docker's `--init` flag uses `tini` internally).

Trade-off: Requires adding `tini` to the image build. Since PeiDocker already
manages Dockerfile generation, this could be injected into the stage-1 base
layer.

### Option C — Docker `--init` flag

Docker has built-in support via `docker run --init`, which injects a `tini`
binary automatically:

```yaml
# docker-compose.yml
services:
  stage-2:
    init: true
```

Key points:
- Zero changes to entrypoint scripts or Dockerfiles.
- Requires the user (or PeiDocker's compose generation) to set `init: true`.

Trade-off: Depends on the Docker host having `docker-init` available (it is
included by default in standard Docker installations). Does not work if the
user overrides the compose file without the flag.

### Spec Impact Analysis

The entrypoint runtime behavior spec
(`openspec/changes/entrypoint-non-tty-default-blocking/specs/entrypoint-default-runtime-behavior/spec.md`)
defines the non-interactive fallback as:

> entrypoint MUST execute `sleep infinity` **(or equivalent)** as a blocking
> foreground process

The E2E test spec
(`openspec/changes/entrypoint-e2e-test-cases/specs/entrypoint-e2e-functional-tests/spec.md`)
defines S01 as:

> WHEN a container is running in non-interactive blocking fallback mode and
> receives SIGTERM, THEN the test verifies the container exits within a bounded
> timeout

**Option A touches only the sleep-fallback branch:**

- **Specs**: No violations. The "(or equivalent)" language explicitly allows a
  bash trap wrapper that blocks forever and handles SIGTERM. S01 would go from
  failing to **passing**, which is closer to spec compliance than the current
  state.
- **Test E01**: The test *implementation* (not the spec) asserts
  `assert_contains "$cmdline" "sleep infinity"` against `/proc/1/cmdline`. With
  Option A, PID 1 is bash, so this assertion needs updating. The E01 *spec*
  only requires "the test verifies the container remains running and confirms
  the expected fallback branch behavior" — container stays alive, branch log
  says "sleep fallback", SSH works. All still true.
- **All other branches untouched**: E02–E07, C01–C06 have zero impact.

**Options B/C (tini / `init: true`) affect ALL branches:**

- PID 1 becomes `docker-init` for every branch, not just the sleep fallback.
- **Test E01** breaks: PID 1 cmdline is `docker-init`, not `sleep infinity`.
- **Test E02** breaks: PID 1 cmdline is `docker-init`, not `/bin/bash`.
- **E04, E05, E07, C01–C06**: PID 1 observable identity changes for all of
  them, since `exec` no longer makes the target process PID 1.
- The runtime behavior spec says `entrypoint MUST start /bin/bash` for the
  interactive branch — with tini as PID 1, bash is PID 2, which pushes against
  the spec's `exec` semantics.

Summary:

| Aspect           | Option A (bash trap) | Option B/C (tini)         |
|------------------|----------------------|---------------------------|
| Spec violations  | None                 | Arguable (`exec` semantics)|
| Branches affected| sleep-fallback only  | ALL branches              |
| Test updates     | E01 cmdline check    | E01, E02, and potentially E04/E05/E07/C01–C06 |
| S01 outcome      | Passes               | Passes                    |

### Recommendation

Option A is the safest choice for PeiDocker's architecture — it fixes the
problem entirely within the entrypoint script, touches only the sleep-fallback
branch, requires no external dependencies, and stays within the spec's
"(or equivalent)" allowance. The only required follow-up is relaxing the E01
test's PID 1 cmdline assertion.

Option B/C (tini) has a much wider blast radius, changing PID 1 identity for
every entrypoint branch and requiring spec and test updates across the board.
It could be offered as an optional user-facing recommendation (`init: true` in
compose) for users who want full init semantics including zombie reaping, but
should not be the primary fix.

## Related Files

- `tests/functional/entrypoint-non-tty-default-blocking/run.bash`
- `src/pei_docker/project_files/installation/stage-1/internals/entrypoint.sh`
- `src/pei_docker/project_files/installation/stage-2/internals/entrypoint.sh`
