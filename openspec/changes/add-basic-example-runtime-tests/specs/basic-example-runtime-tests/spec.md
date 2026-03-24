## ADDED Requirements

### Requirement: Basic example docs and packaged assets stay aligned
The project MUST provide automatic tests that verify the basic example docs continue to match the packaged example assets.

#### Scenario: Documented example source exists
- **WHEN** a docs page under `docs/examples/basic/` references an example source path
- **THEN** the referenced packaged example asset exists under `src/pei_docker/examples/basic/`

#### Scenario: Documented supporting files exist
- **WHEN** a docs page says an example requires additional supporting files
- **THEN** those supporting files exist in the packaged example subtree

#### Scenario: Documented config remains aligned
- **WHEN** a docs page embeds the example config snippet
- **THEN** the embedded config remains aligned with the packaged `user_config.yml` for that example

### Requirement: Pytest-driven opt-in basic example runtime suite
The project MUST provide a pytest-driven Docker-backed functional suite for the packaged basic examples. The Docker-heavy suite MUST be excluded from the default fast test path and MUST run only on explicit user invocation.

#### Scenario: Default test path excludes heavy example suite
- **WHEN** developers run the default project test command
- **THEN** the basic example runtime suite is not executed automatically

#### Scenario: Explicit invocation executes heavy example suite
- **WHEN** developers run the documented raw pytest command or equivalent Pixi task for the basic example runtime suite
- **THEN** the suite builds and runs the selected packaged basic examples

### Requirement: Basic example runtime coverage is implemented as pytest tests
The runtime suite MUST be implemented as pytest tests using pytest assertions and reusable fixtures or helpers for orchestration, rather than only as ad hoc shell-script checks.

#### Scenario: Example scenario is selectable in pytest
- **WHEN** developers request the basic example runtime suite through pytest
- **THEN** individual example scenarios are collected and selectable as pytest tests

### Requirement: Runtime suite isolates scenario resources automatically
The runtime harness MUST isolate scenario resources automatically so repeated or concurrent local runs do not depend on the packaged examples' fixed host ports or image names.

#### Scenario: Run-scoped ports and names are used
- **WHEN** a basic example runtime scenario runs
- **THEN** the harness uses run-scoped project/image identifiers and host-port assignments needed for that scenario

### Requirement: Packaged basic examples are verified after build and startup
The suite MUST turn each packaged basic example into a runnable project, build its stage-2 image, start the example container, and verify runtime observables that match the example's documented purpose.

#### Scenario: Minimal SSH example proves non-root login
- **WHEN** the `minimal-ssh` example is built and started
- **THEN** the configured non-root user can log in and execute a minimal shell command successfully

#### Scenario: GPU example exposes expected runtime configuration
- **WHEN** the `gpu-container` example is built and started
- **THEN** the configured non-root user observes the expected GPU-related runtime configuration for that example

#### Scenario: Host mount example proves host-backed workspace
- **WHEN** the `host-mount` example is built and started
- **THEN** data written through the container workspace path is observable in the configured host workspace path

#### Scenario: Docker volume example proves persistence across recreation
- **WHEN** the `docker-volume` example is built, started, stopped, and started again
- **THEN** data written to the persistent example storage remains available after recreation

#### Scenario: Custom script example proves build hook effect
- **WHEN** the `custom-script` example is built and started
- **THEN** the runtime container contains the expected artifact created by the configured build hook

#### Scenario: Port mapping example exposes declared ports
- **WHEN** the `port-mapping` example is built and started
- **THEN** the declared host/container mappings are observable from the host according to the example configuration

#### Scenario: Proxy example reflects invoking proxy behavior
- **WHEN** the `proxy-setup` example is built and started with proxy environment available
- **THEN** the example uses the invoking proxy configuration during build and the runtime container reflects the configured proxy cleanup behavior

#### Scenario: Configure-time env example resolves before runtime
- **WHEN** the `env-variables` example is configured with explicit environment values, then built and started
- **THEN** the runtime container exposes concrete resolved values rather than unresolved config-time placeholders

