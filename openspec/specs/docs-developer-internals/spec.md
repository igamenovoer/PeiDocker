# docs-developer-internals Specification

## Purpose
TBD - created by archiving change rewrite-docs-structure. Update Purpose after archive.
## Requirements
### Requirement: Architecture overview document
The architecture doc (`developer/architecture.md`) SHALL provide a system-level overview of PeiDocker's components: CLI entry points, config processor, template engine, stage builders, and entrypoint system. It SHALL include an architecture diagram (migrated from existing `internals-diagrams/`).

#### Scenario: New contributor understands the system
- **WHEN** a developer reads the architecture doc
- **THEN** they understand how the major components relate and where to find each in the source tree

### Requirement: Build pipeline documentation
The build pipeline doc (`developer/build-pipeline.md`) SHALL explain the full flow from `user_config.yml` → config processor → environment variable substitution → compose template rendering → `docker-compose.yml` output → generated scripts in `installation/stage-*/generated/`.

#### Scenario: Developer traces config to output
- **WHEN** a developer reads the build pipeline doc
- **THEN** they can trace how a specific config key (e.g., `ssh.enable: true`) becomes Docker build artifacts

### Requirement: Config processing documentation
The config processing doc (`developer/config-processing.md`) SHALL explain how `PeiConfigProcessor` parses each config section (SSH, APT, proxy, storage, custom scripts, ports) and generates corresponding Docker Compose entries and shell scripts.

#### Scenario: Developer adds a new config section
- **WHEN** a developer reads the config processing doc
- **THEN** they understand the pattern for adding a new config section to the processor

### Requirement: Contracts and interfaces documentation
The contracts doc (`developer/contracts.md`) SHALL document the interfaces between stages (stage-1 output → stage-2 input), the install script parameter interface, installer flag conventions, and stage-2 wrapper policies. It SHALL reference the relevant openspec specs.

#### Scenario: Developer writes a new system script
- **WHEN** a developer reads the contracts doc
- **THEN** they know the parameter interface, flag naming conventions, and wrapper policies their script must follow

### Requirement: Storage internals documentation
The storage internals doc (`developer/storage-internals.md`) SHALL explain the symlink strategy (`/soft/*` → `/hard/*`), how storage type switching works at the Docker level, and the mount path resolution logic.

#### Scenario: Developer debugs a storage issue
- **WHEN** a developer reads the storage internals doc
- **THEN** they understand the symlink structure and can trace how a user's `storage.app.type: host` becomes a Docker volume mount

### Requirement: Entrypoint system documentation
The entrypoint doc (`developer/entrypoint-system.md`) SHALL explain the entrypoint preparation phase, script handoff, logging, and SIGTERM handling. It SHALL reference the entrypoint openspec specs.

#### Scenario: Developer modifies entrypoint behavior
- **WHEN** a developer reads the entrypoint doc
- **THEN** they understand the preparation → handoff → logging flow and SIGTERM propagation

### Requirement: Environment variable processing documentation
The env var doc (`developer/env-var-processing.md`) SHALL explain the substitution engine implementation, the difference between config-time and compose-time processing, and how passthrough markers (`{{VAR}}`) are handled.

#### Scenario: Developer traces env var resolution
- **WHEN** a developer reads the env var processing doc
- **THEN** they can trace how `${VAR:-default}` and `{{VAR}}` are processed at different stages

### Requirement: Testing documentation
The testing doc (`developer/testing.md`) SHALL explain how to run unit and e2e tests, the e2e test framework, and how to add new tests.

#### Scenario: Developer runs the test suite
- **WHEN** a developer reads the testing doc
- **THEN** they can run the full test suite and add a new test for a feature they're building

### Requirement: Diagrams migrated and organized
Existing diagram assets from `docs/internals-diagrams/` SHALL be moved to `docs/developer/diagrams/` and referenced from the relevant developer docs.

#### Scenario: Developer views architecture diagram
- **WHEN** a developer reads the architecture doc
- **THEN** the embedded diagram renders correctly from `developer/diagrams/`

