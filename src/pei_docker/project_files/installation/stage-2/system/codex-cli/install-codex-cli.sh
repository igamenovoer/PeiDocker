#!/usr/bin/env bash
#
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
#   - If installing for another user: uses 'su' (requires root/sudo privileges)
#   - Handles root user home directory (/root) correctly
#
# Examples:
#   ./install-codex-cli.sh              # Install for current user
#   ./install-codex-cli.sh username     # Install for 'username'
#   ./install-codex-cli.sh root         # Install for root user
#
# Usage:
#   ./install-codex-cli.sh [user_name]
#
# Arguments:
#   user_name  - Optional. User to install Codex CLI for (defaults to current user).
#
# Environment Variables (optional):
#   CODEX_API_KEY   - API key for custom Codex endpoint
#   CODEX_BASE_URL  - Base URL for custom Codex endpoint
#
set -euo pipefail

# Default to current user if no argument provided
USER_NAME="${1:-$(whoami)}"

# Determine user home directory
if [[ "${USER_NAME}" == "root" ]]; then
  USER_HOME="/root"
else
  USER_HOME="$(getent passwd "${USER_NAME}" | cut -d: -f6 || true)"
  if [[ -z "${USER_HOME}" ]]; then
    USER_HOME="/home/${USER_NAME}"
  fi
fi

echo "[codex] Installing CLI tools for ${USER_NAME}"

# Execute installation: directly if current user, otherwise via su
if [[ "$(whoami)" == "${USER_NAME}" ]]; then
  bash -c 'set -eu; export PATH="$HOME/.local/node/bin:$HOME/.local/bin:$PATH"; npm install -g @openai/codex@latest'
else
  su -l "${USER_NAME}" -c 'set -eu; export PATH="$HOME/.local/node/bin:$HOME/.local/bin:$PATH"; npm install -g @openai/codex@latest'
fi

echo "[codex] Codex CLI ready for API key-based authentication"

if [[ -n "${CODEX_API_KEY:-}" && -n "${CODEX_BASE_URL:-}" ]]; then
  echo "[codex] Configuring custom API alias for ${USER_NAME}"
  {
    printf '\nexport CODEX_API_KEY=%q\n' "${CODEX_API_KEY}"
    printf 'export CODEX_BASE_URL=%q\n' "${CODEX_BASE_URL}"
    printf 'alias codex-custom-api='\''OPENAI_API_KEY="${CODEX_API_KEY}" OPENAI_BASE_URL="${CODEX_BASE_URL}" codex --dangerously-bypass-approvals-and-sandbox'\''\n'
  } >> "${USER_HOME}/.bashrc"
  chown "${USER_NAME}:${USER_NAME}" "${USER_HOME}/.bashrc"
else
  echo "[codex] CODEX_API_KEY/CODEX_BASE_URL not set; skipping alias setup"
fi
