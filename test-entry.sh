#!/bin/bash

echo "========================================="
echo "CUSTOM ENTRY POINT TEST"
echo "========================================="
echo "Script: $0"
echo "Number of arguments: $#"
echo "All arguments: $*"
echo "Time: $(date)"
echo ""

# Default values
MODE="interactive"
COUNT=1

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode=*)
            MODE="${1#*=}"
            shift
            ;;
        --count=*)
            COUNT="${1#*=}"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            shift
            ;;
    esac
done

echo "Parsed Configuration:"
echo "  MODE: $MODE"
echo "  COUNT: $COUNT"
echo ""

if [ "$MODE" = "test" ]; then
    echo "=== RUNNING IN TEST MODE ==="
    echo "This demonstrates runtime arguments overriding defaults"
    for i in $(seq 1 $COUNT); do
        echo "Test iteration $i of $COUNT"
        sleep 1
    done
    echo "Test mode complete!"
elif [ "$MODE" = "default" ]; then
    echo "=== RUNNING IN DEFAULT MODE ==="
    echo "This demonstrates default arguments from YAML config"
    for i in $(seq 1 $COUNT); do
        echo "Default action $i of $COUNT"
        sleep 1
    done
    echo "Default mode complete, starting interactive shell..."
    export SHELL=/bin/bash
    exec /bin/bash
else
    echo "=== RUNNING IN INTERACTIVE MODE ==="
    echo "Starting interactive shell..."
    export SHELL=/bin/bash
    exec /bin/bash
fi