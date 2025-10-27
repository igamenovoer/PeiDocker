#!/bin/bash

# Example build script demonstrating parameter support
# Supports parameters: --verbose --config=<path>

# get the path of this file
SCRIPTFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# Default values
VERBOSE=false
CONFIG_FILE=""

echo "=== Stage 1 Custom Build Script ==="
echo "Executing: $SCRIPTFILE"
echo "Arguments received: $*"

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --config=*)
            CONFIG_FILE="${arg#*=}"
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

echo "Configuration:"
echo "  Verbose mode: $VERBOSE"
echo "  Config file: ${CONFIG_FILE:-"(not specified)"}"

# Demonstrate different behavior based on parameters
if [ "$VERBOSE" = true ]; then
    echo "[VERBOSE] Starting detailed build process..."
    echo "[VERBOSE] Checking system resources..."
    echo "[VERBOSE] Available memory: $(free -h | grep '^Mem:' | awk '{print $2}') total"
    echo "[VERBOSE] Disk space: $(df -h / | tail -1 | awk '{print $4}') available"
fi

if [ -n "$CONFIG_FILE" ]; then
    echo "Using configuration file: $CONFIG_FILE"
    if [ -f "$CONFIG_FILE" ]; then
        echo "Configuration file exists and is accessible"
    else
        echo "Configuration file not found, using defaults"
    fi
fi

echo "Custom build operations completed successfully"
echo "=== End Stage 1 Custom Build ==="