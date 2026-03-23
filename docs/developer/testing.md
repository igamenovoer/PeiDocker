# Testing

PeiDocker uses a mix of unit tests, config fixtures, and manual-trigger functional Docker tests.

## Main Commands

From repository root:

```bash
pixi run test
pixi run lint
pixi run type-check
pixi run test-entrypoint-e2e
```

Without Pixi:

```bash
pytest tests/
ruff check src/
mypy src/
```

## Test Layout

| Path | Purpose |
| --- | --- |
| `tests/test_*.py` | Unit and integration-style Python tests |
| `tests/configs/` | Reusable YAML fixtures |
| `tests/scripts/` | Helper shell scripts and wrappers |
| `tests/functional/entrypoint-non-tty-default-blocking/` | Heavy Docker end-to-end runtime tests |

## Functional Entrypoint Suite

The entrypoint suite is intentionally manual-triggered because it builds images, starts containers, and performs SSH and signal-handling checks.

Useful commands:

```bash
bash tests/functional/entrypoint-non-tty-default-blocking/run.bash
bash tests/functional/entrypoint-non-tty-default-blocking/run.bash --cases E01,E05,S01
bash tests/scripts/run-entrypoint-e2e-functional.bash --cases C01,C02,C06
```

## Adding New Tests

- Put schema or behavior regressions in Python tests when possible.
- Add reusable YAML inputs under `tests/configs/`.
- Reserve Docker-heavy runtime behavior for the functional suite.
- When changing entrypoint behavior, update both the specs and the case matrix so the contract and the test stay aligned.
