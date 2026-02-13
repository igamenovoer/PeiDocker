#!/bin/bash

# run in entrypoint before ssh service starts

_log_verbose() {
    if [ "${PEI_ENTRYPOINT_VERBOSE:-0}" = "1" ]; then
        echo "$@"
    fi
}

# get current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
_log_verbose "Executing $DIR/on-entry.sh ..."

# create links before anything
bash "$DIR/create-links.sh"

# first run
first_run_signature_file="$PEI_DOCKER_DIR/stage-2-init-done"

# if first run signature file exists, skip the first run tasks
# otherwise, run the first run tasks
if [ -f "$first_run_signature_file" ]; then
    _log_verbose "$first_run_signature_file found, skipping first run tasks"
else
    _log_verbose "$first_run_signature_file not found, running first run tasks ..."
    bash "$DIR/on-first-run.sh"
    _log_verbose "Writing $first_run_signature_file"
    echo "stage-2 is initialized" > "$first_run_signature_file"
fi

# execute on-every-run tasks
bash "$DIR/on-every-run.sh"
