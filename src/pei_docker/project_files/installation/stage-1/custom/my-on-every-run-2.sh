#!/bin/bash

# Example every-run script demonstrating parameter support
# Supports parameters: --check-health

# get the path of this file
SCRIPTFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# Default values
CHECK_HEALTH=false

echo "=== Stage 1 Custom Every-Run Script ==="
echo "Executing: $SCRIPTFILE"
echo "Arguments received: $*"

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --check-health)
            CHECK_HEALTH=true
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

echo "Configuration:"
echo "  Check health: $CHECK_HEALTH"

# Demonstrate different behavior based on parameters
if [ "$CHECK_HEALTH" = true ]; then
    echo "[HEALTH] Performing system health checks..."
    echo "[HEALTH] CPU usage: $(top -bn1 | grep '^%Cpu' | awk '{print $2}' || echo 'N/A')"
    echo "[HEALTH] Load average: $(cat /proc/loadavg | awk '{print $1, $2, $3}' || echo 'N/A')"
    echo "[HEALTH] Disk usage: $(df -h / | tail -1 | awk '{print $5}' || echo 'N/A')"
    echo "[HEALTH] Health checks completed"
fi

echo "Every-run operations completed successfully"
echo "=== End Stage 1 Every-Run ==="