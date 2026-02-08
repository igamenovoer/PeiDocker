# Spec: single-dockerfile-ci-install-flow

## Purpose

Define the requirements for a single `docker build` flow and clarify build-time path constraints for stage-2 custom build hooks.

## Requirements

### Requirement: PeiDocker supports a single docker build flow
The system MUST support generating a standalone multi-stage Dockerfile and helper scripts such that users can build the final image using a single `docker build` invocation (without Docker Compose).

#### Scenario: Generate merged artifacts
- **WHEN** a user runs `pei-docker-cli configure --with-merged`
- **THEN** the project contains `merged.Dockerfile`, `merged.env`, and `build-merged.sh` for a single `docker build` flow

### Requirement: Build-time scripts do not require /soft symlinks
Scripts intended to run during image build (e.g. `custom.on_build`) MUST NOT require `/soft/app`, `/soft/data`, or `/soft/workspace` to exist because stage-2 runtime symlink creation happens after container start.

#### Scenario: Build-time installer uses explicit flags
- **WHEN** a build-time script needs a non-default cache or install location
- **THEN** the caller can pass explicit tool-specific flags targeting `/hard/image/...` paths so the results are baked into the image layer

### Requirement: Build-time script arguments reject runtime-only paths
The system MUST reject configurations where build-time script invocations (`custom.on_build`) pass runtime-only storage paths (including `/soft/...` and `/hard/volume/...`) as tool-specific path flags. The rejection SHOULD happen during configuration parsing as early as possible.

#### Scenario: on_build passes /soft path
- **WHEN** a user configures an `on_build` script invocation that includes a `/soft/...` path, or uses a PeiDocker-defined env var token that expands to a `/soft/...` path (e.g. `$PEI_SOFT_DATA`, `$PEI_PATH_SOFT`)
- **THEN** configuration parsing fails with a clear error explaining that `/soft/...` is not available during build

#### Scenario: on_build passes /hard/volume path
- **WHEN** a user configures an `on_build` script invocation that includes a `/hard/volume/...` path
- **THEN** configuration parsing fails with a clear error explaining that mounted volumes are not available during build

### Requirement: Build modes are preserved
The system MUST preserve the ability for users to choose among:

- stage-1 only (ignore stage-2)
- stage-1 and stage-2 built separately
- stage-1 and stage-2 built via merged artifacts (single `docker build`)

#### Scenario: User chooses stage-1 only
- **WHEN** a user builds only stage-1
- **THEN** the system does not require stage-2 artifacts or stage-2 storage semantics to be used

#### Scenario: User chooses separate stage builds
- **WHEN** a user builds stage-1 and then stage-2 separately
- **THEN** stage-2 builds from stage-1 and can run stage-2 scripts as configured

#### Scenario: User chooses merged build
- **WHEN** a user uses `merged.Dockerfile` and `build-merged.sh`
- **THEN** the final stage-2 image can be built via a single `docker build` command

### Requirement: Documentation includes a minimal CI-style example
Documentation MUST provide a minimal example showing how to invoke a representative set of installers during a single `docker build` flow without relying on `/soft/*`.

#### Scenario: Reader follows the example
- **WHEN** a user follows the documented minimal example
- **THEN** they can run installers during `docker build` using explicit tool-specific flags and obtain a provisioned image
