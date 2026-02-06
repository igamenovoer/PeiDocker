# How Custom Scripts Work in PeiDocker

This document traces the complete lifecycle of custom scripts in PeiDocker, from configuration to execution during various stages of the Docker build and runtime process.

## Overview

PeiDocker's custom script system allows users to execute arbitrary scripts during different lifecycle events:

1. **`on_build`** - Scripts executed during Docker image build process
2. **`on_first_run`** - Scripts executed once when container starts for the first time
3. **`on_every_run`** - Scripts executed every time the container starts
4. **`on_user_login`** - Scripts executed when SSH users log in

The system works through a two-stage architecture with sophisticated script generation and execution mechanisms.

## Configuration Stage

### User Configuration (`user_config.yml`)

Users define custom scripts in the YAML configuration:

```yaml
stage_1:
  custom:
    on_build: 
      - 'stage-1/custom/install-dev-tools.sh'
      - 'stage-1/custom/my-build-1.sh'
    on_first_run:
      - 'stage-1/custom/my-on-first-run-1.sh'
    on_every_run:
      - 'stage-1/custom/my-on-every-run-1.sh'
    on_user_login:
      - 'stage-1/custom/my-on-user-login-1.sh'

stage_2:
  custom:
    on_build: 
      - 'stage-2/custom/install-gui-tools.sh'
    on_first_run:
      - 'stage-2/custom/my-on-first-run-1.sh'
    # ... etc
```

**Key Points:**
- Script paths are relative to the `installation/` directory
- Each stage can define its own custom scripts
- Multiple scripts can be specified for each lifecycle event

## Processing Stage

### Config Processor (`config_processor.py`)

When `pei configure` is run, the `PeiConfigProcessor` processes the configuration through these key methods:

#### 1. Script Validation (`_check_custom_scripts`)
```python
def _check_custom_scripts(self, custom_config : CustomScriptConfig) -> bool:
    # Validates that all listed script files exist on the host
    host_path = f'{self.m_project_dir}/{self.m_host_dir}/{script}'
    if not os.path.exists(host_path):
        logging.warning(f'Script {host_path} not found')
```

#### 2. Wrapper Script Generation (`_generate_script_files`)
```python
def _generate_script_files(self, user_config : UserConfig):
    # Generates wrapper scripts for each lifecycle event
    on_build_script = self._generate_script_text('on-build', on_build_list)
    filename_build = f'{self.m_project_dir}/{self.m_host_dir}/{name}/generated/_custom-on-build.sh'
    with open(filename_build, 'w+') as f:
        f.write(on_build_script)
```

#### 3. Script Content Generation (`_generate_script_text`)
```python
def _generate_script_text(self, on_what:str, filelist : Optional[list[str]]) -> str:
    cmds : list[str] = [
        "DIR=\"$( cd \"$( dirname \"${BASH_SOURCE[0]}\" )\" && pwd )\" ",
        f"echo \"Executing $DIR/_custom-{on_what}.sh\" "
    ]
    
    if filelist:
        if on_what == 'on-user-login':
            # User login scripts use 'source' instead of 'bash'
            for file in filelist:
                cmds.append(f"source $DIR/../../{file}")
        else:
            for file in filelist:
                cmds.append(f"bash $DIR/../../{file}")
        
    return '\n'.join(cmds)
```

### Generated Wrapper Scripts

The processor creates wrapper scripts in the `generated/` directory:
- `installation/stage-{1,2}/generated/_custom-on-build.sh`
- `installation/stage-{1,2}/generated/_custom-on-first-run.sh`  
- `installation/stage-{1,2}/generated/_custom-on-every-run.sh`
- `installation/stage-{1,2}/generated/_custom-on-user-login.sh`

**Example Generated Script:**
```bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" 
echo "Executing $DIR/_custom-on-build.sh" 
bash $DIR/../../stage-1/custom/install-dev-tools.sh
bash $DIR/../../stage-1/custom/my-build-1.sh
```

## Build Stage (Docker Build Process)

### Stage 1 Dockerfile (`stage-1.Dockerfile`)

```dockerfile
# Copy installation files to container
ADD ${PEI_STAGE_HOST_DIR_1}/internals ${PEI_STAGE_DIR_1}/internals
ADD ${PEI_STAGE_HOST_DIR_1}/generated ${PEI_STAGE_DIR_1}/generated
ADD ${PEI_STAGE_HOST_DIR_1}/system ${PEI_STAGE_DIR_1}/system

# ... setup essentials ...

# Copy all installation files including custom scripts
ADD ${PEI_STAGE_HOST_DIR_1} ${PEI_STAGE_DIR_1}

# Convert line endings and make executable
RUN find $PEI_STAGE_DIR_1 -type f -name "*.sh" -exec dos2unix {} \;
RUN find $PEI_STAGE_DIR_1 -type f -name "*.sh" -exec chmod +x {} \;

# Execute custom build scripts
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    $PEI_STAGE_DIR_1/internals/custom-on-build.sh
```

### Internal Build Script (`custom-on-build.sh`)

```bash
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "Executing $DIR/custom-on-build.sh ..."

DIR_GENERATED="$DIR/../generated"

# Execute the generated wrapper script
if [ -f "$DIR_GENERATED/_custom-on-build.sh" ]; then
    echo "Found custom on-build script, executing ..."
    bash "$DIR_GENERATED/_custom-on-build.sh"
fi
```

