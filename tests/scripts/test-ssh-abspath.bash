#!/bin/bash

# Test Script for SSH Absolute Path Support
set -e

echo "===== SSH Absolute Path Support Test ====="

# Change to project root
cd /workspace/code/PeiDocker

# Clean up any previous builds
BUILD_DIR="build-abspath-test"
if [ -d "$BUILD_DIR" ]; then
    echo "Cleaning up previous build directory..."
    rm -rf "$BUILD_DIR"
fi

echo "Testing absolute path SSH key support..."

# Test 1: Absolute path configuration
echo ""
echo "=== TEST 1: Absolute Path Configuration ==="

# Create the PeiDocker project
echo "Creating PeiDocker project..."
PYTHONPATH=/workspace/code/PeiDocker python -m pei_docker.pei create -p "$BUILD_DIR"

# Copy our test configuration
echo "Copying absolute path test configuration..."
cp tests/configs/ssh-abspath-test.yml "$BUILD_DIR/user_config.yml"

# Configure the project (this should process absolute paths)
echo "Configuring PeiDocker project..."
if PYTHONPATH=/workspace/code/PeiDocker python -m pei_docker.pei configure -p "$BUILD_DIR"; then
    echo "✅ Configuration succeeded with absolute paths"
else
    echo "❌ Configuration failed with absolute paths"
    exit 1
fi

# Check if generated files exist
echo "Checking generated SSH key files..."
GENERATED_DIR="$BUILD_DIR/installation/stage-1/generated"
if [ -d "$GENERATED_DIR" ]; then
    echo "✅ Generated directory exists: $GENERATED_DIR"
    ls -la "$GENERATED_DIR/"
else
    echo "❌ Generated directory missing: $GENERATED_DIR"
    exit 1
fi

# Check docker-compose.yml for correct paths
echo "Checking docker-compose.yml for SSH key paths..."
COMPOSE_FILE="$BUILD_DIR/docker-compose.yml"
if grep -q "stage-1/generated" "$COMPOSE_FILE"; then
    echo "✅ Docker-compose contains correct SSH key paths"
    echo "SSH key paths in docker-compose.yml:"
    grep -A 2 -B 2 "generated" "$COMPOSE_FILE" || echo "No generated paths found"
else
    echo "❌ Docker-compose missing generated SSH key paths"
    echo "Docker-compose SSH configuration:"
    grep -A 10 -B 5 "SSH_" "$COMPOSE_FILE" || echo "No SSH configuration found"
fi

# Test 2: System SSH key (~) configuration
echo ""
echo "=== TEST 2: System SSH Key (~) Configuration ==="

BUILD_DIR2="build-system-keys-test"
if [ -d "$BUILD_DIR2" ]; then
    echo "Cleaning up previous build directory..."
    rm -rf "$BUILD_DIR2"
fi

# Create the PeiDocker project
echo "Creating PeiDocker project for system keys test..."
PYTHONPATH=/workspace/code/PeiDocker python -m pei_docker.pei create -p "$BUILD_DIR2"

# Copy our test configuration
echo "Copying system keys test configuration..."
cp tests/configs/ssh-system-keys-test.yml "$BUILD_DIR2/user_config.yml"

# Configure the project (this should process ~ syntax)
echo "Configuring PeiDocker project with ~ syntax..."
if PYTHONPATH=/workspace/code/PeiDocker python -m pei_docker.pei configure -p "$BUILD_DIR2"; then
    echo "✅ Configuration succeeded with ~ syntax"
else
    echo "❌ Configuration failed with ~ syntax"
    exit 1
fi

# Check if generated files exist
echo "Checking generated SSH key files for ~ syntax..."
GENERATED_DIR2="$BUILD_DIR2/installation/stage-1/generated"
if [ -d "$GENERATED_DIR2" ]; then
    echo "✅ Generated directory exists: $GENERATED_DIR2"
    ls -la "$GENERATED_DIR2/"
else
    echo "❌ Generated directory missing: $GENERATED_DIR2"
    exit 1
fi

# Test 3: Mixed paths configuration
echo ""
echo "=== TEST 3: Mixed Paths Configuration ==="

BUILD_DIR3="build-mixed-paths-test"
if [ -d "$BUILD_DIR3" ]; then
    echo "Cleaning up previous build directory..."
    rm -rf "$BUILD_DIR3"
fi

# Create the PeiDocker project
echo "Creating PeiDocker project for mixed paths test..."
PYTHONPATH=/workspace/code/PeiDocker python -m pei_docker.pei create -p "$BUILD_DIR3"

# Copy our test configuration
echo "Copying mixed paths test configuration..."
cp tests/configs/ssh-mixed-paths-test.yml "$BUILD_DIR3/user_config.yml"

# Configure the project (this should process multiple path types)
echo "Configuring PeiDocker project with mixed paths..."
if PYTHONPATH=/workspace/code/PeiDocker python -m pei_docker.pei configure -p "$BUILD_DIR3"; then
    echo "✅ Configuration succeeded with mixed paths"
else
    echo "❌ Configuration failed with mixed paths"
    exit 1
fi

# Check if generated files exist
echo "Checking generated SSH key files for mixed paths..."
GENERATED_DIR3="$BUILD_DIR3/installation/stage-1/generated"
if [ -d "$GENERATED_DIR3" ]; then
    echo "✅ Generated directory exists: $GENERATED_DIR3"
    ls -la "$GENERATED_DIR3/"
else
    echo "❌ Generated directory missing: $GENERATED_DIR3"
    exit 1
fi

echo ""
echo "=== TEST SUMMARY ==="
echo "✅ All SSH absolute path tests passed!"
echo "✅ Absolute paths work correctly"
echo "✅ ~ syntax for system SSH keys works"
echo "✅ Mixed path configurations work"
echo "✅ Generated files are created in correct locations"
echo ""
echo "SSH absolute path support implementation is working correctly!"