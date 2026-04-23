# Networking, Proxy, APT, And Ports Reference

## Source Files

- `docs/manual/guides/port-mapping.md`
- `docs/manual/guides/proxy-configuration.md`
- `docs/manual/guides/networking.md`
- `src/pei_docker/examples/basic/port-mapping/user_config.yml`
- `src/pei_docker/examples/basic/proxy-setup/user_config.yml`
- `src/pei_docker/examples/basic/apt-mirrors/user_config.yml`
- `src/pei_docker/examples/advanced/china-corporate-proxy/user_config.yml`
- `openspec/specs/port-mapping-string-model/spec.md`

## Ports

Use string-shaped Docker Compose port mappings:

```yaml
stage_1:
  ports:
    - "6006:6006"

stage_2:
  ports:
    - "8080:80"
    - "3000-3002:3000-3002"
```

Use `stage_1.ports` for system services and `stage_2.ports` for app services. Stage-2 receives stage-1 mappings plus its own. SSH host mapping is added separately from `stage_1.ssh.host_port`.

## Proxy

Core shape:

```yaml
stage_1:
  proxy:
    address: host.docker.internal
    port: 7890
    enable_globally: true
    remove_after_build: true
    use_https: false
```

Use `host.docker.internal` when the proxy runs on the host. Use `remove_after_build: true` when only the build needs proxy env vars. Use `false` when runtime shells should keep proxy vars.

Stage-2 can override stage-1 proxy fields. Leave stage-2 fields unset or null to inherit.

## APT Mirrors And APT Proxy

Known mirror keywords:

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
    use_proxy: true
    keep_proxy_after_build: false
```

APT proxy is separate from global shell proxy.

## Restricted Networks

For China or corporate networks, combine:

- an APT mirror such as `tuna` or `aliyun`
- proxy config only if required by the network
- tool-specific mirrors in utility scripts such as Pixi, Conda, or UV when available
