#!/usr/bin/env bash

log() {
    echo "[entrypoint-e2e] $*"
}

fail() {
    echo "[entrypoint-e2e][ERROR] $*" >&2
    exit 1
}

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        fail "Missing required command: $1"
    fi
}

sanitize_name() {
    echo "$1" | tr '/:' '__'
}

save_log() {
    local name="$1"
    local content="$2"
    local filename
    filename="$(sanitize_name "$name")"
    printf "%s\n" "$content" > "$LOG_DIR/${filename}.log"
}

register_container() {
    ACTIVE_CONTAINERS+=("$1")
}

remove_container() {
    local cid="$1"
    docker rm -f "$cid" >/dev/null 2>&1 || true
}

cleanup_registered_containers() {
    local cid
    for cid in "${ACTIVE_CONTAINERS[@]}"; do
        remove_container "$cid"
    done
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    if ! grep -Fq "$needle" <<< "$haystack"; then
        fail "Expected output to contain: $needle"
    fi
}

assert_not_contains() {
    local haystack="$1"
    local needle="$2"
    if grep -Fq "$needle" <<< "$haystack"; then
        fail "Expected output NOT to contain: $needle"
    fi
}

assert_running() {
    local cid="$1"
    local running
    running="$(docker inspect -f '{{.State.Running}}' "$cid")"
    if [ "$running" != "true" ]; then
        fail "Container is not running: $cid"
    fi
}

assert_stopped() {
    local cid="$1"
    local running
    running="$(docker inspect -f '{{.State.Running}}' "$cid")"
    if [ "$running" != "false" ]; then
        fail "Container is still running: $cid"
    fi
}

assert_exits_after_sigterm() {
    local cid="$1"
    local timeout_seconds="${2:-20}"
    local i

    docker kill --signal TERM "$cid" >/dev/null

    for i in $(seq 1 "$timeout_seconds"); do
        if [ "$(docker inspect -f '{{.State.Running}}' "$cid")" = "false" ]; then
            return 0
        fi
        sleep 1
    done
    fail "Container did not exit within ${timeout_seconds}s after SIGTERM: $cid"
}

pid1_cmdline() {
    local cid="$1"
    docker exec "$cid" sh -lc 'tr "\0" " " </proc/1/cmdline'
}

container_logs() {
    local cid="$1"
    docker logs "$cid" 2>&1
}

wait_for_ssh() {
    local port="$1"
    local i
    for i in $(seq 1 30); do
        if sshpass -p "$SSH_PASS" ssh \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            -o LogLevel=ERROR \
            -o ConnectTimeout=2 \
            -p "$port" \
            "$SSH_USER@127.0.0.1" \
            "echo ready" >/dev/null 2>&1; then
            return 0
        fi
        sleep 2
    done
    fail "SSH did not become ready on port $port"
}

run_ssh() {
    local port="$1"
    local cmd="$2"
    sshpass -p "$SSH_PASS" ssh \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o LogLevel=ERROR \
        -o ConnectTimeout=3 \
        -p "$port" \
        "$SSH_USER@127.0.0.1" \
        "$cmd"
}
