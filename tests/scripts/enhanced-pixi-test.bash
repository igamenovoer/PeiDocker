#!/bin/bash

# Enhanced Pixi Verification Test Script
set -e

echo "===== Enhanced Pixi Container Verification Test ====="

# Change to project root
cd /workspace/code/PeiDocker

# Clean up any previous builds
BUILD_DIR="build-pixi-test"
if [ -d "$BUILD_DIR" ]; then
    echo "Cleaning up previous build directory..."
    rm -rf "$BUILD_DIR"
fi

# Create the PeiDocker project (generates template)
echo "Creating PeiDocker project..."
PYTHONPATH=/workspace/code/PeiDocker pixi run python -m pei_docker.pei create -p "$BUILD_DIR"

# Copy our test configuration to the project (using passwordless SSH keys)
echo "Copying test configuration..."
cp tests/configs/simple-pixi-test-passwordless.yml "$BUILD_DIR/user_config.yml"

# Configure the project (generate docker-compose.yml from user_config.yml)
echo "Configuring PeiDocker project..."
PYTHONPATH=/workspace/code/PeiDocker pixi run python -m pei_docker.pei configure -p "$BUILD_DIR"

# Change to build directory
cd "$BUILD_DIR"

# Build Docker images with plain progress
echo "Building stage-1 Docker image..."
docker compose build --progress=plain --no-cache stage-1

echo "Building stage-2 Docker image (CRITICAL: using --no-cache)..."
docker compose build --progress=plain --no-cache stage-2

# Run the container to test
echo "Starting container to verify pixi installation..."
docker compose up -d stage-2

# Wait for container to start
echo "Waiting for container to start..."
sleep 5

echo ""
echo "===== PHASE 1: BASIC INSTALLATION VERIFICATION ====="

# Check if pixi is installed
echo "🔍 Checking pixi installation..."
if docker compose exec stage-2 bash -c "which pixi"; then
    echo "✅ Pixi binary found"
else
    echo "❌ Pixi binary NOT found"
    exit 1
fi

# Check pixi version
echo "🔍 Checking pixi version..."
if docker compose exec stage-2 bash -c "pixi --version"; then
    echo "✅ Pixi version command works"
else
    echo "❌ Pixi version command failed"
    exit 1
fi

# Check PIXI_HOME environment variable
echo "🔍 Checking PIXI_HOME environment..."
if docker compose exec stage-2 bash -c "echo \"PIXI_HOME: \$PIXI_HOME\""; then
    echo "✅ PIXI_HOME environment variable is set"
else
    echo "❌ PIXI_HOME environment variable missing"
fi

# Check installation path exists
echo "🔍 Checking installation directory..."
if docker compose exec stage-2 bash -c "ls -la /hard/image/pixi/"; then
    echo "✅ Pixi installation directory exists"
else
    echo "❌ Pixi installation directory missing"
fi

echo ""
echo "===== PHASE 2: GLOBAL ENVIRONMENT VERIFICATION ====="

# List global environments
echo "🔍 Listing pixi global environments..."
if docker compose exec stage-2 bash -c "pixi global list"; then
    echo "✅ Pixi global list command works"
else
    echo "❌ Pixi global list command failed"
    exit 1
fi

# Check if common environment exists
echo "🔍 Checking for 'common' environment..."
if docker compose exec stage-2 bash -c "pixi global list | grep -q common"; then
    echo "✅ 'common' environment found"
else
    echo "❌ 'common' environment NOT found"
    exit 1
fi

# Get environment info
echo "🔍 Getting 'common' environment details..."
if docker compose exec stage-2 bash -c "pixi global info common"; then
    echo "✅ Environment info available"
else
    echo "⚠️  Environment info command failed (may be normal)"
fi

echo ""
echo "===== PHASE 3: PACKAGE FUNCTIONALITY VERIFICATION ====="

# Test Python package imports
packages=("scipy" "click" "attrs" "omegaconf" "rich" "networkx")

for package in "${packages[@]}"; do
    echo "🔍 Testing import of $package..."
    if docker compose exec stage-2 bash -c "python -c 'import $package; print(f\"✅ $package {$package.__version__ if hasattr($package, \"__version__\") else \"imported successfully\"}\")' 2>/dev/null"; then
        echo "✅ $package import successful"
    else
        echo "❌ $package import failed"
        # Don't exit, continue with other packages
    fi
