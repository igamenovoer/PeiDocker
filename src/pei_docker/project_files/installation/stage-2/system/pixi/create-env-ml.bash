#!/usr/bin/env bash

# Stage-2 wrapper: forward to stage-1 canonical script.

_peidocker_is_sourced() {
  [[ "${BASH_SOURCE[0]}" != "$0" ]]
}

_peidocker_die() {
  echo "Error: $*" >&2
  if _peidocker_is_sourced; then
    return 2
  fi
  exit 2
}

if ! _peidocker_is_sourced; then
  set -euo pipefail
fi

if [[ -z "${PEI_STAGE_DIR_1:-}" ]]; then
  _peidocker_die "PEI_STAGE_DIR_1 is not set; cannot locate stage-1 pixi scripts"
fi

stage1_script="$PEI_STAGE_DIR_1/system/pixi/create-env-ml.bash"

if _peidocker_is_sourced; then
  (set -euo pipefail; bash "$stage1_script" "$@")
  return $?
fi

exec bash "$stage1_script" "$@"
