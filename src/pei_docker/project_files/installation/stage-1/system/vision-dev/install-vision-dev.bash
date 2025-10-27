#!/bin/bash

# get dir of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# get filename of this script
FILENAME=$(basename $0)
echo "running $DIR/$FILENAME"

# install vision dev tools
echo "Updating apt package list..."
apt-get update

# Define vision development libraries
vision_libs=(
    "libopencv-dev"           # opencv with gui support
    "libopencv-contrib-dev"   # opencv contrib modules
    "ffmpeg"                  # video processing
    "libsm6"                  # ffmpeg dependency
    "libxext6"                # ffmpeg dependency
    "imagemagick"             # image manipulation
    "qimgv"                   # image viewing
    "python3"                 # python interpreter
    "python3-pip"             # python package manager
)

# Install all vision development libraries
echo "Installing vision development libraries..."
apt-get install -y "${vision_libs[@]}"

# install python packages for vision development
vision_packages=(
    "ipykernel"
    "scipy"
    "numpy"
    "opencv-contrib-python"
    "networkx"
    "matplotlib"
    "pyyaml"
    "attrs"
    "cattrs"
    "omegaconf"
    "rich"
    "click"
)

echo "Installing Python packages for vision development..."
pip3 install "${vision_packages[@]}" --break-system-packages
