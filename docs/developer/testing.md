# Testing

PeiDocker uses a mix of unit tests, config fixtures, fast docs/example contract tests,
and opt-in functional Docker tests.

## Main Commands

From repository root:

```bash
pixi run test
pixi run lint
pixi run type-check
pixi run test-entrypoint-e2e
pixi run test-basic-example-runtime
```

Without Pixi:

```bash
pytest tests/ -m "not basic_example_runtime"
pytest -m basic_example_runtime tests/functional/basic_example_runtime -v
ruff check src/
mypy src/
```

## Test Layout

| Path | Purpose |
| --- | --- |
| `tests/test_*.py` | Unit and integration-style Python tests |
| `tests/test_basic_examples_docs.py` | Fast docs/example contract checks for packaged basic examples |
| `tests/configs/` | Reusable YAML fixtures |
| `tests/scripts/` | Helper shell scripts and wrappers |
| `tests/functional/entrypoint-non-tty-default-blocking/` | Heavy Docker end-to-end runtime tests |
| `tests/functional/basic_example_runtime/` | Heavy Docker-backed packaged-example verification suite |

## Functional Entrypoint Suite

The entrypoint suite is intentionally manual-triggered because it builds images, starts containers, and performs SSH and signal-handling checks.

Useful commands:

```bash
bash tests/functional/entrypoint-non-tty-default-blocking/run.bash
bash tests/functional/entrypoint-non-tty-default-blocking/run.bash --cases E01,E05,S01
bash tests/scripts/run-entrypoint-e2e-functional.bash --cases C01,C02,C06
```

## Basic Example Runtime Suite

The packaged basic-example suite is also manual-triggered. It creates fresh projects
from `src/pei_docker/examples/basic/`, runs `pei-docker-cli configure`, builds
`stage-2`, starts the container, and verifies the documented behavior primarily through
SSH as the configured non-root users.

Useful commands:

```bash
pytest -m basic_example_runtime tests/functional/basic_example_runtime -v
pytest -m basic_example_runtime tests/functional/basic_example_runtime -k pixi-environment -v
pixi run test-basic-example-runtime
```

Notes:

- Artifacts are retained under `tmp/basic-example-runtime-e2e/`.
- `proxy-setup` is skipped when no usable shell proxy environment is available.
- `gpu-container` is skipped when the host does not expose a usable GPU runtime.
- The suite attempts `docker compose down -v` plus stage-image removal after each scenario.

## Adding New Tests

- Put schema or behavior regressions in Python tests when possible.
- Keep docs/example parity checks in the fast Python lane when Docker is not required.
- Add reusable YAML inputs under `tests/configs/`.
- Reserve Docker-heavy runtime behavior for the functional suite.
- When changing entrypoint behavior, update both the specs and the case matrix so the contract and the test stay aligned.
