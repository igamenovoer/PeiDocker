#!/bin/bash

# =================================================================
# Install Node.js LTS (requires NVM to be installed first)
# =================================================================
# Usage: ./install-nodejs.sh [OPTIONS]
#
# Options:
#   --nvm-dir <dir>       Custom NVM installation directory
#                         Default: <target-user-home>/.nvm
#   --user <username>     Install for a specific user (defaults to current user).
#                         Only root may install for another user.
#   --version <ver>       Node.js version to install via nvm (e.g., 20, 20.11.1, v18.20.3, lts)
#                         Default: latest LTS
#
# Description:
#   This script installs the latest LTS version of Node.js using NVM.
#   pnpm installation and npm mirror configuration have been moved to
#   install-nvm.sh.
#
# Prerequisites:
#   - NVM must be installed for the target user (run install-nvm.sh first)
#   - Internet connection required
#
# Examples:
#   ./install-nodejs.sh                           # Install Node.js LTS for current user
#   ./install-nodejs.sh --version 20              # Install Node.js v20.x
#   ./install-nodejs.sh --nvm-dir /opt/nvm        # Use custom NVM directory
#   ./install-nodejs.sh --user alice              # Install for 'alice' (root required)
# =================================================================

set -euo pipefail

# install latest lts nodejs, assuming nvm is already installed
export DEBIAN_FRONTEND=noninteractive

# Parse command line arguments
NVM_INSTALL_DIR=""
TARGET_USER=""
NODE_VERSION=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --nvm-dir)
            NVM_INSTALL_DIR="$2"
            shift 2
            ;;
        --user)
            TARGET_USER="$2"
            shift 2
            ;;
        --version)
            NODE_VERSION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--nvm-dir <directory>] [--user <username>] [--version <ver>]"
            echo "  --nvm-dir <dir>       Custom NVM installation directory (default: <target-home>/.nvm)"
            echo "  --user <username>     Target user to install for (root required for other users)"
            echo "  --version <ver>       Node.js version to install (default: LTS). Examples: 20, v18.20.3, lts"
            exit 1
            ;;
    esac
done

CURRENT_USER="$(whoami)"
if [[ -z "${TARGET_USER}" ]]; then
    TARGET_USER="${CURRENT_USER}"
fi

# Enforce root for cross-user installs and validate user exists
if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
    if [[ "${CURRENT_USER}" != "root" ]]; then
        echo "Error: only root can install for another user (requested --user '${TARGET_USER}')" >&2
        exit 1
    fi
    if ! id -u "${TARGET_USER}" >/dev/null 2>&1; then
        echo "Error: target user '${TARGET_USER}' does not exist" >&2
        exit 1
    fi
fi

# Resolve target user's home directory
if [[ "${TARGET_USER}" == "root" ]]; then
    TARGET_HOME="/root"
else
    if command -v getent >/dev/null 2>&1; then
        TARGET_HOME="$(getent passwd "${TARGET_USER}" | cut -d: -f6)"
    else
        TARGET_HOME="$(eval echo "~${TARGET_USER}")"
    fi
fi

# Determine NVM installation directory if not provided explicitly
if [[ -z "${NVM_INSTALL_DIR}" ]]; then
    NVM_INSTALL_DIR="${TARGET_HOME}/.nvm"
fi

# Set NVM_DIR for this script context (path resolution and checks)
export NVM_DIR="${NVM_INSTALL_DIR}"

# Verify NVM is installed for the target user at the expected path
if [ ! -s "$NVM_DIR/nvm.sh" ]; then
    echo "Error: NVM not found at $NVM_DIR for user $TARGET_USER" >&2
    echo "Please run install-nvm.sh for the target user or specify correct --nvm-dir" >&2
    exit 1
fi

echo "Using NVM from: $NVM_DIR (target user: $TARGET_USER)"

# Install Node.js under the target user's environment
if [[ "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
    if [[ -z "${NODE_VERSION}" ]]; then
        bash -c "set -eu; export NVM_DIR='${NVM_DIR}'; . \"$NVM_DIR/nvm.sh\"; nvm install --lts"
    else
        if [[ "${NODE_VERSION}" == "lts" ]]; then
            bash -c "set -eu; export NVM_DIR='${NVM_DIR}'; . \"$NVM_DIR/nvm.sh\"; nvm install --lts"
        else
            bash -c "set -eu; export NVM_DIR='${NVM_DIR}'; . \"$NVM_DIR/nvm.sh\"; nvm install '${NODE_VERSION}'"
        fi
    fi
else
    if [[ -z "${NODE_VERSION}" ]]; then
        INSTALL_AS_USER_CMD="set -eu; export NVM_DIR='${NVM_DIR}'; . \"$NVM_DIR/nvm.sh\"; nvm install --lts"
    else
        if [[ "${NODE_VERSION}" == "lts" ]]; then
            INSTALL_AS_USER_CMD="set -eu; export NVM_DIR='${NVM_DIR}'; . \"$NVM_DIR/nvm.sh\"; nvm install --lts"
        else
            INSTALL_AS_USER_CMD="set -eu; export NVM_DIR='${NVM_DIR}'; . \"$NVM_DIR/nvm.sh\"; nvm install '${NODE_VERSION}'"
        fi
    fi
    if command -v runuser >/dev/null 2>&1; then
        runuser -u "${TARGET_USER}" -- sh -lc "${INSTALL_AS_USER_CMD}"
    else
        su -l "${TARGET_USER}" -c "${INSTALL_AS_USER_CMD}"
    fi
fi

echo "Done installing Node.js."
