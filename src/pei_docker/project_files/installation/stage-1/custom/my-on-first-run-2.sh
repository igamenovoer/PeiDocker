#!/bin/bash

# Example first-run script demonstrating parameter support
# Supports parameters: --initialize --create-dirs

# get the path of this file
SCRIPTFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# Default values
INITIALIZE=false
CREATE_DIRS=false

echo "=== Stage 1 Custom First-Run Script ==="
echo "Executing: $SCRIPTFILE"
echo "Arguments received: $*"

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --initialize)
            INITIALIZE=true
            shift
            ;;
        --create-dirs)
            CREATE_DIRS=true
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

echo "Configuration:"
echo "  Initialize: $INITIALIZE"
echo "  Create directories: $CREATE_DIRS"

# Demonstrate different behavior based on parameters
if [ "$INITIALIZE" = true ]; then
    echo "[INIT] Performing system initialization..."
    echo "[INIT] Setting up default configurations..."
    echo "[INIT] Checking system services..."
fi

if [ "$CREATE_DIRS" = true ]; then
    echo "[DIRS] Creating application directories..."
    echo "[DIRS] Creating /tmp/app-logs directory"
    mkdir -p /tmp/app-logs
    echo "[DIRS] Creating /tmp/app-config directory"
    mkdir -p /tmp/app-config
    echo "[DIRS] Directory creation completed"
fi

echo "First-run setup operations completed successfully"
echo "=== End Stage 1 First-Run ==="