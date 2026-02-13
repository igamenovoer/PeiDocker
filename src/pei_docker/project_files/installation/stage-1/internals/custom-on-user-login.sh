#!/bin/bash

_log_verbose() {
    if [ "${PEI_ENTRYPOINT_VERBOSE:-0}" = "1" ]; then
        echo "$@"
    fi
}

# get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPTFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
_log_verbose "Executing $SCRIPTFILE"

# source _setup-cuda.sh
# source "$DIR/_setup-cuda.sh"

DIR_GENERATED="$DIR/../generated"

if [ -f "$DIR_GENERATED/_custom-on-user-login.sh" ]; then
    source "$DIR_GENERATED/_custom-on-user-login.sh"
fi