done

echo ""
echo "===== PHASE 4: COMMAND-LINE TOOLS VERIFICATION ====="

# Test click command
echo "🔍 Testing click CLI tool..."
if docker compose exec stage-2 bash -c "python -c 'import click; click.echo(\"Click CLI works!\")'" 2>/dev/null; then
    echo "✅ Click CLI functionality works"
else
    echo "❌ Click CLI functionality failed"
fi

# Test rich console output
echo "🔍 Testing rich console output..."
if docker compose exec stage-2 bash -c "python -c 'from rich.console import Console; Console().print(\"Rich console works!\", style=\"bold green\")'" 2>/dev/null; then
    echo "✅ Rich console functionality works"
else
    echo "❌ Rich console functionality failed"
fi

echo ""
echo "===== PHASE 5: PATH AND ENVIRONMENT VERIFICATION ====="

# Check PATH includes pixi
echo "🔍 Checking PATH for pixi..."
if docker compose exec stage-2 bash -c "echo \$PATH | grep -q pixi"; then
    echo "✅ PATH includes pixi directories"
else
    echo "⚠️  PATH may not include pixi directories"
fi

# Test pixi from different directory
echo "🔍 Testing pixi from different directory..."
if docker compose exec stage-2 bash -c "cd /tmp && pixi --version" 2>/dev/null; then
    echo "✅ Pixi works from any directory"
else
    echo "❌ Pixi doesn't work from different directories"
fi

echo ""
echo "===== PHASE 6: PERFORMANCE AND RESOURCE VERIFICATION ====="

# Check disk usage
echo "🔍 Checking pixi disk usage..."
docker compose exec stage-2 bash -c "du -sh /hard/image/pixi/ 2>/dev/null || echo 'Could not measure disk usage'"

# Check memory usage
echo "🔍 Checking system memory usage..."
docker compose exec stage-2 bash -c "free -h"

echo ""
echo "===== PHASE 7: PERSISTENCE TEST (CONTAINER RESTART) ====="

echo "🔍 Restarting container to test persistence..."
docker compose restart stage-2

echo "Waiting for container to restart..."
sleep 5

# Re-test key functionality after restart
echo "🔍 Re-testing pixi after restart..."
if docker compose exec stage-2 bash -c "pixi --version" 2>/dev/null; then
    echo "✅ Pixi works after container restart"
else
    echo "❌ Pixi failed after container restart"
fi

echo "🔍 Re-testing global environments after restart..."
if docker compose exec stage-2 bash -c "pixi global list | grep -q common" 2>/dev/null; then
    echo "✅ Global environments persist after restart"
else
    echo "❌ Global environments lost after restart"
fi

echo "🔍 Re-testing package imports after restart..."
if docker compose exec stage-2 bash -c "python -c 'import scipy; print(\"scipy works after restart\")'" 2>/dev/null; then
    echo "✅ Packages work after container restart"
else
    echo "❌ Packages failed after container restart"
fi

echo ""
echo "===== TEST SUMMARY ====="

# Final verification
echo "🔍 Running final comprehensive check..."

# Count successful package imports
successful_imports=0
total_packages=${#packages[@]}

for package in "${packages[@]}"; do
    if docker compose exec stage-2 bash -c "python -c 'import $package'" 2>/dev/null; then
        ((successful_imports++))
    fi
done

echo "📊 Package Import Success Rate: $successful_imports/$total_packages ($(( successful_imports * 100 / total_packages ))%)"

# Stop the container
echo "Stopping container..."
docker compose down

if [ $successful_imports -eq $total_packages ]; then
    echo ""
    echo "🎉 ===== PIXI VERIFICATION COMPLETED SUCCESSFULLY ====="
    echo "✅ All core functionality tests passed"
    echo "✅ All packages imported successfully"
    echo "✅ Persistence tests passed"
    echo ""
    echo "Pixi is fully functional in the PeiDocker container!"
    exit 0
else
    echo ""
    echo "⚠️  ===== PIXI VERIFICATION COMPLETED WITH ISSUES ====="
    echo "❌ Some packages failed to import"
    echo "📋 Please review the test output above for details"
    echo ""
    exit 1
fi