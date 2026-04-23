# SSH Access Reference

## Source Files

- `docs/manual/guides/ssh-setup.md`
- `docs/manual/scripts/ssh.md`
- `src/pei_docker/templates/config-template-full.yml`
- `src/pei_docker/examples/basic/minimal-ssh/user_config.yml`
- `src/pei_docker/examples/basic/multi-user-ssh/user_config.yml`

## Placement

Configure SSH under `stage_1.ssh` because SSH is a system-layer concern.

Minimum shape:

```yaml
stage_1:
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      dev:
        password: "123456"
```

## Auth Methods

Each user needs at least one auth method:

- `password`
- `pubkey_file`
- `pubkey_text`
- `privkey_file`
- `privkey_text`

`pubkey_file` conflicts with `pubkey_text`. `privkey_file` conflicts with `privkey_text`.

Use relative key paths from the project `installation/` directory, absolute host paths, or `~` for host SSH key discovery.

## Multi-User Pattern

```yaml
stage_1:
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
```

Set `uid` and `gid` only when predictable ownership matters. Root is never renamed or removed.

## Port Rule

`stage_1.ssh.port` changes the SSH daemon port inside the container. `stage_1.ssh.host_port` adds the host-to-container mapping in generated compose output.
