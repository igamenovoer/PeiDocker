# Environment Variables Usage Guide

PeiDocker supports environment variable substitution in configuration files using the `${VARIABLE_NAME:-default_value}` syntax, similar to Docker Compose. This allows you to create flexible, reusable configurations that can be customized for different environments without modifying the configuration files.

## Quick Start

1. **Use environment variables in your `user_config.yml`:**
   ```yaml
   stage_1:
     ssh:
       host_port: "${SSH_HOST_PORT:-2222}"
   
   stage_2:
     mount:
       shared_data:
         type: host
         host_path: "${DATA_PATH:-C:\\tmp\\data}"
         dst_path: "/data"
   ```

2. **Set environment variables before configuring:**
   ```bash
   # Windows PowerShell
   $env:SSH_HOST_PORT='3333'
   $env:DATA_PATH='D:\my-project\data'
   
   # Linux/macOS
   export SSH_HOST_PORT=3333
   export DATA_PATH='/home/user/project-data'
   ```

3. **Generate configuration:**
   ```bash
   python -m pei_docker.pei configure -p ./my-project
   ```

## Syntax

- `${VARIABLE_NAME}` - Simple substitution (returns empty string if variable doesn't exist)
- `${VARIABLE_NAME:-default_value}` - Substitution with fallback (recommended)
- `${VARIABLE_NAME:-}` - Substitution with empty string as fallback

## Common Use Cases

### 1. Different Development Environments

**Configuration:**
```yaml
stage_1:
  image:
    base: "${BASE_IMAGE:-ubuntu:24.04}"
    output: "${PROJECT_NAME:-my-app}:stage-1"
  ssh:
    host_port: "${SSH_PORT:-2222}"
    users:
      "${DEV_USER:-developer}":
        password: "${DEV_PASSWORD:-devpass}"
```

**Usage:**
```bash
# Development
export PROJECT_NAME="myapp-dev"
export SSH_PORT="2222"

# Production  
export PROJECT_NAME="myapp-prod"
export BASE_IMAGE="ubuntu:22.04"
export SSH_PORT="22022"

# GPU Development
export BASE_IMAGE="nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04"
export PROJECT_NAME="myapp-gpu"
```

### 2. Team Collaboration

Each team member can use their own paths without changing the shared configuration:

**Shared `user_config.yml`:**
```yaml
stage_2:
  mount:
    project_data:
      type: host
      host_path: "${PROJECT_DATA_PATH:-C:\\shared\\data}"
      dst_path: "/data"
    
    workspace:
      type: host
      host_path: "${WORKSPACE_PATH:-C:\\workspace}"
      dst_path: "/workspace"
```

**Team Member A (Windows):**
```powershell
$env:PROJECT_DATA_PATH='D:\team-projects\data'
$env:WORKSPACE_PATH='D:\my-workspace'
```

**Team Member B (Linux):**
```bash
export PROJECT_DATA_PATH="/mnt/shared/project-data"
export WORKSPACE_PATH="/home/bob/workspace"
```

### 3. CI/CD Pipelines

**Configuration:**
```yaml
stage_1:
  image:
    base: "${CI_BASE_IMAGE:-ubuntu:24.04}"
    output: "${CI_IMAGE_NAME:-ci-runner}:${CI_BUILD_NUMBER:-latest}"
  ssh:
    enable: "${CI_ENABLE_SSH:-false}"

stage_2:
  mount:
    artifacts:
      type: host
      host_path: "${CI_ARTIFACTS_PATH:-./artifacts}"
      dst_path: "/artifacts"
```

**In CI Pipeline:**
```yaml
# GitHub Actions example
env:
  CI_IMAGE_NAME: "my-app"
  CI_BUILD_NUMBER: ${{ github.run_number }}
  CI_ENABLE_SSH: "false"
  CI_ARTIFACTS_PATH: "./build-artifacts"
```

### 4. Corporate/Proxy Environments

```yaml
stage_1:
  proxy:
    address: "${PROXY_HOST:-host.docker.internal}"
    port: "${PROXY_PORT:-7890}"
    enable_globally: "${ENABLE_PROXY:-false}"
  
  apt:
    repo_source: "${APT_MIRROR:-aliyun}"
    use_proxy: "${APT_USE_PROXY:-false}"
```

**Usage:**
```bash
# Corporate environment
export PROXY_HOST="proxy.company.com"
export PROXY_PORT="8080"
export ENABLE_PROXY="true"
export APT_MIRROR="company-mirror"
export APT_USE_PROXY="true"
```

## Available Configuration Sections

Environment variables can be used in any string value in the configuration. Common sections include:

### Image Configuration
```yaml
stage_1:
  image:
    base: "${BASE_IMAGE:-ubuntu:24.04}"
    output: "${PROJECT_NAME:-my-app}:${STAGE:-stage-1}"
```

### SSH Configuration
```yaml
stage_1:
  ssh:
    enable: "${ENABLE_SSH:-true}"
    host_port: "${SSH_PORT:-2222}"
    users:
      "${USERNAME:-developer}":
        password: "${PASSWORD:-defaultpass}"
        uid: "${USER_UID:-1000}"
```

### Storage Configuration
```yaml
stage_2:
  storage:
    app:
      type: "${STORAGE_TYPE:-auto-volume}"
      host_path: "${APP_PATH:-}"
      volume_name: "${PROJECT_NAME:-my-app}-app"
```

### Mount Configuration
```yaml
stage_2:
  mount:
    data:
      type: "${MOUNT_TYPE:-host}"
      host_path: "${DATA_PATH:-C:\\data}"
      dst_path: "/data"
```

### Device Configuration
```yaml
stage_1:
  device:
    type: "${DEVICE_TYPE:-cpu}"  # cpu or gpu
```

### Proxy Configuration
```yaml
stage_1:
  proxy:
    address: "${PROXY_HOST:-host.docker.internal}"
    port: "${PROXY_PORT:-7890}"
    enable_globally: "${ENABLE_PROXY:-false}"
```

## Best Practices

### 1. Always Use Fallback Values
```yaml
# Good - works even if variable isn't set
host_port: "${SSH_PORT:-2222}"

# Bad - fails if variable isn't set
host_port: "${SSH_PORT}"
```

### 2. Use Descriptive Variable Names
```yaml
# Good - clear purpose
host_path: "${PROJECT_DATA_PATH:-C:\\data}"

# Bad - unclear purpose  
host_path: "${PATH1:-C:\\data}"
```

### 3. Group Related Variables
```bash
# Database configuration
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="myapp"

# Storage paths
export DATA_PATH="/opt/data"
export CACHE_PATH="/opt/cache"
export LOG_PATH="/opt/logs"
```

### 4. Document Your Variables
Add comments to your configuration explaining the purpose of each variable:

```yaml
# user_config.yml
stage_2:
  mount:
    # Set PROJECT_DATA_PATH to your project's data directory
    # Default: C:\tmp\project-data
    project_data:
      type: host
      host_path: "${PROJECT_DATA_PATH:-C:\\tmp\\project-data}"
      dst_path: "/data"
```

### 5. Create Environment Files
For complex setups, create environment files:

**dev.env:**
```bash
PROJECT_NAME=myapp-dev
SSH_PORT=2222
DEVICE_TYPE=cpu
STORAGE_TYPE=host
DATA_PATH=C:\dev\data
```

**prod.env:**
```bash
PROJECT_NAME=myapp-prod
SSH_PORT=22022
DEVICE_TYPE=gpu
STORAGE_TYPE=manual-volume
```

**Usage:**
```bash
# Windows PowerShell
Get-Content dev.env | ForEach-Object { 
    $name, $value = $_.split('=', 2)
    Set-Item -Path "env:$name" -Value $value
}

# Linux/macOS
source dev.env
# or
export $(cat dev.env | xargs)
```

## Troubleshooting

### Environment Variable Not Being Substituted
- Ensure you're using the correct syntax: `${VAR:-default}`
- Check that the variable is set: `echo $VAR` (Linux/macOS) or `echo $env:VAR` (PowerShell)
- Verify the variable is set before running `configure`

### Windows Path Issues
- Use double backslashes in YAML: `"C:\\path\\to\\dir"`
- Or use forward slashes: `"C:/path/to/dir"`
- Be careful with quotes in PowerShell: `$env:PATH='C:\my\path'`

### Variable Not Found Errors
- Always provide fallback values: `${VAR:-default}`
- Check for typos in variable names
- Ensure variables are exported/set in the correct scope

## Examples

See the [environment-variables.yml](../pei_docker/examples/environment-variables.yml) example for a comprehensive configuration that demonstrates all features.

For more examples, check the [documentation examples](https://igamenovoer.github.io/PeiDocker/examples/#environment-variables).
