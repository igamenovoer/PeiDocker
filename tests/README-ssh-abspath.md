# SSH Absolute Path Feature Testing

This directory contains comprehensive test configurations and scripts for testing the SSH absolute path feature in PeiDocker.

## 🚀 Quick Start

1. **Run the setup script to prepare tests:**
   ```bash
   bash tests/scripts/setup-ssh-abspath-test.bash
   ```

2. **Run a quick test with repository keys:**
   ```bash
   bash tests/scripts/run-ssh-abspath-test.bash testkeys
   ```

3. **Validate the results:**
   ```bash
   bash tests/scripts/validate-ssh-abspath.bash
   ```

## 📁 Test Configurations

### Repository Test Keys (`ssh-abspath-testkeys.yml`)
- **Purpose**: Safe testing using test keys included in the repository
- **Features**: Tests absolute paths with known keys
- **Recommended**: Start here for initial testing
- **SSH Keys**: Uses `tests/test-keys/peidocker-test-*.key`

### User SSH Keys (`ssh-abspath-user.yml`)
- **Purpose**: Test with your actual SSH keys
- **Features**: Real-world usage scenarios
- **Setup Required**: Run setup script first
- **SSH Keys**: Uses your `~/.ssh/` keys

### System SSH Key Discovery (`ssh-system-keys-test.yml`)
- **Purpose**: Test `~` syntax for automatic key discovery
- **Features**: Tests priority order: `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`
- **SSH Keys**: Automatically discovers from `~/.ssh/`

### Mixed Paths (`ssh-mixed-paths-test.yml`)
- **Purpose**: Test combination of different path types
- **Features**: Relative paths, absolute paths, `~` syntax, inline keys
- **SSH Keys**: Mixed sources

### Template (`ssh-abspath-template.yml`)
- **Purpose**: Template for creating custom configurations
- **Features**: Placeholder paths that get customized by setup script
- **Usage**: Automatically processed by setup script

## 🧪 Test Scripts

### Setup Script (`setup-ssh-abspath-test.bash`)
**Purpose**: Interactive setup that prepares personalized test configurations

**What it does:**
- Scans your `~/.ssh/` directory for available keys
- Creates customized test configurations using your SSH keys
- Provides guidance on which tests to run
- Shows available test commands

**Usage:**
```bash
bash tests/scripts/setup-ssh-abspath-test.bash
```

### Test Runner (`run-ssh-abspath-test.bash`)
**Purpose**: Comprehensive test runner for different scenarios

**Available test types:**
- `testkeys` - Repository test keys (safe, recommended first)
- `user` - Your SSH keys (requires setup)
- `system` - System SSH key discovery (~)
- `mixed` - Mixed path configurations
- `all` - Run all available tests

**Usage:**
```bash
bash tests/scripts/run-ssh-abspath-test.bash <test_type>
```

**Examples:**
```bash
# Quick test with repo keys
bash tests/scripts/run-ssh-abspath-test.bash testkeys

# Test with your SSH keys
bash tests/scripts/run-ssh-abspath-test.bash user

# Run all tests
bash tests/scripts/run-ssh-abspath-test.bash all
```

### Validation Script (`validate-ssh-abspath.bash`)
**Purpose**: Detailed validation of test results and implementation correctness

**What it checks:**
- Generated SSH key file formats and permissions
- Docker Compose path correctness
- Source file matching for absolute paths
- Prevention of known path bugs
- File content integrity

**Usage:**
```bash
# Validate all test builds
bash tests/scripts/validate-ssh-abspath.bash

# Validate specific build
bash tests/scripts/validate-ssh-abspath.bash build-abspath-testkeys tests/configs/ssh-abspath-testkeys.yml "Repository Test Keys"
```

## 🔧 Feature Testing Matrix

| Feature | Repository Keys | User Keys | System Discovery | Mixed Paths |
|---------|----------------|-----------|------------------|-------------|
| Absolute path public key | ✅ | ✅ | ❌ | ✅ |
| Absolute path private key | ✅ | ✅ | ❌ | ✅ |
| `~` syntax public key | ❌ | ❌ | ✅ | ✅ |
| `~` syntax private key | ❌ | ❌ | ✅ | ❌ |
| Relative paths | ❌ | ❌ | ❌ | ✅ |
| Inline text keys | ❌ | ❌ | ❌ | ✅ |
| Password-only users | ✅ | ✅ | ✅ | ✅ |

## 📝 Test Workflow

