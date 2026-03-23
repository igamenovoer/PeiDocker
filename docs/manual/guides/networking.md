# Networking

This guide focuses on the parts of PeiDocker that influence package download paths and external connectivity during build.

## APT Mirrors

Stage-1 supports special mirror keywords:

- `tuna`
- `aliyun`
- `163`
- `ustc`
- `cn`

Example:

```yaml
stage_1:
  apt:
    repo_source: tuna
    keep_repo_after_build: true
```

You can also point `repo_source` at a custom file under `installation/`.

## Mirror Persistence

- `keep_repo_after_build: true` keeps the modified APT source in the final image.
- `keep_repo_after_build: false` is better when the mirror is only a build accelerator.

## Proxy-Aware APT

APT proxy behavior is controlled separately from the general shell proxy:

```yaml
apt:
  use_proxy: true
  keep_proxy_after_build: false
```

## China-Friendly Pattern

For China-hosted development machines, the usual combination is:

- `repo_source: tuna` or `aliyun`
- Proxy settings only if your company network requires one
- Tool-specific mirrors such as Pixi or UV mirrors where available

See [13 APT Mirrors](../../examples/basic/13-apt-mirrors.md) and [China Corporate Proxy](../../examples/advanced/china-corporate-proxy.md).
