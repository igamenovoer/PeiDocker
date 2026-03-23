# Proxy Configuration

PeiDocker separates proxy transport details from how broadly the proxy is applied.

## Core Fields

```yaml
proxy:
  address: host.docker.internal
  port: 7890
  enable_globally: true
  remove_after_build: false
  use_https: false
```

## What Each Field Does

| Field | Effect |
| --- | --- |
| `address` + `port` | Builds the proxy URL |
| `enable_globally` | Exports `http_proxy` and `https_proxy` inside the image |
| `remove_after_build` | Removes the global proxy after build if enabled |
| `use_https` | Switches the generated URL scheme to `https://` |

## `host.docker.internal`

`host.docker.internal` is the simplest way to point the container back to a proxy running on the host. It keeps the config portable across developer machines where the host IP changes.

## APT Integration

APT proxy behavior is separate:

```yaml
apt:
  use_proxy: true
  keep_proxy_after_build: false
```

This writes APT-specific proxy config during the build, even if you do not want the proxy exported globally.

## Stage Inheritance

Stage-2 can override stage-1 proxy behavior. Leave stage-2 proxy fields unset when you want stage-1 defaults to carry through.

## Good Default Pattern

- Build needs proxy, runtime does not: `enable_globally: true`, `remove_after_build: true`
- Build and runtime both need proxy: `enable_globally: true`, `remove_after_build: false`

See [07 Proxy Setup](../../examples/basic/07-proxy-setup.md) and [China Corporate Proxy](../../examples/advanced/china-corporate-proxy.md).
