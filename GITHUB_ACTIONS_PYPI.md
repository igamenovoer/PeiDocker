# GitHub Actions PyPI Publishing Workflow

This repository publishes to PyPI by creating a GitHub release. The workflow is defined in
`.github/workflows/publish-to-pypi.yml` and triggers on `release.published`.

## What the workflow does

1. Checks out the tagged source tree.
2. Sets up Python 3.11.
3. Installs `build` and `twine`.
4. Builds both the wheel and source distribution.
5. Runs `twine check dist/*`.
6. Uploads the package to PyPI using the `PYPI_API_TOKEN` repository secret.

## Release prerequisites

Before publishing a release:

1. Ensure the package version in `pyproject.toml` matches the intended release tag.
   Example: tag `v2.0.0` must build from a commit where `version = "2.0.0"`.
2. Update `RELEASE_NOTES.md` for the release.
3. Run the local validation gates you want on the release candidate, at minimum:
   ```bash
   pixi run test
   pixi run lint
   pixi run type-check
   pixi run -e dev docs-build
   ```
4. Confirm the repository secret `PYPI_API_TOKEN` still exists:
   ```bash
   gh secret list
   ```

## How to publish a release

### GitHub CLI

```bash
gh release create v2.0.0 \
  --title "v2.0.0: Major release" \
  --notes-file RELEASE_NOTES.md
```

### GitHub Web UI

1. Open: https://github.com/igamenovoer/PeiDocker/releases
2. Click `Draft a new release`
3. Create the tag `v2.0.0`
4. Paste or upload the release notes from `RELEASE_NOTES.md`
5. Publish the release

Publishing the release triggers the PyPI workflow automatically.

## Monitoring and verification

Check workflow status:

```bash
gh workflow list
gh run list --workflow "Publish to PyPI"
gh run view --log
```

GitHub Actions page:
https://github.com/igamenovoer/PeiDocker/actions

After the workflow succeeds, verify:

1. The Actions run completed successfully.
2. PyPI shows the new version:
   https://pypi.org/project/pei-docker/
3. The package can be installed:
   ```bash
   uv tool install pei-docker==2.0.0
   pei-docker-cli --help
   ```

## Troubleshooting

If publishing fails:

1. Check the workflow logs in GitHub Actions.
2. Confirm `PYPI_API_TOKEN` still exists and is valid.
3. Confirm the version in `pyproject.toml` is unique on PyPI.
4. Confirm the tagged commit contains the intended release metadata and notes.
