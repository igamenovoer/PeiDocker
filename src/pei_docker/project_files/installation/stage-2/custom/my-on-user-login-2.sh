#!/bin/bash

# Example user-login script demonstrating parameter support
# Supports parameters: --welcome-message --check-updates

# get the path of this file
SCRIPTFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# Default values
WELCOME_MESSAGE=false
CHECK_UPDATES=false

echo "=== Stage 2 Custom User-Login Script ==="
echo "Executing: $SCRIPTFILE"
echo "Arguments received: $*"

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --welcome-message)
            WELCOME_MESSAGE=true
            shift
            ;;
        --check-updates)
            CHECK_UPDATES=true
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

echo "Configuration:"
echo "  Welcome message: $WELCOME_MESSAGE"
echo "  Check updates: $CHECK_UPDATES"

# Demonstrate different behavior based on parameters
if [ "$WELCOME_MESSAGE" = true ]; then
    echo "[WELCOME] =================================================="
    echo "[WELCOME] Welcome to your PeiDocker Development Environment!"
    echo "[WELCOME] =================================================="
    echo "[WELCOME] Container: Stage 2 Application Environment"
    echo "[WELCOME] User: $(whoami)"
    echo "[WELCOME] Home: $HOME"
    echo "[WELCOME] Current directory: $(pwd)"
    echo "[WELCOME] Login time: $(date)"
    echo "[WELCOME] =================================================="
fi

if [ "$CHECK_UPDATES" = true ]; then
    echo "[UPDATES] Checking for available updates..."
    if command -v apt >/dev/null 2>&1; then
        echo "[UPDATES] Checking APT packages..."
        echo "[UPDATES] Would check for APT updates (demo mode)"
    fi
    if command -v pip >/dev/null 2>&1; then
        echo "[UPDATES] Checking Python packages..."
        echo "[UPDATES] Would check for pip updates (demo mode)"
    fi
    if command -v npm >/dev/null 2>&1; then
        echo "[UPDATES] Checking Node.js packages..."
        echo "[UPDATES] Would check for npm updates (demo mode)"
    fi
    echo "[UPDATES] Update check completed (demo mode - no actual updates checked)"
fi

echo "Stage 2 user-login operations completed successfully"
echo "=== End Stage 2 User-Login ==="