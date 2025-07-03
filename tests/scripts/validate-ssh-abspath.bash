#!/bin/bash

# SSH Absolute Path Feature Validation Script
# This script performs detailed validation of the SSH absolute path implementation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}===== $1 =====${NC}"
    echo ""
}

print_check() {
    echo -e "${BLUE}🔍${NC} $1"
}

print_pass() {
    echo -e "${GREEN}✅${NC} $1"
}

print_fail() {
    echo -e "${RED}❌${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# Global counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to record check result
check_result() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ "$1" -eq 0 ]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        print_pass "$2"
    else
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        print_fail "$2"
    fi
}

# Function to validate SSH key file content
validate_ssh_key_file() {
    local file_path="$1"
    local expected_type="$2"  # "public" or "private"
    local description="$3"
    
    print_check "Validating $description: $file_path"
    
    if [ ! -f "$file_path" ]; then
        check_result 1 "File does not exist"
        return 1
    fi
    
    # Check file permissions
    local perms=$(stat -c "%a" "$file_path")
    if [ "$expected_type" = "public" ]; then
        if [ "$perms" = "644" ]; then
            check_result 0 "Public key has correct permissions (644)"
        else
            check_result 1 "Public key has incorrect permissions ($perms, expected 644)"
        fi
    else
        if [ "$perms" = "600" ]; then
            check_result 0 "Private key has correct permissions (600)"
        else
            check_result 1 "Private key has incorrect permissions ($perms, expected 600)"
        fi
    fi
    
    # Check file content format
    local first_line=$(head -n 1 "$file_path")
    if [ "$expected_type" = "public" ]; then
        if [[ "$first_line" =~ ^ssh-(rsa|dsa|ecdsa|ed25519) ]]; then
            check_result 0 "Public key has valid SSH format"
        else
            check_result 1 "Public key has invalid format: $first_line"
        fi
    else
        if [[ "$first_line" =~ ^-----BEGIN ]]; then
            check_result 0 "Private key has valid format"
        else
            check_result 1 "Private key has invalid format: $first_line"
        fi
    fi
    
    # Check file size (should not be empty)
    local file_size=$(stat -c "%s" "$file_path")
    if [ "$file_size" -gt 0 ]; then
        check_result 0 "File is not empty ($file_size bytes)"
    else
        check_result 1 "File is empty"
    fi
}

# Function to validate docker-compose.yml paths
validate_compose_paths() {
    local compose_file="$1"
    local build_dir="$2"
    
    print_check "Validating Docker Compose SSH paths"
    
    if [ ! -f "$compose_file" ]; then
        check_result 1 "Docker compose file not found: $compose_file"
        return 1
    fi
    
    # Check for SSH key environment variables
    if grep -q "SSH_PUBKEY_FILE:" "$compose_file" || grep -q "SSH_PRIVKEY_FILE:" "$compose_file"; then
        check_result 0 "SSH key environment variables found in compose file"
    else
        check_result 1 "SSH key environment variables missing from compose file"
        return 1
    fi
    
    # Extract SSH key paths
    local pubkey_paths=$(grep "SSH_PUBKEY_FILE:" "$compose_file" | sed 's/.*SSH_PUBKEY_FILE: //' | tr ',' '\n' | grep -v '^$' || true)
    local privkey_paths=$(grep "SSH_PRIVKEY_FILE:" "$compose_file" | sed 's/.*SSH_PRIVKEY_FILE: //' | tr ',' '\n' | grep -v '^$' | tr -d "'" || true)
    
    # Validate each path format
    echo "$pubkey_paths" | while read -r path; do
        if [ -n "$path" ]; then
            if [[ "$path" =~ ^/pei-from-host/stage-1/generated/ ]]; then
                check_result 0 "Public key path has correct format: $path"
            else
                check_result 1 "Public key path has incorrect format: $path"
            fi
        fi
    done
    
    echo "$privkey_paths" | while read -r path; do
        if [ -n "$path" ]; then
            if [[ "$path" =~ ^/pei-from-host/stage-1/generated/ ]]; then
                check_result 0 "Private key path has correct format: $path"
            else
                check_result 1 "Private key path has incorrect format: $path"
            fi
        fi
    done
    
    # Check for the path bug (incorrect paths)
    if grep -q "/pei-from-host/installation/stage-1/generated" "$compose_file"; then
        check_result 1 "CRITICAL: Path bug detected! Found incorrect installation paths"
    else
        check_result 0 "No path bug detected"
    fi
}

