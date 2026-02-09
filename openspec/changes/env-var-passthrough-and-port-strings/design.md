## Context

PeiDocker currently performs config-time environment variable substitution on `user_config.yml` by expanding `${VAR}` and `${VAR:-default}` before generating `docker-compose.yml`. This makes configs flexible at configuration time, but it prevents users from deferring variable resolution to `docker compose` runtime (host env / `.env`) without re-running `pei-docker-cli configure`.

Additionally, parts of configuration processing treat ports as numeric (convert to int dict, merge, then compress), which prevents port mappings from containing placeholders (either `${...}` or the new `{{...}}` markers) and blocks passthrough use cases in port mappings.

Constraints:
- Must support both modes simultaneously:
  - **Config-time substitution** (expand during `configure`)
  - **Compose-time passthrough** (preserve placeholders into generated compose)
- Passthrough syntax is limited to `{{VAR}}` and `{{VAR:-default}}` (no `?` / `:?` forms).
- Avoid conflicts with OmegaConf interpolation and the existing config processing pipeline.

## Testing Conventions

- For end-to-end tests that build images on this host, use `ubuntu:24.04` as the base image.
- For any temporary test projects / generated artifacts, use a workspace-relative directory under `tmp/<subdir>` (example: `tmp/env-var-passthrough-and-port-strings-test/`).
- Due to networking issues, for any download-related testing (APT, Pixi/Conda installers, etc.), either:
  - use a China-based mirror, or
  - use the host proxy at `127.0.0.1:7890`.

## Goals / Non-Goals

**Goals:**
- Define a passthrough marker syntax that is safe in PeiDocker’s YAML parsing pipeline and produces standard Docker Compose `${...}` placeholders in generated compose artifacts.
- Preserve existing `${VAR}` / `${VAR:-default}` config-time substitution behavior for users who want “configure once with concrete values”.
- Change port mapping handling to be string-based so port mappings can include passthrough markers and be emitted safely.
- Provide clear documentation/examples distinguishing config-time vs compose-time resolution.

**Non-Goals:**
- Supporting Compose error/required forms like `${VAR?err}` / `${VAR:?err}`.
- Implementing a general-purpose templating engine for all generated artifacts.
- Guaranteeing passthrough markers work in non-compose artifacts (e.g., `merged.env`, internal `.sh` scripts) unless explicitly handled.

## Decisions

### Decision: Use `{{...}}` markers as an opaque passthrough syntax

We treat `{{VAR}}` and `{{VAR:-default}}` as “opaque placeholders” that:
- MUST NOT be expanded during config parsing/substitution
- MUST survive through OmegaConf/cattrs processing as plain strings
- MUST be translated to Docker Compose placeholders `${VAR}` / `${VAR:-default}` only at the final emission step for compose-consumed outputs

Rationale:
- Avoids OmegaConf interpolation conflicts (`${...}` is treated as OmegaConf interpolation and will error if unresolved).
- Does not require parsing Compose `${...}` grammar; PeiDocker only needs to transform delimiters (`{{`→`${`, `}}`→`}`) under strict validation.

Alternatives considered:
- `${pass.VAR}` style markers: requires editing inside `${...}` and careful tokenization; higher risk of conflicting with OmegaConf.
- Escaping `${...}` via backslashes: unclear cross-platform behavior, YAML quoting pitfalls, and still risks OmegaConf parsing.

### Decision: Reject leftover `${...}` after config-time substitution

After running config-time substitution, the resulting user config MUST NOT contain any `${...}` sequences. If any remain, PeiDocker MUST fail with a clear error telling users to either:

- set the env var at configure time (so `${...}` can be expanded), or
- use `{{...}}` for compose-time passthrough.

Rationale:
- Remaining `${...}` will be interpreted as OmegaConf interpolation later and typically fails with an interpolation error.
- This rule creates a crisp distinction: `${...}` is configure-time only; `{{...}}` is compose-time only.

### Decision: Perform passthrough rewrite after OmegaConf resolution (one-way path)

Implementation approach:
- Treat OmegaConf resolution as a **one-way** pipeline: perform all OmegaConf template resolution first.
- Keep the in-memory `DictConfig` / `out_compose` representation using `{{...}}` strings through processing.
- At the final step, convert the fully-resolved compose output into a **plain Python container** (`dict`/`list`) and tree-walk rewrite passthrough markers:
  - Replace `{{VAR}}` → `${VAR}`
  - Replace `{{VAR:-default}}` → `${VAR:-default}`
  - Reject malformed patterns (anything not matching the supported forms).
