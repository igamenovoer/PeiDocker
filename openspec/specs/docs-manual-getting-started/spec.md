# docs-manual-getting-started Specification

## Purpose
TBD - created by archiving change rewrite-docs-structure. Update Purpose after archive.
## Requirements
### Requirement: Installation guide covers all supported platforms
The installation guide (`manual/getting-started/installation.md`) SHALL document installation via pip and pixi on Linux, macOS, and Windows (WSL). Each platform section SHALL include prerequisites, install commands, and verification steps.

#### Scenario: User installs on Linux
- **WHEN** a user reads the Linux installation section
- **THEN** they find pip and pixi install commands, Docker prerequisites, and a verification command (`pei-docker-cli --version`)

#### Scenario: User installs on Windows WSL
- **WHEN** a user reads the Windows section
- **THEN** they find WSL setup prerequisites, Docker Desktop integration notes, and platform-specific gotchas

### Requirement: Quickstart creates a working container in minimal steps
The quickstart guide (`manual/getting-started/quickstart.md`) SHALL walk a user from zero to a running SSH-accessible container in under 10 commands. It SHALL use the `--quick minimal` template and show the full workflow: create → configure → build → run → connect.

#### Scenario: First-time user follows quickstart
- **WHEN** a user follows the quickstart from top to bottom
- **THEN** they have a running container they can SSH into, having run no more than 10 commands

### Requirement: Project structure guide explains generated files
The project structure guide (`manual/getting-started/project-structure.md`) SHALL explain every file and directory created by `pei-docker-cli create`, including `user_config.yml`, `reference_config.yml`, `compose-template.yml`, and the `installation/` directory tree with its stage-1 and stage-2 subdivisions.

#### Scenario: User wants to understand what was generated
- **WHEN** a user reads the project structure guide after running `create`
- **THEN** they understand the purpose of each generated file and directory, and know which files they should edit vs which are auto-generated

