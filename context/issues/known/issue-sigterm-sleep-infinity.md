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

## Potential Fix Directions (Not Implemented Here)

- Change the sleep-fallback branch to keep a signal-handling process as PID1
  (for example, a small bash wrapper that traps `SIGTERM` and exits), rather
  than `exec sleep infinity`.
- Use an init such as `tini`/`dumb-init` to ensure PID1 handles signals and
  reaps children correctly.

Related files:

- `tests/functional/entrypoint-non-tty-default-blocking/run.bash`
- `src/pei_docker/project_files/installation/stage-1/internals/entrypoint.sh`
- `src/pei_docker/project_files/installation/stage-2/internals/entrypoint.sh`
