#!/bin/bash

# Test script to verify custom script parameters are correctly passed
# This script will be used to test parameter parsing and passing functionality

# Default values
MESSAGE="No message provided"
VERBOSE=false

echo "=== Custom Script Parameters Test ==="
echo "Script: $0"
echo "Arguments received: $*"
echo "Number of arguments: $#"

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --message=*)
            MESSAGE="${arg#*=}"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

echo "Parsed parameters:"
echo "  MESSAGE: $MESSAGE"
echo "  VERBOSE: $VERBOSE"

if [ "$VERBOSE" = true ]; then
    echo "[VERBOSE] Detailed parameter parsing test completed"
    echo "[VERBOSE] Script execution environment:"
    echo "[VERBOSE]   PWD: $(pwd)"
    echo "[VERBOSE]   USER: $(whoami)"
    echo "[VERBOSE]   DATE: $(date)"
fi

echo "=== Parameter Test Complete ==="
echo "$MESSAGE"