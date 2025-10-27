#!/usr/bin/env bash

# =================================================================
# Install NVM and Node.js for a target user
# =================================================================
# Usage: ./install-nvm-nodejs.sh [OPTIONS]
#
# Options:
#   --user <username>         Install for a specific user (defaults to current user).
#                             Only root may install for another user.
#   --install-dir <dir>       NVM installation directory (replaces --nvm-dir)
#                             Default: <target-user-home>/.nvm
#   --no-pnpm                 Skip installing pnpm
#   --with-cn-mirror          Configure npm registry to Chinese mirror
#   --nvm-version <ver>       NVM version to install (e.g., 0.39.7 or v0.39.7). Default: latest
#   --nodejs-version <ver>    Node.js version to install via nvm (e.g., 20, 20.11.1, v18.20.3, lts)
#                             Default: latest LTS
#
# Description:
#   Installs NVM for the target user in the specified directory, then installs
#   Node.js using NVM. Optionally installs pnpm and configures the npm registry
#   to the CN mirror for faster downloads in China.
#
# Prerequisites:
#   - Internet connection required
#   - Root required only when targeting another user via --user
#
# Examples:
#   ./install-nvm-nodejs.sh
#   ./install-nvm-nodejs.sh --user alice --install-dir /home/alice/.nvm
#   ./install-nvm-nodejs.sh --with-cn-mirror --no-pnpm
#   ./install-nvm-nodejs.sh --nvm-version 0.39.7 --nodejs-version 20
# =================================================================

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

