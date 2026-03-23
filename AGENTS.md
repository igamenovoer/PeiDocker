# Repository Guidelines

## Project Structure & Module Organization
`src/pei_docker/` contains the package code. Key modules include `pei.py` for the CLI, `webgui/` for the GUI launcher and tabs, `user_config/` for config models, and `config_processor.py` plus `pei_utils*.py` for build orchestration. Docker templates and generated project assets live under `src/pei_docker/templates/` and `src/pei_docker/project_files/`. Tests are in `tests/`, with reusable YAML samples in `tests/configs/`, helper scripts in `tests/scripts/`, and end-to-end flows in `tests/functional/`. Documentation is in `docs/`; repository utilities are in `scripts/`.

## Build, Test, and Development Commands
Prefer Pixi for local work:

- `pixi run test` runs the pytest suite.
- `pixi run lint` checks `src/` with Ruff.
- `pixi run format` formats `src/` and `tests/` with Black.
- `pixi run type-check` runs mypy on `src/`.
- `pixi run -e dev docs-serve` serves the MkDocs site locally.
- `pixi run -e dev docs-build` builds documentation.
- `pixi run -e dev build` creates wheel and sdist artifacts.

Without Pixi, use `pytest -v`, `ruff check src/`, `black src/ tests/`, and `mypy src/`. For smoke tests, run `pei-docker-cli --help` or `pei-docker-gui start --native`.

## Coding Style & Naming Conventions
Target Python 3.11+. Use 4-space indentation and Black's 88-character line length. Keep imports Ruff-clean and grouped consistently. New functions should be typed; mypy is configured with `disallow_untyped_defs = true`. Follow `snake_case` for modules and functions, `CapWords` for classes, and `UPPER_SNAKE` for constants. Keep Click option names explicit and help strings concise.

## Testing Guidelines
Pytest discovers `test_*.py` and `*_test.py`, plus `Test*` classes and `test_*` functions. Add tests with each behavior change, especially around config parsing, path resolution, entrypoint generation, and GUI state conversion. Reuse samples from `tests/configs/` where possible. Optional coverage runs with `pytest --cov=src`.

## Commit & Pull Request Guidelines
Recent history uses Conventional Commits such as `fix:`, `docs:`, `test:`, and `chore:`. Keep commit subjects short, imperative, and scoped when helpful, for example `fix(webgui): validate host mount paths`. Before opening a PR, run lint, format, type checks, and tests. PRs should describe the behavior change, link related issues, note Docker or GUI impact, and include screenshots for UI changes.

## Security & Collaboration Notes
Do not commit secrets, real SSH keys, or machine-specific paths; use placeholders in configs and docs. Test Docker-related changes on a machine with Docker installed. This workspace may be shared, so do not delete files you did not create and avoid broad git reset or checkout operations unless explicitly requested.
