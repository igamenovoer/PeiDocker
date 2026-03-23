# SSH

PeiDocker does not use a single installer script for SSH the way it does for Pixi or Conda. Instead, SSH is driven by the `stage_1.ssh` config and a set of internal setup scripts plus key assets.

## Relevant Paths

- `stage-1/system/ssh/keys/` for example key assets
- `stage-1/internals/setup-ssh.sh` for daemon setup
- `stage-1/internals/setup-users.sh` for login-hook wiring

## What The SSH System Handles

- User creation
- Passwords
- Public and private key import
- Optional UID and GID control
- SSH daemon port changes
- Host port mapping via generated compose output

## Useful Patterns

- Password-only development access
- Public key authentication for long-lived users
- Mixed users with different auth methods
- Root access only when you explicitly define the `root` user in config

## Example Asset Path

```yaml
pubkey_file: "stage-1/system/ssh/keys/example-pubkey.pub"
```

For full config guidance, read [SSH Setup](../guides/ssh-setup.md).
