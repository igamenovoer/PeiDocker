# docs-manual-concepts Specification

## Purpose
TBD - created by archiving change rewrite-docs-structure. Update Purpose after archive.
## Requirements
### Requirement: Two-stage architecture concept explanation
The two-stage architecture doc (`manual/concepts/two-stage-architecture.md`) SHALL explain the separation between stage-1 (system layer) and stage-2 (application layer), why this separation exists, what belongs in each stage, and how stage-2 builds on stage-1's output image.

#### Scenario: User decides which stage to use
- **WHEN** a user reads the two-stage architecture doc
- **THEN** they can determine whether a given configuration (e.g., SSH, custom script, apt mirror) belongs in stage-1 or stage-2

### Requirement: Storage model concept explanation
The storage model doc (`manual/concepts/storage-model.md`) SHALL explain the four storage types (auto-volume, manual-volume, host, image), the three fixed storage keys (app, data, workspace) with their default paths, and the difference between `storage` and `mount` configuration. It SHALL include a decision matrix for choosing storage types.

#### Scenario: User chooses between storage types
- **WHEN** a user reads the storage model doc
- **THEN** they can select the appropriate storage type for their use case (development vs production, persistent vs ephemeral)

### Requirement: Script lifecycle concept explanation
The script lifecycle doc (`manual/concepts/script-lifecycle.md`) SHALL explain the five lifecycle hooks (on_build, on_entry, on_first_run, on_every_run, on_user_login), their execution order, execution context (build-time vs runtime), and constraints (e.g., on_entry max 1 per stage).

#### Scenario: User places a custom script at the right lifecycle point
- **WHEN** a user reads the script lifecycle doc
- **THEN** they can determine which lifecycle hook to use for their script (e.g., "install a package" → on_build, "start a service" → on_every_run)

### Requirement: Environment variables concept explanation
The environment variables doc (`manual/concepts/environment-variables.md`) SHALL explain the two substitution modes: config-time (`${VAR:-default}`) and compose-time passthrough (`{{VAR}}`), when each is evaluated, and how to combine them. It SHALL include a comparison table.

#### Scenario: User understands when substitution happens
- **WHEN** a user reads the environment variables doc
- **THEN** they understand that `${VAR}` is resolved during `pei-docker-cli configure` while `{{VAR}}` is resolved during `docker compose up`

