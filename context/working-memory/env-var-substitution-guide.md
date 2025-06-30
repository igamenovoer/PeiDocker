# Environment Variable Substitution in PeiDocker

## Overview

PeiDocker now supports environment variable substitution with fallback values, similar to Docker Compose. This allows you to create more flexible and reusable configurations.

## Syntax

### Basic Environment Variable
```yaml
host_path: "${MY_VAR}"
```
Uses the value of `MY_VAR` environment variable. If not set, keeps the literal string `${MY_VAR}`.

### Environment Variable with Fallback
```yaml
host_path: "${MY_VAR:-/default/path}"
```
Uses the value of `MY_VAR` if set, otherwise uses `/default/path` as the default value.

## Examples

### 1. Mount Paths
```yaml
mount:
  shared_host:
    type: host
    host_path: "${SHARED_HOST_PATH:-/mnt/d/docker-space/workspace/minimal-gpu}"
    dst_path: "/shared"
```

**Usage:**
```bash
# Use default path
python -m pei_docker.pei configure -p ./build

# Use custom path
export SHARED_HOST_PATH="/custom/path"
python -m pei_docker.pei configure -p ./build
```

### 2. SSH Configuration
```yaml
ssh:
  host_port: "${SSH_PORT:-2222}"
  users:
    "${USER_NAME:-developer}":
      password: "${USER_PASSWORD:-123456}"
      uid: "${USER_UID:-1000}"
```

**Usage:**
```bash
# Use defaults (port 2222, user 'developer')
python -m pei_docker.pei configure -p ./build

# Customize
export SSH_PORT=3333
export USER_NAME=myuser
export USER_PASSWORD=mysecret
export USER_UID=1001
python -m pei_docker.pei configure -p ./build
```

### 3. Project Configuration
```yaml
stage_1:
  image:
    base: "${BASE_IMAGE:-ubuntu:24.04}"
    output: "${PROJECT_NAME:-myapp}:stage-1"

stage_2:
  storage:
    app:
      type: manual-volume
      volume_name: "${PROJECT_NAME:-myapp}-app"
    data:
      type: manual-volume
      volume_name: "${PROJECT_NAME:-myapp}-data"
```

**Usage:**
```bash
# For different projects
export PROJECT_NAME=project-alpha
export BASE_IMAGE=nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
python -m pei_docker.pei configure -p ./project-alpha

export PROJECT_NAME=project-beta
export BASE_IMAGE=ubuntu:22.04
python -m pei_docker.pei configure -p ./project-beta
```

### 4. Development vs Production
```yaml
proxy:
  address: "${PROXY_HOST:-host.docker.internal}"
  port: "${PROXY_PORT:-7890}"

apt:
  repo_source: "${APT_REPO:-aliyun}"

mount:
  workspace:
    type: host
    host_path: "${WORKSPACE_PATH:-./workspace}"
    dst_path: "/workspace"
```

**Development:**
```bash
export WORKSPACE_PATH="/home/dev/projects/myapp"
export PROXY_PORT=7890
export APT_REPO=aliyun
```

**Production:**
```bash
export WORKSPACE_PATH="/opt/app/workspace"
unset PROXY_PORT  # Uses default
export APT_REPO=official
```

## Benefits

1. **Reusable Configurations**: Same config file works across different environments
2. **CI/CD Friendly**: Easy to customize builds in automated pipelines
3. **Developer Flexibility**: Each developer can customize paths without modifying configs
4. **Environment Isolation**: Different projects can use different settings

## Best Practices

### 1. Always Provide Sensible Defaults
```yaml
# Good - provides reasonable fallback
host_path: "${DATA_PATH:-./data}"

# Less ideal - no fallback, might break if env var missing
host_path: "${DATA_PATH}"
```

### 2. Use Descriptive Variable Names
```yaml
# Good - clear what this variable controls
host_path: "${SHARED_WORKSPACE_PATH:-/tmp/workspace}"

# Less clear - ambiguous name
host_path: "${PATH:-/tmp/workspace}"
```

### 3. Document Your Variables
Create a `.env.example` file:
```bash
# Project configuration
PROJECT_NAME=my-awesome-project
BASE_IMAGE=ubuntu:24.04

# Paths
SHARED_WORKSPACE_PATH=/home/user/workspace
PROJECT_DATA_PATH=/home/user/data

# SSH settings
SSH_PORT=2222
USER_NAME=developer
USER_PASSWORD=secure123

# Network
PROXY_HOST=proxy.company.com
PROXY_PORT=8080
```

### 4. Environment-Specific Configs
You can create different environment files:

**dev.env:**
```bash
PROJECT_NAME=myapp-dev
SSH_PORT=2222
WORKSPACE_PATH=./dev-workspace
```

**prod.env:**
```bash
PROJECT_NAME=myapp-prod
SSH_PORT=2223
WORKSPACE_PATH=/opt/myapp/workspace
```

**Usage:**
```bash
# Development
source dev.env
python -m pei_docker.pei configure -p ./build

# Production
source prod.env
python -m pei_docker.pei configure -p ./build
```

## Integration with Existing Workflow

The environment variable substitution happens automatically when you run:
```bash
python -m pei_docker.pei configure -p ./build
```

Environment variables are resolved at configuration time, so the generated `docker-compose.yml` will contain the final resolved values.

## Limitations

- Environment variables are resolved only during the `configure` step
- No support for complex expressions (only simple substitution)
- Variables in nested interpolations are not supported (e.g., `${${VAR}_SUFFIX}`)
- Only string values support environment variable substitution
