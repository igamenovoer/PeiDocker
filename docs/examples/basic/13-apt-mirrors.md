# 13 APT Mirrors

Use this when you want to switch package download sources without adding proxy logic.

Source: `examples/basic/apt-mirrors/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-apt-mirror:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2234
    users:
      dev:
        password: "123456"
  apt:
    repo_source: tuna
    keep_repo_after_build: true

stage_2:
  image:
    output: pei-example-apt-mirror:stage-2
```

Swap `tuna` for `aliyun`, `163`, `ustc`, or `cn` when that better matches your network.

Use this example as a building block for the more complete [China Corporate Proxy](../advanced/china-corporate-proxy.md) scenario.
