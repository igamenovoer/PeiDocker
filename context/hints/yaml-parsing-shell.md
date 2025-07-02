# YAML Parsing in Linux Shell - Complete Guide

## Overview
This guide covers various methods to parse YAML files in Linux shell, with a focus on the `yq` tool which is the most popular and powerful option for YAML processing.

## Primary Tool: yq

**yq** is a lightweight command-line YAML processor that works similarly to `jq` for JSON. It's the recommended tool for robust YAML parsing in shell scripts.

### Installation

```bash
# Ubuntu/Debian
sudo apt-get install yq

# CentOS/RHEL/Fedora
sudo dnf install yq

# macOS
brew install yq

# Using Go
go install github.com/mikefarah/yq/v4@latest

# Using snap
sudo snap install yq

# Download binary directly
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq && chmod +x /usr/bin/yq
```

### Basic Usage Examples

```bash
# Read a single value
yq '.key' file.yaml

# Read nested values
yq '.parent.child' file.yaml

# Read array elements
yq '.array[0]' file.yaml      # First element
yq '.array[]' file.yaml       # All elements

# Multiple values
yq '.name, .age' file.yaml

# Convert YAML to JSON
yq -o=json '.' file.yaml

# Update values in-place
yq -i '.key = "new value"' file.yaml

# Filter arrays
yq '.items[] | select(.name == "specific")' file.yaml

# Raw output (without quotes)
yq -r '.key' file.yaml
```

## Real Examples with PeiDocker Configuration

Based on the `simple-pixi-test.yml` configuration file:

```bash
# Get the base image
yq '.stage_1.image.base' simple-pixi-test.yml
# Output: ubuntu:24.04

# Get SSH port
yq '.stage_1.ssh.port' simple-pixi-test.yml
# Output: 22

# Get all storage types in stage_2
yq '.stage_2.storage[].type' simple-pixi-test.yml

# Get custom build scripts
yq '.stage_2.custom.on_build[]' simple-pixi-test.yml

# Get admin user password
yq '.stage_1.ssh.users.admin.password' simple-pixi-test.yml

# Extract all host paths
yq '.stage_2.storage.*.host_path' simple-pixi-test.yml

# Get storage configuration names
yq '.stage_2.storage | keys' simple-pixi-test.yml

# Check if SSH is enabled
yq '.stage_1.ssh.enable' simple-pixi-test.yml
```

## Advanced yq Operations

```bash
# Conditional selection
yq '.stage_2.storage | to_entries | map(select(.value.type == "host"))' file.yaml

# Transform arrays to strings
yq '.stage_2.custom.on_build | join(" && ")' file.yaml

# Merge files
yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' file1.yaml file2.yaml

# Update multiple values
yq -i '(.stage_1.ssh.port = 2223) | (.stage_1.image.base = "ubuntu:22.04")' file.yaml

# Handle missing keys with defaults
yq '.some.missing.key // "default_value"' file.yaml

# Complex filtering
yq '.stage_2.storage | to_entries | map(select(.value.type == "host")) | .[].key' file.yaml
```

## Practical Bash Script Example

```bash
#!/bin/bash

CONFIG_FILE="simple-pixi-test.yml"

# Function to extract configuration values
get_config() {
    yq "$1" "$CONFIG_FILE"
}

# Extract basic values
BASE_IMAGE=$(get_config '.stage_1.image.base')
SSH_PORT=$(get_config '.stage_1.ssh.port')
OUTPUT_IMAGE=$(get_config '.stage_2.image.output')

echo "Base Image: $BASE_IMAGE"
echo "SSH Port: $SSH_PORT"
echo "Output Image: $OUTPUT_IMAGE"

# Process arrays
echo "Build Scripts:"
yq '.stage_2.custom.on_build[]' "$CONFIG_FILE" | while read -r script; do
    echo "  - $script"
done

# Process storage configurations
echo "Storage Configurations:"
yq '.stage_2.storage | to_entries[] | "\(.key): \(.value.type)"' "$CONFIG_FILE"

# Check conditions
if [[ $(get_config '.stage_1.ssh.enable') == "true" ]]; then
    echo "SSH is enabled on port $(get_config '.stage_1.ssh.host_port')"
fi
```

## Alternative Methods

### Using Python (one-liner)
```bash
python3 -c "import yaml; import sys; print(yaml.safe_load(sys.stdin)['key'])" < file.yaml
```

### Using Ruby
```bash
ruby -ryaml -e "puts YAML.load_file('file.yaml')['key']"

# Convert YAML to JSON
ruby -ryaml -rjson -e 'puts JSON.pretty_generate(YAML.load(ARGF))' < file.yaml
```

### Using awk/sed (for simple cases)
```bash
# Extract simple key-value pairs
grep "^key:" file.yaml | cut -d: -f2 | tr -d ' '

# Using awk for basic parsing
awk '/^key:/ {print $2}' file.yaml

# Extract nested values with awk (limited)
awk '/^  subkey:/ {print $2}' file.yaml
```

## Best Practices

1. **Always quote expressions** to avoid shell interpretation:
   ```bash
   yq '.key' file.yaml        # Good
   yq .key file.yaml          # Risky
   ```

2. **Use `-r` flag** for raw output without quotes when needed:
   ```bash
   yq -r '.string_value' file.yaml
   ```

3. **Use `-i` flag** for in-place editing:
   ```bash
   yq -i '.key = "new_value"' file.yaml
   ```

4. **Test expressions** with simple files first before using in production

5. **Handle missing keys** gracefully:
   ```bash
   yq '.missing.key // "default"' file.yaml
   ```

6. **Use proper error handling** in scripts:
   ```bash
   if ! command -v yq >/dev/null 2>&1; then
       echo "Error: yq is not installed"
       exit 1
   fi
   ```

## Common Use Cases

- **Configuration management**: Extract settings from config files
- **CI/CD pipelines**: Parse deployment configurations  
- **Infrastructure as Code**: Process Kubernetes manifests
- **Data transformation**: Convert between YAML and JSON
- **Validation**: Check configuration values before deployment
- **Dynamic script generation**: Use YAML values to generate shell commands

## Tips for Complex YAML Structures

1. **Multi-document YAML**: Use `---` separator and process with `yq eval-all`
2. **Large files**: Use `yq` with specific paths to avoid loading entire file
3. **Binary data**: Be careful with base64 encoded content (like SSH keys)
4. **Indentation**: YAML is sensitive to indentation - one misaligned space can break parsing

## Performance Considerations

- `yq` is generally fast for most use cases
- For very large files, consider using more specific queries
- When processing multiple values, combine queries when possible
- Use `yq eval-all` for operations across multiple files

## Troubleshooting

- **Invalid YAML**: Use `yq . file.yaml` to validate syntax
- **Missing values**: Use `// "default"` syntax for fallbacks
- **Complex queries**: Break down into smaller parts and test incrementally
- **Shell escaping**: Use single quotes around yq expressions

This guide covers the essential techniques for YAML parsing in shell environments, with `yq` being the primary recommended tool for its power, flexibility, and reliability.
