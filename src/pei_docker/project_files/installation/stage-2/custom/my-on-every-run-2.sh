#!/bin/bash

# Example every-run script demonstrating parameter support
# Supports parameters: --update-status --log-startup

# get the path of this file
SCRIPTFILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# Default values
UPDATE_STATUS=false
LOG_STARTUP=false

echo "=== Stage 2 Custom Every-Run Script ==="
echo "Executing: $SCRIPTFILE"
echo "Arguments received: $*"

# Parse command line parameters
for arg in "$@"; do
    case $arg in
        --update-status)
            UPDATE_STATUS=true
            shift
            ;;
        --log-startup)
            LOG_STARTUP=true
            shift
            ;;
        *)
            echo "Unknown parameter: $arg"
            ;;
    esac
done

echo "Configuration:"
echo "  Update status: $UPDATE_STATUS"
echo "  Log startup: $LOG_STARTUP"

# Demonstrate different behavior based on parameters
if [ "$UPDATE_STATUS" = true ]; then
    echo "[STATUS] Updating application status..."
    echo "[STATUS] Checking service health..."
    echo "[STATUS] Service status: Running"
    echo "[STATUS] Last started: $(date)"
    echo "[STATUS] Memory usage: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2 }' || echo 'N/A')"
    echo "[STATUS] Status update completed"
fi

if [ "$LOG_STARTUP" = true ]; then
    echo "[LOGGING] Recording startup event..."
    LOG_FILE="/tmp/startup.log"
    echo "$(date): Stage 2 every-run script executed" >> "$LOG_FILE"
    echo "$(date): Container startup logged" >> "$LOG_FILE"
    echo "[LOGGING] Startup logged to: $LOG_FILE"
    echo "[LOGGING] Recent log entries:"
    tail -3 "$LOG_FILE" 2>/dev/null | sed 's/^/[LOGGING]   /' || echo "[LOGGING]   No previous entries"
fi

echo "Stage 2 every-run operations completed successfully"
echo "=== End Stage 2 Every-Run ==="