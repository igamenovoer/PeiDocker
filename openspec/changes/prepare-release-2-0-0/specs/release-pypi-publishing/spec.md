## ADDED Requirements

### Requirement: Release candidate metadata aligns before publication
The repository SHALL align package version metadata, release notes, and release tag naming before an official PeiDocker release is published to GitHub.

#### Scenario: Preparing the `2.0.0` release commit
- **WHEN** maintainers prepare the `2.0.0` release candidate on `main`
- **THEN** [`pyproject.toml`](/data1/huangzhe/code/PeiDocker/pyproject.toml) MUST declare version `2.0.0`
- **AND** [`RELEASE_NOTES.md`](/data1/huangzhe/code/PeiDocker/RELEASE_NOTES.md) MUST include release notes for `v2.0.0`
- **AND** the intended GitHub release tag MUST be `v2.0.0`

#### Scenario: Preventing tag/package drift
- **WHEN** a maintainer is about to publish a GitHub release
- **THEN** the tagged commit MUST already contain the package version that matches the release tag without relying on post-tag edits

### Requirement: Official releases pass a defined readiness checklist
An official PeiDocker release SHALL complete a documented pre-publication readiness checklist before the GitHub release is created.

#### Scenario: Standard release verification
- **WHEN** maintainers prepare an official release candidate
- **THEN** they MUST confirm the working tree is clean on the release branch
- **AND** they MUST run and review the results of `pixi run test`, `pixi run lint`, `pixi run type-check`, and `pixi run -e dev docs-build`

#### Scenario: Major release performs extended validation
- **WHEN** maintainers prepare a major release such as `2.0.0`
- **THEN** they MUST evaluate the Docker-backed example verification suite as part of release readiness
- **AND** the release checklist MUST record whether `pixi run test-basic-example-runtime` was executed or explicitly deferred

### Requirement: GitHub release publication drives PyPI publishing
Official PeiDocker releases SHALL publish to PyPI by publishing a non-draft, non-prerelease GitHub release that triggers the repository’s release workflow.

#### Scenario: Publishing `v2.0.0`
- **WHEN** a maintainer publishes the GitHub release `v2.0.0`
- **THEN** the `Publish to PyPI` GitHub Actions workflow MUST be triggered from the `release.published` event
- **AND** the workflow MUST build the package from the tagged source tree before attempting upload

#### Scenario: Repository secret dependency is present
- **WHEN** maintainers prepare to use the release-triggered publish flow
- **THEN** the repository MUST have a configured `PYPI_API_TOKEN` secret available to the publish workflow

### Requirement: Release completion includes post-publication verification
Official PeiDocker releases SHALL not be treated as complete until the publish workflow and resulting PyPI artifact have been verified.

#### Scenario: Confirming GitHub Actions success
- **WHEN** a GitHub release has been published
- **THEN** maintainers MUST check that the triggered `Publish to PyPI` workflow run completed successfully

#### Scenario: Confirming PyPI visibility
- **WHEN** the publish workflow finishes successfully
- **THEN** maintainers MUST verify that PyPI reports the newly released package version
- **AND** the verified version MUST match the GitHub release tag and package metadata

### Requirement: Major-version release notes explain migration impact
Major PeiDocker releases SHALL include release notes that summarize key changes and call out migration-relevant behavior shifts.

#### Scenario: Writing `v2.0.0` notes
- **WHEN** maintainers prepare release notes for `v2.0.0`
- **THEN** the notes MUST summarize the major themes of change since `v1.2.7`
- **AND** they MUST identify breaking or migration-relevant changes for existing users
