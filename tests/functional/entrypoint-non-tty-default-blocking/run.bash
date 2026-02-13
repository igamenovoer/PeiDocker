#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

source "$SCRIPT_DIR/lib/helpers.bash"

TMP_ROOT="$REPO_ROOT/tmp/entrypoint-non-tty-default-blocking-e2e"
LOG_DIR="$TMP_ROOT/logs"
PROJECT_DIR="$TMP_ROOT/project"
IMAGES_DIR="$TMP_ROOT/images"

PROJECT_BASE="$PROJECT_DIR/base"
PROJECT_CUSTOM_STAGE1="$PROJECT_DIR/custom-stage1"
PROJECT_CUSTOM_BOTH="$PROJECT_DIR/custom-both"
PROJECT_MISSING="$PROJECT_DIR/missing-custom"

BASE_CONFIG="$SCRIPT_DIR/configs/base.yml"
CUSTOM_STAGE1_CONFIG="$SCRIPT_DIR/configs/stage1-custom-entry.yml"
CUSTOM_BOTH_CONFIG="$SCRIPT_DIR/configs/both-custom-entry.yml"
MISSING_CONFIG="$SCRIPT_DIR/configs/missing-custom-entry.yml"

IMAGE_BASE_STAGE1="pei-entrypoint-e2e:stage-1"
IMAGE_BASE_STAGE2="pei-entrypoint-e2e:stage-2"
IMAGE_CUSTOM_STAGE1_STAGE1="pei-entrypoint-e2e-custom-stage1:stage-1"
IMAGE_CUSTOM_STAGE1_STAGE2="pei-entrypoint-e2e-custom-stage1:stage-2"
IMAGE_CUSTOM_BOTH_STAGE2="pei-entrypoint-e2e-custom-both:stage-2"
IMAGE_MISSING_STAGE2="pei-entrypoint-e2e-missing:stage-2"

SSH_USER="tester"
SSH_PASS="tester123"

ACTIVE_CONTAINERS=()
PYTHON_CMD=()

ALL_CASES=(
    E01 E02 E03 E04 E05 E06 E07
    C01 C02 C03 C04 C05 C06
    S01
)
SELECTED_CASES=()

print_usage() {
    cat <<'EOF'
Usage:
  bash tests/functional/entrypoint-non-tty-default-blocking/run.bash [--cases CASE_LIST]

Options:
  --cases CASE_LIST   Comma or space separated case IDs (for example: E01,E02,S01)
  -h, --help          Show this help message

Environment:
  SAVE_E2E_IMAGE_TARS=1   Save built image tarballs under tmp/.../images/
EOF
}

case_id_supported() {
    local case_id="$1"
    local id
    for id in "${ALL_CASES[@]}"; do
        if [ "$id" = "$case_id" ]; then
            return 0
        fi
    done
    return 1
}

set_selected_cases() {
    local raw="${1//,/ }"
    local case_id

    SELECTED_CASES=()
    for case_id in $raw; do
        if ! case_id_supported "$case_id"; then
            fail "Unsupported case ID: $case_id"
        fi
        SELECTED_CASES+=("$case_id")
    done

    if [ "${#SELECTED_CASES[@]}" -eq 0 ]; then
        fail "No case IDs were provided to --cases"
    fi
}

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --cases)
                shift
                if [ $# -eq 0 ]; then
                    fail "Missing value for --cases"
                fi
                set_selected_cases "$1"
                ;;
            --cases=*)
                set_selected_cases "${1#*=}"
                ;;
            -h|--help)
                print_usage
                exit 0
                ;;
            *)
                fail "Unknown argument: $1"
                ;;
        esac
        shift
    done
}

case_enabled() {
    local case_id="$1"
    local selected
    for selected in "${SELECTED_CASES[@]}"; do
        if [ "$selected" = "$case_id" ]; then
            return 0
        fi
    done
    return 1
}

any_case_enabled() {
    local case_id
    for case_id in "$@"; do
        if case_enabled "$case_id"; then
            return 0
        fi
    done
    return 1
}

