# compose-env-passthrough-markers Specification

## Purpose
TBD - created by archiving change env-var-passthrough-and-port-strings. Update Purpose after archive.
## Requirements
### Requirement: Passthrough markers map to Docker Compose substitution
PeiDocker MUST support a compose-time passthrough marker syntax `{{VAR}}` that is emitted into the generated `docker-compose.yml` as the Docker Compose variable substitution form `${VAR}`.

#### Scenario: Passthrough marker in a compose-emitted value
- **WHEN** a user config value contains `{{PROJECT_NAME}}` and that value is emitted into `docker-compose.yml`
- **THEN** the emitted compose file contains `${PROJECT_NAME}` in the corresponding position

### Requirement: Passthrough markers support default values
PeiDocker MUST support `{{VAR:-default}}` and MUST emit it into the generated `docker-compose.yml` as `${VAR:-default}`.

#### Scenario: Passthrough marker with default
- **WHEN** a user config value contains `{{TAG:-dev}}` and that value is emitted into `docker-compose.yml`
- **THEN** the emitted compose file contains `${TAG:-dev}` in the corresponding position

### Requirement: Passthrough markers are not expanded during configuration parsing
PeiDocker MUST treat `{{...}}` passthrough markers as literal strings during config parsing and config-time substitution, and MUST NOT expand them using the host environment during `pei-docker-cli configure`.

#### Scenario: Marker survives config parsing
- **WHEN** a config value contains `{{VAR}}`
- **THEN** PeiDocker does not replace it with a host environment value during `configure`

### Requirement: Passthrough markers are allowed only when Docker Compose can interpolate them
Passthrough markers MUST be allowed only in values that end up in the generated `docker-compose.yml` (Docker Compose performs interpolation).

Note: `stage_?.environment` values are compose-emitted and are therefore permitted to contain passthrough markers (they become compose `environment:` entries). The fact that PeiDocker also generates `stage-?/generated/_etc_environment.sh` from stage environment values does not make them invalid unless env baking is enabled; the baking requirement below governs that case.

PeiDocker MUST reject passthrough markers in any configuration value that is:

- consumed by PeiDocker’s stage internals scripts under `installation/stage-{1,2}/internals/**` without going through Docker Compose substitution, or
- baked into PeiDocker-generated scripts at configure time in a way that Docker Compose cannot influence (i.e., Docker Compose has no opportunity to expand the value).

Rationale: `{{...}}` is a PeiDocker passthrough marker, not a shell expression. If it is embedded into scripts that are executed/sourced without Docker Compose interpolation, it will remain a literal string and silently misconfigure the system.

#### Scenario: Marker used in a generated internal script
- **WHEN** a configuration value containing a passthrough marker would be consumed by `installation/stage-{1,2}/internals/**` scripts without Docker Compose interpolation, or would be baked into a generated script at configure time
- **THEN** `pei-docker-cli configure` fails with a clear error explaining that `{{...}}` is supported only for values emitted into `docker-compose.yml`

### Requirement: Baking env into /etc/environment forbids passthrough markers
If env “baking” into `/etc/environment` is requested (via `PEI_BAKE_ENV_STAGE_1` or `PEI_BAKE_ENV_STAGE_2`), PeiDocker MUST reject any configuration where passthrough markers would be written into the baked environment data.

#### Scenario: Baking requested with passthrough markers in stage environment
- **WHEN** stage environment values include `{{...}}` passthrough markers
- **AND** env baking into `/etc/environment` is enabled
- **THEN** `pei-docker-cli configure` fails with a clear error stating that passthrough markers cannot be baked

### Requirement: Merged build artifacts are incompatible with passthrough markers (initial scope)
If `pei-docker-cli configure --with-merged` is requested, PeiDocker MUST reject the configuration when any passthrough markers are present.

#### Scenario: User requests merged artifacts with passthrough markers
- **WHEN** the configuration contains any `{{...}}` passthrough markers
- **AND** `pei-docker-cli configure --with-merged` is used
- **THEN** `pei-docker-cli configure` fails with a clear error explaining that passthrough markers are supported only for `docker-compose.yml` in the initial implementation

### Requirement: Passthrough markers in docker-run helper scripts are out of scope initially
If PeiDocker generates host-side helper scripts that invoke `docker run`, passthrough marker support MUST be explicitly implemented for those scripts (by rewriting `{{...}}` into a shell/compose-interpreted form). In the initial implementation, passthrough markers are supported only for `docker-compose.yml`.

#### Scenario: User expects docker-run passthrough behavior
- **WHEN** a user attempts to rely on `{{...}}` passthrough markers in a workflow that uses host-side `docker run` helper scripts
- **THEN** PeiDocker rejects the configuration (or the relevant command) with a clear error explaining the initial passthrough scope is `docker-compose.yml` only

### Requirement: Marker validation is strict and predictable
PeiDocker MUST validate passthrough markers as follows:

- Supported forms are only `{{VAR}}` and `{{VAR:-default}}`.
- `VAR` MUST match the regex `[A-Za-z_][A-Za-z0-9_]*`.
- Whitespace inside braces MAY be present and MUST be trimmed before validation (e.g. `{{ VAR }}` is treated as `{{VAR}}`).
- The default portion is treated opaquely, but it MUST NOT contain the terminator `}}`.

#### Scenario: Invalid passthrough marker is rejected
- **WHEN** a config contains a malformed passthrough marker (unsupported form, invalid var name, or default containing `}}`)
- **THEN** `pei-docker-cli configure` fails with a clear validation error identifying the invalid marker

### Requirement: Mixed-mode strings are supported
PeiDocker MUST allow a single string value to contain both config-time substitution tokens (`${...}`) and compose-time passthrough markers (`{{...}}`), as long as the `${...}` tokens are fully resolved during configure and the `{{...}}` markers are valid.

#### Scenario: Mixed-mode string in output image tag
- **WHEN** a config value is `"${PROJECT_NAME:-app}-{{TAG:-dev}}"`
- **THEN** PeiDocker expands `${PROJECT_NAME:-app}` during configure and emits `${TAG:-dev}` into `docker-compose.yml`

