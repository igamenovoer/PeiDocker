#!/usr/bin/env bash

# Stage-2 wrapper: source stage-1 canonical activation script.

set -euo pipefail

if [[ -z "${PEI_STAGE_DIR_1:-}" ]]; then
  echo "Error: PEI_STAGE_DIR_1 is not set; cannot locate stage-1 conda activation script" >&2
  return 2 2>/dev/null || exit 2
fi

# shellcheck source=/dev/null
source "$PEI_STAGE_DIR_1/system/conda/activate-conda-on-login.sh" "$@"
