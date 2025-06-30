# CLI Reference

PeiDocker provides a command-line interface with two main commands: `create` and `configure`. This document provides a comprehensive reference for all available options.

## Commands Overview

```sh
python -m pei_docker.pei [COMMAND] [OPTIONS]
```

Available commands:
- `create`: Create a new PeiDocker project
- `configure`: Process configuration and generate Docker files

## create

Creates a new PeiDocker project with template files, examples, and contrib files.

### Usage

```sh
python -m pei_docker.pei create [OPTIONS]
```

### Options

| Option | Short | Type | Required | Default | Description |
|--------|-------|------|----------|---------|-------------|
| `--project-dir` | `-p` | DIRECTORY | Yes | - | Project directory path |
| `--with-examples` | `-e` | Flag | No | True | Copy example files to project dir |
| `--with-contrib` | - | Flag | No | True | Copy contrib directory to project dir |
| `--help` | - | - | No | - | Show help message |

### Examples

```sh
# Create a complete project with all templates and examples
python -m pei_docker.pei create -p ./my-project

# Create project with examples but without contrib files
python -m pei_docker.pei create -p ./my-project --no-with-contrib

# Create minimal project without examples or contrib
python -m pei_docker.pei create -p ./minimal-project --no-with-examples --no-with-contrib
```

### What Gets Created

When you run the `create` command, the following structure is generated:

```
project_dir/
├── user_config.yml           # Main configuration file
├── compose-template.yml      # Docker Compose template
├── stage-1.Dockerfile        # Stage 1 Dockerfile
├── stage-2.Dockerfile        # Stage 2 Dockerfile
├── installation/             # Installation scripts and configs
│   ├── stage-1/
│   │   ├── custom/          # Custom scripts for stage 1
│   │   ├── system/          # System configuration files
│   │   └── tmp/             # Temporary files directory
│   └── stage-2/
│       ├── custom/          # Custom scripts for stage 2
│       ├── system/          # System configuration files
│       └── tmp/             # Temporary files directory
├── examples/                 # Example configurations (if --with-examples)
│   ├── minimal-ubuntu-ssh.yml
│   ├── gpu-with-opengl-win32.yml
│   ├── environment-variables.yml
│   └── ... (more examples)
└── contrib/                  # Contributed configurations (if --with-contrib)
    └── ... (community contributions)
```

## configure

Processes the user configuration file and generates the final `docker-compose.yml` and related Docker files.

### Usage

```sh
python -m pei_docker.pei configure [OPTIONS]
```

### Options

| Option | Short | Type | Required | Default | Description |
|--------|-------|------|----------|---------|-------------|
| `--project-dir` | `-p` | DIRECTORY | Yes | - | Project directory path |
| `--config` | `-c` | FILE | No | `user_config.yml` | Config file name (relative to project dir) |
| `--full-compose` | `-f` | Flag | No | False | Generate full compose file with x-??? sections |
| `--help` | - | - | No | - | Show help message |

### Examples

```sh
# Use default configuration file (user_config.yml)
python -m pei_docker.pei configure -p ./my-project

# Use a custom configuration file
python -m pei_docker.pei configure -p ./my-project -c prod-config.yml

# Generate full compose file with extended Docker Compose sections
python -m pei_docker.pei configure -p ./my-project -f

# Use absolute path for config file
python -m pei_docker.pei configure -p ./my-project -c /path/to/my-config.yml
```

### Environment Variable Processing

The `configure` command automatically processes environment variable substitution in your configuration files using the `${VARIABLE_NAME:-default_value}` syntax. This happens before Docker files are generated.

### Output Files

After running `configure`, the following files are generated/updated:

- `docker-compose.yml`: Main Docker Compose configuration
- Updated Dockerfiles (if necessary)
- Processed configuration with environment variables substituted

## Global Options

### Help

Get help for any command:

```sh
# General help
python -m pei_docker.pei --help

# Command-specific help
python -m pei_docker.pei create --help
python -m pei_docker.pei configure --help
```

### Error Handling

The CLI provides informative error messages for common issues:

- Missing required options
- Invalid file paths
- Configuration file errors
- Environment variable substitution errors

## Common Workflows

### Development Workflow

```sh
# 1. Create new project
python -m pei_docker.pei create -p ./dev-project

# 2. Edit user_config.yml with your requirements
# (edit ./dev-project/user_config.yml)

# 3. Generate Docker files
python -m pei_docker.pei configure -p ./dev-project

# 4. Build and run
cd ./dev-project
docker compose build stage-1
docker compose build stage-2
docker compose up stage-2
```

### Production Deployment Workflow

```sh
# 1. Create project from template
python -m pei_docker.pei create -p ./prod-deployment --no-with-examples

# 2. Use environment-specific config
python -m pei_docker.pei configure -p ./prod-deployment -c production.yml

# 3. Deploy with production environment variables
export PROJECT_NAME="myapp-prod"
export BASE_IMAGE="ubuntu:22.04"
export SSH_PORT="22022"
python -m pei_docker.pei configure -p ./prod-deployment
```

### CI/CD Integration

```sh
# In your CI/CD pipeline
export CI_BUILD_NUMBER="${BUILD_NUMBER}"
export CI_IMAGE_NAME="myapp"
export CI_BASE_IMAGE="ubuntu:24.04"

python -m pei_docker.pei create -p ./ci-build --no-with-examples --no-with-contrib
python -m pei_docker.pei configure -p ./ci-build -c ci-config.yml
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure the project directory is writable
2. **Missing Config File**: Check that the config file exists and the path is correct
3. **Environment Variable Issues**: Verify environment variables are set correctly
4. **Docker Build Failures**: Check the generated docker-compose.yml for errors

### Debug Tips

- Use `--full-compose` to see all generated Docker Compose sections
- Check the generated `docker-compose.yml` file for correctness
- Verify environment variable substitution by examining the processed configuration
- Use Docker Compose validation: `docker compose config` in the project directory