USE_CN_MIRROR=false
INSTALL_PNPM=true
TARGET_USER=""
INSTALL_DIR=""
NVM_VERSION=""
NODE_VERSION=""

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
    --no-pnpm)
      INSTALL_PNPM=false
      shift
      ;;
    --with-cn-mirror)
      USE_CN_MIRROR=true
      shift
      ;;
    --nvm-version)
      if [[ $# -lt 2 ]]; then
        echo "Error: --nvm-version requires a version argument" >&2
        exit 1
      fi
      NVM_VERSION="$2"
      shift 2
      ;;
    --nodejs-version)
      if [[ $# -lt 2 ]]; then
        echo "Error: --nodejs-version requires a version argument" >&2
        exit 1
      fi
      NODE_VERSION="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--user <username>] [--install-dir <directory>] [--no-pnpm] [--with-cn-mirror] [--nvm-version <ver>] [--nodejs-version <ver>]" >&2
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
if [[ -z "${INSTALL_DIR}" ]]; then
  INSTALL_DIR="${TARGET_HOME}/.nvm"
fi

echo "[nvm+node] Target user: ${TARGET_USER} (invoked by ${CURRENT_USER})"
echo "[nvm+node] NVM_DIR: ${INSTALL_DIR}"

# Ensure target bashrc exists (nvm and pnpm installers will append to it)
BASHRC_PATH="${TARGET_HOME}/.bashrc"
if [[ ! -f "${BASHRC_PATH}" ]]; then
  echo "[nvm+node] Creating ${BASHRC_PATH}"
  touch "${BASHRC_PATH}"
  if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
    chown "${TARGET_USER}:${TARGET_USER}" "${BASHRC_PATH}" || true
  fi
fi

# Pre-create NVM_DIR if cross-user or custom path provided
if [[ ! -d "${INSTALL_DIR}" ]]; then
  mkdir -p "${INSTALL_DIR}"
  if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
    chown -R "${TARGET_USER}:${TARGET_USER}" "${INSTALL_DIR}" || true
  fi
fi

# Prepare the installer command for NVM
if [[ -n "${NVM_VERSION}" ]]; then
  # Normalize to v-prefixed tag for URL
  if [[ "${NVM_VERSION}" != v* ]]; then
    NVM_TAG="v${NVM_VERSION}"
  else
    NVM_TAG="${NVM_VERSION}"
  fi
  NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_TAG}/install.sh"
else
  NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh"
fi

INSTALLER_SNIPPET='if command -v curl >/dev/null 2>&1; then curl -fsSL '"${NVM_INSTALL_URL}"' | bash; else wget -qO- '"${NVM_INSTALL_URL}"' | bash; fi'

# Run NVM installation as the target user
if [[ "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
  bash -lc "set -eu; export NVM_DIR='${INSTALL_DIR}'; export PROFILE='${BASHRC_PATH}'; ${INSTALLER_SNIPPET}"
else
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "${TARGET_USER}" -- sh -lc "set -eu; export NVM_DIR='${INSTALL_DIR}'; export PROFILE='${BASHRC_PATH}'; ${INSTALLER_SNIPPET}"
  else
    su -l "${TARGET_USER}" -c "set -eu; export NVM_DIR='${INSTALL_DIR}'; export PROFILE='${BASHRC_PATH}'; ${INSTALLER_SNIPPET}"
  fi
fi

# Verify NVM installation
if [[ ! -s "${INSTALL_DIR}/nvm.sh" ]]; then
  echo "Error: NVM installation failed or nvm.sh not found at ${INSTALL_DIR}" >&2
  exit 1
fi

echo "[nvm+node] NVM installed. Installing Node.js ..."

# Install Node.js via NVM (default to LTS) and optionally set npm registry
if [[ -z "${NODE_VERSION}" || "${NODE_VERSION}" == "lts" ]]; then
  NODE_INSTALL_CMD="nvm install --lts"
else
  NODE_INSTALL_CMD="nvm install '${NODE_VERSION}'"
fi

NODE_SETUP_SNIPPET='set -eu; export NVM_DIR='"'${INSTALL_DIR}'"'; . "$NVM_DIR/nvm.sh"; '"${NODE_INSTALL_CMD}"';'
if [[ "${USE_CN_MIRROR}" == true ]]; then
  NODE_SETUP_SNIPPET+=" npm config set registry https://registry.npmmirror.com/;"
fi

if [[ "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
  bash -lc "${NODE_SETUP_SNIPPET}"
else
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "${TARGET_USER}" -- sh -lc "${NODE_SETUP_SNIPPET}"
  else
    su -l "${TARGET_USER}" -c "${NODE_SETUP_SNIPPET}"
  fi
fi

# Optionally install pnpm for the target user
if [[ "${INSTALL_PNPM}" == true ]]; then
  echo "[nvm+node] Installing pnpm for ${TARGET_USER} ..."
  if [[ "${TARGET_USER}" == "${CURRENT_USER}" ]]; then
    if command -v curl >/dev/null 2>&1; then
      curl -fsSL https://get.pnpm.io/install.sh | sh -
    else
      wget -qO- https://get.pnpm.io/install.sh | sh -
    fi
  else
    if command -v runuser >/dev/null 2>&1; then
      runuser -u "${TARGET_USER}" -- sh -lc 'if command -v curl >/dev/null 2>&1; then curl -fsSL https://get.pnpm.io/install.sh | sh -; else wget -qO- https://get.pnpm.io/install.sh | sh -; fi'
    else
      su -l "${TARGET_USER}" -c 'if command -v curl >/dev/null 2>&1; then curl -fsSL https://get.pnpm.io/install.sh | sh -; else wget -qO- https://get.pnpm.io/install.sh | sh -; fi'
    fi
  fi
else
  echo "[nvm+node] Skipping pnpm installation (--no-pnpm)"
fi

# Also persist npm registry to .npmrc if CN mirror requested (best-effort)
if [[ "${USE_CN_MIRROR}" == true ]]; then
  NPMRC_PATH="${TARGET_HOME}/.npmrc"
  mkdir -p "$(dirname "${NPMRC_PATH}")"
  if [[ -f "${NPMRC_PATH}" ]] && grep -q '^registry=' "${NPMRC_PATH}"; then
    sed -i 's#^registry=.*#registry=https://registry.npmmirror.com/#' "${NPMRC_PATH}"
  else
    echo 'registry=https://registry.npmmirror.com/' >> "${NPMRC_PATH}"
  fi
  if [[ "${TARGET_USER}" != "${CURRENT_USER}" ]]; then
    chown "${TARGET_USER}:${TARGET_USER}" "${NPMRC_PATH}" || true
  fi
fi

echo "[nvm+node] Done."
