# docs-manual-scripts-catalog Specification

## Purpose
TBD - created by archiving change rewrite-docs-structure. Update Purpose after archive.
## Requirements
### Requirement: Scripts catalog index page
The scripts catalog index (`manual/scripts/index.md`) SHALL provide a table listing all available system scripts with columns: name, description, stage, and complexity (simple/complex).

#### Scenario: User browses available scripts
- **WHEN** a user reads the scripts index
- **THEN** they see all 19 scripts in a table and can navigate to the relevant detail page

### Requirement: Complex scripts have individual documentation pages
Complex system scripts (pixi, conda, ssh, ros2, proxy, opengl, opencv) SHALL each have a dedicated page documenting: what it installs, available parameters, usage in `user_config.yml` custom scripts, common patterns, and known gotchas.

#### Scenario: User wants to install pixi with custom parameters
- **WHEN** a user reads the pixi script page
- **THEN** they find the available parameters (e.g., `--pypi-repo`, `--conda-repo`, `--cache-dir`) and example config snippets

### Requirement: Simple scripts have a grouped catalog page
Simple system scripts (nodejs, bun, uv, clang, firefox, ngc, litellm, claude-code, codex-cli, magnum, vision-dev) SHALL be documented together in `manual/scripts/simple-installers.md` with a brief description and example usage for each.

#### Scenario: User wants to install Node.js
- **WHEN** a user reads the simple installers page
- **THEN** they find a brief entry for nodejs with the install script path and a config snippet showing how to add it to `on_build`

