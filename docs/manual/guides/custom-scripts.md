# Custom Scripts

Custom scripts are the main extension point when the built-in config model is not enough.

## Where Scripts Live

Put your scripts under:

- `installation/stage-1/custom/`
- `installation/stage-2/custom/`

Reference them from `user_config.yml` with paths relative to `installation/`.

## Example

```yaml
stage_1:
  custom:
    on_build:
      - "stage-1/custom/setup-dev-tools.sh --verbose --mirror=tuna"
```

## Parameter Passing

Script entries are shell-like strings. PeiDocker preserves the argument text after the script path, so quoted values and `$VARS` inside arguments still work when the wrapper executes them.

## Build vs Runtime

- Use `on_build` for changes that belong in the image.
- Use `on_first_run` when the change needs runtime-only paths such as `/soft/...`.
- Use `on_user_login` when the script should affect the login shell.

## Logging

Generated wrappers print a banner when `PEI_ENTRYPOINT_VERBOSE=1` or when you pass `--verbose` to the default entrypoint mode. This helps when you are tracing startup behavior.

## Supporting Files

If a script depends on companion files, keep them inside the same `installation/` subtree so they are copied into the image with the rest of the project.

See [05 Custom Script](../../examples/basic/05-custom-script.md) for a minimal working example.
