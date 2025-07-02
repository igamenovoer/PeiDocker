#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing PeiDocker SSH Keys Inline Configuration${NC}"
echo "================================================"

# Test directory
TEST_DIR="./test-ssh-inline"
CONFIG_FILE="pei_docker/examples/ssh-keys-inline.yml"

# Clean up previous test
if [ -d "$TEST_DIR" ]; then
    echo -e "${YELLOW}Cleaning up previous test directory...${NC}"
    rm -rf "$TEST_DIR"
fi

# Step 1: Create project
echo -e "\n${GREEN}Step 1: Creating new project...${NC}"
python -m pei_docker.pei create -p "$TEST_DIR"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create project${NC}"
    exit 1
fi

# Step 2: Copy the SSH inline config
echo -e "\n${GREEN}Step 2: Copying SSH inline configuration...${NC}"
cp "$CONFIG_FILE" "$TEST_DIR/user_config.yml"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to copy configuration file${NC}"
    exit 1
fi

# Step 3: Configure project (generate docker-compose.yml)
echo -e "\n${GREEN}Step 3: Configuring project...${NC}"
python -m pei_docker.pei configure -p "$TEST_DIR"
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to configure project${NC}"
    exit 1
fi

# Step 4: Build stage-1
echo -e "\n${GREEN}Step 4: Building stage-1 image...${NC}"
cd "$TEST_DIR"
docker compose build stage-1
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to build stage-1${NC}"
    exit 1
fi

# Step 5: Build stage-2
echo -e "\n${GREEN}Step 5: Building stage-2 image...${NC}"
docker compose build stage-2
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to build stage-2${NC}"
    exit 1
fi

# Step 6: Verify images exist
echo -e "\n${GREEN}Step 6: Verifying Docker images...${NC}"
if docker images | grep -q "pei-ssh-example"; then
    echo -e "${GREEN}✓ Images built successfully:${NC}"
    docker images | grep "pei-ssh-example"
else
    echo -e "${RED}✗ Images not found${NC}"
    exit 1
fi

# Step 7: Test container startup
echo -e "\n${GREEN}Step 7: Testing container startup...${NC}"
docker compose up -d stage-2
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to start container${NC}"
    exit 1
fi

# Wait for container to be ready
echo "Waiting for container to be ready..."
sleep 5

# Step 8: Verify SSH service
echo -e "\n${GREEN}Step 8: Verifying SSH service...${NC}"
CONTAINER_NAME=$(docker compose ps -q stage-2)
if [ -z "$CONTAINER_NAME" ]; then
    echo -e "${RED}Container not running${NC}"
    exit 1
fi

# Check if SSH is running inside container
docker exec "$CONTAINER_NAME" ps aux | grep -q sshd
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ SSH service is running${NC}"
else
    echo -e "${RED}✗ SSH service not found${NC}"
fi

# Step 9: Check users were created
echo -e "\n${GREEN}Step 9: Checking created users...${NC}"
for user in developer admin tester legacy; do
    docker exec "$CONTAINER_NAME" id "$user" &>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ User '$user' exists${NC}"
        # Check authorized_keys
        AUTH_KEYS="/home/$user/.ssh/authorized_keys"
        if docker exec "$CONTAINER_NAME" test -f "$AUTH_KEYS"; then
            KEY_COUNT=$(docker exec "$CONTAINER_NAME" wc -l < "$AUTH_KEYS" | tr -d ' ')
            echo "  - Has $KEY_COUNT authorized key(s)"
        fi
    else
        echo -e "${RED}✗ User '$user' not found${NC}"
    fi
done

# Step 10: Test SSH connection (optional - requires valid keys)
echo -e "\n${GREEN}Step 10: SSH connectivity test...${NC}"
echo -e "${YELLOW}Note: Actual SSH login would require valid matching private keys${NC}"
echo "SSH should be available on localhost:2222"

# Cleanup
echo -e "\n${GREEN}Cleaning up...${NC}"
docker compose down
cd ..

echo -e "\n${GREEN}===================================${NC}"
echo -e "${GREEN}✓ All tests passed successfully!${NC}"
echo -e "${GREEN}===================================${NC}"
echo -e "\nTest artifacts remain in: $TEST_DIR"
echo "To fully clean up, run: rm -rf $TEST_DIR"