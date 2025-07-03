# PeiDocker Utility Scripts

This directory contains utility scripts for PeiDocker development and usage.

## Scripts

### `build-config.bash`

**Purpose**: CLI tool for building any PeiDocker configuration with flexible options

**Usage**: 
```bash
build-config.bash [OPTIONS] <config_file>
```

**Options**:
- `--no-cache` - Use --no-cache for docker compose build (default: false)
- `--stage=1|2|all` - Build specific stage or all stages (default: all)  
- `--recreate-project=true|false` - Recreate project directory (default: true)
- `--verbose` - Enable verbose output (default: false)
- `--help, -h` - Show help message

**Examples**:
```bash
# Build all stages with cache, recreate project
./scripts/build-config.bash myconfig.yml

# Build only stage-1 without cache
./scripts/build-config.bash --no-cache --stage=1 myconfig.yml

# Build stage-2 without recreating project
./scripts/build-config.bash --stage=2 --recreate-project=false myconfig.yml

# Build with verbose output
./scripts/build-config.bash --verbose tests/configs/ssh-test.yml
```

**Features**:
- Automatic build directory naming based on config filename
- Flexible stage building (stage-1, stage-2, or both)
- Optional cache control
- Project recreation control
- Comprehensive error handling and validation
- Colored output for better readability

**Build Directory Naming**:
- `myconfig.yml` → `build-myconfig`
- `tests/configs/ssh-test.yml` → `build-ssh-test`
- `/path/to/custom.yml` → `build-custom`