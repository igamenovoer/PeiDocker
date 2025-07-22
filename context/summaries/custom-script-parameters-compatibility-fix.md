# Custom Script Parameters Compatibility Fix

## Overview

Updated all custom scripts referenced in `config-template-full.yml` to properly handle the parameters specified in the template. This ensures the configuration template works out-of-the-box without errors.

## Problem

The `config-template-full.yml` template included parameter examples for custom scripts that didn't actually accept those parameters:

```yaml
# Example from template
on_build: 
  - 'stage-1/custom/my-build-2.sh --verbose --config=/tmp/build.conf'
```

But the actual `my-build-2.sh` script was basic and would fail with unknown parameter errors.

## Solution

Updated all affected scripts to:
1. Parse command line parameters using proper bash parameter parsing
2. Display different behavior based on parameters provided
3. Provide educational examples of how parameter passing works
4. Maintain backward compatibility (scripts work with or without parameters)

## Scripts Updated

### Stage 1 Scripts

| Script | Parameters Supported | Functionality |
|--------|---------------------|---------------|
| `my-build-2.sh` | `--verbose --config=<path>` | Verbose build output, config file usage |
| `my-on-first-run-2.sh` | `--initialize --create-dirs` | System initialization, directory creation |
| `my-on-every-run-2.sh` | `--check-health` | System health monitoring |
| `my-on-user-login-2.sh` | `--show-motd --update-prompt` | Welcome message, custom shell prompt |

### Stage 2 Scripts

| Script | Parameters Supported | Functionality |
|--------|---------------------|---------------|
| `my-build-2.sh` | `--enable-desktop --theme=<value>` | Desktop environment, theme configuration |
| `my-on-first-run-2.sh` | `--setup-workspace --clone-repos` | Development workspace, repository management |
| `my-on-every-run-2.sh` | `--update-status --log-startup` | Status monitoring, startup logging |
| `my-on-user-login-2.sh` | `--welcome-message --check-updates` | Welcome display, update checking |

## Parameter Parsing Pattern

All scripts use a consistent parameter parsing pattern:

```bash
# Default values
VERBOSE=false
CONFIG_FILE=""

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --config=*)
            CONFIG_FILE="${arg#*=}"
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done
```

## Features Added

1. **Educational Value**: Scripts demonstrate how to properly handle parameters
2. **Debugging Support**: All scripts show received arguments and parsed values
3. **Conditional Behavior**: Different functionality based on parameters
4. **Error Handling**: Unknown parameters are reported but don't cause failures
5. **Backward Compatibility**: Scripts work without parameters (using defaults)

## Testing

The config template now works as-is without modification. Users can:
- Use the template directly for immediate functionality
- See working examples of parameter passing
- Modify parameters to customize behavior
- Learn proper parameter parsing techniques

## Benefits

1. **Template Works Out-of-Box**: No more parameter-related errors
2. **Educational Examples**: Users learn parameter passing best practices
3. **Flexible Configuration**: Parameters can be customized per deployment
4. **Professional Appearance**: Scripts provide detailed feedback and logging
5. **Development Ready**: Demonstrates real-world script development patterns

This fix ensures that the `config-template-full.yml` serves as both a working template and an educational resource for custom script parameter usage.