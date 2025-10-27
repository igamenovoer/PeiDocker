#!/bin/bash

# get dir of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# get filename of this script
FILENAME=$(basename $0)
echo "running $DIR/$FILENAME"

# install dev tools
export DEBIAN_FRONTEND=noninteractive
export TZ=Asia/Shanghai

# for general development
apt-get update

# Define development libraries
dev_libs=(
    "python3"
    "python3-pip"
    "cmake"
    "cmake-curses-gui"
    "pkg-config"
    "git"
    "git-lfs"
    "micro"
    "nano"
    "mc"
    "tzdata"  # install this to avoid tzdata asking for timezone in the future
)

# Install all development libraries
echo "Installing development libraries..."
apt-get install -y "${dev_libs[@]}"
