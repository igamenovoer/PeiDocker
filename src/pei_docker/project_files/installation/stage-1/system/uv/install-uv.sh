#!/usr/bin/env bash
#
# Install uv (Python package and project manager) for the current user
#
# This script installs uv using the official installer and optionally allows
# specifying a custom installation directory.
#
# Usage:
#   ./install-uv.sh [--install-dir <directory>] [--user <username>]
#
# Options:
#   --install-dir <dir>  - Optional. Directory where uv will be installed.
#                         Defaults to ~/.local/bin for non-root users.
#                         For root (no --user), defaults to /usr/local/bin (system-wide).
#   --user <username>    - Optional. Install for a specific user. Defaults to the
#                         current user. Only root may install for another user.
#
set -euo pipefail

##########
# Parse command-line arguments
##########
INSTALL_DIR=""
TARGET_USER=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-dir)
      if [[ $# -lt 2 ]]; then
        echo "Error: --install-dir requires a directory argument" >&2
        exit 1
      fi
      INSTALL_DIR="$2"
      shift 2
      ;;
    --user)
      if [[ $# -lt 2 ]]; then
        echo "Error: --user requires a username argument" >&2
        exit 1
      fi
      TARGET_USER="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--install-dir <directory>] [--user <username>]" >&2
      exit 1
      ;;
  esac
done

# Get current user information
CURRENT_USER="$(whoami)"

# Default target user to current user if not specified
if [[ -z "${TARGET_USER}" ]]; then
  TARGET_USER="${CURRENT_USER}"
fi

# Validate permission to install for a different user
if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
  if [[ "${CURRENT_USER}" != "root" ]]; then
    echo "Error: only root can install uv for another user (requested --user '${TARGET_USER}')" >&2
    exit 1
  fi
  if ! id -u "${TARGET_USER}" >/dev/null 2>&1; then
    echo "Error: target user '${TARGET_USER}' does not exist" >&2
    exit 1
  fi
fi

# Resolve target user's home directory
if [[ "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
  TARGET_HOME="${HOME}"
else
  if command -v getent >/dev/null 2>&1; then
    TARGET_HOME="$(getent passwd "${TARGET_USER}" | cut -d: -f6)"
  else
    # Fallback: expand ~user
    TARGET_HOME="$(eval echo "~${TARGET_USER}")"
  fi
fi

echo "[uv] Installing uv for user: ${TARGET_USER} (invoked by ${CURRENT_USER})"

##########
# Determine installation directory default notes (informational)
##########
if [[ -z "${INSTALL_DIR}" ]]; then
  if [[ "${TARGET_USER}" == "root" && "${CURRENT_USER}" == "root" && "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
    echo "[uv] Root without --user: installer will use system-wide default (/usr/local/bin)"
  else
    echo "[uv] Installer will use per-user default: ${TARGET_HOME}/.local/bin"
  fi
else
  echo "[uv] Using custom installation directory: ${INSTALL_DIR}"
fi

##########
# Build and run the installation command
##########
if [[ "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
  # Installing for the invoking user
  if [[ -n "${INSTALL_DIR}" ]]; then
    mkdir -p "${INSTALL_DIR}"
    export UV_INSTALL_DIR="${INSTALL_DIR}"
    INSTALL_CMD="curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR='${INSTALL_DIR}' sh"
  else
    INSTALL_CMD="curl -LsSf https://astral.sh/uv/install.sh | sh"
  fi
  eval "${INSTALL_CMD}"
else
  # Installing for a different user (requires root)
  if [[ -n "${INSTALL_DIR}" ]]; then
    mkdir -p "${INSTALL_DIR}"
    # Ensure the target user owns the install dir
    chown -R "${TARGET_USER}:${TARGET_USER}" "${INSTALL_DIR}" || true
    INSTALL_AS_USER_CMD="curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR='${INSTALL_DIR}' sh"
  else
    INSTALL_AS_USER_CMD="curl -LsSf https://astral.sh/uv/install.sh | sh"
  fi

  if command -v runuser >/dev/null 2>&1; then
    runuser -u "${TARGET_USER}" -- sh -lc "${INSTALL_AS_USER_CMD}"
  else
    su - "${TARGET_USER}" -c "${INSTALL_AS_USER_CMD}"
  fi
fi

##########
# Determine the actual installation path for uv
##########
if [[ -n "${INSTALL_DIR}" ]]; then
  UV_BIN_PATH="${INSTALL_DIR}"
else
  if [[ "${TARGET_USER}" == "root" && "${CURRENT_USER}" == "root" && "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
    UV_BIN_PATH="/usr/local/bin"
  else
    UV_BIN_PATH="${TARGET_HOME}/.local/bin"
  fi
fi

# Add to PATH in shell configuration if needed
# Check if UV_BIN_PATH needs to be added to PATH
if [[ "${UV_BIN_PATH}" != "/usr/local/bin" ]] && [[ "${UV_BIN_PATH}" != "/usr/bin" ]]; then
  # Update the target user's shell configuration
  BASHRC="${TARGET_HOME}/.bashrc"
  
  # Create .bashrc if it doesn't exist (common in Docker containers)
  if [[ ! -f "${BASHRC}" ]]; then
    echo "[uv] Creating ${BASHRC}"
    touch "${BASHRC}"
    # Ensure ownership is correct if targeting another user
    if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
      chown "${TARGET_USER}:${TARGET_USER}" "${BASHRC}" || true
    fi
  fi
  
  if ! grep -q "export PATH=\"${UV_BIN_PATH}:\$PATH\"" "${BASHRC}"; then
    echo "[uv] Adding ${UV_BIN_PATH} to PATH in ${BASHRC}"
    {
      printf '\n# Added by uv installer\n'
      printf 'export PATH="%s:$PATH"\n' "${UV_BIN_PATH}"
    } >> "${BASHRC}"
    if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
      chown "${TARGET_USER}:${TARGET_USER}" "${BASHRC}" || true
    fi
  else
    echo "[uv] PATH already configured in ${BASHRC}"
  fi
else
  echo "[uv] Installation directory is already in standard PATH"
fi

# Verify installation
if [[ -f "${UV_BIN_PATH}/uv" ]]; then
  echo "[uv] Successfully installed uv at ${UV_BIN_PATH}/uv"
  "${UV_BIN_PATH}/uv" --version || true
else
  echo "[uv] Warning: uv binary not found at expected location ${UV_BIN_PATH}/uv"
fi