# Function to validate that source files exist and match generated files
validate_source_file_matching() {
    local config_file="$1"
    local build_dir="$2"
    
    print_check "Validating source file matching"
    
    if [ ! -f "$config_file" ]; then
        check_result 1 "Config file not found: $config_file"
        return 1
    fi
    
    # Extract absolute paths from config
    local abs_pubkey_paths=$(grep "pubkey_file:" "$config_file" | grep -E "pubkey_file: ['\"]?/" | sed "s/.*pubkey_file: ['\"]*//" | sed "s/['\"]*//" || true)
    local abs_privkey_paths=$(grep "privkey_file:" "$config_file" | grep -E "privkey_file: ['\"]?/" | sed "s/.*privkey_file: ['\"]*//" | sed "s/['\"]*//" || true)
    
    # Check if source files exist
    echo "$abs_pubkey_paths" | while read -r source_path; do
        if [ -n "$source_path" ] && [ "$source_path" != "~" ]; then
            if [ -f "$source_path" ]; then
                check_result 0 "Source public key exists: $source_path"
                
                # Find corresponding generated file
                local user_name=$(grep -B 5 "pubkey_file: ['\"]\\?$source_path" "$config_file" | grep -E "^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*:" | tail -n 1 | sed 's/:.*//' | xargs)
                if [ -n "$user_name" ]; then
                    local generated_file="$build_dir/installation/stage-1/generated/temp-$user_name-pubkey.pub"
                    if [ -f "$generated_file" ]; then
                        # Compare file contents
                        if cmp -s "$source_path" "$generated_file"; then
                            check_result 0 "Generated public key matches source for user: $user_name"
                        else
                            check_result 1 "Generated public key differs from source for user: $user_name"
                        fi
                    else
                        check_result 1 "Generated public key file not found for user: $user_name"
                    fi
                fi
            else
                check_result 1 "Source public key not found: $source_path"
            fi
        fi
    done
    
    echo "$abs_privkey_paths" | while read -r source_path; do
        if [ -n "$source_path" ] && [ "$source_path" != "~" ]; then
            if [ -f "$source_path" ]; then
                check_result 0 "Source private key exists: $source_path"
                
                # Find corresponding generated file
                local user_name=$(grep -B 5 "privkey_file: ['\"]\\?$source_path" "$config_file" | grep -E "^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*:" | tail -n 1 | sed 's/:.*//' | xargs)
                if [ -n "$user_name" ]; then
                    local generated_file="$build_dir/installation/stage-1/generated/temp-$user_name-privkey"
                    if [ -f "$generated_file" ]; then
                        # Compare file contents
                        if cmp -s "$source_path" "$generated_file"; then
                            check_result 0 "Generated private key matches source for user: $user_name"
                        else
                            check_result 1 "Generated private key differs from source for user: $user_name"
                        fi
                    else
                        check_result 1 "Generated private key file not found for user: $user_name"
                    fi
                fi
            else
                check_result 1 "Source private key not found: $source_path"
            fi
        fi
    done
}

# Function to validate a single build directory
validate_build_directory() {
    local build_dir="$1"
    local config_file="$2"
    local test_name="$3"
    
    print_header "Validating: $test_name"
    print_check "Build directory: $build_dir"
    print_check "Config file: $config_file"
    
    if [ ! -d "$build_dir" ]; then
        check_result 1 "Build directory does not exist: $build_dir"
        return 1
    fi
    
    local generated_dir="$build_dir/installation/stage-1/generated"
    if [ ! -d "$generated_dir" ]; then
        check_result 1 "Generated directory does not exist: $generated_dir"
        return 1
    fi
    
    check_result 0 "Build directory structure is valid"
    
    # Find and validate SSH key files
    local pubkey_files=$(find "$generated_dir" -name "temp-*-pubkey.pub" 2>/dev/null || true)
    local privkey_files=$(find "$generated_dir" -name "temp-*-privkey" 2>/dev/null || true)
    
    if [ -n "$pubkey_files" ]; then
        local count=$(echo "$pubkey_files" | wc -l)
        check_result 0 "Found $count public key file(s)"
        
        echo "$pubkey_files" | while read -r file; do
            validate_ssh_key_file "$file" "public" "Public key"
        done
    else
        print_warn "No public key files found"
    fi
    
    if [ -n "$privkey_files" ]; then
        local count=$(echo "$privkey_files" | wc -l)
        check_result 0 "Found $count private key file(s)"
        
        echo "$privkey_files" | while read -r file; do
            validate_ssh_key_file "$file" "private" "Private key"
        done
    else
        print_warn "No private key files found"
    fi
    
    # Validate docker-compose.yml
    local compose_file="$build_dir/docker-compose.yml"
    validate_compose_paths "$compose_file" "$build_dir"
    
    # Validate source file matching (for absolute paths)
    if [ -f "$config_file" ]; then
        validate_source_file_matching "$config_file" "$build_dir"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [build_directory config_file test_name]"
    echo ""
    echo "If no arguments provided, validates all known test builds"
    echo ""
    echo "Examples:"
    echo "  $0                                              # Validate all builds"
    echo "  $0 build-abspath-testkeys tests/configs/... testkeys   # Validate specific build"
}

# Main validation function
main() {
    cd "$PROJECT_ROOT"
    
    print_header "SSH Absolute Path Feature Validation"
    
    if [ $# -eq 3 ]; then
        # Validate specific build
        validate_build_directory "$1" "$2" "$3"
    elif [ $# -eq 0 ]; then
        # Validate all known builds
        local builds=(
            "build-abspath-testkeys:tests/configs/ssh-abspath-testkeys.yml:Repository Test Keys"
            "build-abspath-user:tests/configs/custom/ssh-abspath-user.yml:User SSH Keys"
            "build-abspath-system:tests/configs/ssh-system-keys-test.yml:System SSH Key Discovery"
            "build-abspath-mixed:tests/configs/ssh-mixed-paths-test.yml:Mixed Path Configurations"
        )
        
        for build_info in "${builds[@]}"; do
            IFS=':' read -r build_dir config_file test_name <<< "$build_info"
            
            if [ -d "$build_dir" ]; then
                validate_build_directory "$build_dir" "$config_file" "$test_name"
            else
                print_warn "Skipping $test_name: build directory not found ($build_dir)"
            fi
        done
    else
        show_usage
        exit 1
    fi
    
    print_header "Validation Summary"
    echo "Total checks: $TOTAL_CHECKS"
    echo "Passed: $PASSED_CHECKS"
    echo "Failed: $FAILED_CHECKS"
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        print_pass "All validations passed! ✅"
        exit 0
    else
        print_fail "$FAILED_CHECKS validation(s) failed ❌"
        exit 1
    fi
}

# Run main function
main "$@"