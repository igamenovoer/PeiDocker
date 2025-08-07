# PeiDocker v1.0.0 Release Notes

## 🚀 Release Overview

PeiDocker v1.0.0 is the first stable production release, introducing a web-based GUI, modular architecture, and PyPI distribution.

## 📦 PyPI Publication Instructions

### Pre-publication Checklist

1. ✅ PR #3 has been created: https://github.com/igamenovoer/PeiDocker/pull/3
2. ✅ Version updated to 1.0.0 in pyproject.toml
3. ✅ LICENSE file added (MIT)
4. ✅ MANIFEST.in configured for package distribution
5. ✅ Dependencies updated (nicegui added, textual removed)
6. ✅ README updated with PyPI installation instructions

### After PR Merge

1. **Merge the PR**
   ```sh
   # On GitHub, merge PR #3 into main branch
   ```

2. **Switch to main branch locally**
   ```sh
   git checkout main
   git pull origin main
   ```

3. **Create a GitHub Release**
   ```sh
   gh release create v1.0.0 --title "v1.0.0: Production Release with Web GUI" --notes-file RELEASE_NOTES.md
   ```

4. **Build the distribution**
   ```sh
   # Clean any previous builds
   rm -rf dist/ build/ *.egg-info/
   
   # Build the package
   python -m build
   ```

5. **Upload to TestPyPI first (optional but recommended)**
   ```sh
   python -m twine upload --repository testpypi dist/*
   
   # Test installation
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pei-docker
   ```

6. **Upload to PyPI**
   ```sh
   python -m twine upload dist/*
   ```

### Post-publication

1. **Verify installation**
   ```sh
   pip install pei-docker
   pei-docker-cli --help
   pei-docker-gui --help
   ```

2. **Update documentation**
   - Update GitHub Pages if applicable
   - Add PyPI badge to README

3. **Announce the release**
   - Create announcement on GitHub
   - Update project website if applicable

## ✨ New Features

### Web GUI (`pei-docker-gui`)
- Browser-based interface using NiceGUI
- Auto-port selection
- Visual project configuration
- Project export/import (ZIP files)
- Real-time validation

### Architecture Improvements
- Modular codebase structure
- `user_config` split into 10 focused modules
- `ui_state_bridge` split into 6 focused modules
- Full backward compatibility

### Configuration Enhancements
- Separate port mappings for stage-1 and stage-2
- Enhanced SSH configuration
- Environment variable substitution
- Improved validation

## 📝 Migration Guide

For existing users:
- No breaking changes
- All CLI commands remain the same
- New `pei-docker-gui` command is optional
- Existing projects work without modification

## 🙏 Acknowledgments

Thanks to all contributors and users who helped shape this release!

---

**Installation**: `pip install pei-docker`  
**Documentation**: https://github.com/igamenovoer/PeiDocker  
**Issues**: https://github.com/igamenovoer/PeiDocker/issues