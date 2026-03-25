## Context

PeiDocker already has an active GitHub Actions workflow that publishes to PyPI when a GitHub release is published. The current release automation is therefore not missing; the critical issue is release correctness. On March 25, 2026, the repository is clean on `main`, the package version in `pyproject.toml` is still `1.2.7`, PyPI’s latest published version is `1.2.7`, and the `Publish to PyPI` workflow has a recent successful run for `v1.2.7`.

The `2.0.0` release is intended to ship a substantial set of changes already present on `main`, including example restructuring, docs rewrites, installer migration work, environment passthrough changes, entrypoint fixes, and the new automatic example verification suite. Because the publication path is triggered by `release.published`, the design must ensure that:

1. the repository contents being tagged are internally consistent
2. the release notes justify the major-version bump
3. the GitHub release event produces the intended PyPI upload without manual patch-up work

## Goals / Non-Goals

**Goals:**
- Prepare `main` for an official `v2.0.0` release using the existing release-triggered PyPI workflow.
- Align release-critical metadata across package version, git tag, and release notes.
- Define the minimum validation gates that must pass before creating the GitHub release.
- Capture the operational release flow, including post-release verification of GitHub Actions and PyPI state.
- Keep the release-prep work narrow enough to execute as a single release commit plus a GitHub release action.

**Non-Goals:**
- Replacing the current token-based PyPI upload workflow with PyPI Trusted Publishing.
- Redesigning the package build backend, artifact contents, or general CI topology.
- Archiving unrelated OpenSpec changes as part of the release unless explicitly requested.
- Requiring every optional heavy runtime verification on every future patch release.
- Making additional product-scope changes unrelated to release readiness.

## Decisions

1. **Use the existing `release.published` GitHub Actions workflow as-is**
   - The repo already has [`.github/workflows/publish-to-pypi.yml`](/data1/huangzhe/code/PeiDocker/.github/workflows/publish-to-pypi.yml), and recent history shows successful release-triggered publishes through `v1.2.7`.
   - The release change will therefore focus on preparing a correct release input, not changing the automation mechanism.
   - Alternative considered: switch to Trusted Publishing first. Rejected for this release because it expands scope and is not necessary for `2.0.0`.

2. **Treat version alignment as a hard release gate**
   - The tagged commit must satisfy all of the following before the GitHub release is published:
     - [`pyproject.toml`](/data1/huangzhe/code/PeiDocker/pyproject.toml) version is `2.0.0`
     - the GitHub release tag is `v2.0.0`
     - release notes describe `v2.0.0`
   - This is necessary because the publish workflow builds from the tagged source tree and does not independently validate tag/package-version alignment.
   - Alternative considered: rely on tag naming alone. Rejected because PyPI uploads use the package metadata from the build artifacts, not the Git tag.

3. **Use a release-prep checklist instead of adding new workflow gates**
   - The change will define a concrete pre-release checklist:
     - clean working tree on `main`
     - version bump committed
     - release notes updated
     - `pixi run test`
     - `pixi run lint`
     - `pixi run type-check`
     - `pixi run -e dev docs-build`
     - optional heavy validation: `pixi run test-basic-example-runtime`
   - This keeps the release mechanics explicit and reproducible without requiring CI workflow edits immediately before release.
   - Alternative considered: add new mandatory GitHub workflow gating before release. Rejected for this change because the release is imminent and local validation already reflects current maintainer practice.

4. **Frame `2.0.0` as a major release with migration notes**
   - The release notes must summarize the major themes since `v1.2.7` and explicitly identify breaking or behaviorally significant changes.
   - The release notes should also include a short migration section for users impacted by environment passthrough, example layout changes, or docs/navigation changes.
   - Alternative considered: treat this as a large patch/minor release. Rejected because the repo history includes an explicit breaking-change marker and a broad enough surface-area shift to warrant a major version.

5. **Require post-release verification of both GitHub Actions and PyPI**
   - The release process does not end at `gh release create`. It must include:
     - checking that the `Publish to PyPI` workflow run starts and succeeds
     - verifying PyPI now reports `2.0.0`
     - optionally verifying installability with a fresh `uv tool install` or `pip install`
   - Alternative considered: trust the workflow and stop at release publication. Rejected because release success is only meaningful once the package is visible and installable.

## Risks / Trade-offs

- **[Risk] Tag/version mismatch causes failed or misleading publication** → **Mitigation**: make version alignment an explicit release gate and update all release-facing files in one release-prep commit.
- **[Risk] The `2.0.0` scope is not clearly justified to users** → **Mitigation**: include a concise major-release summary plus migration notes in `RELEASE_NOTES.md`.
- **[Risk] Local validation misses environment-sensitive regressions** → **Mitigation**: treat the heavy Docker-backed example suite as strongly recommended for this major release, even if it remains optional in general.
- **[Risk] Publishing fails because the PyPI token is stale or permissions changed** → **Mitigation**: verify the `PYPI_API_TOKEN` repository secret exists before release and monitor the release-triggered workflow immediately after publication.
- **[Risk] Additional cleanup or archival work distracts from release readiness** → **Mitigation**: scope the change to release preparation only and defer unrelated hygiene work unless it blocks the release.

## Migration Plan

1. Update package version metadata from `1.2.7` to `2.0.0`.
2. Refresh `RELEASE_NOTES.md` with a `v2.0.0` section that summarizes changes, breaking points, and migration notes.
3. Update any release-facing docs that still imply `1.2.7` or outdated release mechanics, if such references are found.
4. Run the defined pre-release validation checklist on the release candidate commit.
5. Commit and push the release-prep changes to `main`.
6. Create and publish the GitHub release tag `v2.0.0`.
7. Monitor the `Publish to PyPI` workflow and verify the `2.0.0` package appears on PyPI.

## Open Questions

- Should this release change also archive the completed `add-basic-example-runtime-tests` OpenSpec change for repo hygiene, or should that stay separate from release prep?
- Do we want to document a single canonical install verification command after release, or keep both `uv tool install` and `pip install` paths in the release checklist?
