## Why

PeiDocker is currently at package version `1.2.7`, but the repository state on March 25, 2026 contains a large set of changes that are intended to ship as `2.0.0`. The GitHub release workflow already auto-publishes to PyPI when a release is published, so the remaining risk is not missing automation but releasing with inconsistent versioning, incomplete notes, or insufficient verification.

## What Changes

- Prepare an official `v2.0.0` release from the current `main` branch state.
- Update release-facing metadata so the package version, release tag, and release notes are aligned on `2.0.0`.
- Define a release checklist that verifies the repository is publish-ready before the GitHub release is created.
- Document the release-triggered PyPI publish path and the validations required immediately after publishing.
- Clarify the user-facing release notes and migration framing for the major-version bump.

## Capabilities

### New Capabilities

- `release-pypi-publishing`: Defines the required repository state, release metadata alignment, verification checklist, and release-triggered PyPI publication flow for official PeiDocker releases.

### Modified Capabilities

- None.

## Impact

- Affected areas: `pyproject.toml`, `RELEASE_NOTES.md`, release-facing documentation if needed, and the GitHub release workflow usage.
- Operational systems: GitHub Releases, GitHub Actions, PyPI publishing, and repository tagging/versioning practices.
- Validation impact: release prep must run the standard local quality gates and may optionally run the heavy Docker-backed runtime verification suite before publishing.
- No runtime product behavior changes are introduced by this change; it governs release preparation and publication correctness.
