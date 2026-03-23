# 12 Multi-User SSH

Use this when one container should support multiple humans with different auth styles.

Source: `examples/basic/multi-user-ssh/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-multi-ssh:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2233
    users:
      alice:
        password: "alice123"
        uid: 1100
      bob:
        password: "bob123"
        pubkey_file: "stage-1/system/ssh/keys/example-pubkey.pub"
        uid: 1101
      root:
        password: "root123"
  apt:
    repo_source: aliyun

stage_2:
  image:
    output: pei-example-multi-ssh:stage-2
```

This example mixes:

- password-only auth for `alice`
- password plus packaged public key for `bob`
- explicit root access

If you need host-discovered keys, switch a key field to `~` and run `configure` on the machine that has the key.
