#!/bin/bash

script_dir="$PEI_STAGE_DIR_1/internals"
custom_wrapper="$PEI_STAGE_DIR_1/generated/_custom-on-entry.sh"

_stdin_is_interactive() {
    if [ -t 0 ]; then
        return 0
    fi

    stdin_target="$(readlink /proc/$$/fd/0 2>/dev/null || true)"
    if [ -n "$stdin_target" ] && [ "$stdin_target" != "/dev/null" ]; then
        return 0
    fi

    return 1
}

_prescan_verbose_default_mode() {
    # Only parse entrypoint options in default mode.
    if [ -s "$custom_wrapper" ]; then
        return 0
    fi
    if [ $# -eq 0 ]; then
        return 0
    fi
    case "$1" in
        --*)
            ;;
        *)
            return 0
            ;;
    esac

    while [ $# -gt 0 ]; do
        case "$1" in
            --)
                break
                ;;
            --verbose)
                export PEI_ENTRYPOINT_VERBOSE=1
                return 0
                ;;
            *)
                shift
                ;;
        esac
    done
}

_prescan_verbose_default_mode "$@"

# Always run preparation before handoff.
bash "$script_dir/on-entry.sh"

if [ -f /etc/ssh/sshd_config ]; then
    echo "Starting ssh service..."
    service ssh start
fi

if [ -s "$custom_wrapper" ]; then
    echo "Entrypoint branch: custom on_entry wrapper ($custom_wrapper)"
    exec bash "$custom_wrapper" "$@"
fi

# Preserve legacy command passthrough when argv does not start with '--'.
if [ $# -gt 0 ]; then
    case "$1" in
        --*)
            ;;
        *)
            echo "Entrypoint branch: exec user command ($*)"
            exec "$@"
            ;;
    esac
fi

no_block=0
args=("$@")
cmd_start=0
idx=0
len=${#args[@]}

while [ $idx -lt $len ]; do
    arg="${args[$idx]}"
    case "$arg" in
        --no-block)
            no_block=1
            ;;
        --verbose)
            export PEI_ENTRYPOINT_VERBOSE=1
            ;;
        --)
            cmd_start=$((idx + 1))
            break
            ;;
        --*)
            echo "Error: Unknown entrypoint option: $arg" >&2
            exit 2
            ;;
        *)
            echo "Error: Unexpected entrypoint argument before '--': $arg" >&2
            exit 2
            ;;
    esac
    idx=$((idx + 1))
done

if [ $cmd_start -gt 0 ] && [ $cmd_start -lt $len ]; then
    cmd=("${args[@]:$cmd_start}")
    echo "Entrypoint branch: exec user command (${cmd[*]})"
    exec "${cmd[@]}"
fi

if [ "$no_block" = "1" ]; then
    echo "Entrypoint branch: no-block exit"
    exit 0
fi

if _stdin_is_interactive; then
    echo "Entrypoint branch: bash fallback"
    export SHELL=/bin/bash
    exec /bin/bash
fi

echo "Entrypoint branch: sleep fallback"
trap 'exit 0' TERM
while :; do sleep infinity & wait $!; done
