# PeiDocker GUI Testing Plan Overview

## Testing Strategy

This document outlines the comprehensive testing strategy for the PeiDocker GUI implementation using the Textual framework. The testing approach covers unit tests, integration tests, validation tests, snapshot tests, auto-operation tests, and performance tests.

## Test Scope

### Implemented Features to Test

Based on the current GUI implementation, the following features need comprehensive testing:

#### Core Application Components
- **Main Application Entry Point** (`app.py`)
- **Startup Screen** (`screens/startup.py`) - System checks and Docker detection
- **Mode Selection Screen** (`screens/mode_selection.py`) - Simple vs Advanced mode selection
- **Simple Mode Wizard** (`screens/simple/wizard.py`) - Step navigation and progress tracking

#### Simple Mode Screens
- **Project Information Screen** (`screens/simple/project_info.py`) - Project name and base image configuration
- **SSH Configuration Screen** (`screens/simple/ssh_config.py`) - SSH users, ports, and authentication methods
- **Summary Screen** (`screens/simple/summary.py`) - Configuration review and saving

#### Data Models and Utilities
- **Configuration Models** (`models/config.py`) - Type-safe configuration data structures
- **Docker Utilities** (`utils/docker_utils.py`) - Docker availability checking
- **File Utilities** (`utils/file_utils.py`) - File system operations and validation

### Test Categories

1. **Unit Tests** - Testing individual components in isolation
2. **Integration Tests** - Testing component interactions and workflows
3. **Validation Tests** - Testing input validation and error handling
4. **Snapshot Tests** - Visual regression testing for UI consistency
5. **Auto-Operation Tests** - Automated end-to-end workflow testing
6. **Performance Tests** - Resource usage and responsiveness testing
7. **Cross-Platform Tests** - Testing across Windows, Linux, and macOS

## Testing Tools and Framework

### Required Dependencies

```bash
# Core testing dependencies
pip install pytest pytest-asyncio pytest-textual-snapshot

# Additional testing utilities
pip install pytest-mock pytest-xdist pytest-html pytest-cov

# For performance testing
pip install psutil memory-profiler
```

### Pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--tb=short",
    "--strict-markers",
    "--cov=src/pei_docker/gui",
    "--cov-report=html",
    "--cov-report=term-missing"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "validation: Input validation tests",
    "snapshot: Visual snapshot tests",
    "auto_operation: Automated end-to-end tests",
    "performance: Performance tests",
    "slow: Slow-running tests",
    "docker_required: Tests requiring Docker"
]
```

## Test Organization Structure

```
tests/
├── __init__.py
├── conftest.py                      # Pytest fixtures and configuration
├── unit/                           # Unit tests
│   ├── __init__.py
│   ├── test_app.py                 # Main application tests
│   ├── test_startup_screen.py      # Startup screen tests
│   ├── test_mode_selection.py      # Mode selection tests
│   ├── test_wizard.py              # Wizard controller tests
│   ├── test_project_info.py        # Project info screen tests
│   ├── test_ssh_config.py          # SSH configuration tests
│   ├── test_summary.py             # Summary screen tests
│   ├── test_config_models.py       # Configuration model tests
│   ├── test_docker_utils.py        # Docker utilities tests
│   └── test_file_utils.py          # File utilities tests
├── integration/                    # Integration tests
│   ├── __init__.py
│   ├── test_simple_mode_flow.py    # Complete simple mode workflow
│   ├── test_configuration_save.py  # Configuration saving workflow
│   ├── test_docker_integration.py  # Docker command integration
│   └── test_navigation_flow.py     # Screen navigation testing
├── validation/                     # Input validation tests
│   ├── __init__.py
│   ├── test_project_validation.py  # Project input validation
│   ├── test_ssh_validation.py      # SSH configuration validation
│   ├── test_port_validation.py     # Port mapping validation
│   └── test_path_validation.py     # File path validation
├── snapshots/                      # Snapshot tests
│   ├── __init__.py
│   ├── test_ui_snapshots.py        # Visual regression tests
│   └── __snapshots__/              # Generated snapshot files
├── auto_operation/                 # Automated end-to-end tests
│   ├── __init__.py
│   ├── test_complete_workflows.py  # Full automation tests
│   ├── test_batch_operations.py    # Batch configuration tests
│   └── test_headless_operation.py  # Headless automation tests
├── performance/                    # Performance tests
│   ├── __init__.py
│   ├── test_startup_performance.py # Application startup timing
│   ├── test_memory_usage.py        # Memory consumption tests
│   └── test_responsiveness.py      # UI responsiveness tests
├── cross_platform/                 # Cross-platform tests
│   ├── __init__.py
│   ├── test_windows_specific.py    # Windows-specific functionality
│   ├── test_linux_specific.py      # Linux-specific functionality
│   └── test_path_handling.py       # Cross-platform path handling
└── fixtures/                       # Test data and fixtures
    ├── __init__.py
    ├── sample_configs.py           # Sample configuration data
    ├── mock_docker_responses.py    # Mock Docker API responses
    └── test_projects/              # Sample project directories
