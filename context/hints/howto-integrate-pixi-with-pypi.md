# How to Integrate Pixi into pyproject.toml for PyPI Publishing

This guide covers best practices for integrating Pixi package management into `pyproject.toml` for projects intended for PyPI publication.

## Overview

Pixi supports using `pyproject.toml` as its manifest file, which allows you to maintain one configuration file for both package management and PyPI publishing. This is recommended for Python projects to avoid configuration duplication.

## Key Benefits

1. **Single Configuration File**: Keep all project configuration in `pyproject.toml`
2. **PyPI Compatibility**: Maintains standard PyPI project structure
3. **Dependency Management**: Supports both conda and PyPI dependencies
4. **Development Workflow**: Seamless integration with development tools

## Migration from pixi.toml to pyproject.toml

### 1. Initialize with pyproject.toml Format

For new projects:
```bash
pixi init --format pyproject
```

For existing projects with `pyproject.toml`:
```bash
pixi init  # Will automatically detect and extend existing pyproject.toml
```

### 2. Namespace Conversion

All pixi-specific configuration in `pyproject.toml` must be prefixed with `[tool.pixi.]`:

**From pixi.toml:**
```toml
[project]
name = "my_project"
channels = ["conda-forge"]

[dependencies]
numpy = "*"

[tasks]
test = "pytest"
```

**To pyproject.toml:**
```toml
[project]
name = "my_project"
requires-python = ">=3.9"
dependencies = ["numpy"]

[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-arm64", "osx-64", "win-64"]

[tool.pixi.tasks]
test = "pytest"
```

## PyPI Publishing Configuration

### 1. Essential pyproject.toml Sections for PyPI