#### Scenario: Compose-time env passthrough resolves at startup
- **WHEN** the `env-passthrough` example is configured, started with explicit compose-time environment values, and inspected at runtime
- **THEN** the runtime container exposes the resolved compose-time values for the passthrough fields

#### Scenario: Pixi example provides user-scoped tooling
- **WHEN** the `pixi-environment` example is built and started
- **THEN** the configured non-root user can run `pixi` and use the example-installed packages from that user's session

#### Scenario: Conda example provides login-time Conda usability
- **WHEN** the `conda-environment` example is built and started
- **THEN** the configured non-root user receives a usable Conda login session consistent with the example's setup hooks

#### Scenario: Multi-user example provides non-root access for multiple users
- **WHEN** the `multi-user-ssh` example is built and started
- **THEN** each configured non-root user covered by the example can log in and use a minimal session successfully

#### Scenario: Multi-user example installs packaged public key
- **WHEN** the `multi-user-ssh` example is built and started
- **THEN** the configured packaged public key for the relevant user is present in that user's SSH authorization setup

#### Scenario: APT mirror example reflects selected mirror configuration
- **WHEN** the `apt-mirrors` example is built and started
- **THEN** the runtime container exposes APT source configuration matching the selected mirror behavior

### Requirement: Non-root users are the primary verification subjects
The suite MUST execute tool availability and runtime usability checks as configured non-root users. When an example also defines `root`, the suite MAY verify root account existence but MUST NOT require root-targeted tool-installation checks.

#### Scenario: Tool checks run as configured non-root users
- **WHEN** an example defines one or more non-root users
- **THEN** the suite performs login and tool-availability assertions through those non-root user sessions

#### Scenario: Root is not a required tool-installation target
- **WHEN** an example defines a `root` account in addition to non-root users
- **THEN** the suite does not treat root as the required subject for tool-availability assertions

### Requirement: Proxy-sensitive scenarios follow invoking shell environment
Proxy-sensitive scenarios MUST derive their proxy configuration from the invoking shell environment. If no relevant proxy environment variables are set, those scenarios MUST be skipped with a clear reason.

#### Scenario: Proxy environment is available
- **WHEN** the invoking shell provides relevant proxy environment variables
- **THEN** the proxy-sensitive scenario uses those values as the source of proxy configuration

#### Scenario: Proxy cleanup is visible at runtime
- **WHEN** the proxy scenario is built with cleanup enabled
- **THEN** runtime shell proxy variables and APT proxy configuration reflect the configured cleanup behavior

#### Scenario: Proxy environment is absent
- **WHEN** the invoking shell does not provide relevant proxy environment variables
- **THEN** the proxy-sensitive scenario is skipped and reports that no proxy environment was available

### Requirement: Runtime suite preserves documented environment-resolution semantics
The runtime harness MUST preserve the documented distinction between configure-time `${...}` substitution and compose-time `{{...}}` passthrough when preparing and running scenarios.

#### Scenario: Mixed env example preserves both resolution phases
- **WHEN** a scenario uses both `${...}` and `{{...}}` forms
- **THEN** configure-time values resolve during configuration and compose-time values remain available for resolution at container startup

### Requirement: Runtime suite guarantees cleanup of example resources
The harness MUST tear down scenario resources after each example run, including containers, compose-created volumes, and the stage-1 and stage-2 images built for that scenario.

#### Scenario: Cleanup runs after a successful scenario
- **WHEN** an example scenario completes successfully
- **THEN** the harness removes the scenario's containers, compose-created volumes, and built images

#### Scenario: Cleanup runs after a failing scenario
- **WHEN** an example scenario fails after creating runtime resources
- **THEN** the harness still attempts teardown of the scenario's containers, compose-created volumes, and built images

### Requirement: Runtime artifacts are retained for debugging
The suite MUST retain generated projects, command transcripts, and relevant logs under a dedicated tmp artifact root so failures remain inspectable after the run.

#### Scenario: Example run artifacts are preserved
- **WHEN** a basic example runtime test run completes
- **THEN** the generated project files and logs for the scenario are available under the documented tmp artifact directory
