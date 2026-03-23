# SSH Setup

SSH is configured in `stage_1.ssh` because it is a system-layer concern.

## Minimum Shape

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

## Authentication Methods

Per user, you can use any of these:

- `password`
- `pubkey_file`
- `pubkey_text`
- `privkey_file`
- `privkey_text`

At least one authentication method is required. `pubkey_*` fields are mutually exclusive with each other, and the same applies to `privkey_*`.

## Multi-User Setup

```yaml
users:
  alice:
    password: "alice123"
    uid: 1100
  bob:
    pubkey_file: "stage-1/system/ssh/keys/example-pubkey.pub"
    uid: 1101
```

You can also set `gid` when you need predictable primary groups.

## Auto-Discovery And Paths

- Relative key paths are resolved from the installation directory.
- Absolute paths are supported.
- `~` triggers system SSH key discovery on the host for file-based key fields.

## Port Mapping

- `port` changes the SSH daemon port inside the container.
- `host_port` adds the host-to-container mapping in generated compose output.

## UID/GID Behavior

The build logic tries to keep requested user IDs usable:

- Existing non-root username conflicts are renamed out of the way.
- Existing non-root UID conflicts are reassigned.
- Existing requested GIDs are reused; missing ones are created.
- Root is never renamed or removed.

See [12 Multi-User SSH](../../examples/basic/12-multi-user-ssh.md) for a copyable example.
