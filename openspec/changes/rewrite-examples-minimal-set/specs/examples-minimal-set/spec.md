## ADDED Requirements

### Requirement: Canonical example configs are shipped
PeiDocker SHALL ship a small canonical set of example configuration files under
`src/pei_docker/examples/` intended for new users and for `pei-docker-cli create
--with-examples`.

#### Scenario: Canonical example files exist in the repository
- **WHEN** the repository is checked out
- **THEN** the canonical examples exist as files under `src/pei_docker/examples/` with stable names

### Requirement: Canonical example set includes core and optional examples
The canonical examples SHALL be split into:

- **Core** examples (minimal, essential day-1 features)
- **Optional** examples (conditional or advanced, clearly labeled)

#### Scenario: Core and optional examples are both present
- **WHEN** a user inspects `src/pei_docker/examples/`
- **THEN** they can identify a core sequence and a separate optional set by filename convention and/or README

### Requirement: Core examples cover essential workflow and features
The core example set SHALL collectively demonstrate the recommended workflow:
`pei-docker-cli create` → edit `user_config.yml` → `pei-docker-cli configure` →
build/run with Docker/Compose.

The core example set SHALL collectively cover:
- Stage-1 vs Stage-2 mental model (base vs derived image output)
- Persistence via `stage_2.storage`
- At least one `stage_2.mount` entry using volume-based storage
- At least one `stage_2.ports` mapping
- At least one minimal `custom` hook usage
- Basic env semantics (configure-time `${...}` vs compose-time `{{...}}`)

#### Scenario: Each essential feature appears in at least one core example
- **WHEN** core examples are validated by repository checks/tests
- **THEN** the checks confirm each essential feature is represented at least once

### Requirement: Core examples are cross-platform by default
Core examples SHALL avoid requiring host-specific absolute bind-mount paths.
Core examples SHALL prefer volume-based storage types where possible.

#### Scenario: Core examples do not require host paths
- **WHEN** core examples are validated by repository checks/tests
- **THEN** the validation confirms core examples do not contain `host_path` fields

### Requirement: Optional examples include GPU, proxy/APT, and merged-build flows
The optional example set SHALL include at least:
- A GPU example demonstrating `device: gpu` (conditional on NVIDIA runtime)
- A proxy/APT acceleration example demonstrating proxy and APT mirror settings
- A merged-build-compatible example intended to be used with `--with-merged`

#### Scenario: Optional examples are present and labeled as optional
- **WHEN** a user inspects the examples index/README
- **THEN** it lists optional examples and calls out any prerequisites/constraints

### Requirement: Legacy examples are retained but not canonical
Historical examples MAY remain under `src/pei_docker/examples/legacy/`, but they
SHALL NOT be presented as the canonical “starting point” examples.

#### Scenario: Legacy examples are excluded from the default canonical index
- **WHEN** a user reads the examples index/README
- **THEN** it directs users to the canonical core/optional examples rather than `legacy/`

### Requirement: Project creation copies canonical examples and excludes legacy by default
When `pei-docker-cli create --with-examples` (and equivalent project creation
utilities) copies examples into a new project, it SHALL include canonical core
and optional examples (and `envs/` tutorials), and SHALL exclude `legacy/` by
default.

#### Scenario: Created project contains canonical examples without legacy
- **WHEN** a user runs `pei-docker-cli create -p <dir> --with-examples`
- **THEN** `<dir>/examples/` contains canonical examples and `envs/`, and does not contain `legacy/`