```

## Testing Workflow

### Development Testing
1. **Continuous Testing** - Run unit tests during development
2. **Pre-commit Testing** - Run validation and snapshot tests before commits
3. **Integration Testing** - Run integration tests before merging

### CI/CD Pipeline Testing
1. **Fast Tests** - Unit and validation tests (< 5 minutes)
2. **Standard Tests** - Integration and snapshot tests (< 15 minutes)
3. **Full Test Suite** - All tests including performance and cross-platform (< 30 minutes)

### Test Execution Commands

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
pytest -m validation            # Validation tests only
pytest -m snapshot              # Snapshot tests only
pytest -m auto_operation        # Auto-operation tests only
pytest -m performance           # Performance tests only

# Run tests with coverage
pytest --cov=src/pei_docker/gui --cov-report=html

# Run tests in parallel
pytest -n auto

# Run specific test files
pytest tests/unit/test_app.py
pytest tests/integration/test_simple_mode_flow.py

# Update snapshots (when UI changes are intentional)
pytest --snapshot-update

# Run slow tests (performance, full integration)
pytest -m slow

# Run tests requiring Docker
pytest -m docker_required
```

## Test Data Management

### Mock Data Strategy
- **Configuration Templates** - Pre-built configuration objects for testing
- **Docker Mock Responses** - Simulated Docker API responses
- **File System Mocks** - Temporary directories and file structures
- **SSH Key Fixtures** - Test SSH keys for authentication testing

### Test Environment Setup
- **Temporary Directories** - Isolated test project directories
- **Docker Container Cleanup** - Automatic cleanup of test containers/images
- **Resource Isolation** - Prevent tests from affecting system resources
- **Deterministic Testing** - Reproducible test results across environments

## Quality Metrics and Targets

### Coverage Targets
- **Overall Code Coverage**: ≥ 90%
- **Critical Path Coverage**: 100% (user workflows, data persistence)
- **Error Handling Coverage**: ≥ 95%
- **Edge Case Coverage**: ≥ 80%

### Performance Targets
- **Application Startup**: < 2 seconds
- **Screen Transitions**: < 500ms
- **Configuration Validation**: < 100ms
- **Memory Usage**: < 100MB during normal operation

### Quality Gates
- **All Unit Tests Pass**: Required for merging
- **No Visual Regressions**: Snapshot tests must pass
- **No Performance Degradation**: Performance tests within targets
- **Cross-Platform Compatibility**: Tests pass on all supported platforms

## Test Maintenance Strategy

### Regular Maintenance
- **Weekly Snapshot Review** - Review and update visual snapshots
- **Monthly Performance Baseline Update** - Update performance benchmarks
- **Quarterly Test Strategy Review** - Review and update testing approach

### Test Debt Management
- **Identify Flaky Tests** - Monitor and fix unstable tests
- **Update Test Data** - Keep mock data and fixtures current
- **Refactor Test Code** - Maintain test code quality and readability

This comprehensive testing strategy ensures the PeiDocker GUI is reliable, performant, and maintainable across all supported platforms and use cases.