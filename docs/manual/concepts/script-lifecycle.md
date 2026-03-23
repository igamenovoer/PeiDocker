# Script Lifecycle

PeiDocker does most customization through shell hooks. Knowing when each hook runs is more important than memorizing the filenames.

## Order

1. `on_build`
2. `on_entry`
3. `on_first_run`
4. `on_every_run`
5. `on_user_login`

## Hook Meanings

| Hook | When it runs | Best for |
| --- | --- | --- |
| `on_build` | During `docker build` | Installing packages, writing files into the image |
| `on_entry` | PID 1 handoff on container start | Replacing the default entry behavior |
| `on_first_run` | First container startup only | One-time initialization |
| `on_every_run` | Every container startup | Reapplying runtime setup |
| `on_user_login` | When a user logs in via SSH | Shell environment tweaks |

## Constraints

- `on_build` cannot rely on `/soft/...` or mounted volumes in stage-2.
- `on_user_login` scripts are sourced, not executed with `bash`, so they can modify the login shell environment.
- `on_entry` is limited to one script per stage.
- Script entries may include arguments such as `stage-1/custom/setup.sh --mode=dev`.

## Execution Context

Generated wrapper scripts live under `installation/stage-*/generated/`. Those wrappers call your listed script paths relative to the installation directory. You edit the source script, not the generated wrapper.

## Rule Of Thumb

- Build-time change: `on_build`
- First boot initialization: `on_first_run`
- Repeatable startup fixup: `on_every_run`
- Per-user shell customization: `on_user_login`
- Full startup override: `on_entry`
