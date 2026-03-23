# docs-manual-troubleshooting Specification

## Purpose
TBD - created by archiving change rewrite-docs-structure. Update Purpose after archive.
## Requirements
### Requirement: Troubleshooting guide covers common errors
The troubleshooting guide (`manual/troubleshooting.md`) SHALL document common errors encountered during create, configure, build, and run phases, with symptoms, causes, and resolution steps.

#### Scenario: User encounters a build error
- **WHEN** a user's docker build fails and they check troubleshooting
- **THEN** they find their error symptom listed with a cause and fix

### Requirement: Troubleshooting includes known issues
The troubleshooting guide SHALL include a known issues section documenting current limitations and workarounds, sourced from `context/issues/known/`.

#### Scenario: User hits a known issue
- **WHEN** a user encounters a known issue (e.g., env var passthrough edge case, SIGTERM/sleep)
- **THEN** they find it documented with a workaround

### Requirement: Troubleshooting includes FAQ
The troubleshooting guide SHALL include a FAQ section addressing common questions about PeiDocker usage patterns, configuration choices, and Docker concepts.

#### Scenario: User has a conceptual question
- **WHEN** a user wonders "can I use PeiDocker with Podman?" or "how do I update my container without losing data?"
- **THEN** they find the answer in the FAQ

