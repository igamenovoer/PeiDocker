# Integration Guide: storage-agnostic-install-scripts

**Change**: `storage-agnostic-install-scripts` | **Groups**: 6

## Overview

This change makes “installer scripts” usable in both build-time and runtime contexts by:

- preserving custom script argument text (so `$VARS` expand at execution time), and
- enforcing a lifecycle rule: build-time (`stage_2.custom.on_build`) must not reference runtime-only storage paths (`/soft/...`, `/hard/volume/...`).

It also establishes the pattern “stage-1 is canonical, stage-2 forwards” for the first migrated installer batch (Pixi + Conda).

## Group Flow

**MUST HAVE: End-to-End Sequence Diagram**

```mermaid
sequenceDiagram
    participant UC as user_config.yml<br/>(custom hooks)
    participant CP as PeiConfigProcessor<br/>(Python)
    participant WR as _custom-on-*.sh<br/>(generated)
    participant DK as docker build<br/>(stage-2)
    participant S2 as stage-2/system<br/>(wrapper)
    participant S1 as stage-1/system<br/>(canonical)

    UC->>CP: configure
    CP->>CP: validate stage_2.custom.on_build
    CP->>WR: render wrappers<br/>preserve $VARS

    alt build-time hook
        DK->>WR: RUN _custom-on-build.sh
        WR->>S2: bash stage-2/system/...<br/>(flags)
        S2->>S1: exec stage-1/system/...<br/>(forward "$@")
        S1-->>DK: writes /hard/image/...
    else runtime hook
        WR->>S1: bash stage-1/system/...<br/>(flags with /soft/...)
        S1-->>WR: runs after /soft links exist
    end
```

## Artifact Flow Between Groups

```mermaid
graph TD
    subgraph G1["Group 1: Inventory and conventions"]
        G1D1[installation/README.md];
    end

    subgraph G2["Group 2: Custom script args"]
        G2C1[src/pei_docker/config_processor.py];
        G2T1[tests/test_custom_script_args.py];
    end

    subgraph G3["Group 3: on_build validation"]
        G3C1[src/pei_docker/config_processor.py];
        G3T1[tests/test_on_build_path_validation.py];
    end

    subgraph G4["Group 4: Stage-1 canonical installers"]
        G4S1[stage-1/system/pixi scripts];
        G4S2[stage-1/system/conda scripts];
        G4W1[stage-2/system/pixi wrappers];
        G4W2[stage-2/system/conda wrappers];
    end

    subgraph G5["Group 5: Merged build docs"]
        G5D1[docs/index.md];
        G5D2[docs/cli_reference.md];
    end

    subgraph G6["Group 6: Verification"]
        G6X1[tests/configs/storage-agnostic-install-flow.yml];
    end

    G1D1 -.->|defines conventions| G4S1;
    G1D1 -.->|defines conventions| G4S2;

    G2C1 --> G3C1;
    G2T1 -.->|covers| G2C1;
    G3T1 -.->|covers| G3C1;

    G4W1 --> G4S1;
    G4W2 --> G4S2;

    G3C1 -.->|enables safe CI example| G5D1;
    G4S1 -.->|document usage| G5D1;
    G4S2 -.->|document usage| G5D1;

    G6X1 -.->|smoke config| G5D1;
```

## System Architecture

```mermaid
classDiagram
    class UserConfig

    class PeiConfigProcessor {
        +process
        -_parse_script_entry
        -_generate_script_text
        -_validate_stage2_on_build_script_entries
    }

    class Stage2CustomWrappers
    class Stage2SystemWrappers
    class Stage1SystemInstallers
    class MergedBuildArtifacts

    UserConfig --> PeiConfigProcessor : structured input
    PeiConfigProcessor --> Stage2CustomWrappers : generates
    Stage2SystemWrappers --> Stage1SystemInstallers : forwards
    PeiConfigProcessor --> MergedBuildArtifacts : optional output
```

## Use Cases

