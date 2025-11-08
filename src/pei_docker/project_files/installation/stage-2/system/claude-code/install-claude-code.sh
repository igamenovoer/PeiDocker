#!/usr/bin/env bash
#
# Install Claude Code CLI for a specified user or the current user.
#
# Usage:
#   ./install-claude-code.sh [--user <username>]
#
# Options:
#   --user <username>  - Optional. Install for a specific user. Defaults to the
#                        current user. Only root may install for another user.
#
# Behavior:
#   - Installs @anthropic-ai/claude-code via npm in the target user's environment
#   - Sets hasCompletedOnboarding=true in ~/.claude.json to skip first-run prompts
#   - If CLAUDE_CODE_API_KEY and CLAUDE_CODE_BASE_URL are set, configures a custom
#     alias 'claude-custom-api' in the user's ~/.bashrc
#   - If installing for current user: runs directly without privilege escalation
#   - If installing for another user: uses 'runuser' or 'su' (requires root)
#   - Handles root user home directory (/root) correctly
#
# Examples:
#   ./install-claude-code.sh                   # Install for current user
#   ./install-claude-code.sh --user username   # Install for 'username' (root required)
#   ./install-claude-code.sh --user root       # Install for root user (root required unless already root)
#
set -euo pipefail

##########
# Parse command-line arguments
##########
TARGET_USER=""
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

# Permission checks when targeting another user
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

echo "[claude-code] Installing CLI tools for ${TARGET_USER} (invoked by ${CURRENT_USER}, home: ${TARGET_HOME})"

# Execute installation: directly if current user, otherwise via runuser/su
if [[ "${CURRENT_USER}" == "${TARGET_USER}" ]]; then
  bash -c 'set -eu; export PATH="$HOME/.local/node/bin:$HOME/.local/bin:$PATH"; npm install -g @anthropic-ai/claude-code@latest'
else
  INSTALL_AS_USER_CMD='set -eu; export PATH="$HOME/.local/node/bin:$HOME/.local/bin:$PATH"; npm install -g @anthropic-ai/claude-code@latest'
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "${TARGET_USER}" -- sh -lc "${INSTALL_AS_USER_CMD}"
  else
    su -l "${TARGET_USER}" -c "${INSTALL_AS_USER_CMD}"
  fi
fi

echo "[claude-code] Configuring onboarding settings"

# Configure onboarding using explicit path
CLAUDE_CONFIG="${TARGET_HOME}/.claude.json"
python3 - <<PY
import json
import os

cfg_path = "${CLAUDE_CONFIG}"
try:
    with open(cfg_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
except (FileNotFoundError, json.JSONDecodeError):
    data = {}

data["hasCompletedOnboarding"] = True

with open(cfg_path, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2)
    fh.write("\n")

print("[claude-code] set hasCompletedOnboarding=true in {}".format(cfg_path))
PY

# Ensure correct ownership
primary_group=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")
chown "${TARGET_USER}:${primary_group}" "${CLAUDE_CONFIG}" 2>/dev/null || true

echo "[claude-code] Marking onboarding complete"

if [[ -n "${CLAUDE_CODE_API_KEY:-}" && -n "${CLAUDE_CODE_BASE_URL:-}" ]]; then
  echo "[claude-code] Configuring custom API alias for ${TARGET_USER}"
  BASHRC="${TARGET_HOME}/.bashrc"
  if [[ ! -f "${BASHRC}" ]]; then
    echo "[claude-code] Creating ${BASHRC}"
    touch "${BASHRC}"
    primary_group=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")
    chown "${TARGET_USER}:${primary_group}" "${BASHRC}" 2>/dev/null || true
  fi
  {
    printf '\nexport CLAUDE_CODE_API_KEY=%q\n' "${CLAUDE_CODE_API_KEY}"
    printf 'export CLAUDE_CODE_BASE_URL=%q\n' "${CLAUDE_CODE_BASE_URL}"
    printf 'alias claude-custom-api='\''ANTHROPIC_API_KEY="${CLAUDE_CODE_API_KEY}" ANTHROPIC_BASE_URL="${CLAUDE_CODE_BASE_URL}" claude --dangerously-skip-permissions'\''\n'
  } >> "${BASHRC}"
primary_group=$(id -gn "${TARGET_USER}" 2>/dev/null || echo "${TARGET_USER}")
chown "${TARGET_USER}:${primary_group}" "${BASHRC}" 2>/dev/null || true
else
  echo "[claude-code] CLAUDE_CODE_API_KEY/CLAUDE_CODE_BASE_URL not set; skipping alias setup"
fi
