## 1. Define Canonical Examples Set

- [ ] 1.1 Add `src/pei_docker/examples/README.md` that lists core vs optional examples, recommended order, and prerequisites
- [ ] 1.2 Decide final filenames for the 5 core + 3 optional examples (matching the design naming convention)

## 2. Create Core Examples (Minimal)

- [ ] 2.1 Add `01-minimal.yml` demonstrating the simplest `create → configure → build/run` flow
- [ ] 2.2 Add `02-persistence.yml` demonstrating `stage_2.storage` and one volume-based `stage_2.mount` entry
- [ ] 2.3 Add `03-ports.yml` demonstrating one `stage_2.ports` mapping
- [ ] 2.4 Add `04-access.yml` demonstrating the primary “get a shell” story (SSH or `docker compose exec`), with safe-by-default guidance
- [ ] 2.5 Add `05-env-basics.yml` demonstrating configure-time `${...}` vs compose-time `{{...}}` (minimal, with a visible effect like tag/port)

## 3. Create Optional Examples (Common Advanced Needs)

- [ ] 3.1 Add `optional-gpu.yml` demonstrating `device: gpu` in both stages and documenting NVIDIA runtime prerequisites
- [ ] 3.2 Add `optional-proxy-apt.yml` demonstrating proxy settings + APT mirror acceleration (with clear defaults and notes)
- [ ] 3.3 Add `optional-merged-build.yml` demonstrating a config intended for `pei-docker-cli configure --with-merged` (avoid `/soft/*` usage in `on_build`)

## 4. Project Creation Behavior (Exclude Legacy)

- [ ] 4.1 Update `src/pei_docker/pei.py` `create` to copy examples while excluding `examples/legacy/` by default
- [ ] 4.2 Update `src/pei_docker/pei_utils_create.py` `create_project_direct` to match the CLI behavior (exclude `legacy/`)
- [ ] 4.3 Verify `pei-docker-cli create --with-examples` output contains canonical examples + `envs/`, and does not contain `legacy/`

## 5. Docs, Packaging, and Validation

- [ ] 5.1 Update docs pages that point to shipped examples to reference the canonical set (and avoid pointing at legacy)
- [ ] 5.2 Ensure packaging includes the new canonical example files (adjust `pyproject.toml` / package data rules if needed)
- [ ] 5.3 Add a lightweight repository check/test that validates required canonical example files exist
- [ ] 5.4 Add a lightweight repository check/test that validates core examples do not contain `host_path`
- [ ] 5.5 Add a lightweight repository check/test that validates optional examples are listed in the examples README with prerequisites