### Stage 2 Process

Stage 2 follows the same pattern but builds upon the Stage 1 image:
- Uses Stage 1 output as base image
- Copies Stage 2 installation files  
- Executes Stage 2 custom build scripts

## Runtime Stage (Container Startup)

### Entrypoint Script (`entrypoint.sh`)

The container entrypoint orchestrates runtime script execution:

**Stage 2 Entrypoint:**
```bash
#!/bin/bash
script_dir_1=$PEI_STAGE_DIR_1/internals
script_dir_2=$PEI_STAGE_DIR_2/internals

# Run stage 1 on-entry tasks
bash $script_dir_1/on-entry.sh

# Run stage 2 on-entry tasks  
bash $script_dir_2/on-entry.sh

# Start SSH service
if [ -f /etc/ssh/sshd_config ]; then
    echo "Starting ssh service..."
    service ssh start
fi

# Start shell
/bin/bash
```

### On-Entry Script (`on-entry.sh`)

```bash
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Create storage links first
bash "$DIR/create-links.sh"

# First-run logic with persistence
first_run_signature_file=$PEI_DOCKER_DIR/stage-2-init-done

if [ -f $first_run_signature_file ]; then
    echo "$first_run_signature_file found, skipping first run tasks"
else
    echo "$first_run_signature_file not found, running first run tasks ..."
    bash "$DIR/on-first-run.sh"
    echo "stage-2 is initialized" > $first_run_signature_file
fi

# Execute on-every-run tasks
bash "$DIR/on-every-run.sh"
```

### Runtime Script Execution

**First Run Script:**
```bash
# on-first-run.sh calls custom-on-first-run.sh
bash "$DIR/custom-on-first-run.sh"
```

**Every Run Script:**
```bash  
# on-every-run.sh calls custom-on-every-run.sh
bash "$DIR/custom-on-every-run.sh"
```

**Custom Runtime Scripts:**
```bash
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DIR_GENERATED="$DIR/../generated"

if [ -f "$DIR_GENERATED/_custom-on-first-run.sh" ]; then
    echo "Found custom on-first-run script, executing ..."
    bash "$DIR_GENERATED/_custom-on-first-run.sh"
fi
```

## User Login Stage (SSH Sessions)

### User Setup Process (`setup-users.sh`)

During container build, the user setup script configures SSH user login scripts:

```bash
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Add custom-on-user-login.sh to .bashrc for each user
for user in $(ls /home); do
    su - $user -c "echo 'source $DIR/custom-on-user-login.sh' >> /home/$user/.bashrc"
done

# Also configure for root user
echo "source $DIR/custom-on-user-login.sh" >> /root/.bashrc
```

### User Login Script (`custom-on-user-login.sh`)

```bash
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
DIR_GENERATED="$DIR/../generated"

if [ -f "$DIR_GENERATED/_custom-on-user-login.sh" ]; then
    # Note: Uses 'source' instead of 'bash' for login scripts
    source "$DIR_GENERATED/_custom-on-user-login.sh"
fi
```

**Key Difference:** User login scripts use `source` instead of `bash` to execute in the current shell context, allowing them to modify the user's environment.

## Architecture Summary

### File Structure
```
project_dir/
└── installation/
    ├── stage-1/
    │   ├── custom/               # User-provided scripts
    │   │   ├── my-script.sh
    │   │   └── ...
    │   ├── generated/            # Auto-generated wrappers  
    │   │   ├── _custom-on-build.sh
    │   │   ├── _custom-on-first-run.sh
    │   │   ├── _custom-on-every-run.sh
    │   │   └── _custom-on-user-login.sh
    │   └── internals/            # PeiDocker internal scripts
    │       ├── custom-on-build.sh
    │       ├── custom-on-first-run.sh
    │       ├── custom-on-every-run.sh
    │       ├── custom-on-user-login.sh
    │       └── ...
    └── stage-2/
        └── (same structure as stage-1)
```

### Execution Flow

1. **Configuration Processing:**
   - User defines scripts in `user_config.yml`
   - `pei configure` validates and generates wrapper scripts
   - Wrapper scripts created in `generated/` directory

2. **Docker Build:**
   - Installation files copied to container
   - Scripts made executable with proper line endings
   - Build-time custom scripts executed via `custom-on-build.sh`

3. **Container Runtime:**
   - Entrypoint script calls `on-entry.sh`
   - First-run scripts executed once (with persistence tracking)
   - Every-run scripts executed on each startup
   - SSH service started

4. **User Login:**
   - SSH users get custom login scripts sourced in `.bashrc`
   - Login scripts execute in user's shell context

### Key Features

- **Cross-Platform Compatibility:** Handles CRLF/LF line endings automatically
- **Persistence Tracking:** First-run scripts execute only once using signature files
- **Multi-Stage Support:** Each stage can have independent custom scripts  
- **User Context:** Login scripts execute in user's environment
- **Error Handling:** Script validation during configuration processing
- **Flexible Execution:** Different execution methods (bash vs source) for different contexts

This architecture enables PeiDocker to provide a flexible, extensible system for customizing Docker containers while maintaining clean separation between user scripts and system internals.