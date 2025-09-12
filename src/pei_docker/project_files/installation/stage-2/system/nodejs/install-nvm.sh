#!/bin/bash

# =================================================================
# Install Node Version Manager (NVM)
# =================================================================
# Usage: ./install-nvm.sh
#
# Description:
#   This script installs NVM (Node Version Manager) which allows you
#   to install and manage multiple versions of Node.js. It either
#   clones NVM from GitHub or copies from a cached directory if available.
#   The script also configures your ~/.bashrc to load NVM automatically.
#
# Prerequisites:
#   - Git must be installed
#   - Internet connection required (if no cached version available)
#   - $PEI_STAGE_DIR_2 environment variable should be set for cached install
#
# Post-installation:
#   - Restart your shell or run: source ~/.bashrc
#   - Use install-nodejs.sh to install Node.js versions
#
# Examples:
#   ./install-nvm.sh
# =================================================================

# install nvm only, to install nodejs, use install-nodejs.sh
export DEBIAN_FRONTEND=noninteractive

stage_dir=$PEI_STAGE_DIR_2
tmp_dir=$stage_dir/tmp

# do we have tmp/nvm directory? if not, git clone nvm
if [ ! -d "$tmp_dir/nvm" ]; then
    echo "cloning nvm to ~/.nvm ..."
    git clone https://github.com/nvm-sh/nvm.git .nvm
else
    # copy tmp/nvm to ~/.nvm
    echo "copying $tmp_dir/nvm to $HOME/.nvm ..."
    cp -r $tmp_dir/nvm $HOME/.nvm
fi

read -r -d '' NVM_SCRIPT << 'EOF'
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
EOF

# add NVM_SCRIPT to ~/.bashrc
echo "" >> ~/.bashrc
echo "$NVM_SCRIPT" >> ~/.bashrc
echo "" >> ~/.bashrc