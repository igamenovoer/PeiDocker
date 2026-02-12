# env-build-run-walkthrough Specification

## Purpose
TBD - created by archiving change env-var-examples. Update Purpose after archive.
## Requirements
### Requirement: Provide an env-focused build-and-run walkthrough
The documentation SHALL include an env-focused build-and-run walkthrough that takes a reader from project creation through configure/build/run and basic validation.

#### Scenario: Reader follows the walkthrough end-to-end
- **WHEN** a reader follows the walkthrough steps in order
- **THEN** they can create a project, generate `docker-compose.yml`, build images, start containers, and confirm the environment is running

### Requirement: Walkthrough uses a disposable workspace
The walkthrough SHALL use `tmp/<subdir>/cases/<case-name>/` as the project directory structure and SHALL describe how to clean up the created artifacts.

#### Scenario: Walkthrough does not pollute the workspace
- **WHEN** a reader completes the walkthrough
- **THEN** all created files are contained under `tmp/<subdir>/cases/` and can be removed safely

### Requirement: Walkthrough pins base image to ubuntu:24.04
The walkthrough SHALL configure the system base image to `ubuntu:24.04` for testing on this host.

#### Scenario: Base image is set explicitly
- **WHEN** the reader runs the walkthrough with the documented settings
- **THEN** the configured build uses `ubuntu:24.04` as the stage base image

### Requirement: Walkthrough includes download/network guidance
The walkthrough SHALL include guidance for environments with download/network issues by recommending China-based mirrors, and SHALL avoid proxy setup in example steps.

#### Scenario: Reader applies mirror guidance before build
- **WHEN** the reader needs to download packages during image build
- **THEN** the walkthrough shows how to apply mirror guidance before running the build

### Requirement: Walkthrough includes validation commands
The walkthrough SHALL include validation commands and expected signals that confirm successful image builds and correct runtime environment values (e.g., `docker compose build`, `docker compose config`, `docker compose ps`, and an env-inspection command in a running container).

#### Scenario: Reader can confirm the environment is running
- **WHEN** the reader runs the validation commands
- **THEN** they can see that images build successfully, containers are up, and runtime environment values match tutorial expectations

