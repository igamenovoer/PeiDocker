#!/bin/bash

# Example build script demonstrating parameter support
# Supports parameters: --enable-desktop --theme=<value>

# get the path of this file
SCRIPTFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# Default values
ENABLE_DESKTOP=false
THEME="light"

echo "=== Stage 2 Custom Build Script ==="
echo "Executing: $SCRIPTFILE"
echo "Arguments received: $*"

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --enable-desktop)
            ENABLE_DESKTOP=true
            shift
            ;;
        --theme=*)
            THEME="${arg#*=}"
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

echo "Configuration:"
echo "  Enable desktop: $ENABLE_DESKTOP"
echo "  Theme: $THEME"

# Demonstrate different behavior based on parameters
if [ "$ENABLE_DESKTOP" = true ]; then
    echo "[DESKTOP] Configuring desktop environment..."
    echo "[DESKTOP] Installing desktop packages..."
    echo "[DESKTOP] Setting up window manager..."
    echo "[DESKTOP] Configuring display settings..."
    echo "[DESKTOP] Desktop environment setup completed"
fi

echo "[THEME] Applying theme: $THEME"
case $THEME in
    "dark")
        echo "[THEME] Setting dark theme colors..."
        echo "[THEME] Configuring dark mode preferences..."
        ;;
    "light")
        echo "[THEME] Setting light theme colors..."
        echo "[THEME] Configuring light mode preferences..."
        ;;
    "default")
        echo "[THEME] Using system default theme..."
        ;;
    *)
        echo "[THEME] Unknown theme '$THEME', using default..."
        ;;
esac

echo "Stage 2 build operations completed successfully"
echo "=== End Stage 2 Custom Build ==="