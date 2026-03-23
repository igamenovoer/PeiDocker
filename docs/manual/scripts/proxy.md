# Proxy

The proxy helper scripts are simple but useful when you want an explicit shell-level proxy toggle in custom workflows.

## Scripts

| Script | Purpose |
| --- | --- |
| `enable-pei-proxy.sh` | Export `http_proxy`, `https_proxy`, and uppercase variants from PeiDocker-generated proxy vars |
| `disable-pei-proxy.sh` | Unset those proxy variables |

## When To Use Them

- In a custom build script that needs to control proxy usage manually
- In a runtime hook where you want explicit enable/disable boundaries

## Relationship To Config

Most users should prefer the config-driven `proxy:` and `apt.use_proxy` fields. Reach for these helpers only when a tool needs proxy control at a specific point in a longer shell workflow.
