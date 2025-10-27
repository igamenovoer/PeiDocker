#!/bin/bash

# Example user-login script demonstrating parameter support
# Supports parameters: --show-motd --update-prompt

# get the path of this file
SCRIPTFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# Default values
SHOW_MOTD=false
UPDATE_PROMPT=false

echo "=== Stage 1 Custom User-Login Script ==="
echo "Executing: $SCRIPTFILE"
echo "Arguments received: $*"

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --show-motd)
            SHOW_MOTD=true
            shift
            ;;
        --update-prompt)
            UPDATE_PROMPT=true
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

echo "Configuration:"
echo "  Show MOTD: $SHOW_MOTD"
echo "  Update prompt: $UPDATE_PROMPT"

# Demonstrate different behavior based on parameters
if [ "$SHOW_MOTD" = true ]; then
    echo "[MOTD] === Welcome to PeiDocker Container ==="
    echo "[MOTD] System uptime: $(uptime -p || echo 'N/A')"
    echo "[MOTD] Current user: $(whoami)"
    echo "[MOTD] Working directory: $(pwd)"
    echo "[MOTD] === End Welcome Message ==="
fi

if [ "$UPDATE_PROMPT" = true ]; then
    echo "[PROMPT] Updating shell prompt..."
    echo "[PROMPT] Setting custom PS1 variable"
    export PS1="[PeiDocker:\u@\h \W]$ "
    echo "[PROMPT] Prompt updated for current session"
fi

echo "User-login operations completed successfully"
echo "=== End Stage 1 User-Login ==="