#!/bin/bash

# =================================================================
# Install Bun Runtime
# =================================================================
# Usage: ./install-bun.sh [OPTIONS]
#
# Options:
#   --user <username>         Install for a specific user (defaults to current user).
#                             Only root may install for another user.
#   --install-dir <dir>       Custom installation directory
#                             Default: <target-user-home>/.bun
#   --npm-repo <url>          Configure default npm registry in bunfig.toml
#                             Example: https://registry.npmmirror.com
#
# Description:
#   Installs the Bun runtime for the target user.
#   Configures PATH in .bashrc to include ~/.bun/bin.
#   Optionally configures the global npm registry for Bun.
# =================================================================

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

TARGET_USER=""
INSTALL_DIR=""
NPM_REPO=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)
      if [[ $# -lt 2 ]]; then
        echo "Error: --user requires a username argument" >&2
        exit 1
      fi
      TARGET_USER="$2"
      shift 2
      ;;
    --install-dir)
      if [[ $# -lt 2 ]]; then
        echo "Error: --install-dir requires a directory argument" >&2
        exit 1
      fi
      INSTALL_DIR="$2"
      shift 2
      ;;
    --npm-repo)
      if [[ $# -lt 2 ]]; then
        echo "Error: --npm-repo requires a url argument" >&2
        exit 1
      fi
      NPM_REPO="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--user <username>] [--install-dir <directory>] [--npm-repo <url>]" >&2
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

# Determine install directory
if [[ -z "${INSTALL_DIR}" ]]; then
  INSTALL_DIR="${TARGET_HOME}/.bun"
fi

echo "[bun] Installing Bun for user: ${TARGET_USER} (invoked by ${CURRENT_USER})"
echo "[bun] Install Dir: ${INSTALL_DIR}"

# Install Bun
INSTALL_CMD="curl -fsSL https://bun.sh/install | bash"

# If custom dir, set BUN_INSTALL env var
if [[ -n "${INSTALL_DIR}" ]]; then
    INSTALL_CMD="export BUN_INSTALL='${INSTALL_DIR}'; ${INSTALL_CMD}"
fi

if [[ "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
  bash -c "${INSTALL_CMD}"
else
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "${TARGET_USER}" -- bash -c "${INSTALL_CMD}"
  else
    su -l "${TARGET_USER}" -c "${INSTALL_CMD}"
  fi
fi

# Add to PATH in .bashrc if not present
BASHRC="${TARGET_HOME}/.bashrc"
BIN_DIR="${INSTALL_DIR}/bin"

if [[ ! -f "${BASHRC}" ]]; then
    touch "${BASHRC}"
    if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
        primary_group=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")
        chown "${TARGET_USER}:${primary_group}" "${BASHRC}" || true
    fi
fi

if ! grep -q "export BUN_INSTALL=\"${INSTALL_DIR}\"" "${BASHRC}"; then
    echo "" >> "${BASHRC}"
    echo "# Bun" >> "${BASHRC}"
    echo "export BUN_INSTALL=\"${INSTALL_DIR}\"" >> "${BASHRC}"
    echo "export PATH=\"
${BIN_DIR}:n${PATH}\"" >> "${BASHRC}"
    echo "[bun] Configured PATH in ${BASHRC}"
fi

# Configure npm repo if requested
if [[ -n "${NPM_REPO}" ]]; then
    BUNFIG="${TARGET_HOME}/.bunfig.toml"
    echo "[bun] Configuring default registry to ${NPM_REPO} in ${BUNFIG}"
    
    # Simple overwrite/append logic. A real parser would be better but overkill here.
    # Check if [install] exists
    if [[ -f "${BUNFIG}" ]] && grep -q "\[install\]" "${BUNFIG}"; then
        # Check if registry exists under it (approximate)
        if grep -q "registry =" "${BUNFIG}"; then
             sed -i "s|registry = .*|registry = \"${NPM_REPO}\"|" "${BUNFIG}"
        else
             # Append registry after [install]
             sed -i "/\[install\]/a registry = \"${NPM_REPO}\"" "${BUNFIG}"
        fi
    else
        # Create new or append
        echo "" >> "${BUNFIG}"
        echo "[install]" >> "${BUNFIG}"
        echo "registry = \"${NPM_REPO}\"" >> "${BUNFIG}"
    fi
    
    if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
        primary_group=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")
        chown "${TARGET_USER}:${primary_group}" "${BUNFIG}" || true
    fi
fi

echo "[bun] Installation complete."
