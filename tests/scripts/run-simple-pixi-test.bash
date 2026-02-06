#!/bin/bash

# Generalized test script for any PeiDocker configuration
set -e

# Function to show usage
show_usage() {
    echo "Usage: $0 [config_file]"
    echo ""
    echo "Arguments:"
    echo "  config_file    Path to the YAML configuration file (default: tests/configs/simple-pixi-test.yml)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use default pixi config"
    echo "  $0 tests/configs/ssh-test.yml        # Use specific config"
    echo "  $0 my-custom-config.yml              # Use custom config"
}

# Parse arguments
CONFIG_FILE="${1:-tests/configs/simple-pixi-test.yml}"

# Show help if requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

# Validate config file
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: Configuration file not found: $CONFIG_FILE"
    echo ""
    show_usage
    exit 1
fi

# Extract base name for build directory
CONFIG_BASENAME=$(basename "$CONFIG_FILE" .yml)
BUILD_DIR="build-${CONFIG_BASENAME}"

echo "===== Running PeiDocker Build Test ====="
echo "Config file: $CONFIG_FILE"
echo "Build directory: $BUILD_DIR"
echo ""

# Change to project root
cd /workspace/code/PeiDocker

# Clean up any previous builds
if [ -d "$BUILD_DIR" ]; then
    echo "Cleaning up previous build directory..."
    rm -rf "$BUILD_DIR"
fi

# Create the PeiDocker project (generates template)
echo "Creating PeiDocker project..."
python -m pei_docker.pei create -p "$BUILD_DIR"

# Copy our test configuration to the project
echo "Copying test configuration..."
cp "$CONFIG_FILE" "$BUILD_DIR/user_config.yml"

# Configure the project (generate docker-compose.yml from user_config.yml)
echo "Configuring PeiDocker project..."
python -m pei_docker.pei configure -p "$BUILD_DIR"

# Change to build directory
cd "$BUILD_DIR"

# Build Docker images with plain progress
# echo "Building stage-1 Docker image..."
# docker compose build --progress=plain --no-cache stage-1

echo "Building stage-2 Docker image..."
docker compose build --progress=plain --no-cache stage-2

# # Run the container briefly to test
# echo "Starting container to verify pixi installation..."
# docker compose up -d stage-2

# # Wait for container to start
# echo "Waiting for container to start..."
# sleep 5

# # Check if pixi is installed
# echo "Checking pixi installation..."
# docker compose exec stage-2 bash -c "which pixi && pixi --version"

# # Check if ML packages are available
# echo "Checking pixi global packages..."
# docker compose exec stage-2 bash -c "pixi global list"

# # Stop the container
# echo "Stopping container..."
# docker compose down

echo "===== PeiDocker Build Test Completed Successfully ====="