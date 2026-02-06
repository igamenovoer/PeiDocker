# Spec: mount-path-resolution

## Purpose

Define deterministic rules for resolving mount destinations so storage keywords (`app`, `data`, `workspace`) cannot override explicit mount destinations, while remaining compatible with Docker Compose behavior.

## Requirements

### Requirement: Storage keywords are fixed
The system MUST treat storage keywords as a fixed set of `app`, `data`, and `workspace`.

#### Scenario: Storage keyword validation
- **WHEN** a configuration defines storage entries
- **THEN** only the fixed keywords `app`, `data`, and `workspace` are recognized as storage entries

### Requirement: Mount destinations honor explicit dst_path
The system MUST require an explicit absolute `dst_path` for each mount entry and MUST resolve mount destinations using that `dst_path`, regardless of the mount entry name.

#### Scenario: Mount name matches storage keyword
- **WHEN** a mount entry is named `data` but specifies `dst_path: /custom/data`
- **THEN** the resolved container destination is `/custom/data`

### Requirement: Name collisions do not imply conflicts
The system MUST treat storage and mount namespaces as unrelated; name collisions between storage and mount entries MUST NOT be treated as conflicts.

#### Scenario: Storage and mount share the same name
- **WHEN** storage defines `data` and mount defines a separate entry also named `data`
- **THEN** resolution proceeds without conflict as long as their resolved container destinations differ

### Requirement: Duplicate container destinations emit a warning
The system MUST emit a warning when multiple entries resolve to the same container destination path but MUST NOT reject the configuration.

#### Scenario: Duplicate container destination detected
- **WHEN** two entries resolve to the same container destination path by simple string matching
- **THEN** the system logs a warning using `logging.warning` and continues

### Requirement: Duplicate mount keys are invalid
The system MUST reject configurations that define duplicate mount keys during configuration parsing.

#### Scenario: Duplicate mount entries
- **WHEN** two mount entries share the same key
- **THEN** the configuration is rejected with an error

### Requirement: Duplicate mount keys are errors
The system MUST reject configurations when duplicate mount keys are detected.

#### Scenario: Duplicate mount key detected
- **WHEN** a duplicate mount key is found
- **THEN** the configuration is rejected with a clear error message
