#!/bin/bash

# this is to be generated by python front end

# install miniconda
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SYSTEM_DIR=$DIR/../system

# install miniconda
bash $SYSTEM_DIR/conda/install-miniconda.sh