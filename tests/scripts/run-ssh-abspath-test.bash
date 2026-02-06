#!/bin/bash

# SSH Absolute Path Test Runner Script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}===== $1 =====${NC}"
    echo ""
}

# Function to validate test results
validate_test_results() {
    local build_dir="$1"
    local test_name="$2"
    
    print_status "Validating results for $test_name..."
    
    # Check if generated directory exists
    local generated_dir="$build_dir/installation/stage-1/generated"
    if [ ! -d "$generated_dir" ]; then
        print_error "Generated directory missing: $generated_dir"
        return 1
    fi
    
    # Check for SSH key files
    local key_files=$(find "$generated_dir" -name "temp-*-pubkey.pub" -o -name "temp-*-privkey" 2>/dev/null)
    if [ -z "$key_files" ]; then
        print_warning "No SSH key files found in generated directory"
    else
        print_success "Found SSH key files:"
        echo "$key_files" | while read -r file; do
            echo "  - $(basename "$file")"
        done
    fi
    
    # Check docker-compose.yml
    local compose_file="$build_dir/docker-compose.yml"
    if [ ! -f "$compose_file" ]; then
        print_error "Docker compose file missing: $compose_file"
        return 1
    fi
    
    # Check for correct SSH key paths in compose file
    if grep -q "stage-1/generated" "$compose_file"; then
        print_success "Docker compose contains correct SSH key paths"
    else
        print_warning "SSH key paths may be missing in docker-compose.yml"
    fi
    
    # Check for path bug (incorrect paths)
    if grep -q "/installation/stage-1/generated" "$compose_file"; then
        print_error "FOUND PATH BUG: Incorrect paths in docker-compose.yml"
        print_error "This indicates the path bug mentioned in requirements"
        return 1
    fi
    
    print_success "Validation completed for $test_name"
    return 0
}

# Function to run a single test
run_single_test() {
    local config_file="$1"
    local test_name="$2"
    local build_dir="$3"
    
    print_header "Running Test: $test_name"
    
    # Clean up previous build
    if [ -d "$build_dir" ]; then
        print_status "Cleaning up previous build directory..."
        rm -rf "$build_dir"
    fi
    
    # Create project
    print_status "Creating PeiDocker project..."
    if ! PYTHONPATH="$PROJECT_ROOT" pixi run python -m pei_docker.pei create -p "$build_dir"; then
        print_error "Failed to create project"
        return 1
    fi
    
    # Copy configuration
    if [ ! -f "$config_file" ]; then
        print_error "Configuration file not found: $config_file"
        return 1
    fi
    
    print_status "Using configuration: $config_file"
    cp "$config_file" "$build_dir/user_config.yml"
    
    # Configure project
    print_status "Configuring PeiDocker project..."
    if ! PYTHONPATH="$PROJECT_ROOT" pixi run python -m pei_docker.pei configure -p "$build_dir"; then
        print_error "Failed to configure project"
        return 1
    fi
    
    # Validate results
    if ! validate_test_results "$build_dir" "$test_name"; then
        print_error "Test validation failed"
        return 1
    fi
    
    print_success "Test completed successfully: $test_name"
    return 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 <test_type>"
    echo ""
    echo "Available test types:"
    echo "  testkeys  - Test with repository test keys (safe, recommended)"
    echo "  user      - Test with user's SSH keys (requires setup)"
    echo "  system    - Test system SSH key discovery (~)"
    echo "  mixed     - Test mixed path configurations"
    echo "  all       - Run all available tests"
    echo ""
    echo "Examples:"
    echo "  $0 testkeys     # Quick test with repo keys"
    echo "  $0 all          # Comprehensive testing"
    echo ""
    echo "Note: Run 'bash tests/scripts/setup-ssh-abspath-test.bash' first"
    echo "      to prepare user-specific configurations."
}

# Main script logic
main() {
    cd "$PROJECT_ROOT"
    
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    local test_type="$1"
    
    print_header "SSH Absolute Path Feature Test Runner"
    print_status "Project root: $PROJECT_ROOT"
    print_status "Test type: $test_type"
    
    case "$test_type" in
        "testkeys")
            run_single_test \
                "tests/configs/ssh-abspath-testkeys.yml" \
                "Repository Test Keys" \
                "build-abspath-testkeys"
            ;;
            
        "user")
            local user_config="tests/configs/custom/ssh-abspath-user.yml"
            if [ ! -f "$user_config" ]; then
                print_error "User configuration not found: $user_config"
                print_error "Please run: bash tests/scripts/setup-ssh-abspath-test.bash"
                exit 1
            fi
            run_single_test \
                "$user_config" \
                "User SSH Keys" \
                "build-abspath-user"
            ;;
            
        "system")
            run_single_test \
                "tests/configs/ssh-system-keys-test.yml" \
                "System SSH Key Discovery" \
                "build-abspath-system"
            ;;
            
        "mixed")
            run_single_test \
                "tests/configs/ssh-mixed-paths-test.yml" \
                "Mixed Path Configurations" \
                "build-abspath-mixed"
            ;;
            
        "all")
            print_header "Running All Available Tests"
            
            local failed_tests=()
            
            # Test 1: Repository test keys
            if ! run_single_test \
                "tests/configs/ssh-abspath-testkeys.yml" \
                "Repository Test Keys" \
                "build-abspath-testkeys"; then
                failed_tests+=("Repository Test Keys")
            fi
            
            # Test 2: User SSH keys (if available)
            local user_config="tests/configs/custom/ssh-abspath-user.yml"
            if [ -f "$user_config" ]; then
                if ! run_single_test \
                    "$user_config" \
                    "User SSH Keys" \
                    "build-abspath-user"; then
                    failed_tests+=("User SSH Keys")
                fi
            else
                print_warning "Skipping user SSH keys test (configuration not found)"
                print_warning "Run setup script first: bash tests/scripts/setup-ssh-abspath-test.bash"
            fi
            
            # Test 3: System SSH key discovery
            if ! run_single_test \
                "tests/configs/ssh-system-keys-test.yml" \
                "System SSH Key Discovery" \
                "build-abspath-system"; then
                failed_tests+=("System SSH Key Discovery")
            fi
            
            # Test 4: Mixed configurations
            if ! run_single_test \
                "tests/configs/ssh-mixed-paths-test.yml" \
                "Mixed Path Configurations" \
                "build-abspath-mixed"; then
                failed_tests+=("Mixed Path Configurations")
            fi
            
            # Summary
            print_header "Test Summary"
            if [ ${#failed_tests[@]} -eq 0 ]; then
                print_success "All tests passed! ✅"
            else
                print_error "Some tests failed:"
                for test in "${failed_tests[@]}"; do
                    echo "  ❌ $test"
                done
                exit 1
            fi
            ;;
            
        *)
            print_error "Unknown test type: $test_type"
            show_usage
            exit 1
            ;;
    esac
    
    print_header "Test Complete"
    print_status "You can now examine the generated files in the build directories"
    print_status "To build and test the Docker containers, run:"
    echo "  cd build-abspath-<test-name>"
    echo "  docker compose build stage-1"
    echo "  docker compose up -d stage-1"
    echo "  # Test SSH access with the configured users"
}

# Run main function
main "$@"