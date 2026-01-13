#!/usr/bin/env bash

# Install OpenAI Codex CLI for a specified user or the current user.
#
# This script installs the @openai/codex package globally via npm and optionally
# configures a custom API alias if CODEX_API_KEY and CODEX_BASE_URL are set.
#
# Behavior:
#   - Installs @openai/codex via npm in the target user's environment
#   - If CODEX_API_KEY and CODEX_BASE_URL are set, configures a custom
#     alias 'codex-custom-api' in the user's ~/.bashrc
#   - If installing for current user: runs directly without privilege escalation
#   - If installing for another user: uses runuser/su (requires root)
#   - Handles root user home directory (/root) correctly
#
# Usage:
#   ./install-codex-cli.sh [--user <username>]
#
# Options:
#   --user <username>   Install for a specific user (defaults to current user).
#                       Only root may install for another user.
#
# Environment Variables (optional):
#   CODEX_API_KEY   - API key for custom Codex endpoint
#   CODEX_BASE_URL  - Base URL for custom Codex endpoint

set -euo pipefail

TARGET_USER=""

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
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--user <username>]" >&2
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

# Determine target user's home directory
if [[ "${TARGET_USER}" == "root" ]]; then
  TARGET_HOME="/root"
else
  if command -v getent >/dev/null 2>&1; then
    TARGET_HOME="$(getent passwd "${TARGET_USER}" | cut -d: -f6)"
  else
    TARGET_HOME="$(eval echo "~${TARGET_USER}")"
  fi
fi

echo "[codex] Installing CLI tools for ${TARGET_USER} (invoked by ${CURRENT_USER})"

INSTALL_SNIPPET='set -eu; export PATH="$HOME/.bun/bin:$PATH"; if ! command -v bun >/dev/null; then echo "Error: bun not found. Please run install-bun.sh first."; exit 1; fi; bun add -g @openai/codex@latest'

# Execute installation: directly if current user, otherwise via runuser/su
if [[ "${CURRENT_USER}" == "${TARGET_USER}" ]]; then
  bash -lc "${INSTALL_SNIPPET}"
else
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "${TARGET_USER}" -- sh -lc "${INSTALL_SNIPPET}"
  else
    su -l "${TARGET_USER}" -c "${INSTALL_SNIPPET}"
  fi
fi

echo "[codex] Codex CLI ready for API key-based authentication"

if [[ -n "${CODEX_API_KEY:-}" && -n "${CODEX_BASE_URL:-}" ]]; then
  echo "[codex] Configuring custom API alias for ${TARGET_USER}"
  {
    printf '\nexport CODEX_API_KEY=%q\n' "${CODEX_API_KEY}"
    printf 'export CODEX_BASE_URL=%q\n' "${CODEX_BASE_URL}"
    printf 'alias codex-custom-api='\''OPENAI_API_KEY="${CODEX_API_KEY}" OPENAI_BASE_URL="${CODEX_BASE_URL}" codex --dangerously-bypass-approvals-and-sandbox'\''\n'
  } >> "${TARGET_HOME}/.bashrc"
  primary_group=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")
  chown "${TARGET_USER}:${primary_group}" "${TARGET_HOME}/.bashrc" || true
else
  echo "[codex] CODEX_API_KEY/CODEX_BASE_URL not set; skipping alias setup"
fi
