# Repository Guidelines

## Project Structure & Module Organization
- `src/pei_docker/` — core package. Key modules: `pei.py` (CLI), `webgui/` (GUI + launcher), `config_processor.py`, `pei_utils*.py`, `templates/`, `project_files/`.
- `tests/` — sample configs and helper scripts for integration flows (`tests/configs`, `tests/scripts`).
- `docs/` + `mkdocs.yml` — documentation site.
- `scripts/` — utility scripts (e.g., `scripts/build-config.bash`).

## Build, Test, and Development Commands
- With Pixi (recommended):
  - `pixi run test` — run pytest.
  - `pixi run lint` / `pixi run format` — Ruff/Black.
  - `pixi run type-check` — mypy.
  - `pixi run -e dev docs-serve` — live docs; `pixi run -e dev docs-build` — build docs.
  - Packaging: `pixi run -e dev build` (wheel/sdist).
- Without Pixi:
  - `pytest -v`, `ruff check src/`, `black src/ tests/`, `mypy src/`, `mkdocs serve`.
- Try the app:
  - CLI: `pei-docker-cli --help`.
  - GUI: `pei-docker-gui start --native` (desktop) or `pei-docker-gui start` (browser).

## Coding Style & Naming Conventions
- Python 3.11+. Format with Black (line length 88); lint with Ruff; type-check with mypy (no untyped defs).
- Indentation: 4 spaces. Imports grouped/ordered by Ruff rules.
- Naming: modules/functions `snake_case`, classes `CapWords`, constants `UPPER_SNAKE`.
- Keep CLI help strings concise; prefer Click options with clear names and defaults.

## Testing Guidelines
- Framework: pytest (see `pyproject.toml` settings). Test discovery: `test_*.py` or `*_test.py`, classes `Test*`, functions `test_*`.
- Use sample configs under `tests/configs` and helper scripts under `tests/scripts` for realistic flows.
- Optional coverage: `pytest --cov=src` (coverage config is preset). Add tests for new features and bug fixes.

## Commit & Pull Request Guidelines
- Commit style: Conventional Commits (`feat:`, `fix:`, `docs:`, `ci:`). Examples exist in `git log`.
- Before PR: run `pixi run lint`, `pixi run format`, `pixi run type-check`, and `pixi run test`.
- PRs should include: clear description, linked issues, behavior notes, screenshots for GUI changes, and doc updates when flags/CLI change.
- CI builds docs and validates packaging; ensure workflows pass.

## Security & Configuration Tips
- Do not commit secrets or real SSH keys; use placeholders in examples.
- Changes involving Docker behavior should be tested with Docker installed; avoid hard-coded host paths/ports.
