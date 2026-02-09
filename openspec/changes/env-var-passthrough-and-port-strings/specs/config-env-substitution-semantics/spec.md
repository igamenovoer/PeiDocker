## ADDED Requirements

### Requirement: Config-time substitution expands ${VAR} from the configure environment
PeiDocker MUST support config-time substitution for `${VAR}` by expanding it using the environment variables of the process running `pei-docker-cli configure`.

#### Scenario: ${VAR} expanded during configure
- **WHEN** a config contains a value `${HOME}/workspace`
- **THEN** PeiDocker emits a concrete value with `$HOME` expanded in generated artifacts

### Requirement: Config-time substitution supports fallback defaults
PeiDocker MUST support config-time substitution for `${VAR:-default}` by using the value of `VAR` from the configure environment if set, and otherwise using `default`.

#### Scenario: Fallback default used when undefined
- **WHEN** a config contains a value `${BASE_IMAGE:-ubuntu:24.04}`
- **AND** `BASE_IMAGE` is not set in the configure environment
- **THEN** PeiDocker substitutes the value to `ubuntu:24.04`

### Requirement: Config-time substitution is recursive and string-only
PeiDocker MUST apply config-time substitution recursively to all string values across the user configuration structure (nested dicts/lists). Non-string values MUST remain unchanged.

#### Scenario: Substitution in nested structures
- **WHEN** a nested config value contains `${VAR:-x}` under a dict or list
- **THEN** PeiDocker substitutes it during configure

### Requirement: Config-time substitution does not modify passthrough markers
PeiDocker MUST NOT treat `{{...}}` passthrough markers as config-time substitution inputs, and MUST preserve them verbatim during config-time substitution.

#### Scenario: {{...}} is preserved during config-time substitution
- **WHEN** a config value contains `{{TAG:-dev}}`
- **THEN** config-time substitution leaves the value unchanged

### Requirement: No ${...} tokens may remain after config-time substitution
After config-time substitution runs, the resulting processed configuration MUST NOT contain any `${...}` sequences. If any remain, PeiDocker MUST fail with a clear error telling users to either set the relevant env var at configure time or use `{{...}}` passthrough markers.

#### Scenario: Undefined ${VAR} causes a clear error
- **WHEN** a config value contains `${UNDEFINED_VAR}`
- **AND** `UNDEFINED_VAR` is not set in the configure environment
- **THEN** `pei-docker-cli configure` fails with an error directing the user to use `{{UNDEFINED_VAR}}` for passthrough or set `UNDEFINED_VAR` before configuring

### Requirement: Defaults are not recursively interpreted
For `${VAR:-default}` config-time substitution, PeiDocker MUST treat `default` as a literal string and MUST NOT recursively interpret nested `${...}` tokens inside the default.

#### Scenario: Nested ${...} in a default is rejected via the no-leftover rule
- **WHEN** a config value is `${A:-${B}}` and `A` is not set
- **THEN** config-time substitution yields `${B}` as a literal string
- **AND** the configuration is rejected because a `${...}` token remains after substitution