ensure_python_cmd() {
    if command -v pixi >/dev/null 2>&1; then
        PYTHON_CMD=(pixi run python)
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD=(python3)
    elif command -v python >/dev/null 2>&1; then
        PYTHON_CMD=(python)
    else
        fail "Missing required command: pixi (preferred) or python3/python"
    fi
}

write_stage1_custom_entry_script() {
    local project_dir="$1"
    local path="$project_dir/installation/stage-1/custom/stage1-entry.sh"
    mkdir -p "$(dirname "$path")"
cat > "$path" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "CUSTOM_ENTRY_STAGE1"
echo "CUSTOM_STAGE1_ARGS:$*"
for arg in "$@"; do
    if [ "$arg" = "--no-block" ]; then
        echo "CUSTOM_STAGE1_RECEIVED_NO_BLOCK=1"
        break
    fi
done
if [ -f /pei-init/stage-1-init-done ]; then
    echo "CUSTOM_STAGE1_PREP_OK=1"
fi
EOF
    chmod +x "$path"
}

write_stage2_custom_entry_script() {
    local project_dir="$1"
    local path="$project_dir/installation/stage-2/custom/stage2-entry.sh"
    mkdir -p "$(dirname "$path")"
    cat > "$path" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "CUSTOM_ENTRY_STAGE2"
echo "CUSTOM_STAGE2_ARGS:$*"
if [ -f /pei-init/stage-2-init-done ]; then
    echo "CUSTOM_STAGE2_PREP_OK=1"
fi
EOF
    chmod +x "$path"
}

prepare_custom_scripts() {
    local project_dir="$1"
    local mode="$2"

    case "$mode" in
        none)
            ;;
        stage1)
            write_stage1_custom_entry_script "$project_dir"
            ;;
        both)
            write_stage1_custom_entry_script "$project_dir"
            write_stage2_custom_entry_script "$project_dir"
            ;;
        *)
            fail "Unknown custom script mode: $mode"
            ;;
    esac
}

generate_and_build_stage2() {
    local project_dir="$1"
    local config_file="$2"
    local custom_mode="$3"
    local key
    key="$(basename "$project_dir")"
    local transcript="$LOG_DIR/${key}-build-transcript.log"

    rm -rf "$project_dir"
    mkdir -p "$project_dir"

    {
        log "Creating project at $project_dir"
        "${PYTHON_CMD[@]}" -m pei_docker.pei create -p "$project_dir"
        cp "$config_file" "$project_dir/user_config.yml"
        prepare_custom_scripts "$project_dir" "$custom_mode"
        "${PYTHON_CMD[@]}" -m pei_docker.pei configure -p "$project_dir"

        log "Building stage-1 and stage-2 images from $project_dir"
        (
            cd "$project_dir"
            docker compose build stage-1
            docker compose build stage-2
        )
    } |& tee "$transcript"
}

maybe_save_image_tar() {
    local image="$1"
    if [ "${SAVE_E2E_IMAGE_TARS:-0}" != "1" ]; then
        return 0
    fi
    local filename
    filename="$(sanitize_name "$image").tar"
    log "Saving image tarball: $filename"
    docker image save -o "$IMAGES_DIR/$filename" "$image"
}

