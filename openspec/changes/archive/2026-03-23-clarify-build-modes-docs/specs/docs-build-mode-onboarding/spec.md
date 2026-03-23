## ADDED Requirements

### Requirement: First-time docs expose build-mode choice before quickstart

The published docs SHALL expose PeiDocker’s supported build modes in the first-time-user path before the default quickstart is presented as the main workflow.

#### Scenario: User enters from the docs home page
- **WHEN** a first-time user starts from the docs home page and follows the getting-started path
- **THEN** they are directed to a build-modes explanation before or alongside the quickstart entry point

#### Scenario: User finishes installation and looks for the next step
- **WHEN** a user reads the installation guide and looks for what to read next
- **THEN** the docs point them to a build-modes explanation that clarifies available workflow choices

### Requirement: Build-mode docs define three distinct supported modes

The docs SHALL define and distinguish these three modes:

- stage-1-only
- two-stage Compose
- merged build

The docs SHALL explicitly state that merged build is not the same as omitting `stage_2`.

#### Scenario: User compares stage-1-only and merged build
- **WHEN** a user wants “only one stage” or “one docker build command”
- **THEN** the docs explain which choice changes the config shape and which choice changes only the build workflow

#### Scenario: User wants to choose a mode quickly
- **WHEN** a user scans the build-modes explanation
- **THEN** the docs provide a concise decision-oriented summary of each mode, including what config shape and build/run commands each one implies

### Requirement: Supporting docs declare their mode context consistently

The quickstart, project-structure, concepts, and CLI-reference pages SHALL use terminology consistent with the build-modes page and SHALL identify when they are describing the default two-stage Compose workflow versus an alternative mode.

#### Scenario: User reads the quickstart
- **WHEN** a user follows the quickstart page
- **THEN** the page states that it demonstrates the default two-stage Compose workflow and links to the stage-1-only and merged-build alternatives

#### Scenario: User reads the two-stage architecture page
- **WHEN** a user opens the architecture/concepts page after learning about build modes
- **THEN** the page explains how the two-stage model relates to stage-1-only usage and merged-build usage instead of implying that two stages are always required
