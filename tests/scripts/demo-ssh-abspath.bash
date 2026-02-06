#!/bin/bash

# Quick Demo of SSH Absolute Path Feature
# This script provides a guided demonstration of the new SSH absolute path capabilities

set -e

PROJECT_ROOT="/workspace/code/PeiDocker"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}===== $1 =====${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_demo() {
    echo -e "${YELLOW}[DEMO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

pause_for_user() {
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read -r
}

print_header "SSH Absolute Path Feature Demo"

echo "This demo will show you the new SSH absolute path capabilities:"
echo "1. ✅ Absolute paths: /home/user/.ssh/id_rsa.pub"
echo "2. ✅ System key discovery: ~ syntax"
echo "3. ✅ Mixed configurations with backward compatibility"
echo ""
echo "The demo uses safe repository test keys, so no personal SSH keys are exposed."

pause_for_user

print_header "Step 1: Quick Test with Repository Keys"
print_demo "Running: bash tests/scripts/run-ssh-abspath-test.bash testkeys"
echo ""

if bash tests/scripts/run-ssh-abspath-test.bash testkeys; then
    print_success "Repository keys test completed successfully!"
else
    echo "❌ Test failed. Please check the output above."
    exit 1
fi

pause_for_user

print_header "Step 2: Examining Generated Files"
print_demo "Let's look at what was generated:"

BUILD_DIR="build-abspath-testkeys"
GENERATED_DIR="$BUILD_DIR/installation/stage-1/generated"

if [ -d "$GENERATED_DIR" ]; then
    print_info "Generated SSH key files:"
    ls -la "$GENERATED_DIR"/temp-*-*.pub "$GENERATED_DIR"/temp-*-privkey 2>/dev/null || true
    
    echo ""
    print_info "Example generated public key content:"
    if ls "$GENERATED_DIR"/temp-*-pubkey.pub >/dev/null 2>&1; then
        head -1 "$GENERATED_DIR"/temp-*-pubkey.pub | head -c 80
        echo "..."
    fi
else
    echo "❌ Generated directory not found"
fi

pause_for_user

print_header "Step 3: Docker Compose Configuration"
print_demo "Checking SSH key paths in docker-compose.yml:"

COMPOSE_FILE="$BUILD_DIR/docker-compose.yml"
if [ -f "$COMPOSE_FILE" ]; then
    print_info "SSH configuration in Docker Compose:"
    grep -A 2 -B 2 "SSH_.*KEY_FILE" "$COMPOSE_FILE" || true
    
    echo ""
    print_info "Notice the correct container paths:"
    echo "✅ /pei-from-host/stage-1/generated/ (correct)"
    echo "❌ /pei-from-host/installation/stage-1/generated/ (would be wrong)"
else
    echo "❌ Docker compose file not found"
fi

pause_for_user

print_header "Step 4: Validation Check"
print_demo "Running comprehensive validation:"

if bash tests/scripts/validate-ssh-abspath.bash "$BUILD_DIR" "tests/configs/ssh-abspath-testkeys.yml" "Demo Test"; then
    print_success "All validations passed!"
else
    echo "❌ Some validations failed"
fi

pause_for_user

print_header "Step 5: Configuration Examples"
print_demo "Here are the different ways you can now specify SSH keys:"

echo ""
echo "🔹 Absolute Path Examples:"
cat << 'EOF'
users:
  developer:
    pubkey_file: '/home/user/.ssh/id_rsa.pub'
    privkey_file: '/home/user/.ssh/id_ed25519'
EOF

echo ""
echo "🔹 System SSH Key Discovery (~):"
cat << 'EOF'
users:
  developer:
    pubkey_file: '~'   # Finds first available public key
    privkey_file: '~'  # Finds first available private key
EOF

echo ""
echo "🔹 Mixed Usage (all work together):"
cat << 'EOF'
users:
  user1:
    pubkey_file: '~'                          # System discovery
  user2:
    pubkey_file: '/custom/path/key.pub'       # Absolute path
  user3:
    pubkey_file: 'relative/key.pub'           # Relative (existing)
  user4:
    pubkey_text: |                            # Inline (existing)
      ssh-rsa AAAAB3NzaC1yc2E... user@host
EOF

pause_for_user

print_header "Next Steps"
echo "Now you can test the feature with your own SSH keys:"
echo ""
echo "1. Setup personalized tests:"
echo "   bash tests/scripts/setup-ssh-abspath-test.bash"
echo ""
echo "2. Test with your SSH keys:"
echo "   bash tests/scripts/run-ssh-abspath-test.bash user"
echo ""
echo "3. Test system SSH key discovery:"
echo "   bash tests/scripts/run-ssh-abspath-test.bash system"
echo ""
echo "4. Run all tests:"
echo "   bash tests/scripts/run-ssh-abspath-test.bash all"
echo ""
echo "5. Validate everything:"
echo "   bash tests/scripts/validate-ssh-abspath.bash"
echo ""

print_header "Demo Complete"
print_success "The SSH absolute path feature is working correctly!"
echo ""
echo "📖 For detailed documentation, see: tests/README-ssh-abspath.md"
echo "🧪 For more testing options, explore the tests/scripts/ directory"
echo ""
echo "Key benefits of this feature:"
echo "✅ No need to copy SSH keys into project directories"
echo "✅ Easy access to system SSH keys with ~ syntax"
echo "✅ Full backward compatibility with existing configurations"
echo "✅ Secure handling with proper permissions"

# Cleanup demo build
print_info "Cleaning up demo build directory..."
rm -rf "$BUILD_DIR"
print_success "Cleanup complete!"