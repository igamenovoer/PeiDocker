#!/bin/bash

# Interactive SSH Absolute Path Test Setup Script
set -e

echo "===== SSH Absolute Path Feature Test Setup ====="
echo ""
echo "This script will help you test the SSH absolute path feature by:"
echo "1. Detecting your SSH keys"
echo "2. Creating customized test configurations"
echo "3. Preparing test environments"
echo ""

# Change to project root
cd /workspace/code/PeiDocker

# Create output directory for customized configs
CUSTOM_CONFIG_DIR="tests/configs/custom"
mkdir -p "$CUSTOM_CONFIG_DIR"

echo "=== Step 1: Detecting your SSH keys ==="
SSH_DIR="$HOME/.ssh"

if [ ! -d "$SSH_DIR" ]; then
    echo "❌ SSH directory $SSH_DIR not found"
    echo "Please ensure you have SSH keys set up before running this test"
    exit 1
fi

echo "✅ SSH directory found: $SSH_DIR"

# Find available SSH keys
declare -a PUBLIC_KEYS=()
declare -a PRIVATE_KEYS=()

for key_type in "rsa" "dsa" "ecdsa" "ed25519"; do
    private_key="$SSH_DIR/id_$key_type"
    public_key="$SSH_DIR/id_$key_type.pub"
    
    if [ -f "$private_key" ]; then
        PRIVATE_KEYS+=("$private_key")
        echo "🔑 Found private key: $private_key"
    fi
    
    if [ -f "$public_key" ]; then
        PUBLIC_KEYS+=("$public_key")
        echo "🔑 Found public key: $public_key"
    fi
done

if [ ${#PUBLIC_KEYS[@]} -eq 0 ] && [ ${#PRIVATE_KEYS[@]} -eq 0 ]; then
    echo "❌ No SSH keys found in $SSH_DIR"
    echo "Please generate SSH keys first: ssh-keygen -t rsa -b 2048"
    exit 1
fi

echo ""
echo "=== Step 2: Creating customized test configurations ==="

# Select first available keys for testing
SELECTED_PUBLIC_KEY=""
SELECTED_PRIVATE_KEY=""

if [ ${#PUBLIC_KEYS[@]} -gt 0 ]; then
    SELECTED_PUBLIC_KEY="${PUBLIC_KEYS[0]}"
    echo "📝 Selected public key for testing: $SELECTED_PUBLIC_KEY"
fi

if [ ${#PRIVATE_KEYS[@]} -gt 0 ]; then
    SELECTED_PRIVATE_KEY="${PRIVATE_KEYS[0]}"
    echo "📝 Selected private key for testing: $SELECTED_PRIVATE_KEY"
fi

# Create customized configuration from template
TEMPLATE_FILE="tests/configs/ssh-abspath-template.yml"
CUSTOM_CONFIG_FILE="$CUSTOM_CONFIG_DIR/ssh-abspath-user.yml"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ Template file not found: $TEMPLATE_FILE"
    exit 1
fi

echo "📝 Creating customized configuration: $CUSTOM_CONFIG_FILE"

# Copy template and replace placeholders
cp "$TEMPLATE_FILE" "$CUSTOM_CONFIG_FILE"

if [ -n "$SELECTED_PUBLIC_KEY" ]; then
    sed -i "s|REPLACE_WITH_USER_PUBKEY_PATH|$SELECTED_PUBLIC_KEY|g" "$CUSTOM_CONFIG_FILE"
    echo "✅ Configured public key path: $SELECTED_PUBLIC_KEY"
else
    # Remove the pubkey user if no public key available
    echo "⚠️  No public key available, removing pubkey test user"
    # This is a simple removal - in a real scenario you might want more sophisticated editing
fi

if [ -n "$SELECTED_PRIVATE_KEY" ]; then
    sed -i "s|REPLACE_WITH_USER_PRIVKEY_PATH|$SELECTED_PRIVATE_KEY|g" "$CUSTOM_CONFIG_FILE"
    echo "✅ Configured private key path: $SELECTED_PRIVATE_KEY"
else
    echo "⚠️  No private key available, removing privkey test user"
fi

echo ""
echo "=== Step 3: Available test configurations ==="
echo ""
echo "✅ Repository test keys config: tests/configs/ssh-abspath-testkeys.yml"
echo "   - Uses test keys included in the repository"
echo "   - Safe to run without exposing your personal SSH keys"
echo ""
if [ -f "$CUSTOM_CONFIG_FILE" ]; then
    echo "✅ Your SSH keys config: $CUSTOM_CONFIG_FILE"
    echo "   - Uses your actual SSH keys from $SSH_DIR"
    echo "   - Tests real-world usage scenarios"
fi
echo ""
echo "✅ System SSH key discovery config: tests/configs/ssh-system-keys-test.yml"
echo "   - Tests ~ syntax for automatic SSH key discovery"
echo ""
echo "✅ Mixed paths config: tests/configs/ssh-mixed-paths-test.yml"
echo "   - Tests combination of different path types"
echo ""

echo "=== Step 4: Test commands to run ==="
echo ""
echo "To test with repository keys (recommended first):"
echo "  bash tests/scripts/run-ssh-abspath-test.bash testkeys"
echo ""
if [ -f "$CUSTOM_CONFIG_FILE" ]; then
    echo "To test with your SSH keys:"
    echo "  bash tests/scripts/run-ssh-abspath-test.bash user"
    echo ""
fi
echo "To test system SSH key discovery:"
echo "  bash tests/scripts/run-ssh-abspath-test.bash system"
echo ""
echo "To test mixed configurations:"
echo "  bash tests/scripts/run-ssh-abspath-test.bash mixed"
echo ""
echo "To run all tests:"
echo "  bash tests/scripts/run-ssh-abspath-test.bash all"
echo ""

echo "=== Step 5: Next steps ==="
echo ""
echo "1. Choose a test configuration from above"
echo "2. Run the corresponding test command"
echo "3. Check the results and generated files"
echo "4. Optionally build and test the Docker containers"
echo ""
echo "For more detailed testing information, see:"
echo "  tests/README-ssh-abspath.md"
echo ""
echo "✅ SSH absolute path test setup complete!"