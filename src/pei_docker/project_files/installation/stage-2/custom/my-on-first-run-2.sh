#!/bin/bash

# Example first-run script demonstrating parameter support
# Supports parameters: --setup-workspace --clone-repos

# get the path of this file
SCRIPTFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# Default values
SETUP_WORKSPACE=false
CLONE_REPOS=false

echo "=== Stage 2 Custom First-Run Script ==="
echo "Executing: $SCRIPTFILE"
echo "Arguments received: $*"

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --setup-workspace)
            SETUP_WORKSPACE=true
            shift
            ;;
        --clone-repos)
            CLONE_REPOS=true
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

echo "Configuration:"
echo "  Setup workspace: $SETUP_WORKSPACE"
echo "  Clone repositories: $CLONE_REPOS"

# Demonstrate different behavior based on parameters
if [ "$SETUP_WORKSPACE" = true ]; then
    echo "[WORKSPACE] Setting up development workspace..."
    echo "[WORKSPACE] Creating project directories..."
    mkdir -p /tmp/workspace/{projects,tools,docs}
    echo "[WORKSPACE] Setting up development tools..."
    echo "[WORKSPACE] Configuring environment variables..."
    export WORKSPACE_ROOT="/tmp/workspace"
    echo "[WORKSPACE] Workspace setup completed"
fi

if [ "$CLONE_REPOS" = true ]; then
    echo "[REPOS] Cloning development repositories..."
    echo "[REPOS] Checking for git availability..."
    if command -v git >/dev/null 2>&1; then
        echo "[REPOS] Git is available"
        echo "[REPOS] Would clone repositories (demo mode - no actual cloning)"
        echo "[REPOS]   - Sample project repository"
        echo "[REPOS]   - Configuration repository"
        echo "[REPOS]   - Documentation repository"
    else
        echo "[REPOS] Git not available, skipping repository cloning"
    fi
    echo "[REPOS] Repository setup completed"
fi

echo "Stage 2 first-run operations completed successfully"
echo "=== End Stage 2 First-Run ==="