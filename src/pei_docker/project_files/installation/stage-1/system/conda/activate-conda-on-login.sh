#!/usr/bin/env bash

# Storage-agnostic conda activation helper (stage-1 canonical).
#
# Intended usage: as an on_user_login hook (sourced), so `conda activate` affects
# the login shell.

set -euo pipefail

CONDA_DIR="/opt/miniconda3"

usage() {
  cat <<'EOF'
Usage: ./activate-conda-on-login.sh [OPTIONS]

Options:
  --conda-dir=PATH   Absolute conda install directory (default: /opt/miniconda3)
  -h, --help         Show help
EOF
}

safe_return() {
  local code="$1"
  return "$code" 2>/dev/null || exit "$code"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --conda-dir=*)
      CONDA_DIR="${1#*=}"
      shift 1
      ;;
    -h|--help)
      usage
      safe_return 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      safe_return 2
      ;;
  esac
done

if [[ "$CONDA_DIR" != /* ]]; then
  echo "Error: --conda-dir must be an absolute path, got: $CONDA_DIR" >&2
  safe_return 2
fi

if [[ ! -d "$CONDA_DIR" ]]; then
  echo "Conda not found at $CONDA_DIR; skipping activation."
  safe_return 0
fi

# Optional: link shared config, if present (does not assume any storage model).
if [[ -d "$CONDA_DIR/app-config" ]]; then
  if [[ -f "$CONDA_DIR/app-config/.condarc" ]] && [[ ! -e "$HOME/.condarc" ]]; then
    ln -s "$CONDA_DIR/app-config/.condarc" "$HOME/.condarc"
  fi
  if [[ -d "$CONDA_DIR/app-config/.pip" ]] && [[ ! -e "$HOME/.pip" ]]; then
    ln -s "$CONDA_DIR/app-config/.pip" "$HOME/.pip"
  fi
fi

if [[ ! -f "$CONDA_DIR/etc/profile.d/conda.sh" ]]; then
  echo "Conda profile script not found: $CONDA_DIR/etc/profile.d/conda.sh"
  safe_return 0
fi

# shellcheck source=/dev/null
source "$CONDA_DIR/etc/profile.d/conda.sh"

# Activate the base environment (best-effort; don't fail login if it errors).
conda activate base >/dev/null 2>&1 || true
