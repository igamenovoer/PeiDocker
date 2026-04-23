# Proxy Helpers Reference

## Source Files

- `docs/manual/scripts/proxy.md`
- `docs/manual/guides/proxy-configuration.md`
- `src/pei_docker/examples/basic/proxy-setup/user_config.yml`
- `src/pei_docker/examples/advanced/china-corporate-proxy/user_config.yml`

## Scripts

Canonical path: `stage-1/system/proxy/`.

Scripts:

- `enable-pei-proxy.sh`
- `disable-pei-proxy.sh`

These export or unset shell proxy variables based on PeiDocker-generated proxy values.

## When To Use

Prefer config-level `proxy:` and `apt.use_proxy` for most projects. Use proxy helper scripts when a longer custom workflow needs explicit proxy boundaries around one command group.

Example:

```yaml
stage_1:
  custom:
    on_build:
      - "stage-1/system/proxy/enable-pei-proxy.sh"
      - "stage-1/custom/download-with-proxy.sh"
      - "stage-1/system/proxy/disable-pei-proxy.sh"
```

Check whether the runtime needs proxy vars before leaving global proxy enabled in the final image.