run_default_mode_checks() {
    local image="$1"
    local stage_label="$2"
    local image_key
    image_key="$(sanitize_name "$image")"

    if case_enabled E01; then
        log "[$image][$stage_label] E01 non-interactive no-command -> sleep + SSH login"
        local cid
        cid="$(docker run -d -p 0:22 "$image")"
        register_container "$cid"
        sleep 4
        assert_running "$cid"

        local cmdline
        cmdline="$(pid1_cmdline "$cid")"
        save_log "${image_key}-E01-pid1" "$cmdline"
        assert_contains "$cmdline" "bash"

        local logs
        logs="$(container_logs "$cid")"
        save_log "${image_key}-E01-container-logs" "$logs"
        assert_contains "$logs" "Entrypoint branch: sleep fallback"

        local port_line
        port_line="$(docker port "$cid" 22/tcp | head -n1 || true)"
        if [ -z "$port_line" ]; then
            fail "Unable to resolve mapped SSH port for $cid"
        fi
        local host_port="${port_line##*:}"
        wait_for_ssh "$host_port"

        local whoami_out
        whoami_out="$(run_ssh "$host_port" "whoami")"
        if [ "$whoami_out" != "$SSH_USER" ]; then
            fail "Unexpected SSH user. Expected $SSH_USER, got $whoami_out"
        fi
        local ssh_smoke_out
        ssh_smoke_out="$(run_ssh "$host_port" "env | grep -E '^HOME='")"
        save_log "${image_key}-E01-ssh-smoke" "$ssh_smoke_out"
        assert_contains "$ssh_smoke_out" "HOME="

        remove_container "$cid"
    fi

    if case_enabled E02; then
        log "[$image][$stage_label] E02 -i no-command -> bash fallback"
        local cid_i
        cid_i="$(docker run -d -i "$image")"
        register_container "$cid_i"
        sleep 3
        assert_running "$cid_i"

        local cmdline_i
        cmdline_i="$(pid1_cmdline "$cid_i")"
        save_log "${image_key}-E02-pid1" "$cmdline_i"
        assert_contains "$cmdline_i" "/bin/bash"

        local logs_i
        logs_i="$(container_logs "$cid_i")"
        save_log "${image_key}-E02-container-logs" "$logs_i"
        assert_contains "$logs_i" "Entrypoint branch: bash fallback"

        remove_container "$cid_i"
    fi

    if case_enabled E03; then
        log "[$image][$stage_label] E03 --no-block exits successfully"
        local no_block_out
        no_block_out="$(docker run --rm "$image" --no-block 2>&1)"
        save_log "${image_key}-E03-no-block" "$no_block_out"
        assert_contains "$no_block_out" "Entrypoint branch: no-block exit"
    fi

    if case_enabled E04; then
        log "[$image][$stage_label] E04 passthrough command env"
        local env_out
        env_out="$(docker run --rm "$image" env 2>&1)"
        save_log "${image_key}-E04-env" "$env_out"
        assert_contains "$env_out" "Entrypoint branch: exec user command"
        assert_contains "$env_out" "HOME="
    fi

    if case_enabled E05; then
        log "[$image][$stage_label] E05 --verbose toggles hook logging"
        local quiet_out
        quiet_out="$(docker run --rm "$image" -- env 2>&1)"
        save_log "${image_key}-E05-quiet" "$quiet_out"
        assert_not_contains "$quiet_out" "/on-entry.sh"

        local verbose_out
        verbose_out="$(docker run --rm "$image" --verbose -- env 2>&1)"
        save_log "${image_key}-E05-verbose" "$verbose_out"
        assert_contains "$verbose_out" "PEI_ENTRYPOINT_VERBOSE=1"
        assert_contains "$verbose_out" "/on-entry.sh"
    fi

    if case_enabled E06; then
        log "[$image][$stage_label] E06 unknown option exits non-zero"
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
    fi

    if case_enabled E07; then
        log "[$image][$stage_label] E07 preparation runs before command handoff"
        local prep_cmd
        local prep_marker
        if [ "$stage_label" = "stage-1" ]; then
            prep_cmd='test -f /pei-init/stage-1-init-done && echo E07_STAGE1_PREP_OK'
            prep_marker='E07_STAGE1_PREP_OK'
        else
            prep_cmd='test -f /pei-init/stage-1-init-done && test -f /pei-init/stage-2-init-done && echo E07_STAGE2_PREP_OK'
            prep_marker='E07_STAGE2_PREP_OK'
        fi

        local prep_out
        prep_out="$(docker run --rm "$image" -- sh -lc "$prep_cmd" 2>&1)"
        save_log "${image_key}-E07-preparation" "$prep_out"
        assert_contains "$prep_out" "$prep_marker"
        assert_contains "$prep_out" "Entrypoint branch: exec user command"
    fi
}

