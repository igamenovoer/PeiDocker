## ADDED Requirements

### Requirement: Repository-local PeiDocker agent skillset
The repository SHALL provide a `skillset/` directory containing exactly four initial top-level PeiDocker agent skills: `pei-docker-cli-workflow`, `pei-docker-user-config`, `pei-docker-utility-scripts`, and `pei-docker-run-project`. Each skill directory MUST contain a valid `SKILL.md` whose frontmatter name matches the directory name and whose description states the contexts that should trigger the skill.

#### Scenario: User scans available PeiDocker skills
- **WHEN** a user or agent lists the repository-local `skillset/` directory
- **THEN** the four top-level PeiDocker skill directories are present with valid `SKILL.md` entrypoints

### Requirement: Skills use existing PeiDocker sources as authority
The PeiDocker skills SHALL treat existing documentation, templates, packaged examples, and OpenSpec specs as the source of truth for behavior. Skills MUST prefer directing the agent to relevant source files over duplicating full documentation content.

#### Scenario: Agent needs exact YAML syntax
- **WHEN** an agent uses a PeiDocker skill to author or revise `user_config.yml`
- **THEN** the skill points the agent to the relevant docs, `src/pei_docker/templates/config-template-full.yml`, quick templates, or packaged example configs before inventing syntax

### Requirement: CLI workflow skill covers project lifecycle
The `pei-docker-cli-workflow` skill SHALL cover installing or verifying the CLI, creating projects, choosing quick templates, running `configure`, understanding generated project structure, choosing among stage-1-only, two-stage Compose, and merged build workflows, and deciding which project files are safe to edit after configuration.

#### Scenario: User wants to create and configure a project
- **WHEN** a user asks how to create a new PeiDocker project and generate its Docker artifacts
- **THEN** the skill guides the agent through `pei-docker-cli create`, `pei-docker-cli configure`, relevant build-mode choices, and post-configure edit boundaries

### Requirement: User config skill indexes focused config subtopics
The `pei-docker-user-config` skill SHALL use its `SKILL.md` as an index and entrypoint for authoring `user_config.yml`. It MUST route the agent to focused reference material for stage/image structure, SSH access, storage and mounts, networking/proxy/APT/ports, environment-variable semantics, and lifecycle custom hooks.

#### Scenario: User asks for a storage-backed workspace config
- **WHEN** a user asks the agent to add or revise storage and mounts in `user_config.yml`
- **THEN** the skill routes the agent to storage-specific guidance and source files instead of loading unrelated SSH, proxy, or installer-script details

### Requirement: Utility scripts skill covers built-in script usage
The `pei-docker-utility-scripts` skill SHALL explain what built-in utility script families exist, where their canonical paths live, which important parameters they accept, and how to add them to `user_config.yml` custom hooks. It MUST prefer `stage-1/system/*` canonical script paths where the current docs and specs define stage-1 as canonical.

#### Scenario: User wants to add Pixi to a project
- **WHEN** a user asks how to install Pixi through PeiDocker built-in scripts
- **THEN** the skill identifies the Pixi script family, key flags such as user, install, cache, and mirror options, and the appropriate `custom` hook entry pattern for the user's build-time or runtime intent

### Requirement: Run project skill covers configured project operation
The `pei-docker-run-project` skill SHALL cover building and running a configured PeiDocker project through Docker Compose and merged-build helper scripts, connecting through SSH, using `docker compose exec`, validating ports and GPU access, using verbose entrypoint behavior, stopping services, and cleaning up with PeiDocker or Docker commands.

#### Scenario: User wants to run a configured project
- **WHEN** a user has already run `pei-docker-cli configure` and asks how to build, start, connect to, or stop the project
- **THEN** the skill guides the agent to the correct Compose or merged-build commands for the project's configured build mode

### Requirement: Skills include validation and safety guidance
The skillset SHALL include guidance for validating agent-assisted changes without modifying generated outputs as primary sources. Skills MUST tell agents to prefer editing `user_config.yml` and `installation/stage-*/custom/` scripts, to run `pei-docker-cli configure` after meaningful config edits when feasible, and to treat `docker-compose.yml` and `installation/stage-*/generated/` files as generated artifacts.

#### Scenario: Agent changes a user config
- **WHEN** an agent modifies a PeiDocker `user_config.yml`
- **THEN** the relevant skill instructs the agent to validate the change with `pei-docker-cli configure` when feasible and avoid hand-editing generated wrapper files as the durable fix
