# Team Dev Environment

Use this when a single image needs to serve multiple users and some shared team state.

Source: `examples/advanced/team-dev-environment/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-team-dev:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2237
    users:
      alice:
        password: "alice123"
        uid: 1100
      bob:
        password: "bob123"
        uid: 1101
      reviewer:
        pubkey_file: "stage-1/system/ssh/keys/example-pubkey.pub"
        uid: 1102
      root:
        password: "root123"
  apt:
    repo_source: aliyun

stage_2:
  image:
    output: pei-example-team-dev:stage-2
  ports:
    - "8080:8080"
  storage:
    app:
      type: image
    data:
      type: auto-volume
    workspace:
      type: auto-volume
  mount:
    home_alice:
      type: auto-volume
      dst_path: /home/alice
    home_bob:
      type: auto-volume
      dst_path: /home/bob
    shared_docs:
      type: auto-volume
      dst_path: /srv/shared
  environment:
    - "TEAM_NAME=platform"
```

Why it works:

- stage-1 owns user creation and SSH auth
- stage-2 adds shared writable areas without hardcoding host paths
- user homes stay separate while `/srv/shared` becomes a team handoff area

Useful cross-refs:

- [SSH Setup](../../manual/guides/ssh-setup.md)
- [12 Multi-User SSH](../basic/12-multi-user-ssh.md)