run_custom_stage1_checks() {
    local image="$1"
    local image_key
    image_key="$(sanitize_name "$image")"

    if case_enabled C01; then
        log "[$image] C01 stage-1 custom on_entry and argument forwarding"
        local c01_out
        c01_out="$(docker run --rm "$image" --c01-probe 2>&1)"
        save_log "${image_key}-C01-stage1-custom" "$c01_out"
        assert_contains "$c01_out" "Entrypoint branch: custom on_entry wrapper"
        assert_contains "$c01_out" "CUSTOM_ENTRY_STAGE1"
        assert_contains "$c01_out" "CUSTOM_STAGE1_ARGS:--baked-stage=1 --baked-order=first --c01-probe"
        assert_not_contains "$c01_out" "Unknown entrypoint option"
    fi

    if case_enabled C02; then
        log "[$image] C02 baked args precede runtime args"
        local c02_out
        c02_out="$(docker run --rm "$image" runtime-alpha runtime-beta 2>&1)"
        save_log "${image_key}-C02-baked-order" "$c02_out"
        assert_contains "$c02_out" "CUSTOM_STAGE1_ARGS:--baked-stage=1 --baked-order=first runtime-alpha runtime-beta"
    fi

    if case_enabled C06; then
        log "[$image] C06 no parsing under custom on_entry for --no-block"
        local c06_out
        c06_out="$(docker run --rm "$image" --no-block 2>&1)"
        save_log "${image_key}-C06-no-parse-under-custom" "$c06_out"
        assert_contains "$c06_out" "CUSTOM_STAGE1_RECEIVED_NO_BLOCK=1"
        assert_contains "$c06_out" "CUSTOM_STAGE1_ARGS:--baked-stage=1 --baked-order=first --no-block"
        assert_not_contains "$c06_out" "Entrypoint branch: no-block exit"
    fi
}

run_custom_stage2_checks() {
    local image_both="$1"
    local image_stage1_fallback="$2"
    local both_key
    both_key="$(sanitize_name "$image_both")"
    local fallback_key
    fallback_key="$(sanitize_name "$image_stage1_fallback")"

    if case_enabled C03; then
        log "[$image_both] C03 stage-2 custom on_entry overrides stage-1"
        local c03_out
        c03_out="$(docker run --rm "$image_both" runtime-c03 2>&1)"
        save_log "${both_key}-C03-stage2-overrides" "$c03_out"
        assert_contains "$c03_out" "Entrypoint branch: custom on_entry wrapper (stage-2)"
        assert_contains "$c03_out" "CUSTOM_ENTRY_STAGE2"
        assert_contains "$c03_out" "CUSTOM_STAGE2_ARGS:--baked-stage=2 --baked-order=first runtime-c03"
        assert_not_contains "$c03_out" "CUSTOM_ENTRY_STAGE1"
    fi

    if case_enabled C04; then
        log "[$image_stage1_fallback] C04 stage-1 custom fallback on stage-2 image"
        local c04_out
        c04_out="$(docker run --rm "$image_stage1_fallback" runtime-c04 2>&1)"
        save_log "${fallback_key}-C04-stage1-fallback" "$c04_out"
        assert_contains "$c04_out" "Entrypoint branch: custom on_entry wrapper (stage-1)"
        assert_contains "$c04_out" "CUSTOM_ENTRY_STAGE1"
        assert_not_contains "$c04_out" "CUSTOM_ENTRY_STAGE2"
    fi
}

run_missing_custom_checks() {
    local image="$1"
    local image_key
    image_key="$(sanitize_name "$image")"

    if case_enabled C05; then
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
        assert_not_contains "$miss_out" "Entrypoint branch: no-block exit"
    fi
}

