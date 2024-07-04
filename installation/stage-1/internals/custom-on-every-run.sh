#!/bin/bash

# get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "Executing $DIR/custom-on-every-run.sh ..."

if [ -f "$DIR/_custom-on-every-run.sh" ]; then
    echo "Found custom on-every-run script, executing ..."
    bash "$DIR/_custom-on-every-run.sh"
fi