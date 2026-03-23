## ADDED Requirements

### Requirement: Docs provide a runnable stage-1-only beginner path

The docs SHALL provide a runnable beginner-facing stage-1-only path that shows how to omit `stage_2` and how to build and run the resulting project.

#### Scenario: User wants the simplest SSH-ready container
- **WHEN** a user wants a minimal project with only stage-1
- **THEN** the docs show a minimal runnable config or config variant plus the commands needed to configure, build, run, and connect

### Requirement: Docs provide a concrete merged-build beginner path

The docs SHALL provide a concrete merged-build walkthrough that shows how to generate merged artifacts and use them to build and run the final image.

#### Scenario: User wants a plain docker-build workflow
- **WHEN** a user wants to avoid the default Compose build path
- **THEN** the docs show `pei-docker-cli configure --with-merged`, identify the generated artifacts, and show the commands used to build and run the merged image

#### Scenario: User evaluates merged-build constraints
- **WHEN** a user reads the merged-build walkthrough
- **THEN** the docs mention at least one important workflow constraint that affects first-time usage, including the incompatibility with passthrough markers

### Requirement: Example-facing docs surface the alternative paths

The example indexes or entry-point example docs SHALL point readers to the stage-1-only and merged-build guidance so the default minimal example is not mistaken for the only beginner workflow.

#### Scenario: User opens the minimal example first
- **WHEN** a user starts with the minimal SSH example instead of the manual
- **THEN** the page points them to the stage-1-only variant guidance and to the merged-build workflow guidance

#### Scenario: User browses examples from the repo root or docs index
- **WHEN** a user scans the examples index or examples README to choose a starting point
- **THEN** they can discover that beginner guidance exists for both stage-1-only and merged-build usage
