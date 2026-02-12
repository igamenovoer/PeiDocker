# port-mapping-string-model Specification

## Purpose
TBD - created by archiving change env-var-passthrough-and-port-strings. Update Purpose after archive.
## Requirements
### Requirement: Port mappings are represented as strings
PeiDocker MUST treat `stage_1.ports` and `stage_2.ports` as ordered lists of Docker Compose-compatible port mapping strings, and MUST NOT require numeric parsing of those entries.

#### Scenario: Port entries are preserved as strings
- **WHEN** a user sets `stage_2.ports` to include the entry `"127.0.0.1:8080:80"`
- **THEN** the generated `docker-compose.yml` contains that exact port mapping entry under `services.stage-2.ports`

### Requirement: Stage-2 ports include stage-1 ports plus stage-2 ports
When generating stage-2 service configuration, PeiDocker MUST include stage-1 port entries and then append stage-2 port entries.

#### Scenario: Stage-2 inherits stage-1 ports
- **WHEN** stage-1 defines ports `["2222:22"]`
- **AND** stage-2 defines ports `["8080:80"]`
- **THEN** the generated stage-2 ports list contains both entries in that order

### Requirement: SSH host port mapping is expressed as a port mapping string
If SSH is enabled and an SSH host port mapping is configured, PeiDocker MUST express it as a Docker Compose port mapping string and include it in the appropriate service port list.

#### Scenario: SSH mapping is included as a port string
- **WHEN** SSH is enabled with container port `22` and host port `2222`
- **THEN** the generated compose includes a port mapping entry equivalent to `"2222:22"`

### Requirement: Port mappings may include passthrough markers
Port mapping strings MAY include passthrough markers `{{VAR}}` / `{{VAR:-default}}`, and PeiDocker MUST preserve them through processing and emit them into `docker-compose.yml` as Docker Compose `${...}` substitution expressions.

#### Scenario: Port mapping uses passthrough host port
- **WHEN** a port entry is `"{{SSH_HOST_PORT:-2222}}:22"`
- **THEN** the generated compose contains `"${SSH_HOST_PORT:-2222}:22"`

### Requirement: PeiDocker does not reject placeholder ports by parsing
PeiDocker MUST NOT reject port entries solely because they contain placeholders, and MUST defer validation of placeholder-containing port strings to Docker Compose.

#### Scenario: Placeholder port entry is accepted
- **WHEN** a port mapping entry contains passthrough markers
- **THEN** `pei-docker-cli configure` succeeds (assuming other validation passes) and emits the entry for Docker Compose to interpret

