# Entrypoint Non-TTY Default Blocking Functional Tests

This test case validates the OpenSpec change:

- `openspec/changes/entrypoint-non-tty-default-blocking`

These tests are heavy end-to-end checks that build real Docker images and run
containers, so they are manual trigger only.

## Scope

- Default-mode fallback behavior for non-interactive vs interactive stdin
- `--no-block` and `--verbose` option behavior
- Unknown option handling
- Passthrough command execution (`docker run image env`)
- SSH-first success criteria (container remains reachable via SSH and installed tools are usable)
- Missing custom `on_entry` target script fails with non-zero exit

## Run

From repository root:

```bash
bash tests/functional/entrypoint-non-tty-default-blocking/run.bash
```

Artifacts are written under:

- `tmp/entrypoint-non-tty-default-blocking-e2e/`

## Requirements

- Docker + Docker Compose plugin
- OpenSSH client
- `sshpass` (used for password-based SSH automation in this manual test)
