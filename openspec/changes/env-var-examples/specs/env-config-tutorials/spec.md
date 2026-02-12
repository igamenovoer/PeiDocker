## ADDED Requirements

### Requirement: Provide three environment-variable tutorials
The documentation SHALL include three reproducible tutorials explaining how environment variables are handled in PeiDocker user config.

#### Scenario: Reader finds the three tutorials
- **WHEN** a reader opens the documentation site under the Examples section
- **THEN** they can navigate to three separate tutorials: basic (no passthrough), passthrough, and advanced

### Requirement: Tutorials use consistent local constraints
All tutorials SHALL:
- use `tmp/<subdir>/cases/<case-name>/` as the working directory for disposable projects and generated files
- use `ubuntu:24.04` as the base image for testing
- include guidance for downloads in constrained networks (China mirrors only; no proxy setup in examples)

#### Scenario: Reader follows tutorial commands on this host
- **WHEN** a reader executes the tutorial commands verbatim
- **THEN** each tutorial case is created under `tmp/<subdir>/cases/<case-name>/` and uses `ubuntu:24.04` as the configured base image

### Requirement: Tutorials include build and env verification
Each tutorial SHALL include verification steps that prove the case can be built and that environment variables are set as expected at runtime.

#### Scenario: Case verification validates build and runtime env
- **WHEN** the reader runs the tutorial verification steps for a case
- **THEN** image build succeeds and runtime output confirms the expected environment-variable values

### Requirement: Basic tutorial covers configure-time substitution only
The basic tutorial SHALL explain and demonstrate configure-time substitution using `${VAR}` and `${VAR:-default}` and SHALL avoid compose-time passthrough markers.

#### Scenario: Configure-time substitution produces concrete values
- **WHEN** the reader runs `pei-docker-cli configure` with environment variables set
- **THEN** the generated `docker-compose.yml` contains resolved concrete strings (no `{{...}}` passthrough markers)

### Requirement: Passthrough tutorial covers compose-time resolution
The passthrough tutorial SHALL explain and demonstrate compose-time passthrough markers using `{{VAR}}` and `{{VAR:-default}}`, including how they are emitted into `docker-compose.yml` as Compose `${...}` expressions and how `.env` / host env affects `docker compose`.

#### Scenario: Passthrough markers survive configure and resolve at compose-time
- **WHEN** the reader runs `pei-docker-cli configure` on a config that uses `{{VAR:-default}}`
- **THEN** the generated `docker-compose.yml` contains `${VAR:-default}` and `docker compose config` shows the resolved value

### Requirement: Advanced tutorial covers full env-handling surface area
The advanced tutorial SHALL demonstrate all supported env-handling functionality and guardrails, including:
- mixing `${...}` and `{{...}}` within a single string
- port mappings expressed as strings, including passthrough in ports
- failure modes for invalid/unresolved substitution
- guardrails that reject passthrough markers in unsupported contexts (merged builds, baked env, and script-baked contexts)

#### Scenario: Reader can recognize and avoid unsupported contexts
- **WHEN** a reader attempts a documented unsupported configuration (e.g., passthrough inside a script-baked context)
- **THEN** the tutorial explains the expected error and provides a supported alternative