```toml
[project]
name = "your-package-name"
version = "0.1.0"
description = "Your package description"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
keywords = ["package", "development"]
dependencies = [
    "numpy>=1.20",
    "pandas>=1.3",
]

[project.urls]
Homepage = "https://github.com/yourusername/yourpackage"
Documentation = "https://yourpackage.readthedocs.io"
Repository = "https://github.com/yourusername/yourpackage"
Issues = "https://github.com/yourusername/yourpackage/issues"

[project.optional-dependencies]
dev = ["pytest", "black", "ruff"]
docs = ["mkdocs", "mkdocs-material"]

[project.scripts]
your-cli = "your_package.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 2. Recommended Build Backend

Use `hatchling` (modern, feature-rich) over `setuptools`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Alternative options:
- `setuptools`: Traditional but still supported
- `flit`: Minimal for simple packages
- `pdm-backend`: If using PDM

### 3. Pixi Configuration for Development

```toml
[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-arm64", "osx-64", "win-64"]

[tool.pixi.dependencies]
# System/conda dependencies that PyPI can't provide
compilers = "*"
cmake = "*"
# Add your project as editable dependency
your-package = { path = ".", editable = true }

[tool.pixi.pypi-dependencies]
# Development dependencies from PyPI
pytest = "*"
black = "*"
ruff = "*"
twine = "*"  # For PyPI publishing
build = "*"  # For building distributions

[tool.pixi.tasks]
install-dev = "pip install -e ."
test = "pytest tests/"
lint = "ruff check src/"
format = "black src/"
build = "python -m build"
publish-test = "python -m twine upload --repository testpypi dist/*"
publish = "python -m twine upload dist/*"
clean = "rm -rf dist/ build/ *.egg-info/"

[tool.pixi.environments]
default = {features = [], solve-group = "default"}
dev = {features = ["dev"], solve-group = "default"}
docs = {features = ["docs"], solve-group = "default"}
```

## Dependency Management Best Practices

### 1. Dependency Priority

When the same package is specified in both `[project.dependencies]` and `[tool.pixi.dependencies]`, Pixi prioritizes conda dependencies:

```toml
[project]
dependencies = ["numpy"]  # PyPI version

[tool.pixi.dependencies]
numpy = "*"  # Conda version (this takes precedence)
```

### 2. Separating PyPI and Conda Dependencies

```toml
[project]
dependencies = [
    "requests",      # Pure Python, available on PyPI
    "click",         # CLI framework
]

[tool.pixi.dependencies]
numpy = "*"          # Scientific computing, better from conda
opencv = "*"         # Computer vision, complex binary deps
mkl = "*"           # Math libraries, better from conda

[tool.pixi.pypi-dependencies]
your-internal-tool = { git = "https://github.com/yourorg/tool.git" }
```

### 3. Optional Dependencies and Features

```toml
[project.optional-dependencies]
ml = ["scikit-learn", "torch"]
viz = ["matplotlib", "plotly"]
dev = ["pytest", "black", "ruff"]
all = ["your-package[ml,viz]"]

[tool.pixi.feature.ml.dependencies]
cuda-toolkit = "*"  # GPU support via conda

[tool.pixi.feature.test.pypi-dependencies]
pytest-cov = "*"
pytest-xdist = "*"

[tool.pixi.environments]
default = {features = [], solve-group = "default"}
ml = {features = ["ml"], solve-group = "default"}
full = {features = ["ml", "viz", "dev"], solve-group = "default"}
```

## Publishing Workflow

### 1. Prepare for Publishing

```bash
# Clean previous builds
pixi run clean

# Run tests
pixi run test

# Format and lint
pixi run format
pixi run lint

# Build distributions
pixi run build
```

### 2. Test Publishing

```bash
# Upload to TestPyPI first
pixi run publish-test
```

### 3. Production Publishing

```bash
# Upload to PyPI
pixi run publish
```

## Project Structure for PyPI

Ensure your project follows PyPI conventions:

```
your-project/
├── pyproject.toml          # Single config file
├── README.md               # Project documentation
├── LICENSE                 # License file
├── src/                    
│   └── your_package/       # Source code
│       ├── __init__.py
│       └── main.py
├── tests/                  # Test files
│   └── test_main.py
├── docs/                   # Documentation
└── .gitignore
```

## Migration Checklist

When migrating from `pixi.toml` to integrated `pyproject.toml`:

- [ ] Run `pixi init` in project with existing `pyproject.toml`
- [ ] Move all `[project]` section from `pixi.toml` to `[tool.pixi.workspace]`
- [ ] Convert `[dependencies]` to `[tool.pixi.dependencies]`
- [ ] Convert `[tasks]` to `[tool.pixi.tasks]`
- [ ] Add proper `[build-system]` section
- [ ] Add PyPI metadata in `[project]` section
- [ ] Set up publishing tasks
- [ ] Test with `pixi install` and `pixi run test`
- [ ] Remove `pixi.toml` file
- [ ] Update `.gitignore` to include `.pixi/` directory

## Common Pitfalls

1. **Forgetting `tool.pixi.` prefix**: All pixi configuration must be under `[tool.pixi.*]`
2. **Missing build-system**: Always include `[build-system]` for PyPI compatibility
3. **Dependency conflicts**: Be careful about specifying same package in both PyPI and conda
4. **Platform specification**: Include all target platforms in `[tool.pixi.workspace.platforms]`
5. **Editable installs**: For development, add your package as editable dependency

## Additional Resources

- [Pixi Documentation - pyproject.toml](https://pixi.sh/latest/python/pyproject_toml/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/section-build-and-publish/)
- [Hatchling Documentation](https://hatch.pypa.io/latest/)

## Example Complete pyproject.toml

```toml
[project]
name = "example-pixi-package"
version = "0.1.0"
description = "An example package using Pixi with PyPI publishing"
authors = [{name = "Your Name", email = "you@example.com"}]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10", 
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "click>=8.0",
    "requests>=2.28",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "black", "ruff"]
docs = ["mkdocs", "mkdocs-material"]

[project.urls]
Homepage = "https://github.com/yourusername/example-pixi-package"
Repository = "https://github.com/yourusername/example-pixi-package"

[project.scripts]
example-cli = "example_package.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-arm64", "osx-64", "win-64"]

[tool.pixi.dependencies]
example-pixi-package = { path = ".", editable = true }

[tool.pixi.pypi-dependencies]
build = "*"
twine = "*"

[tool.pixi.feature.dev.pypi-dependencies]
pytest = ">=7.0"
pytest-cov = "*"
black = "*"
ruff = "*"

[tool.pixi.tasks]
test = "pytest tests/"
lint = "ruff check src/"
format = "black src/ tests/"
build = "python -m build"
clean = "rm -rf dist/ build/ *.egg-info/"
publish-test = "twine upload --repository testpypi dist/*"
publish = "twine upload dist/*"

[tool.pixi.environments]
default = {solve-group = "default"}
dev = {features = ["dev"], solve-group = "default"}
```

This configuration provides a complete setup for both development with Pixi and publishing to PyPI.
