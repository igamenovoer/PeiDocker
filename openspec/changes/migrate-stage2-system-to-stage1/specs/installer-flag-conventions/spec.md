## ADDED Requirements

### Requirement: Installers use explicit path flags where applicable
Installer scripts under `src/pei_docker/project_files/installation/stage-1/system/**` MUST prefer explicit, tool-specific path flags when they write outside a user’s home directory and when path selection materially affects behavior.

Common flags (when applicable):

- `--install-dir=PATH`: where the tool is installed
- `--cache-dir=PATH`: where caches/downloads are stored
- `--tmp-dir=PATH`: where temporary install artifacts are stored
- `--user <name>`: target user for user-scoped installs

#### Scenario: Caller controls storage visibility explicitly
- **WHEN** an installer needs to write into a non-default location (e.g., `/hard/image/...` during build)
- **THEN** the caller MUST be able to select that location via explicit flags (rather than the script probing `/soft/...`)

### Requirement: No implicit `/soft/*` behavior
Installers MUST NOT hardcode writes to `/soft/app`, `/soft/data`, or `/soft/workspace`, and MUST NOT probe `/soft/*` to infer stage or storage behavior.

#### Scenario: Script does not probe `/soft/*` to decide behavior
- **WHEN** an installer runs in a build-time context where `/soft/*` does not exist
- **THEN** it MUST still behave correctly (or fail only due to missing tool prerequisites), without probing `/soft/*`

### Requirement: Stage tmp dirs are optional and safe
If an installer uses a per-stage tmp/cache directory under `$PEI_STAGE_DIR_*/tmp`, it MUST follow these rules:

- If the script **writes** into the stage tmp dir, it MUST create it (`mkdir -p`) first.
- If the script **only reads** from the stage tmp dir, it MUST treat a missing dir as a cache miss and MUST NOT fail.

#### Scenario: Stage tmp dir missing during read-only access
- **WHEN** a script attempts to read from `$PEI_STAGE_DIR_1/tmp` (or `$PEI_STAGE_DIR_2/tmp`) and the directory does not exist
- **THEN** the script MUST continue without error and behave as if the cache is empty

#### Scenario: Script needs a stage tmp dir for writes
- **WHEN** a script needs to write temporary or cached artifacts into `$PEI_STAGE_DIR_1/tmp` (or `$PEI_STAGE_DIR_2/tmp`)
- **THEN** it MUST create the directory before writing and MUST fail only if the write itself fails

### Requirement: Migrated scripts do not depend on stage-2 tmp layout
When a script is migrated from stage-2 canonical to stage-1 canonical, any use of `$PEI_STAGE_DIR_2/tmp` for scratch/caching MUST be migrated to `$PEI_STAGE_DIR_1/tmp` (or be parameterized via `--tmp-dir`).

#### Scenario: A migrated installer previously used PEI_STAGE_DIR_2/tmp
- **WHEN** a migrated installer previously used `$PEI_STAGE_DIR_2/tmp` for caching/scratch
- **THEN** the stage-1 canonical version MUST use `$PEI_STAGE_DIR_1/tmp` (or a caller-provided `--tmp-dir`) instead
