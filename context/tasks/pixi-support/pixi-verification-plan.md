# Pixi Container Functionality Verification Plan

## Overview

This task involves comprehensive testing of pixi functionality within PeiDocker containers to ensure the pixi package manager is properly installed, configured, and operational for Python package management.

## Current Implementation Status

### Core Implementation
- ✅ Pixi installation script: `pei_docker/project_files/installation/stage-2/system/pixi/install-pixi.bash`
- ✅ Common environment script: `pei_docker/project_files/installation/stage-2/system/pixi/create-env-common.bash` 
- ✅ ML environment script: `pei_docker/project_files/installation/stage-2/system/pixi/create-env-ml.bash`

### Test Infrastructure
- ✅ Test configuration: `tests/configs/simple-pixi-test.yml`
- ✅ Passwordless test configuration: `tests/configs/simple-pixi-test-passwordless.yml`
- ✅ Test SSH keys: `tests/test-keys/` (passwordless for automation)
- ✅ Basic test script: `tests/scripts/run-simple-pixi-test.bash`
- ✅ Enhanced verification script: `tests/scripts/enhanced-pixi-test.bash`

## Testing Objectives

### 1. Installation Verification
- **Goal**: Confirm pixi is properly installed and accessible
- **Tests**:
  - Verify pixi binary exists at expected location
  - Check pixi version output
  - Validate installation path (`/hard/image/pixi`)
  - Confirm environment variables are set correctly
  - Test pixi help command functionality

