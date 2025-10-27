#!/bin/bash

# =================================================================
# Install Angular CLI with pnpm
# =================================================================
# Usage: ./install-angular.sh
#
# Description:
#   This script installs Angular CLI globally using pnpm package manager
#   and configures Angular to use pnpm as the default package manager
#   for new projects.
#
# Prerequisites:
#   - Node.js must be installed (run install-nodejs.sh first)
#   - pnpm must be installed (included with install-nodejs.sh)
#   - Internet connection required
#
# Post-installation:
#   - Use 'ng new project-name' to create new Angular projects
#   - Projects will automatically use pnpm for package management
#
# Examples:
#   ./install-angular.sh
# =================================================================

echo "installing angular/cli"
pnpm install -g @angular/cli

echo "using pnpm as angular package manager"
ng config -g cli.packageManager pnpm