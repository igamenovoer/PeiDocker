#!/usr/bin/env bash
set -euo pipefail

# Append NVIDIA library path defaults into /etc/shinit_v2 so that
# SSH and non-interactive shells see the same CUDA/TRT env as docker exec.
#
# Intended usage:
#   - Run inside a freshly started NGC-based container as root, e.g.:
#       /pei-from-host/stage-1/system/ngc/fix-shinit.sh
#   - Safe to run multiple times; it will not duplicate the patch.

SHINIT_FILE="/etc/shinit_v2"

if [[ ! -f "${SHINIT_FILE}" ]]; then
    echo "ngc/fix-shinit.sh: ${SHINIT_FILE} not found; nothing to patch." >&2
    exit 0
fi

# Avoid duplicating the block if the script is run multiple times.
if grep -Fq "Custom: Ensure NVIDIA library paths exist for SSH/non-interactive shells" "${SHINIT_FILE}"; then
    echo "ngc/fix-shinit.sh: ${SHINIT_FILE} already contains NVIDIA SSH env fix; skipping." >&2
    exit 0
fi

{
    echo ""
    # Use single-quoted EOF so ${...} is preserved literally in /etc/shinit_v2.
    cat <<'EOF'
# Custom: Ensure NVIDIA library paths exist for SSH/non-interactive shells
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-/usr/local/cuda/compat/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64}
export LIBRARY_PATH=${LIBRARY_PATH:-/usr/local/cuda/lib64/stubs:}
EOF
} >> "${SHINIT_FILE}"

echo "ngc/fix-shinit.sh: Appended NVIDIA SSH env fix to ${SHINIT_FILE}." >&2
