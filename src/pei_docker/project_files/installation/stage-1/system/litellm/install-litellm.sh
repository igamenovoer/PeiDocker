#!/usr/bin/env bash
set -euo pipefail

TARGET_USER=""

usage() {
  cat <<'USAGE'
Usage: install-litellm.sh [--user <username>]

Installs:
  - LiteLLM proxy (as a uv tool) for the target user

Options:
  --user <username>  Install LiteLLM for a specific user (defaults to current user).
                     Only root may install for another user.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)
      [[ $# -ge 2 ]] || { echo "Error: --user requires a username argument" >&2; exit 1; }
      TARGET_USER="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

CURRENT_USER="$(whoami)"
if [[ -z "${TARGET_USER}" ]]; then
  TARGET_USER="${CURRENT_USER}"
fi

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

echo "[litellm] Installing LiteLLM (proxy) for ${TARGET_USER} (invoked by ${CURRENT_USER})"

INSTALL_LITELLM_SNIPPET='set -eu; export PATH="$HOME/.local/bin:$PATH"; if ! command -v uv >/dev/null; then echo "Error: uv not found (install uv first)."; exit 1; fi; uv tool install --force litellm[proxy]; command -v litellm >/dev/null; litellm --version >/dev/null || true'

if [[ "${CURRENT_USER}" == "${TARGET_USER}" ]]; then
  bash -lc "${INSTALL_LITELLM_SNIPPET}"
else
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "${TARGET_USER}" -- bash -lc "${INSTALL_LITELLM_SNIPPET}"
  else
    su -l "${TARGET_USER}" -c "${INSTALL_LITELLM_SNIPPET}"
  fi
fi

echo "[litellm] Done."
echo "[litellm] - LiteLLM: $(command -v litellm 2>/dev/null || echo 'installed in user env')"
echo "[litellm] - Proxy Python: python3"

