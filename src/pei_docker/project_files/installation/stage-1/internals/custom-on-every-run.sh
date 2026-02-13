#!/bin/bash

_log_verbose() {
    if [ "${PEI_ENTRYPOINT_VERBOSE:-0}" = "1" ]; then
        echo "$@"
    fi
}

# get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
_log_verbose "Executing $DIR/custom-on-every-run.sh ..."

DIR_GENERATED="$DIR/../generated"

if [ -f "$DIR_GENERATED/_custom-on-every-run.sh" ]; then
    _log_verbose "Found custom on-every-run script, executing ..."
    bash "$DIR_GENERATED/_custom-on-every-run.sh"
fi
