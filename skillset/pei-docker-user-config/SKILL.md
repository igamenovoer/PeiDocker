---
name: pei-docker-user-config
description: Guidance for authoring PeiDocker user_config.yml files. Use when Codex needs to create or modify PeiDocker YAML for stages, images, SSH, ports, proxy, APT, environment variables, storage, mounts, devices, or lifecycle custom hooks.
---

# PeiDocker User Config

## Working Rules

Use this skill for `user_config.yml` authoring. For CLI project creation use `$pei-docker-cli-workflow`; for built-in installer scripts use `$pei-docker-utility-scripts`; for running an already configured project use `$pei-docker-run-project`.

Before inventing YAML, consult the narrowest relevant source:

- Full schema shape: `src/pei_docker/templates/config-template-full.yml`
- Quick templates: `src/pei_docker/templates/quick/*.yml`
- Packaged examples: `src/pei_docker/examples/**/user_config.yml`
- User docs: `docs/manual/concepts/*`, `docs/manual/guides/*`
- Contracts: `openspec/specs/*/spec.md` for env, ports, mounts, scripts, and installers

Preserve user-owned values. Do not replace a whole config when a focused YAML edit is enough.

## Reference Routing

Read only the reference files needed for the user's task:

| Task | Reference |
| --- | --- |
| Stage selection, image base/output, devices | `references/stage-image.md` |
| SSH users, auth, keys, UID/GID | `references/ssh-access.md` |
| `stage_2.storage`, `mount`, `/soft`, `/hard` | `references/storage-and-mounts.md` |
| Ports, proxy, APT mirrors, China/corporate network setup | `references/networking-proxy-apt-ports.md` |
| `${VAR}` and `{{VAR}}` semantics | `references/environment-variables.md` |
| Custom lifecycle hooks and script placement | `references/custom-hooks.md` |

## Authoring Workflow

1. Identify the target project root and config file.
2. Read the existing `user_config.yml`.
3. Read the relevant reference file and source docs/templates listed there.
4. Make the smallest YAML edit that satisfies the user request.
5. Validate with `pei-docker-cli configure` when feasible.

## Common Boundaries

- SSH belongs in `stage_1.ssh`.
- `stage_2.storage` accepts only `app`, `data`, and `workspace`.
- Extra `mount` entries need explicit absolute `dst_path` values.
- Stage-2 inherits the stage-1 image output as its base when `stage_2.image.base` is omitted.
- Stage-2 receives stage-1 port mappings plus its own additional ports.
- Runtime-only paths such as `/soft/...` do not exist during stage-2 `on_build`.
- Compose-time passthrough markers `{{...}}` are limited to compose-emitted values and are incompatible with merged build.

## Validation

After meaningful edits, prefer:

```bash
pei-docker-cli configure -p <project-dir>
```

If validation fails, inspect the error and adjust `user_config.yml` or custom source scripts. Do not hand-edit generated wrappers as the durable fix.
