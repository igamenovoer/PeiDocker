## Why

PeiDocker has enough user-facing workflow, YAML, script, and runtime behavior that a CLI agent needs repository-specific guidance to answer and edit accurately. A repository-local `skillset/` can make that guidance invokable from agent sessions while keeping the existing docs as the source of truth.

## What Changes

- Add repository-local agent skills under `<repo-root>/skillset/` for PeiDocker usage guidance.
- Provide four top-level skills:
  - `pei-docker-cli-workflow` for project creation, configuration, generated project layout, and post-configure editing guidance.
  - `pei-docker-user-config` for authoring `user_config.yml`, with `SKILL.md` acting as an index into focused reference material for config subsections.
  - `pei-docker-utility-scripts` for built-in installer/helper scripts, supported parameters, and how to invoke them from config hooks.
  - `pei-docker-run-project` for building, running, connecting to, validating, and cleaning up configured PeiDocker projects.
- Keep skills concise and route to existing docs, templates, examples, and specs instead of duplicating the full documentation set.
- Include validation guidance so agents know when to run `pei-docker-cli configure`, inspect generated files, or use Docker/Compose commands.

## Capabilities

### New Capabilities

- `peidocker-agent-skillset`: Defines the repository-local agent skillset for PeiDocker CLI workflows, user config authoring, built-in utility scripts, and running generated projects.

### Modified Capabilities

- None.

## Impact

- Affected areas: new `<repo-root>/skillset/` directory and OpenSpec artifacts for the skillset contract.
- Documentation impact: skills reference existing `docs/`, `src/pei_docker/templates/`, `src/pei_docker/examples/`, and relevant `openspec/specs/` contracts as source material.
- User workflow impact: users can invoke focused PeiDocker skills inside a CLI agent instead of manually traversing the documentation tree for common project, config, script, and runtime tasks.
- No PeiDocker runtime, CLI, Docker template, or package API behavior changes are introduced.
