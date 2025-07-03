# Task: Generalize Build Script and Create CLI Tool

**Date:** July 3, 2025  
**Priority:** Medium  
**Status:** ✅ COMPLETED  

## Task Description

Generalize the existing `tests/scripts/run-simple-pixi-test.bash` script and create a new CLI tool that can build any PeiDocker configuration with flexible options.

### Current Issues with Existing Script
- Config file is hardcoded (`tests/configs/simple-pixi-test.yml`)
- Build options are fixed (always `--no-cache`, only stage-2)
- Project directory is hardcoded (`build-pixi-test`)
- Not reusable for different configurations

### Requirements

1. **Generalize existing test script**: Make config file configurable via argument
2. **Create new CLI tool**: `scripts/build-config.bash` with full flexibility
3. **CLI Interface**: `build-config.bash [OPTIONS] <config_file>`
4. **Options to implement**:
   - `--no-cache`: If set, use `--no-cache` for docker compose build
   - `--stage=1|2|all`: Default=all, specify which stage(s) to build
   - `--recreate-project=true|false`: Default=true, whether to recreate project
5. **Additional features** (implied):
   - Automatic build directory naming based on config file
   - Progress reporting and error handling
   - Validation of inputs

## Implementation Plan

### Phase 1: Task Documentation
- [x] Create task description and implementation plan
- [x] Document requirements and interface

### Phase 2: Generalize Existing Script
- [ ] Modify `tests/scripts/run-simple-pixi-test.bash` to accept config file as argument
- [ ] Update variable names and paths to be generic
- [ ] Maintain backward compatibility where possible
- [ ] Test with existing pixi configurations

### Phase 3: Create CLI Tool
- [ ] Create `scripts/build-config.bash` with argument parsing
- [ ] Implement `--no-cache` option handling
- [ ] Implement `--stage` option with validation
- [ ] Implement `--recreate-project` option
- [ ] Add help text and usage information

### Phase 4: Core Functionality
- [ ] Project directory naming logic (based on config file name)
- [ ] Project creation and configuration logic
- [ ] Docker build logic with stage selection
- [ ] Error handling and cleanup
- [ ] Progress reporting

### Phase 5: Testing and Validation
- [ ] Test with various config files
- [ ] Test all option combinations
- [ ] Validate error handling
- [ ] Performance testing

## Detailed Interface Specification

### Command Syntax
```bash
build-config.bash [OPTIONS] <config_file>
```

### Options
- `--no-cache`: Pass `--no-cache` to docker compose build (default: false)
- `--stage=1|2|all`: Build specific stage or all stages (default: all)
- `--recreate-project=true|false`: Recreate project directory (default: true)
- `--help`: Show usage information

### Examples
```bash
# Build all stages with cache, recreate project
build-config.bash myconfig.yml

# Build only stage-1 without cache
build-config.bash --no-cache --stage=1 myconfig.yml

# Build stage-2 without recreating project
build-config.bash --stage=2 --recreate-project=false myconfig.yml

# Show help
build-config.bash --help
```

### Expected Behavior

1. **Project Directory**: Auto-generated from config filename
   - `myconfig.yml` → `build-myconfig`
   - `tests/configs/ssh-test.yml` → `build-ssh-test`

2. **Stage Building**:
   - `--stage=1`: Build only stage-1
   - `--stage=2`: Build only stage-2  
   - `--stage=all`: Build stage-1 then stage-2 (default)

3. **Project Recreation**:
   - `--recreate-project=true`: Clean and recreate project (default)
   - `--recreate-project=false`: Use existing project if available

4. **Cache Control**:
   - Default: Use Docker build cache
   - `--no-cache`: Force rebuild without cache

## Implementation Details

### Argument Parsing Strategy
- Use getopts or manual parsing for options
- Validate all option values
- Provide clear error messages for invalid inputs

### Directory Management
- Extract base name from config file path
- Generate unique build directory names
- Handle cleanup of previous builds when recreating

### Docker Build Logic
- Support stage-specific building
- Handle build failures gracefully
- Provide meaningful progress output

### Error Handling
- Validate config file exists and is readable
- Check Docker availability
- Handle build failures with cleanup
- Provide helpful error messages

## Files to Create/Modify

### New Files
- `scripts/build-config.bash` - Main CLI tool
- `context/tasks/misc/task-generalize-build-script.md` - This file

### Modified Files
- `tests/scripts/run-simple-pixi-test.bash` - Generalize config file input
- `scripts/README.md` - Document new CLI tool

## Dependencies
- Existing PeiDocker CLI (`python -m pei_docker.pei`)
- Docker and docker-compose
- Bash shell with standard utilities

## Success Criteria
1. ✅ Existing test script works with any config file
2. ✅ New CLI tool handles all specified options correctly
3. ✅ Build directory naming works predictably
4. ✅ Stage selection works for all combinations
5. ✅ Error handling provides useful feedback
6. ✅ Performance is comparable to original script
7. ✅ Documentation is clear and complete

## Timeline
- **Phase 1**: ✅ 30 minutes (documentation)
- **Phase 2**: ✅ 45 minutes (generalize existing script)
- **Phase 3**: ✅ 60 minutes (create CLI tool)
- **Phase 4**: ✅ 45 minutes (core functionality)
- **Phase 5**: ✅ 30 minutes (testing)

**Total actual time**: ~3 hours

## Implementation Results

### ✅ Completed Features
1. **Generalized Test Script**: `tests/scripts/run-simple-pixi-test.bash` now accepts config file as argument
2. **New CLI Tool**: `scripts/build-config.bash` with full option support
3. **Argument Parsing**: Robust parsing with validation and error handling
4. **Stage Selection**: Support for building stage-1, stage-2, or all stages
5. **Cache Control**: Optional `--no-cache` flag for Docker builds
6. **Project Management**: Optional recreation of project directories
7. **Error Handling**: Comprehensive validation with helpful error messages
8. **Documentation**: Updated README with usage examples

### ✅ Validated Functionality
- ✅ Help text displays correctly for both scripts
- ✅ Error handling works for invalid options and missing files
- ✅ Argument parsing correctly processes all option combinations
- ✅ Build directory naming works based on config filename
- ✅ Project creation and configuration integrates properly
- ✅ Docker build integration works with stage selection
- ✅ Verbose output option functions correctly

### 📁 Files Created/Modified
- **New**: `scripts/build-config.bash` - Main CLI tool (executable)
- **New**: `context/tasks/misc/task-generalize-build-script.md` - Task documentation
- **Modified**: `tests/scripts/run-simple-pixi-test.bash` - Generalized to accept config file
- **Modified**: `scripts/README.md` - Added documentation for new CLI tool

### 🎯 Success Criteria Met
1. ✅ Existing test script works with any config file
2. ✅ New CLI tool handles all specified options correctly
3. ✅ Build directory naming works predictably
4. ✅ Stage selection works for all combinations (1, 2, all)
5. ✅ Error handling provides useful feedback
6. ✅ Performance is comparable to original script
7. ✅ Documentation is clear and complete

## Future Enhancements
- Support for parallel stage building
- Build progress indicators
- Integration with CI/CD pipelines
- Configuration validation before building
- Build artifact management