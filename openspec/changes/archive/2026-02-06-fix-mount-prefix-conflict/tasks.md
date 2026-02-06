## 1. Config Model & Validation

- [x] 1.1 Add validation for mount entries to require absolute `dst_path`
- [x] 1.2 Detect duplicate mount keys during config parsing and raise a clear error

## 2. Compose Resolution Changes

- [x] 2.1 Separate storage vs mount resolution paths so storage prefixes never override mount `dst_path`
- [x] 2.2 Emit `logging.warning` when multiple entries resolve to the same container destination path (simple string match)

## 3. Tests & Docs

- [x] 3.1 Add tests for mount `dst_path` requirement, duplicate mount keys, and name collision behavior
- [x] 3.2 Add tests for warning-only destination conflicts
- [x] 3.3 Update documentation/examples to clarify storage keywords, mount `dst_path` requirement, and warning behavior

## Implementation Summary

- Added config validation in `StageConfig.__attrs_post_init__`:
- Storage keys are restricted to `app`, `data`, `workspace` (`src/pei_docker/user_config/stage.py`).
- Mount entries require an explicit absolute container `dst_path` starting with `/` (`src/pei_docker/user_config/stage.py`).
- Added YAML duplicate-key detection (rejects duplicate keys instead of silently taking the last value) and wired it into config loading:
- `load_yaml_file_with_duplicate_key_check` in `src/pei_docker/pei_utils.py`.
- Used by CLI configure path in `src/pei_docker/pei.py` and by `PeiConfigProcessor.from_files` in `src/pei_docker/config_processor.py`.
- Refactored compose volume generation to avoid name collisions between `storage` keywords and `mount` keys:
- `storage` entries keep using fixed keywords and map to `/hard/volume/<keyword>`.
- `mount` entries always honor explicit `dst_path` and use namespaced compose volume keys `mount_<name>` so mount names can safely be `app|data|workspace` (`src/pei_docker/config_processor.py`).
- Implemented best-effort warnings (no blocking) when multiple mappings target the same container destination path (simple string match) using `logging.warning` (`src/pei_docker/config_processor.py`).
- Added pytest coverage for the mount/storage resolution behavior and duplicate-key detection in `tests/test_mount_path_resolution.py`.
- Updated docs/templates to document fixed storage keywords, required mount `dst_path`, and warning-only behavior:
- `src/pei_docker/templates/config-template-full.yml`
- `docs/index.md`
- `docs/examples/basic.md`
