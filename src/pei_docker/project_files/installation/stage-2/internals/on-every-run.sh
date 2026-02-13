#!/bin/bash

_log_verbose() {
    if [ "${PEI_ENTRYPOINT_VERBOSE:-0}" = "1" ]; then
        echo "$@"
    fi
}

# get current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
_log_verbose "Executing $DIR/on-every-run.sh ..."

# nothing to do, just call custom on-first-run script
bash "$DIR/custom-on-every-run.sh"
