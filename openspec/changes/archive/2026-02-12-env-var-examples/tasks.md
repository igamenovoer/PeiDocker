## 1. Docs Structure

- [x] 1.1 Add three env tutorial pages under `docs/examples/`
- [x] 1.2 Add an env-focused build-and-run walkthrough page under `docs/examples/`
- [x] 1.3 Update `mkdocs.yml` nav to link the new pages under Examples

## 2. Env Tutorials (Docs Content)

- [x] 2.1 Write “Env Tutorial 1 (no passthrough)” covering `${VAR}` / `${VAR:-default}` semantics and re-configure workflow
- [x] 2.2 Write “Env Tutorial 2 (passthrough)” covering `{{VAR}}` / `{{VAR:-default}}`, `.env`, and `docker compose config`
- [x] 2.3 Write “Env Tutorial 3 (advanced)” covering mixed-mode strings, ports-as-strings, guardrails, and failure modes

## 3. Env Build-and-Run Walkthrough (Docs Content)

- [x] 3.1 Document an end-to-end flow (create → configure → build → run → validate) using `tmp/<subdir>/cases/<case-name>/`
- [x] 3.2 Ensure the walkthrough uses `ubuntu:24.04` as the configured base image
- [x] 3.3 Add a networking note for download steps (China mirrors only; no proxy setup in examples)

## 4. Examples and Cross-Links

- [x] 4.1 Ensure tutorial snippets align with `src/pei_docker/examples/envs/*.yml` (update if needed)
- [x] 4.2 Add minimal cross-links from existing examples (`docs/examples/basic.md` and/or `docs/examples/advanced.md`) to the new tutorials

## 5. Verification

- [x] 5.1 Run a docs build (`pixi run -e dev docs-build` or `mkdocs build`) and fix any issues introduced by the new pages/nav
- [x] 5.2 For each case under `tmp/<subdir>/cases/`, run through configure/build/start and verify the case image builds successfully
- [x] 5.3 For each case, verify runtime environment values with container-level checks (for example `docker compose run --rm stage-2 env`)
