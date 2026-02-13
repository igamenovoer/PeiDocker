#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

exec bash "$REPO_ROOT/tests/functional/entrypoint-non-tty-default-blocking/run.bash" "$@"