- Emit YAML from the rewritten plain container (do not reintroduce `${...}` into a `DictConfig` that might be resolved again).

Rationale:
- Avoids placing `${...}` inside OmegaConf structures (where it is interpolation syntax).
- Ensures the final output is valid Docker Compose syntax while keeping implementation structured.

Edge cases & rules:
- Validate variable names (`VAR`) with `[A-Za-z_][A-Za-z0-9_]*` and allow whitespace inside braces (trim during parsing).
- Defaults are treated opaquely (no PeiDocker validation beyond structural parsing); disallow `}}` inside defaults.
- Due to the “no leftover `${...}`” rule (OmegaConf interpolation safety), defaults MUST NOT contain `${...}` tokens anywhere in the user config.
- Prefer error over silent passthrough for malformed patterns.

### Decision: Move port mapping model to strings (BREAKING)

Ports are currently merged via int parsing; this breaks when port entries contain placeholders.

New model:
- Treat `stage_1.ports` and `stage_2.ports` as ordered lists of **strings** (Docker Compose `ports:` entries).
- Composition rule:
  - Stage-2 effective ports = stage-1 ports (if any) + stage-2 ports (if any) + SSH mapping (if configured)
- Optional best-effort validation:
  - If a port entry is fully numeric, we MAY detect duplicates and warn.
  - If a port entry contains placeholders, do not attempt numeric parsing.

Rationale:
- Enables passthrough markers in port mappings without requiring special escape hatches.
- Keeps user mental model aligned with Docker Compose.

Alternatives considered:
- Two fields (`ports` numeric + `ports_raw`): avoids breaking changes but increases schema complexity and user confusion.
- Hybrid parser (parse if numeric else passthrough): possible, but still complicates merge logic; string-first is simpler and supports future placeholder use.

### Decision: Clarify passthrough scope (compose-only initially)

Supported (initial scope):
- Any string that ends up in generated `docker-compose.yml` (e.g., image names, build args values, service environment values, volume host paths, ports entries).

Not guaranteed / out of scope (initial):
- Host-side helper scripts that invoke `docker run` (currently produced via the merged-build flow). If/when we want passthrough there, it must be explicitly implemented for those scripts.
- PeiDocker internal `.sh` scripts and non-compose artifacts where Docker Compose does not perform interpolation.
- `merged.env` / merged build flow outputs (not interpreted by docker compose).

Enforcement:
- Error if `--with-merged` is requested while any passthrough markers are present (merged artifacts out of scope initially).
- Reject passthrough markers in any configuration values that are written directly into `installation/stage-{1,2}/internals/**` (or other generated scripts/files) without Docker Compose substitution, or that must be baked into generated scripts during `configure`.
- `_etc_environment.sh` is always generated, but it is only *used* when baking is enabled. Therefore:
  - allow `{{...}}` in `stage_?.environment` generally (because it becomes compose env),
  - but error if baking is requested (`PEI_BAKE_ENV_STAGE_*` is true) and any passthrough markers would be written into `/etc/environment`.

### Decision: Typed fields and validation responsibility

If a compose-emitted field contains passthrough markers, PeiDocker treats it as an opaque string and does not attempt to validate its final value. Any errors from Docker Compose interpolation or downstream build/runtime behavior are considered user responsibility.

If a value is consumed directly by internal scripts/files without Docker Compose substitution (or is baked into a generated script during `configure`), passthrough markers are rejected (because nothing will expand them).

Note: for values used during image build, Docker Compose resolves variables at build invocation time; changing the host env later typically requires a rebuild to take effect.

## Risks / Trade-offs

- [Risk] Users confuse `${...}` vs `{{...}}` semantics → Mitigation: docs/examples; emit clear errors when `${VAR}` is left unresolved at configure time.
- [Risk] Port merge behavior changes and may allow duplicates that Compose rejects → Mitigation: best-effort numeric duplicate detection + warnings; document that Compose is source of truth.
- [Risk] Passthrough markers leaking into non-compose artifacts and behaving unexpectedly → Mitigation: define supported contexts; add validation in generation paths that write non-compose outputs.
- [Risk] Placeholder validation too strict/too loose → Mitigation: restrict to the two supported forms and keep validation explicit; add tests for transformation behavior.
- [Risk] YAML quoting / Windows paths in defaults → Mitigation: document best practices (prefer forward slashes; escape backslashes if needed) and add tests for common Windows path defaults.
