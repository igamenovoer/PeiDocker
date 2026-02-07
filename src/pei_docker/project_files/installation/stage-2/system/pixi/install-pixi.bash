#!/usr/bin/env bash

# Stage-2 wrapper: forward to stage-1 canonical installer.

set -euo pipefail

if [[ -z "${PEI_STAGE_DIR_1:-}" ]]; then
  echo "Error: PEI_STAGE_DIR_1 is not set; cannot locate stage-1 pixi installer" >&2
  exit 2
fi

exec "$PEI_STAGE_DIR_1/system/pixi/install-pixi.bash" "$@"
