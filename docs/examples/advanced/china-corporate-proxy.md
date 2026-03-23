# China Corporate Proxy

Use this when you need both a company proxy and China-friendly package mirrors.

Source: `examples/advanced/china-corporate-proxy/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-cn-proxy:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2238
    users:
      dev:
        password: "123456"
  proxy:
    address: host.docker.internal
    port: "${PROXY_PORT:-7890}"
    enable_globally: true
    remove_after_build: false
    use_https: false
  apt:
    repo_source: tuna
    use_proxy: true
    keep_proxy_after_build: true

stage_2:
  image:
    output: pei-example-cn-proxy:stage-2
  proxy:
    enable_globally: true
  storage:
    app:
      type: image
    data:
      type: auto-volume
    workspace:
      type: auto-volume
  custom:
    on_build:
      - "stage-1/system/uv/install-uv.sh --user dev --pypi-repo tuna"
```

Why it works:

- stage-1 handles the build network path and APT mirror
- stage-2 keeps the shell proxy enabled for the final runtime
- the UV installer also uses a China-friendly package index

Useful cross-refs:

- [Proxy Configuration](../../manual/guides/proxy-configuration.md)
- [Networking](../../manual/guides/networking.md)
- [07 Proxy Setup](../basic/07-proxy-setup.md)