```mermaid
graph LR
    Actor((User));

    UC1[Run build-time installs<br/>on_build with /hard/image];
    UC2[Run runtime installs<br/>on_first_run with /soft];
    UC3[Build via merged.Dockerfile<br/>single docker build];

    Actor --> UC1;
    Actor --> UC2;
    Actor --> UC3;
```

## Activity Flow

```mermaid
stateDiagram-v2
    [*] --> Configure
    Configure --> ValidateOnBuild : parse user_config
    ValidateOnBuild --> Fail : runtime-only token found
    ValidateOnBuild --> GenerateWrappers : ok
    GenerateWrappers --> Build : docker build or compose build
    Build --> RuntimeStart : container start creates /soft links
    RuntimeStart --> RuntimeHooks : first-run / login hooks
    RuntimeHooks --> [*]
    Fail --> [*]
```

## Inter-Group Dependencies

### Group 2 → Group 3

**Dependency**: Group 3 relies on Group 2’s “raw args text” handling so validation and wrapper rendering remain consistent and do not re-tokenize user strings.

**Code**:

```python
# src/pei_docker/config_processor.py
#
# - Group 2: _parse_script_entry() and wrapper rendering preserve args text
# - Group 3: _validate_stage2_on_build_script_entries() rejects runtime-only tokens
```

### Group 4 → Groups 5 and 6

**Artifacts**:
- `src/pei_docker/project_files/installation/stage-1/system/pixi/README.md` provides canonical usage guidance.
- `tests/configs/storage-agnostic-install-flow.yml` demonstrates referencing stage-1 canonical scripts from stage-2 hooks.

## Integration Testing

```bash
# Unit checks (fast)
pixi run pytest -q

# Optional Docker smoke (requires Docker)
pixi run pei-docker-cli create -p <tmp-project>
cp tests/configs/storage-agnostic-install-flow.yml <tmp-project>/user_config.yml
pixi run pei-docker-cli configure -p <tmp-project>
docker compose -f <tmp-project>/docker-compose.yml build stage-2
```

## Critical Integration Points

1. **Wrapper arg forwarding**: wrapper scripts must not rewrite `$VARS` into single quotes.
2. **Build-time path validation**: `stage_2.custom.on_build` must fail fast on `/soft/...`, `/hard/volume/...`, `$PEI_SOFT_*`, `$PEI_PATH_SOFT`.
3. **Stage forwarding**: stage-2 system paths remain callable but forward to stage-1 canonical via `$PEI_STAGE_DIR_1`.

## References

- Proposal: `openspec/changes/storage-agnostic-install-scripts/proposal.md`
- Design: `openspec/changes/storage-agnostic-install-scripts/design.md`
- Tasks: `openspec/changes/storage-agnostic-install-scripts/tasks.md`
- Specs: `openspec/changes/storage-agnostic-install-scripts/specs/`
- Group guides: `openspec/changes/storage-agnostic-install-scripts/impl-guides/grp*.md`

## Implementation Summary

The implementation centers on `PeiConfigProcessor` generating lifecycle wrapper
scripts that preserve custom args text while enforcing the build-time lifecycle
constraints. Pixi + Conda were migrated to stage-1 canonical implementations,
with stage-2 system paths converted into thin wrappers.

### What has been implemented

- Wrapper arg passthrough:
  - `src/pei_docker/config_processor.py` (`_parse_script_entry`, `_generate_script_text`)
  - `tests/test_custom_script_args.py`
- Build-time validation:
  - `src/pei_docker/config_processor.py` (`_validate_stage2_on_build_script_entries`)
  - `tests/test_on_build_path_validation.py`
- Stage-1 canonical installers + stage-2 forwarders:
  - Pixi: `src/pei_docker/project_files/installation/stage-1/system/pixi/*`
  - Conda: `src/pei_docker/project_files/installation/stage-1/system/conda/*`
  - Forwarders: `src/pei_docker/project_files/installation/stage-2/system/{pixi,conda}/*`
- Merged build docs:
  - `docs/index.md`, `docs/cli_reference.md`

### How to verify

- `pixi run pytest -q`
- Optional: run the Docker smoke flow in “Integration Testing” above.
