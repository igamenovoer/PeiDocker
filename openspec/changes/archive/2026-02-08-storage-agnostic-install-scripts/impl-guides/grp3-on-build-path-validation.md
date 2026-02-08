# Implementation Guide: on_build Path Validation

**Group**: 3 | **Change**: storage-agnostic-install-scripts | **Tasks**: [3.1]–[3.3]

## Goal

Reject stage-2 build-time custom scripts (`stage_2.custom.on_build`) that pass runtime-only storage paths (or soft-path env var tokens) in their arguments, because `/soft/*` symlinks and mounted volumes are not available during `docker build`.

## Public APIs

### Task 3.1: Validate stage-2 `custom.on_build` script arguments

Add an explicit validation step in `src/pei_docker/config_processor.py` that runs after `UserConfig` is structured (via `cattrs`) and before scripts/compose are generated.

Implemented helper API (Python):

```python
# src/pei_docker/config_processor.py

from __future__ import annotations

class PeiConfigProcessor:
    @staticmethod
    def _validate_stage2_on_build_script_entries(script_entries: list[str]) -> None:
        """Reject runtime-only storage paths in stage-2 build-time custom scripts."""
        ...
```

Notes:

- Validate only stage-2 `on_build` (runtime hooks may still use `/soft/...`).
- Prefer pointing users to `/hard/image/...` for build-time installs.

### Task 3.2: Unit tests for validator behavior

Add tests that:

- accept: `/hard/image/...`, `/opt/...`, `/usr/local/...`
- reject: `/soft/...`, `/hard/volume/...`, `$PEI_SOFT_DATA`, `$PEI_PATH_SOFT`

### Task 3.3: Improve user-facing error/help text

Where errors surface (CLI / logs), include the lifecycle rule:

- Build-time: use in-image paths (typically `/hard/image/...`)
- Runtime: `/soft/...` is allowed

**Usage Flow**:

```mermaid
sequenceDiagram
    participant UC as user_config.yml<br/>(stage_2.custom)
    participant CP as PeiConfigProcessor<br/>(Python)
    participant ER as Error<br/>(ValueError)

    UC->>CP: parse and structure config
    CP->>CP: validate stage-2 on_build entries
    alt runtime-only token found
        CP-->>ER: raise with offending entry
    else valid
        CP->>CP: generate wrapper scripts
    end
```

**Pseudocode**:

```text
if stage_2.custom.on_build contains:
  - "/soft/"
  - "/hard/volume/"
  - "$PEI_SOFT_*" tokens
  - "$PEI_PATH_SOFT"
then:
  fail fast with a clear error
```

---

## Group Integration

```mermaid
graph LR
  T21[Task 2.1: Preserve args text] --> T31[Task 3.1: Validation];
  T31 --> T32[Task 3.2: Tests];
  T31 --> T41[Task 4.1: Stage-1 installers];
```

## Testing

### Test Input

- Minimal structured configs for stage-2 `custom.on_build`:
  - valid entries using `/hard/image/...`
  - invalid entries using `/soft/...`, `/hard/volume/...`, `$PEI_SOFT_DATA`, `$PEI_PATH_SOFT`

### Test Procedure

```bash
pixi run pytest -q tests/test_on_build_path_validation.py
```

### Test Output

- Valid configs pass without error
- Invalid configs fail during configuration parsing with a message that:
  - includes the offending entry
  - explains why `/soft` is unavailable during build

## References

- Proposal: `openspec/changes/storage-agnostic-install-scripts/proposal.md`
- Design: `openspec/changes/storage-agnostic-install-scripts/design.md`
- Specs:
  - `openspec/changes/storage-agnostic-install-scripts/specs/stage2-wrapper-forwarding/spec.md`
  - `openspec/changes/storage-agnostic-install-scripts/specs/single-dockerfile-ci-install-flow/spec.md`

## Implementation Summary

Stage-2 build-time scripts are now validated to reject runtime-only storage paths
early (during config processing), with an actionable error message pointing to
the offending entry.

### What has been implemented

- Implemented `PeiConfigProcessor._validate_stage2_on_build_script_entries()` in
  `src/pei_docker/config_processor.py`.
- Invoked that validator from `PeiConfigProcessor.process()` before wrapper/compose generation.
- Validator rejects these tokens in `stage_2.custom.on_build` entries:
  - `/soft/...`
  - `/hard/volume/...`
  - `$PEI_SOFT_*` / `${PEI_SOFT_*`
  - `$PEI_PATH_SOFT` / `${PEI_PATH_SOFT`
- Added unit coverage in `tests/test_on_build_path_validation.py`.

### How to verify

- Run the unit tests:
  - `pixi run pytest -q tests/test_on_build_path_validation.py`
- Sanity check with an intentionally bad config:
  - set `stage_2.custom.on_build` to include `/soft/...`
  - run `pei-docker-cli configure` and confirm it fails fast with the lifecycle hint
