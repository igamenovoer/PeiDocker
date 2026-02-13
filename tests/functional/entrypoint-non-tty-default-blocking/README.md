# Entrypoint Non-TTY Default Blocking Functional Tests

This suite validates entrypoint runtime behavior from:

- `openspec/changes/entrypoint-non-tty-default-blocking`

These are heavy Docker end-to-end checks and are manual trigger only.

## Covered Case Matrix

Default mode:

- `E01`: non-interactive no args -> sleep fallback + SSH login
- `E02`: `-i` no TTY no args -> bash fallback
- `E03`: `--no-block` -> exit `0`
- `E04`: passthrough command (`docker run image env`)
- `E05`: `--verbose` toggles hook logs
- `E06`: unknown option fails non-zero
- `E07`: preparation runs before command handoff

Custom `on_entry`:

- `C01`: stage-1 custom branch selected and runtime args forwarded
- `C02`: baked config args precede runtime args
- `C03`: stage-2 custom overrides stage-1 custom on stage-2 image
- `C04`: stage-1 custom fallback works on stage-2 image when stage-2 custom is unset
- `C05`: missing custom target script fails hard (non-zero)
- `C06`: custom mode does not parse default-mode flags (`--no-block` forwarded)

Signal handling:

- `S01`: sleep fallback exits promptly on `SIGTERM`

## Run

From repository root:

```bash
bash tests/functional/entrypoint-non-tty-default-blocking/run.bash
```

Run specific cases only:

```bash
bash tests/functional/entrypoint-non-tty-default-blocking/run.bash --cases E01,E05,S01
```

Alternative stable wrapper:

```bash
bash tests/scripts/run-entrypoint-e2e-functional.bash --cases C01,C02,C06
```

Pixi task:

```bash
pixi run test-entrypoint-e2e
```

## Artifacts

Outputs are stored under:

- `tmp/entrypoint-non-tty-default-blocking-e2e/project/`
- `tmp/entrypoint-non-tty-default-blocking-e2e/logs/`
- `tmp/entrypoint-non-tty-default-blocking-e2e/images/` (when `SAVE_E2E_IMAGE_TARS=1`)

## Requirements

- Docker and Docker Compose plugin
- OpenSSH client
- `sshpass` (used for automated SSH smoke checks)