run_signal_check() {
    local image="$1"
    local stage_label="$2"
    local image_key
    image_key="$(sanitize_name "$image")"

    if ! case_enabled S01; then
        return 0
    fi

    log "[$image][$stage_label] S01 sleep fallback exits promptly on SIGTERM"
    local cid
    cid="$(docker run -d "$image")"
    register_container "$cid"
    sleep 3
    assert_running "$cid"

    local before_logs
    before_logs="$(container_logs "$cid")"
    save_log "${image_key}-S01-before-sigterm" "$before_logs"
    assert_contains "$before_logs" "Entrypoint branch: sleep fallback"

    assert_exits_after_sigterm "$cid" 20
    assert_stopped "$cid"

    local after_logs
    after_logs="$(container_logs "$cid")"
    save_log "${image_key}-S01-after-sigterm" "$after_logs"

    local exit_code
    exit_code="$(docker inspect -f '{{.State.ExitCode}}' "$cid")"
    save_log "${image_key}-S01-exit-code" "$exit_code"

    remove_container "$cid"
}

build_required_projects() {
    if any_case_enabled E01 E02 E03 E04 E05 E06 E07 S01; then
        log "Preparing and building base project"
        generate_and_build_stage2 "$PROJECT_BASE" "$BASE_CONFIG" none
        maybe_save_image_tar "$IMAGE_BASE_STAGE1"
        maybe_save_image_tar "$IMAGE_BASE_STAGE2"
    fi

    if any_case_enabled C01 C02 C04 C06; then
        log "Preparing and building stage-1 custom project"
        generate_and_build_stage2 "$PROJECT_CUSTOM_STAGE1" "$CUSTOM_STAGE1_CONFIG" stage1
        maybe_save_image_tar "$IMAGE_CUSTOM_STAGE1_STAGE1"
        maybe_save_image_tar "$IMAGE_CUSTOM_STAGE1_STAGE2"
    fi

    if any_case_enabled C03; then
        log "Preparing and building stage-1+stage-2 custom project"
        generate_and_build_stage2 "$PROJECT_CUSTOM_BOTH" "$CUSTOM_BOTH_CONFIG" both
        maybe_save_image_tar "$IMAGE_CUSTOM_BOTH_STAGE2"
    fi

    if any_case_enabled C05; then
        log "Preparing and building missing-custom-entry project"
        generate_and_build_stage2 "$PROJECT_MISSING" "$MISSING_CONFIG" none
        maybe_save_image_tar "$IMAGE_MISSING_STAGE2"
    fi
}

run_selected_cases() {
    if any_case_enabled E01 E02 E03 E04 E05 E06 E07; then
        run_default_mode_checks "$IMAGE_BASE_STAGE1" "stage-1"
        run_default_mode_checks "$IMAGE_BASE_STAGE2" "stage-2"
    fi

    if any_case_enabled C01 C02 C06; then
        run_custom_stage1_checks "$IMAGE_CUSTOM_STAGE1_STAGE1"
    fi

    if any_case_enabled C03 C04; then
        run_custom_stage2_checks "$IMAGE_CUSTOM_BOTH_STAGE2" "$IMAGE_CUSTOM_STAGE1_STAGE2"
    fi

    if any_case_enabled C05; then
        run_missing_custom_checks "$IMAGE_MISSING_STAGE2"
    fi

    if any_case_enabled S01; then
        run_signal_check "$IMAGE_BASE_STAGE1" "stage-1"
        run_signal_check "$IMAGE_BASE_STAGE2" "stage-2"
    fi
}

main() {
    SELECTED_CASES=("${ALL_CASES[@]}")
    parse_args "$@"

    require_cmd docker
    require_cmd ssh
    require_cmd sshpass
    ensure_python_cmd

    export PYTHONPATH="$REPO_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
    mkdir -p "$LOG_DIR" "$PROJECT_DIR" "$IMAGES_DIR"
    trap cleanup_registered_containers EXIT

    log "Selected cases: ${SELECTED_CASES[*]}"
    log "Artifacts root: $TMP_ROOT"

    build_required_projects
    run_selected_cases

    log "Functional checks completed successfully"
    log "Logs: $LOG_DIR"
    log "Projects: $PROJECT_DIR"
    log "Images (optional): $IMAGES_DIR"
}

main "$@"
