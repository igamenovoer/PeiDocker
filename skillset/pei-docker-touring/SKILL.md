---
name: pei-docker-touring
description: New-user entrypoint and router for PeiDocker guidance. Use when Codex needs to orient a user who is new, unsure where to start, asking broad PeiDocker questions, or needing help choosing among project workflow, user_config.yml authoring, built-in utility scripts, and running configured projects.
---

# PeiDocker Touring

## Purpose

Use this skill as the front door for broad PeiDocker help. It should classify the user's situation, choose the right sibling skill, then read and follow that sibling skill instead of duplicating its guidance.

Sibling skills:

- `$pei-docker-cli-workflow`: create projects, choose build modes, run `configure`, inspect generated project layout.
- `$pei-docker-user-config`: author or modify `user_config.yml`.
- `$pei-docker-utility-scripts`: choose built-in installer/helper scripts and add them to config hooks.
- `$pei-docker-run-project`: build, run, connect to, validate, troubleshoot, or clean up configured projects.

## Orientation Workflow

1. Identify the user's current state.
2. Identify the task type.
3. Read the matching sibling `SKILL.md`.
4. Follow that skill's workflow and source-file guidance.
5. If the request crosses boundaries, handle the earliest dependency first.

Example dependency order:

```text
create project -> edit user_config.yml -> add utility scripts -> configure -> build/run
```

## State Detection

Check local context before giving commands when possible:

| Signal | Meaning |
| --- | --- |
| `src/pei_docker/`, `docs/`, `pyproject.toml` | PeiDocker repository root |
| `user_config.yml`, `compose-template.yml`, `installation/` | Generated PeiDocker project |
| `docker-compose.yml` | Project has been configured |
| `build-merged.sh`, `run-merged.sh`, `merged.env` | Project has merged-build artifacts |
| no project files | User likely needs CLI workflow onboarding |

When the state is unclear, ask one concise question or inspect the working directory.

## Routing Table

| User asks | Route |
| --- | --- |
| "I am new", "how do I start", install, create, quickstart | `$pei-docker-cli-workflow` |
| build modes, stage-1-only, two-stage, merged build setup | `$pei-docker-cli-workflow` |
| generated files, what to edit after `configure` | `$pei-docker-cli-workflow` |
| YAML, `user_config.yml`, SSH users, ports, proxy, APT, storage, mounts, env vars, hooks | `$pei-docker-user-config` |
| Pixi, Conda, ROS2, OpenGL, OpenCV, Node.js, UV, Bun, built-in installers | `$pei-docker-utility-scripts` |
| `on_build`, `on_first_run`, hook placement for built-in scripts | `$pei-docker-utility-scripts` first, then `$pei-docker-user-config` if editing YAML |
| build images, `docker compose up`, SSH into container, `exec`, logs, GPU check, cleanup | `$pei-docker-run-project` |
| errors after configure/build/run | `$pei-docker-run-project`, then route to config or scripts if root cause is YAML or hook placement |

## Default New-User Path

For a user with no project yet, route through:

1. `$pei-docker-cli-workflow` to install/verify tools, create a project, and choose a build mode.
2. `$pei-docker-user-config` only if they need to customize `user_config.yml`.
3. `$pei-docker-utility-scripts` only if they need built-in installers.
4. `$pei-docker-run-project` to build, run, connect, and clean up.

Keep the first answer short. Do not unload the whole PeiDocker manual onto a new user.

## Source Of Truth

Do not invent PeiDocker behavior from memory. After routing, use the sibling skill's listed docs, templates, examples, and OpenSpec specs as authority.

Useful global starting points:

- `docs/index.md`
- `docs/manual/getting-started/build-modes.md`
- `docs/manual/getting-started/quickstart.md`
- `docs/manual/cli-reference.md`
- `docs/manual/troubleshooting.md`

## Safety

- Prefer editing `user_config.yml` and custom source scripts over generated files.
- Run `pei-docker-cli configure` after meaningful config edits when feasible.
- Treat Docker-heavy build/run validation as optional unless the user asks for it or the task requires it.
- Mention that the Web GUI is deprecated/unavailable in PeiDocker 2.0 when users ask for GUI workflows.
