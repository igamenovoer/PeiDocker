# Spec: entrypoint-e2e-functional-tests

## Purpose

Specify the required, manually triggered, Docker-backed functional test coverage for PeiDocker entrypoint runtime behavior (stage-1 and stage-2), including default-mode, custom `on_entry`, SSH-first validation, signal handling, and artifact capture.

## Requirements

### Requirement: Manual Triggered Entrypoint Functional Suite
The project MUST provide a Docker-backed functional test suite for entrypoint runtime behavior that runs only on explicit user invocation and is excluded from the default fast test path.

#### Scenario: Default test path excludes heavy suite
- **WHEN** developers run the default project test command
- **THEN** entrypoint E2E Docker tests are not executed automatically

#### Scenario: Manual invocation executes heavy suite
- **WHEN** developers run the documented manual entrypoint E2E test command
- **THEN** the Docker-backed entrypoint functional tests execute

### Requirement: Default Mode Matrix Coverage Across Stages
The functional suite MUST validate the discussed default-mode scenarios (`E01` through `E07`) against both stage-1 and stage-2 images with branch-specific expectations.

#### Scenario: Non-interactive no-arg fallback blocks
- **WHEN** a stage image is started with no runtime command in a non-interactive context
- **THEN** the test verifies the container remains running and confirms the expected fallback branch behavior

#### Scenario: Interactive stdin fallback uses bash
- **WHEN** a stage image is started with `-i` and no runtime command
- **THEN** the test verifies the interactive fallback branch and associated runtime observables

#### Scenario: Option and passthrough command behavior is preserved
- **WHEN** default-mode options and passthrough commands are run for the stage image
- **THEN** the test verifies expected exit status, command handoff behavior, and branch-identifying logs

### Requirement: Custom On-Entry Matrix Coverage
The functional suite MUST validate custom `on_entry` behavior for scenarios `C01` through `C06`, including wrapper selection precedence, runtime argument forwarding, and hard-failure behavior when configured targets are missing.

#### Scenario: Stage-2 wrapper precedence is enforced
- **WHEN** both stage-1 and stage-2 custom wrappers are present
- **THEN** the test verifies stage-2 custom execution is selected and stage-1 custom execution is not selected

#### Scenario: Missing custom target script fails hard
- **WHEN** runtime invokes a configured custom wrapper whose target script is missing
- **THEN** the test verifies the container exits non-zero and does not fall back to bash or sleep branches

### Requirement: SSH-First Runtime Validation
For blocking runtime branches, the functional suite MUST verify SSH service availability and successful minimal SSH session commands in addition to container liveness checks.

#### Scenario: SSH login succeeds on blocking branch
- **WHEN** a blocking branch test case starts a container and maps SSH access
- **THEN** the test verifies a successful SSH login and at least one smoke command execution in the SSH session

### Requirement: Signal Handling Coverage
The functional suite MUST verify that the non-interactive blocking fallback (`S01`) responds correctly to `SIGTERM` by exiting promptly.

#### Scenario: SIGTERM terminates sleep-fallback container
- **WHEN** a container is running in non-interactive blocking fallback mode and receives `SIGTERM`
- **THEN** the test verifies the container exits within a bounded timeout

### Requirement: Reproducible Artifact Capture
The functional suite MUST persist logs and execution artifacts under a dedicated tmp root so failures are inspectable after test completion.

#### Scenario: Logs are captured under dedicated tmp root
- **WHEN** an entrypoint E2E test run completes
- **THEN** command transcripts and container logs are available under the documented tmp artifact directory structure
