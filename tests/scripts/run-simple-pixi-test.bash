#!/bin/bash

# Test script for pixi support
set -e

echo "===== Running Simple Pixi Test ====="

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
python -m pei_docker.pei create -p "$BUILD_DIR"

# Copy our test configuration to the project
echo "Copying test configuration..."
cp tests/configs/simple-pixi-test.yml "$BUILD_DIR/user_config.yml"

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

echo "===== Simple Pixi Test Completed Successfully ====="