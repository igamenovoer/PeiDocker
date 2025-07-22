# Custom Script Parameters Implementation

This document describes the implementation of custom script parameter support in PeiDocker, allowing users to pass parameters to their custom scripts directly in the YAML configuration.

## Feature Overview

Users can now specify parameters for custom scripts in their `user_config.yml` configuration:

```yaml
stage_1:
  custom:
    on_build: 
      - 'stage-1/custom/install-tools.sh --verbose --update-cache'
      - 'stage-1/custom/setup-proxy.sh --host=proxy.example.com --port=8080'
      - 'stage-1/custom/configure.sh --config="/path/with spaces/config.json"'
```

## Implementation Details

### 1. Script Entry Parsing (`_parse_script_entry`)

**Location**: `pei_docker/config_processor.py`

**Function**: `PeiConfigProcessor._parse_script_entry(script_entry: str) -> Tuple[str, str]`

**Purpose**: Parses script entries that may contain both script paths and parameters.

**Key Features**:
- Uses `shlex.split()` for proper shell-like argument parsing
- Handles quoted parameters with spaces correctly
- Provides safe fallback for malformed entries
- Returns tuple of `(script_path, parameters_string)`

**Example**:
```python
script_path, params = _parse_script_entry('script.sh --param="value with spaces"')
# Returns: ('script.sh', '--param="value with spaces"')
```

### 2. Script Generation (`_generate_script_text`)

**Location**: `pei_docker/config_processor.py`

**Function**: `PeiConfigProcessor._generate_script_text(on_what: str, filelist: Optional[list[str]]) -> str`

**Enhanced Functionality**:
- Now processes each script entry to separate script path from parameters
- Maintains different execution modes for different lifecycle events
- Preserves parameter formatting for shell execution

**Generated Script Examples**:

**Build Script**:
```bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" 
echo "Executing $DIR/_custom-on-build.sh" 
bash $DIR/../../stage-1/custom/install-tools.sh --verbose --update-cache
bash $DIR/../../stage-1/custom/setup-proxy.sh --host=proxy.example.com --port=8080
```

**User Login Script**:
```bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" 
echo "Executing $DIR/_custom-on-user-login.sh" 
source $DIR/../../stage-1/custom/welcome.sh --show-motd --theme=dark
source $DIR/../../stage-1/custom/setup-env.sh --activate-venv --cd-to-project
```

### 3. Configuration Template Updates

**Location**: `pei_docker/templates/config-template-full.yml`

**Enhanced Documentation**: Added comprehensive examples showing parameter usage:

```yaml
custom:
  # Scripts can include parameters: 'script.sh --param1=value1 --param2="value with spaces"'
  on_build: 
    - 'stage-1/custom/my-build-2.sh --verbose --config=/tmp/build.conf'
    # Example with parameters:
    # - 'stage-1/custom/setup-environment.sh --env=development --log-level=debug'
    # - 'stage-1/custom/install-packages.sh --package-list="git curl vim" --update-cache'
```

## Parameter Handling

### Shell Safety

The implementation ensures shell-safe parameter passing:

1. **Parsing**: Uses `shlex.split()` to properly handle quoted arguments
2. **Escaping**: Uses `shlex.quote()` to escape parameters containing special characters
3. **Execution**: Parameters are passed directly to bash/source commands

### Supported Parameter Formats

- **Simple flags**: `--verbose`, `--debug`
- **Key-value pairs**: `--host=localhost`, `--port=8080` 
- **Quoted values**: `--name="My Project"`, `--path="/path/with spaces"`
- **Multiple parameters**: `--verbose --host=localhost --port=8080`
- **Complex values**: `--packages="git curl vim nano" --update-system`

### Cross-Platform Compatibility

- Works on Windows (WSL), Linux, and macOS
- Handles different line ending formats (CRLF/LF)
- Preserves executable permissions

## Lifecycle Integration

The parameter support works seamlessly with all PeiDocker lifecycle events:

1. **`on_build`**: Parameters passed during Docker image build
2. **`on_first_run`**: Parameters passed during container first startup
3. **`on_every_run`**: Parameters passed on every container startup  
4. **`on_user_login`**: Parameters passed when SSH users log in (using `source`)

## Example Usage

### Build-time Configuration

```yaml
stage_1:
  custom:
    on_build:
      - 'stage-1/custom/install-packages.sh --mirror=tsinghua --update-cache'
      - 'stage-1/custom/setup-proxy.sh --host=proxy.company.com --port=3128'
```

### Runtime Configuration

```yaml
stage_2:
  custom:
    on_first_run:
      - 'stage-2/custom/setup-workspace.sh --project-name="My App" --git-clone'
    on_user_login:
      - 'stage-2/custom/activate-env.sh --venv-path="/workspace/.venv" --cd-to-project'
```

### Development Environment Setup

```yaml
stage_2:
  custom:
    on_build:
      - 'stage-2/custom/install-python.sh --version=3.11 --packages="numpy pandas"'
      - 'stage-2/custom/setup-vscode.sh --extensions="python,docker,git" --theme=dark'
    on_user_login:
      - 'stage-2/custom/dev-setup.sh --activate-venv --show-git-status --welcome-msg'
```

## Testing

The implementation has been tested with:

- **Parameter Parsing**: Various parameter formats and edge cases
- **Script Generation**: All lifecycle events (build, first-run, every-run, user-login)  
- **Shell Compatibility**: Complex parameters with spaces and special characters
- **End-to-End**: Full configuration processing and script generation

## Backward Compatibility

The implementation is fully backward compatible:

- Existing configurations without parameters continue to work unchanged
- No breaking changes to the configuration format
- Scripts without parameters are handled identically to before

## Benefits

1. **Flexibility**: Scripts can be configured for different environments/modes
2. **Reusability**: Same script can be used with different parameters
3. **Maintainability**: Reduces need for multiple similar scripts
4. **Configuration-driven**: All customization happens in YAML, not in script files
5. **Shell-safe**: Proper parameter escaping prevents injection issues

This enhancement significantly increases the flexibility and power of PeiDocker's custom script system while maintaining simplicity and safety.