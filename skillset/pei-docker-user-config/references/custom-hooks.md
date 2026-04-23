# Custom Hooks Reference

## Source Files

- `docs/manual/concepts/script-lifecycle.md`
- `docs/manual/guides/custom-scripts.md`
- `docs/developer/entrypoint-system.md`
- `src/pei_docker/templates/config-template-full.yml`
- `src/pei_docker/examples/basic/custom-script/user_config.yml`
- `openspec/specs/entrypoint-default-runtime-behavior/spec.md`
- `openspec/specs/install-script-parameter-interface/spec.md`

## Hook Order

Lifecycle order:

1. `on_build`
2. `on_entry`
3. `on_first_run`
4. `on_every_run`
5. `on_user_login`

Use build hooks for image changes. Use runtime hooks for mounted storage or `/soft/...` paths.

## Script Placement

Put user-owned scripts under:

- `installation/stage-1/custom/`
- `installation/stage-2/custom/`

Reference them from `user_config.yml` with paths relative to `installation/`:

```yaml
stage_1:
  custom:
    on_build:
      - "stage-1/custom/setup-dev-tools.sh --mirror=tuna"
```

Script entries can include arguments and quoted values. Preserve existing quoting when editing.

## Hook Selection

| Need | Hook |
| --- | --- |
| Install packages into image | `on_build` |
| Initialize runtime storage once | `on_first_run` |
| Reapply startup setup | `on_every_run` |
| Affect SSH login shell | `on_user_login` |
| Replace default entry behavior | `on_entry` |

`on_user_login` scripts are sourced, so they can modify the login shell environment. `on_entry` accepts one script entry per stage and stage-2 overrides stage-1 when both exist.

## Debugging

Generated wrappers live under `installation/stage-*/generated/`. Inspect them to understand generated behavior, but make durable edits in `user_config.yml` or source scripts.
