# 07 Proxy Setup

Use this when your build needs a host-side HTTP proxy and you want APT to use it too.

Source: `examples/basic/proxy-setup/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-proxy:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2228
    users:
      dev:
        password: "123456"
  proxy:
    address: host.docker.internal
    port: 7890
    enable_globally: true
    remove_after_build: true
    use_https: false
  apt:
    repo_source: tuna
    use_proxy: true
    keep_proxy_after_build: false

stage_2:
  image:
    output: pei-example-proxy:stage-2
```

Why it matters:

- `enable_globally: true` exports proxy vars during the build
- `remove_after_build: true` avoids leaving that shell proxy in the final image
- `apt.use_proxy: true` gives APT its own proxy config

If your runtime also needs the proxy, set `remove_after_build: false` or override the stage-2 proxy section explicitly.