### 1. Initial Setup
```bash
# Clone and setup
cd /workspace/code/PeiDocker
bash tests/scripts/setup-ssh-abspath-test.bash
```

### 2. Basic Testing
```bash
# Test with repository keys (safe)
bash tests/scripts/run-ssh-abspath-test.bash testkeys

# Validate results
bash tests/scripts/validate-ssh-abspath.bash
```

### 3. Advanced Testing
```bash
# Test system SSH key discovery
bash tests/scripts/run-ssh-abspath-test.bash system

# Test with your SSH keys
bash tests/scripts/run-ssh-abspath-test.bash user

# Test mixed configurations
bash tests/scripts/run-ssh-abspath-test.bash mixed
```

### 4. Comprehensive Testing
```bash
# Run all tests
bash tests/scripts/run-ssh-abspath-test.bash all

# Full validation
bash tests/scripts/validate-ssh-abspath.bash
```

### 5. Manual Docker Testing (Optional)
```bash
# Navigate to a test build
cd build-abspath-testkeys

# Build the Docker images
docker compose build stage-1 --progress=plain
docker compose build stage-2 --progress=plain

# Start the container
docker compose up -d stage-2

# Test SSH access (example)
ssh -p 2226 user_repo_pubkey@localhost  # Password: repo123

# Cleanup
docker compose down
```

## 🔍 What Gets Tested

### File Generation
- SSH keys are copied from absolute paths to `installation/stage-1/generated/`
- Generated files have correct permissions (644 for public, 600 for private)
- File contents match source files exactly

### Path Resolution
- Absolute paths like `/home/user/.ssh/id_rsa.pub` work correctly
- `~` syntax discovers SSH keys in priority order
- Container paths use correct format: `/pei-from-host/stage-1/generated/`
- No path bugs (avoids incorrect `/pei-from-host/installation/` paths)

### Configuration Processing
- Docker Compose files contain correct SSH key environment variables
- Multiple users with different key sources work together
- Backward compatibility with existing relative path functionality

### Error Handling
- Missing source files are properly reported
- Invalid paths are caught and reported
- Permission errors are handled gracefully

## 🐛 Troubleshooting

### "No SSH keys found"
- Ensure you have SSH keys in `~/.ssh/`
- Generate keys: `ssh-keygen -t rsa -b 2048`
- Run setup script: `bash tests/scripts/setup-ssh-abspath-test.bash`

### "Configuration file not found"
- Run setup script first: `bash tests/scripts/setup-ssh-abspath-test.bash`
- Check that files exist in `tests/configs/custom/`

### "Permission denied" errors
- Check SSH key file permissions in `~/.ssh/`
- Ensure you have read access to your SSH keys

### "Path bug detected"
- This indicates a regression in the implementation
- Check that container paths use `/pei-from-host/stage-1/generated/`
- Not `/pei-from-host/installation/stage-1/generated/`

### Docker build failures
- Check that all SSH key files exist in generated directory
- Verify docker-compose.yml has correct paths
- Run validation script to identify specific issues

## 📊 Expected Results

After successful testing, you should see:

1. **Generated Files**: SSH key files in `build-*/installation/stage-1/generated/`
2. **Correct Permissions**: 644 for public keys, 600 for private keys
3. **Matching Content**: Generated files match source files exactly
4. **Valid Docker Compose**: Correct container paths for SSH keys
5. **No Path Bugs**: Validation passes all checks

## 🔗 Related Documentation

- [SSH Key Enhancement Implementation Plan](../context/tasks/ssh-key-advanced/implementation-plan-abspath.md)
- [Implementation Summary](../context/tasks/ssh-key-advanced/implementation-summary-abspath.md)
- [Original Task Specification](../context/tasks/ssh-key-advanced/task-support-key-abspath.md)
- [Main PeiDocker Documentation](../docs/examples/basic.md)

## 💡 Tips for Testing

1. **Start with repository keys** - they're safe and don't expose your personal SSH keys
2. **Use validation script** - it catches issues that manual inspection might miss
3. **Test incrementally** - run one test type at a time to isolate issues
4. **Check file permissions** - SSH is sensitive to incorrect permissions
5. **Verify paths** - the most common issue is incorrect container paths

## 🚨 Security Notes

- Test keys in `tests/test-keys/` are for testing only
- Your personal SSH keys are only read, never modified
- Generated files are copies, originals remain untouched
- Use caution when committing test builds (may contain SSH keys)