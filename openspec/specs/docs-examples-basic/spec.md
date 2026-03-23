# docs-examples-basic Specification

## Purpose
TBD - created by archiving change rewrite-docs-structure. Update Purpose after archive.
## Requirements
### Requirement: Basic examples demonstrate single features with minimal config
Each basic example SHALL focus on exactly one feature, using the minimal `user_config.yml` needed to demonstrate that feature. The doc page (`docs/examples/basic/<slug>.md`) SHALL include embedded YAML with annotations, a brief explanation of what the feature does, and the expected result.

#### Scenario: User reads a basic example
- **WHEN** a user reads any basic example (e.g., `03-host-mount.md`)
- **THEN** they see a single `user_config.yml` snippet with only the fields relevant to that feature, an explanation of each field, and what happens when they build and run

### Requirement: Each doc example has a corresponding config in examples/
Every example doc page SHALL have a corresponding directory at `examples/{basic,advanced}/<slug>/` containing at minimum a `user_config.yml` file. The doc page SHALL reference this path (e.g., "Source: `examples/basic/minimal-ssh/user_config.yml`"). The embedded YAML in the doc page MUST match the content of the corresponding config file.

#### Scenario: User copies an example config
- **WHEN** a user wants to try an example
- **THEN** they find the source path referenced in the doc and can copy the `examples/<slug>/` directory

### Requirement: Basic examples are numbered for progressive learning
Basic examples SHALL be numbered (01–13+) in a progression from foundational (minimal SSH) to more specific features. Earlier examples SHALL NOT depend on understanding later ones. The slug directory names in `examples/basic/` do not need numbering — only the doc filenames are numbered.

#### Scenario: User follows examples in order
- **WHEN** a user reads examples 01 through 05 sequentially
- **THEN** each builds on general Docker/PeiDocker familiarity without requiring knowledge from later examples

### Requirement: Basic examples cover all major features
The basic examples set SHALL include at minimum: minimal SSH container, GPU enablement, host mount, docker volume, custom build script, port mapping, proxy setup, config-time env vars, compose-time env passthrough, pixi environment, conda environment, multi-user SSH, and APT mirrors.

#### Scenario: User looks for a specific feature example
- **WHEN** a user wants to learn about a specific feature (e.g., GPU)
- **THEN** they find a dedicated basic example for that feature

### Requirement: Examples directory has a README
The `examples/` directory at repo root SHALL contain a `README.md` that lists all examples with one-line descriptions and links to corresponding doc pages.

#### Scenario: User browses examples on GitHub
- **WHEN** a user navigates to the `examples/` directory on GitHub
- **THEN** they see a README listing all examples with descriptions and links to the full documentation

