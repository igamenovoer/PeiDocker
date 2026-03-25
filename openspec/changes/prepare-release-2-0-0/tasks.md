## 1. Release Metadata Preparation

- [x] 1.1 Update [`pyproject.toml`](/data1/huangzhe/code/PeiDocker/pyproject.toml) from version `1.2.7` to `2.0.0`.
- [x] 1.2 Update [`RELEASE_NOTES.md`](/data1/huangzhe/code/PeiDocker/RELEASE_NOTES.md) with a `v2.0.0` release section that summarizes the major changes since `v1.2.7`.
- [x] 1.3 Add explicit migration or breaking-change notes for `2.0.0` where user behavior or documented workflows changed materially.
- [x] 1.4 Review release-facing docs and commands for stale version references or outdated release instructions, and update only the ones that are still user-relevant for `2.0.0`.

## 2. Release Readiness Validation

- [ ] 2.1 Confirm the release candidate branch is clean and that the intended release commit contains aligned version, notes, and tag expectations.
- [x] 2.2 Run `pixi run test`, `pixi run lint`, `pixi run type-check`, and `pixi run -e dev docs-build` on the `2.0.0` release candidate.
- [x] 2.3 Evaluate `pixi run test-basic-example-runtime` for the `2.0.0` release and record whether it was executed or intentionally deferred. Deferred for this metadata-only release-prep commit because the full runtime suite already passed across all 13 scenarios on 2026-03-24 UTC and no runtime code changed afterward.
- [x] 2.4 Verify that the GitHub `Publish to PyPI` workflow and the `PYPI_API_TOKEN` repository secret are still available before publication.

## 3. Release Publication

- [ ] 3.1 Commit and push the `2.0.0` release-prep changes to `main`.
- [ ] 3.2 Create and publish the GitHub release with tag `v2.0.0` from the prepared commit.
- [ ] 3.3 Ensure the published release uses the `v2.0.0` release notes content and is not left as a draft or prerelease.

## 4. Post-Publication Verification

- [ ] 4.1 Monitor the triggered `Publish to PyPI` GitHub Actions run and confirm it completes successfully.
- [ ] 4.2 Verify that PyPI reports `pei-docker` version `2.0.0` after publication.
- [ ] 4.3 Perform a basic installation sanity check for the released package, or record why it was deferred.
