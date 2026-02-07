#!/usr/bin/env bash

# Storage-agnostic Miniconda installer (stage-1 canonical).
#
# This script intentionally does NOT write to /soft/* and does not probe /soft/*
# to decide behavior. If you want a non-default install location, pass an
# explicit absolute path via --install-dir.

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

INSTALL_DIR="/opt/miniconda3"
TMP_DIR="/tmp/pei-miniconda"
INSTALLER_URL="official"
PIP_REPO="aliyun"
INCLUDE_ROOT=false
VERBOSE=false

usage() {
  cat <<'EOF'
Usage: ./install-miniconda.sh [OPTIONS]

Options:
  --install-dir=PATH     Absolute install prefix (default: /opt/miniconda3)
  --tmp-dir=PATH         Absolute temp directory for downloads (default: /tmp/pei-miniconda)
  --installer-url VALUE  Installer source: official | tuna | <https-url>
                         (default: official)
  --pip-repo NAME        Configure pip mirror via configure-pip-repo.sh: tuna | aliyun
                         (default: aliyun)
  --include-root         Also initialize conda for root user (default: false)
  --verbose              Verbose output
  -h, --help             Show help
EOF
}

logv() {
  if [[ "$VERBOSE" == "true" ]]; then
    echo "[VERBOSE] $*"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-dir=*)
      INSTALL_DIR="${1#*=}"
      shift 1
      ;;
    --tmp-dir=*)
      TMP_DIR="${1#*=}"
      shift 1
      ;;
    --installer-url)
      INSTALLER_URL="${2:-}"
      shift 2
      ;;
    --pip-repo)
      PIP_REPO="${2:-}"
      shift 2
      ;;
    --include-root)
      INCLUDE_ROOT=true
      shift 1
      ;;
    --verbose)
      VERBOSE=true
      shift 1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$INSTALL_DIR" != /* ]]; then
  echo "Error: --install-dir must be an absolute path, got: $INSTALL_DIR" >&2
  exit 2
fi

if [[ "$TMP_DIR" != /* ]]; then
  echo "Error: --tmp-dir must be an absolute path, got: $TMP_DIR" >&2
  exit 2
fi

arch="$(uname -m)"
case "$arch" in
  aarch64|arm64)
    CONDA_PACKAGE_NAME="Miniconda3-latest-Linux-aarch64.sh"
    ;;
  x86_64|amd64)
    CONDA_PACKAGE_NAME="Miniconda3-latest-Linux-x86_64.sh"
    ;;
  *)
    echo "Warning: unknown arch '$arch', defaulting to x86_64 installer" >&2
    CONDA_PACKAGE_NAME="Miniconda3-latest-Linux-x86_64.sh"
    ;;
esac

case "$INSTALLER_URL" in
  ""|official)
    CONDA_DOWNLOAD_URL="https://repo.anaconda.com/miniconda/${CONDA_PACKAGE_NAME}"
    ;;
  tuna)
    CONDA_DOWNLOAD_URL="https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/${CONDA_PACKAGE_NAME}"
    ;;
  http://*|https://*)
    CONDA_DOWNLOAD_URL="$INSTALLER_URL"
    ;;
  *)
    echo "Error: unknown --installer-url value: $INSTALLER_URL (use official | tuna | <url>)" >&2
    exit 2
    ;;
esac

mkdir -p "$TMP_DIR"
CONDA_INSTALLER_PATH="$TMP_DIR/$CONDA_PACKAGE_NAME"

if [[ ! -f "$CONDA_INSTALLER_PATH" ]]; then
  echo "Downloading Miniconda installer to $CONDA_INSTALLER_PATH ..."
  logv "URL: $CONDA_DOWNLOAD_URL"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL -o "$CONDA_INSTALLER_PATH" "$CONDA_DOWNLOAD_URL"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$CONDA_INSTALLER_PATH" "$CONDA_DOWNLOAD_URL" --show-progress
  else
    echo "Error: curl or wget is required to download Miniconda" >&2
    exit 1
  fi
  chmod +x "$CONDA_INSTALLER_PATH"
fi

if [[ -x "$INSTALL_DIR/bin/conda" ]]; then
  echo "Miniconda already installed at $INSTALL_DIR, skipping install step."
else
  echo "Installing Miniconda to $INSTALL_DIR ..."
  bash "$CONDA_INSTALLER_PATH" -b -p "$INSTALL_DIR"
  echo "Setting permissions for $INSTALL_DIR ..."
  chmod -R 777 "$INSTALL_DIR" || true
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDARC_TEMPLATE="$SCRIPT_DIR/conda-tsinghua.txt"

CURRENT_USER="$(whoami)"

run_as_user() {
  local username="$1"
  shift
  local cmd="$*"
  if [[ "$username" == "$CURRENT_USER" ]]; then
    bash -lc "$cmd"
    return
  fi
  if command -v runuser >/dev/null 2>&1; then
    runuser -u "$username" -- bash -lc "$cmd"
  else
    su -l "$username" -c "$cmd"
  fi
}

users=()
if [[ "$INCLUDE_ROOT" == "true" ]]; then
  users+=(root)
fi
if [[ -d /home ]]; then
  while IFS= read -r u; do
    [[ -n "$u" ]] && users+=("$u")
  done < <(ls /home)
fi

if [[ ${#users[@]} -eq 0 ]]; then
  echo "No users to initialize (use --include-root to include root)."
  exit 0
fi

echo "Initializing conda for users: ${users[*]}"

for user in "${users[@]}"; do
  if ! id -u "$user" >/dev/null 2>&1; then
    echo "Warning: user '$user' does not exist, skipping..."
    continue
  fi

  if [[ "$user" == "root" ]]; then
    home_dir="/root"
  else
    home_dir="$(getent passwd "$user" | cut -d: -f6)"
  fi

  logv "User '$user' home: $home_dir"

  # 1) conda init (writes shell rc files for the user)
  run_as_user "$user" "\"$INSTALL_DIR/bin/conda\" init" || true

  # 2) optional: seed .condarc from template (fast mirrors for CN users)
  if [[ -f "$CONDARC_TEMPLATE" ]]; then
    run_as_user "$user" "cp \"$CONDARC_TEMPLATE\" \"$home_dir/.condarc\"" || true
  fi

  # 3) configure pip mirror inside conda base env (if requested)
  if [[ -n "$PIP_REPO" ]]; then
    run_as_user "$user" "source \"$INSTALL_DIR/bin/activate\" && bash \"$SCRIPT_DIR/configure-pip-repo.sh\" \"$PIP_REPO\"" || true
  fi
done

echo "Miniconda installation completed."
