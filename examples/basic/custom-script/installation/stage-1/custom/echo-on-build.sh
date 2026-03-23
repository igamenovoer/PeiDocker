#!/usr/bin/env bash
set -euo pipefail

message="custom-script-ran"
for arg in "$@"; do
  case "$arg" in
    --message=*)
      message="${arg#--message=}"
      ;;
  esac
done

printf '%s\n' "$message" >/tmp/peidocker-custom-script.txt
echo "wrote /tmp/peidocker-custom-script.txt"
