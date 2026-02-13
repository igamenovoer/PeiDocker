#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

TMP_ROOT="$REPO_ROOT/tmp/entrypoint-non-tty-default-blocking-e2e"
LOG_DIR="$TMP_ROOT/logs"
PROJECT_BASE="$TMP_ROOT/project-base"
PROJECT_MISSING="$TMP_ROOT/project-missing"

BASE_CONFIG="$SCRIPT_DIR/configs/base.yml"
MISSING_CONFIG="$SCRIPT_DIR/configs/missing-custom-entry.yml"

IMAGE_BASE_STAGE1="pei-entrypoint-e2e:stage-1"
IMAGE_BASE_STAGE2="pei-entrypoint-e2e:stage-2"
IMAGE_MISSING_STAGE2="pei-entrypoint-e2e-missing:stage-2"

SSH_USER="tester"
SSH_PASS="tester123"

ACTIVE_CONTAINERS=()
PYTHON_CMD=()

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

cleanup() {
    local cid
    for cid in "${ACTIVE_CONTAINERS[@]}"; do
        docker rm -f "$cid" >/dev/null 2>&1 || true
    done
}
trap cleanup EXIT

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

generate_and_build_stage2() {
    local project_dir="$1"
    local config_file="$2"

    rm -rf "$project_dir"
    mkdir -p "$project_dir"

    log "Creating project at $project_dir"
    "${PYTHON_CMD[@]}" -m pei_docker.pei create -p "$project_dir"
    cp "$config_file" "$project_dir/user_config.yml"
    "${PYTHON_CMD[@]}" -m pei_docker.pei configure -p "$project_dir"

    log "Building stage-2 image from $project_dir"
    (
        cd "$project_dir"
        docker compose build stage-1
        docker compose build stage-2
    )
}

assert_running() {
    local cid="$1"
    local running
    running="$(docker inspect -f '{{.State.Running}}' "$cid")"
    if [ "$running" != "true" ]; then
        fail "Container is not running: $cid"
    fi
}

pid1_cmdline() {
    local cid="$1"
    docker exec "$cid" sh -lc 'tr "\0" " " </proc/1/cmdline'
}

run_default_mode_checks() {
    local image="$1"
    local image_key
    image_key="$(sanitize_name "$image")"

    log "[$image] E01 non-interactive no-command -> sleep + SSH login"
    local cid
    cid="$(docker run -d -p 0:22 "$image")"
    register_container "$cid"
    sleep 4
    assert_running "$cid"
    local cmdline
    cmdline="$(pid1_cmdline "$cid")"
    assert_contains "$cmdline" "sleep infinity"

    local port_line
    port_line="$(docker port "$cid" 22/tcp | head -n1)"
    local host_port="${port_line##*:}"
    wait_for_ssh "$host_port"
    local whoami_out
    whoami_out="$(run_ssh "$host_port" "whoami")"
    if [ "$whoami_out" != "$SSH_USER" ]; then
        fail "Unexpected SSH user. Expected $SSH_USER, got $whoami_out"
    fi
    run_ssh "$host_port" "git --version" >/dev/null

    log "[$image] E02 -i no-command -> bash fallback"
    local cid_i
    cid_i="$(docker run -d -i "$image")"
    register_container "$cid_i"
    sleep 3
    assert_running "$cid_i"
    local cmdline_i
    cmdline_i="$(pid1_cmdline "$cid_i")"
    assert_contains "$cmdline_i" "/bin/bash"

    log "[$image] E03 --no-block exits successfully"
    local no_block_out
    no_block_out="$(docker run --rm "$image" --no-block 2>&1)"
    save_log "${image_key}-E03-no-block" "$no_block_out"
    assert_contains "$no_block_out" "Entrypoint branch: no-block exit"

    log "[$image] E04 passthrough command env"
    local env_out
    env_out="$(docker run --rm "$image" env 2>&1)"
    save_log "${image_key}-E04-env" "$env_out"
    assert_contains "$env_out" "Entrypoint branch: exec user command"
    assert_contains "$env_out" "HOME="

    log "[$image] E05 --verbose toggles hook logging"
    local quiet_out
    quiet_out="$(docker run --rm "$image" -- env 2>&1)"
    save_log "${image_key}-E05-quiet" "$quiet_out"
    assert_not_contains "$quiet_out" "/on-entry.sh"

    local verbose_out
    verbose_out="$(docker run --rm "$image" --verbose -- env 2>&1)"
    save_log "${image_key}-E05-verbose" "$verbose_out"
    assert_contains "$verbose_out" "PEI_ENTRYPOINT_VERBOSE=1"
    assert_contains "$verbose_out" "/on-entry.sh"

    log "[$image] E06 unknown option exits non-zero"
    local unknown_out
    local unknown_rc=0
    set +e
    unknown_out="$(docker run --rm "$image" --wat 2>&1)"
    unknown_rc=$?
    set -e
    save_log "${image_key}-E06-unknown-option" "$unknown_out"
    if [ "$unknown_rc" -eq 0 ]; then
        fail "Unknown entrypoint option should fail for $image"
    fi
    assert_contains "$unknown_out" "Unknown entrypoint option"
}

run_missing_custom_checks() {
    local image="$1"
    local image_key
    image_key="$(sanitize_name "$image")"

    log "[$image] C05 missing custom on_entry target is hard error"
    local miss_out
    local miss_rc=0
    set +e
    miss_out="$(docker run --rm "$image" 2>&1)"
    miss_rc=$?
    set -e
    save_log "${image_key}-C05-missing-custom-entry" "$miss_out"
    if [ "$miss_rc" -eq 0 ]; then
        fail "Missing custom on_entry target should fail for $image"
    fi
    assert_contains "$miss_out" "Custom on-entry target script not found"

    log "[$image] C06 custom on_entry does not parse default-mode options"
    local no_parse_out
    local no_parse_rc=0
    set +e
    no_parse_out="$(docker run --rm "$image" --no-block 2>&1)"
    no_parse_rc=$?
    set -e
    save_log "${image_key}-C06-no-parse-under-custom" "$no_parse_out"
    if [ "$no_parse_rc" -eq 0 ]; then
        fail "Custom on_entry path with missing target should still fail with --no-block"
    fi
    assert_contains "$no_parse_out" "Custom on-entry target script not found"
    assert_not_contains "$no_parse_out" "Entrypoint branch: no-block exit"
}

main() {
    require_cmd docker
    require_cmd ssh
    require_cmd sshpass
    if command -v pixi >/dev/null 2>&1; then
        PYTHON_CMD=(pixi run python)
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD=(python3)
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD=(python)
    else
        fail "Missing required command: pixi (preferred) or python3/python"
    fi

    export PYTHONPATH="$REPO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
    mkdir -p "$LOG_DIR"

    log "Preparing and building base project"
    generate_and_build_stage2 "$PROJECT_BASE" "$BASE_CONFIG"

    run_default_mode_checks "$IMAGE_BASE_STAGE1"
    run_default_mode_checks "$IMAGE_BASE_STAGE2"

    log "Preparing and building missing-custom-entry project"
    generate_and_build_stage2 "$PROJECT_MISSING" "$MISSING_CONFIG"
    run_missing_custom_checks "$IMAGE_MISSING_STAGE2"

    log "Functional checks completed successfully"
    log "Logs: $LOG_DIR"
}

main "$@"
