# Contracts

PeiDocker’s behavior is increasingly documented as explicit OpenSpec contracts. This page points to the most important ones for contributors.

## Core Contract Areas

| Contract | What it covers |
| --- | --- |
| `config-env-substitution-semantics` | `${VAR}` behavior during `configure` |
| `compose-env-passthrough-markers` | `{{VAR}}` behavior for compose-emitted fields |
| `mount-path-resolution` | fixed storage keys and explicit mount destinations |
| `port-mapping-string-model` | string-shaped port mappings and inheritance |
| `entrypoint-default-runtime-behavior` | default runtime modes, `--no-block`, verbose mode, custom `on_entry` |
| `install-script-parameter-interface` | explicit flags for installer scripts |
| `installer-flag-conventions` | storage-agnostic installer behavior |
| `stage1-system-canonical-installers` | stage-1 as the preferred installer location |
| `stage2-system-wrapper-policy` | thin forwarding wrappers in stage-2 |

## Where The Contracts Live

- Active repository-wide specs: `openspec/specs/*/spec.md`
- Change-specific docs rewrite specs: `openspec/changes/rewrite-docs-structure/specs/*/spec.md`

## Practical Contribution Rules

- Prefer `stage-1/system/*` paths in user-facing examples and docs.
- Keep stage-2 wrappers thin and argument-preserving.
- Do not reintroduce implicit `/soft/*` assumptions into installer scripts.
- Treat passthrough markers as compose-only behavior unless a spec explicitly says otherwise.

## Wrapper Policy

Stage-2 wrappers are meant to add only minimal glue:

- locate the stage-1 canonical script
- preserve arguments verbatim
- fail clearly when `PEI_STAGE_DIR_1` is unavailable

If you find business logic accumulating in a wrapper, it probably belongs in the canonical stage-1 script instead.
