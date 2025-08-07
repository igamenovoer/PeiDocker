# PyPI Upload Instructions

## ✅ Release Preparation Complete!

The PeiDocker v1.0.0 package has been successfully prepared for PyPI publication:

- ✅ Version updated to 1.0.0
- ✅ PR #3 merged to main branch
- ✅ GitHub release created: https://github.com/igamenovoer/PeiDocker/releases/tag/v1.0.0
- ✅ Package built successfully
- ✅ Package validation passed

## 📦 Package Files

The following distribution files are ready in the `dist/` directory:
- `pei_docker-1.0.0.tar.gz` (source distribution)
- `pei_docker-1.0.0-py3-none-any.whl` (wheel distribution)

## 🚀 Publishing to PyPI

### Option 1: Publish to PyPI (Production)

```bash
python -m twine upload dist/*
```

You will be prompted for:
- Username: `__token__` (use exactly this string)
- Password: Your PyPI API token (starts with `pypi-`)

### Option 2: Test on TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps pei-docker

# If everything works, upload to production PyPI
python -m twine upload dist/*
```

## 🔑 Getting PyPI Credentials

If you don't have a PyPI API token yet:

1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens" section
3. Click "Add API token"
4. Give it a name (e.g., "pei-docker-upload")
5. Set scope to "Entire account" or specific to "pei-docker" project
6. Copy the token (starts with `pypi-`)
7. Store it securely

## 📝 Post-Upload Checklist

After successful upload:

1. ✅ Verify package on PyPI: https://pypi.org/project/pei-docker/
2. ✅ Test installation: `pip install pei-docker`
3. ✅ Update project README if needed
4. ✅ Announce the release

## 🎉 Congratulations!

PeiDocker v1.0.0 is ready for the world! This production release includes:
- Complete Web GUI with NiceGUI framework
- Separated port mappings for stage-1 and stage-2
- Environment variable substitution support
- Project export/import functionality
- Comprehensive documentation updates