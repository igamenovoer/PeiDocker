## Context

PeiDocker currently documents its usage through `docs/`, examples, templates, and OpenSpec contracts. A CLI agent can read those files, but without repository-local skills it has no concise, invokable workflow for deciding which source files to consult for common PeiDocker tasks.

The requested skillset is user-facing guidance, not a product runtime feature. It should live under `<repo-root>/skillset/` and remain decoupled from the Python package, Docker templates, and generated project files.

## Goals / Non-Goals

**Goals:**

- Add four top-level PeiDocker agent skills that match the user's simplified mental model:
  - CLI and project workflow
  - `user_config.yml` authoring
  - built-in utility scripts
  - running configured projects
- Keep each skill concise enough to load into agent context quickly.
- Make the `pei-docker-user-config` skill an index into focused reference files for YAML subtopics.
- Make the `pei-docker-utility-scripts` skill an index into focused reference files for script families and usage patterns.
- Ground all guidance in existing docs, templates, examples, and OpenSpec specs.

**Non-Goals:**

- Do not change PeiDocker CLI behavior, generated Docker artifacts, templates, examples, or runtime scripts.
- Do not duplicate the complete documentation site inside the skills.
- Do not create one top-level skill per PeiDocker feature.
- Do not make the deprecated Web GUI a primary workflow; skills may mention its current 2.0 status when relevant.

## Decisions

### Use four top-level skills

Use:

- `skillset/pei-docker-cli-workflow/`
- `skillset/pei-docker-user-config/`
- `skillset/pei-docker-utility-scripts/`
- `skillset/pei-docker-run-project/`

Alternative considered: many small top-level skills for SSH, storage, GPU, proxy, Pixi, Conda, troubleshooting, and internals. That matches the docs tree but makes skill selection noisy. The four-skill split better matches how users ask for help.

### Treat config and script "subskills" as reference modules

Nested `SKILL.md` files are not a reliable discovery mechanism for CLI agents. For the config and utility-script skills, use a top-level `SKILL.md` as the triggerable entrypoint and add `references/*.md` files for topic-specific details.

Alternative considered: nested skill directories under `pei-docker-user-config/skills/`. That would look appealing on disk but would make invocation and routing ambiguous.

### Keep docs and examples as source of truth

The skills should include procedural routing and short decision rules, then point the agent to the relevant existing source files:

- `docs/manual/getting-started/*`
- `docs/manual/concepts/*`
- `docs/manual/guides/*`
- `docs/manual/scripts/*`
- `docs/manual/cli-reference.md`
- `docs/manual/troubleshooting.md`
- `src/pei_docker/templates/config-template-full.yml`
- `src/pei_docker/templates/quick/*.yml`
- `src/pei_docker/examples/**/user_config.yml`
- relevant `openspec/specs/*/spec.md`

Alternative considered: copy substantial docs excerpts into each skill. That would increase maintenance cost and risks stale guidance.

### Include agent-facing validation guidance

Each skill should tell the agent when to validate. Examples:

- Run `pei-docker-cli configure` after meaningful `user_config.yml` edits.
- Inspect generated `docker-compose.yml` and `installation/stage-*/generated/` only as outputs, not primary edit targets.
- Use Docker/Compose commands for run validation only when the user asks for runtime verification or the change requires it.
- Use merged-build helpers only after `configure --with-merged`.

Alternative considered: leave validation entirely to the agent. PeiDocker has enough build-mode and lifecycle constraints that explicit validation guidance reduces common mistakes.

## Risks / Trade-offs

- Skill guidance may drift from docs -> Make skills reference docs/templates/examples/specs rather than restating large sections.
- Four skills may still overlap -> Define clear routing boundaries and source files in each `SKILL.md`.
- Nested reference files may be missed -> Put an explicit reference routing table in the top-level `SKILL.md` for config and utility scripts.
- Agent may edit generated files -> Include safety guidance to prefer `user_config.yml` and custom scripts over `docker-compose.yml` and generated wrappers.
- Runtime validation can be expensive -> Separate configure-time validation from Docker-heavy build/run validation and require judgment before running heavy commands.

## Migration Plan

1. Add the new `skillset/` tree.
2. Create the four skill folders with valid `SKILL.md` files.
3. Add focused reference files for config and utility-script subtopics.
4. Validate skill metadata and inspect the skill tree.
5. Optionally run a small forward-use check by asking an agent-style prompt to choose a build mode, edit a config, add a utility script, and run a project.

Rollback is deleting the new `skillset/` tree; no PeiDocker runtime or package behavior depends on it.

## Open Questions

None. The initial implementation should include `agents/openai.yaml` metadata for all four skills and keep runtime troubleshooting inside `pei-docker-run-project` rather than adding a fifth top-level skill.