### 2. Global Environment Management
- **Goal**: Ensure pixi can manage global environments effectively
- **Tests**:
  - List existing global environments
  - Verify `common` environment was created successfully
  - Check environment details and metadata
  - Test environment isolation (packages don't leak between environments)
  - Validate environment storage location

### 3. Package Installation & Management
- **Goal**: Confirm packages can be installed and are functional
- **Tests**:
  - Verify all packages from `create-env-common.bash` are installed:
    - scipy, click, attrs, omegaconf, rich, networkx, ipykernel
  - Test package import functionality in Python
  - Verify command-line tools are accessible (click, rich)
  - Check package versions and dependencies
  - Test package update/removal capabilities

### 4. Shell Integration & PATH
- **Goal**: Ensure pixi integrates properly with the shell environment
- **Tests**:
  - Verify pixi commands work from any directory
  - Check PATH includes pixi binaries
  - Test that installed packages are in PATH
  - Validate environment activation mechanisms
  - Test shell completion (if available)

### 5. Performance & Resource Usage
- **Goal**: Assess pixi performance within containers
- **Tests**:
  - Measure pixi installation time during build
  - Test package installation speed
  - Check memory usage of pixi processes
  - Validate disk space usage
  - Test concurrent package operations

### 6. Persistence & Data Integrity
- **Goal**: Ensure pixi data persists across container lifecycle
- **Tests**:
  - Stop and restart container, verify environments persist
  - Check package installations remain intact
  - Validate configuration files are preserved
  - Test after container rebuild (should use cached data)

### 7. Error Handling & Edge Cases
- **Goal**: Test pixi behavior under adverse conditions
- **Tests**:
  - Install non-existent package (error handling)
  - Test with network connectivity issues
  - Simulate disk space limitations
  - Test permission-related scenarios
  - Validate conflict resolution

## Important Build Notes

**Pixi Installation Location**: Pixi is installed in stage-2, not stage-1. This means:
- ✅ Only stage-2 needs rebuilding when pixi-related changes are made
- ⚠️ **MUST use `--no-cache` when rebuilding stage-2** to ensure pixi installation runs fresh
- 🔄 Stage-1 can remain cached unless system-level changes are made

**Rebuild Strategy**:
```bash
# For pixi-related changes, only rebuild stage-2
docker compose build --no-cache stage-2

# Stage-1 only needs rebuilding for system changes (SSH, apt, etc.)
docker compose build --no-cache stage-1
```

## Test Implementation Plan

### Phase 1: Basic Functionality (High Priority)
```bash
# Build and start container (CRITICAL: use --no-cache for stage-2)
docker compose build --no-cache stage-2
docker compose up -d stage-2

# Basic installation verification
docker compose exec stage-2 bash -c "which pixi"
docker compose exec stage-2 bash -c "pixi --version"
docker compose exec stage-2 bash -c "echo \$PIXI_HOME"

# Environment verification
docker compose exec stage-2 bash -c "pixi global list"
docker compose exec stage-2 bash -c "pixi global info common"
```

### Phase 2: Package Functionality (High Priority)
```bash
# Test Python package imports
docker compose exec stage-2 bash -c "python -c 'import scipy; print(f\"scipy {scipy.__version__}\")'"
docker compose exec stage-2 bash -c "python -c 'import click; print(f\"click {click.__version__}\")'"
docker compose exec stage-2 bash -c "python -c 'import rich; print(\"rich works\")'"

# Test command-line tools
docker compose exec stage-2 bash -c "click --help"
docker compose exec stage-2 bash -c "python -c 'from rich.console import Console; Console().print(\"Rich test\", style=\"bold green\")'"
```

### Phase 3: Advanced Testing (Medium Priority)
```bash
# Test environment creation
docker compose exec stage-2 bash -c "pixi global install-all"
docker compose exec stage-2 bash -c "pixi global install pytest"

# Test from different directories
docker compose exec stage-2 bash -c "cd /tmp && pixi global list"
docker compose exec stage-2 bash -c "cd /home && python -c 'import scipy'"
```

### Phase 4: Persistence Testing (Medium Priority)
```bash
# Restart container and retest
docker compose restart stage-2
docker compose exec stage-2 bash -c "pixi global list"
docker compose exec stage-2 bash -c "python -c 'import scipy'"
```

## Expected Outcomes

### Success Criteria
- ✅ Pixi version displays correctly (≥ 0.30.0)
- ✅ Global environments list shows `common` environment
- ✅ All specified packages import successfully in Python
- ✅ Command-line tools are accessible via PATH
- ✅ Environments persist across container restarts
- ✅ Performance is acceptable (< 2min for environment creation)

### Performance Benchmarks
- Pixi installation: < 30 seconds
- Common environment creation: < 90 seconds
- Package import time: < 1 second per package
- Memory usage: < 100MB for pixi processes

## Risk Assessment

### High Risk Areas
1. **Network Dependencies**: Package installation requires internet access
2. **Disk Space**: ML packages can be large (>1GB total)
3. **Build Time**: Additional build time for pixi setup
4. **Version Conflicts**: Package dependency conflicts

### Mitigation Strategies
1. Use pixi's caching mechanisms
2. Monitor disk usage during installation
3. Implement build-time error handling
4. Test with minimal package set first

## Troubleshooting Guide

### Common Issues
1. **Pixi not found**: Check PATH and PIXI_HOME environment variables
2. **Package import fails**: Verify environment activation and Python path
3. **Network errors**: Check proxy settings and internet connectivity
4. **Permission errors**: Validate file permissions and user ownership

### Debug Commands
```bash
# Environment debugging
env | grep -i pixi
echo $PATH | tr ':' '\n' | grep pixi

# Installation debugging
ls -la /hard/image/pixi/
pixi info
pixi global list --verbose
```

## Documentation Requirements

### Test Report Template
- Test execution date and environment
- Pixi version and configuration details
- Detailed test results for each phase
- Performance measurements
- Issues encountered and resolutions
- Recommendations for improvements

### User Documentation Updates
- Add pixi usage examples to CLAUDE.md
- Create pixi troubleshooting section
- Document recommended package lists
- Provide performance optimization tips

## Enhanced Test Script

A comprehensive test script has been created: `tests/scripts/enhanced-pixi-test.bash`

This script implements all verification phases and provides:
- ✅ Automated build process with correct `--no-cache` for stage-2
- 🔍 7-phase testing methodology
- 📊 Success rate reporting
- 🔄 Container restart persistence testing
- 📋 Detailed output for troubleshooting

**Usage**:
```bash
cd /workspace/code/PeiDocker
./tests/scripts/enhanced-pixi-test.bash
```

## Next Steps After Verification

1. **If tests pass**: Update documentation and mark pixi support as stable
2. **If tests fail**: Create bug reports with detailed reproduction steps
3. **Performance issues**: Optimize installation scripts and caching
4. **Missing features**: Plan additional pixi integration features

## Success Metrics

- [ ] All basic functionality tests pass
- [ ] Package installation success rate > 95%
- [ ] Environment creation time < 2 minutes
- [ ] Zero persistence issues across restarts
- [ ] Documentation is complete and accurate
- [ ] Troubleshooting guide addresses common issues

This verification plan ensures comprehensive testing of pixi functionality while providing clear success criteria and troubleshooting guidance for future development.