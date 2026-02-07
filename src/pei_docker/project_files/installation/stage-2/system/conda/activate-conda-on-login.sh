#!/usr/bin/env bash

# Stage-2 wrapper: source stage-1 canonical activation script.

_peidocker_is_sourced() {
  [[ "${BASH_SOURCE[0]}" != "$0" ]]
}

_peidocker_safe_return() {
  local code="$1"
  return "$code" 2>/dev/null || exit "$code"
}

if ! _peidocker_is_sourced; then
  set -euo pipefail
fi

if [[ -z "${PEI_STAGE_DIR_1:-}" ]]; then
  echo "Error: PEI_STAGE_DIR_1 is not set; cannot locate stage-1 conda activation script" >&2
  _peidocker_safe_return 2
fi

# shellcheck source=/dev/null
stage1_script="$PEI_STAGE_DIR_1/system/conda/activate-conda-on-login.sh"

if _peidocker_is_sourced; then
  # Source into the login shell so `conda activate` can affect the session.
  # shellcheck source=/dev/null
  source "$stage1_script" "$@"
  return $?
fi

bash "$stage1_script" "$@"
