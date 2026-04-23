## 1. Skillset Structure

- [x] 1.1 Create the `skillset/` root with four top-level skill directories: `pei-docker-cli-workflow`, `pei-docker-user-config`, `pei-docker-utility-scripts`, and `pei-docker-run-project`.
- [x] 1.2 Add valid `SKILL.md` frontmatter to each skill with `name` matching the directory and trigger-focused `description` text.
- [x] 1.3 Add `agents/openai.yaml` metadata for each top-level skill and keep it aligned with the corresponding `SKILL.md`.
- [x] 1.4 Add `references/` directories for `pei-docker-user-config` and `pei-docker-utility-scripts`.

## 2. CLI Workflow Skill

- [x] 2.1 Author `pei-docker-cli-workflow/SKILL.md` with guidance for install verification, `create`, quick templates, `configure`, and `remove`.
- [x] 2.2 Cover stage-1-only, default two-stage Compose, and merged-build workflow selection.
- [x] 2.3 Include project-structure guidance that distinguishes durable edit targets from generated artifacts.
- [x] 2.4 Point the skill to relevant docs and templates instead of copying full documentation text.

## 3. User Config Skill

- [x] 3.1 Author `pei-docker-user-config/SKILL.md` as an index and routing entrypoint for `user_config.yml` work.
- [x] 3.2 Add focused config references for stage/image structure, SSH access, storage and mounts, networking/proxy/APT/ports, environment variables, and lifecycle custom hooks.
- [x] 3.3 Include guidance to consult `src/pei_docker/templates/config-template-full.yml`, quick templates, packaged examples, and relevant OpenSpec specs before inventing YAML.
- [x] 3.4 Include validation guidance to run `pei-docker-cli configure` after meaningful config edits when feasible.

## 4. Utility Scripts Skill

- [x] 4.1 Author `pei-docker-utility-scripts/SKILL.md` as an index for built-in utility script families and hook placement decisions.
- [x] 4.2 Add focused utility-script references for Pixi, Conda, ROS2, OpenGL/OpenCV/vision tooling, Node/UV/Bun/simple installers, and proxy helpers.
- [x] 4.3 Document canonical `stage-1/system/*` script path preference and stage-2 wrapper expectations.
- [x] 4.4 Document build-time versus runtime path guidance, including `/hard/image/...` for build-time installs and `/soft/...` only for runtime hooks.

## 5. Run Project Skill

- [x] 5.1 Author `pei-docker-run-project/SKILL.md` with Docker Compose build/run/start/stop guidance for configured projects.
- [x] 5.2 Include merged-build helper usage for projects configured with `--with-merged`.
- [x] 5.3 Include SSH connection, `docker compose exec`, port validation, GPU validation, verbose entrypoint, and cleanup guidance.
- [x] 5.4 Include runtime troubleshooting pointers for common build/run/configuration mistakes without creating a separate troubleshooting skill.

## 6. Validation

- [x] 6.1 Validate the skill tree contains exactly the four required top-level skill directories and no extra top-level PeiDocker usage skills.
- [x] 6.2 Validate all four `SKILL.md` files have valid frontmatter and trigger-focused descriptions.
- [x] 6.3 Validate config and utility-script reference routing tables point to existing reference files and existing PeiDocker source docs/templates/examples.
- [x] 6.4 Run OpenSpec status for `add-peidocker-agent-skillset` and confirm artifacts remain apply-ready.
