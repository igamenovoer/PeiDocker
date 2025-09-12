#!/bin/bash

# =================================================================
# Install Node.js for All Users on the System
# =================================================================
# Usage: ./install-nodejs-for-everyone.sh [OPTIONS]
#
# Options:
#   --npm-cn-mirror    Use Chinese npm mirror (registry.npmmirror.com)
#                      for all users. Default: Use official npm registry
#
# Description:
#   This script installs Node.js and pnpm for all users found in /home.
#   It first installs NVM for each user, then installs Node.js LTS.
#   Requires root privileges to switch between users.
#
# Prerequisites:
#   - Root or sudo privileges required
#   - Internet connection required
#   - install-nvm.sh and install-nodejs.sh must be in the same directory
#
# Examples:
#   sudo ./install-nodejs-for-everyone.sh                 # Official registry
#   sudo ./install-nodejs-for-everyone.sh --npm-cn-mirror # Chinese mirror
# =================================================================

# get current dir
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Parse command line arguments
NODEJS_ARGS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --npm-cn-mirror)
            NODEJS_ARGS="--npm-cn-mirror"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--npm-cn-mirror]"
            echo "  --npm-cn-mirror    Use Chinese npm mirror (registry.npmmirror.com) for all users"
            exit 1
            ;;
    esac
done

# for all users, install nodejs
echo "installing nodejs for all users ..."
for user in $(ls /home); do
  su - $user -c "bash $DIR/install-nvm.sh"
  su - $user -c "bash $DIR/install-nodejs.sh $NODEJS_ARGS"
done