# Port Mapping

PeiDocker treats port mappings as Docker Compose strings and preserves them without trying to parse them into numeric models.

## Where To Put Ports

- `stage_1.ports` for system services
- `stage_2.ports` for application services
- `stage_1.ssh.host_port` for SSH specifically

## Formats

Supported examples:

- `8080:80`
- `3000-3002:3000-3002`
- `127.0.0.1:8080:80`
- `{{WEB_HOST_PORT:-18080}}:80`

Stage-2 receives stage-1 port mappings plus its own additional mappings.

## Example

```yaml
stage_1:
  ports:
    - "6006:6006"

stage_2:
  ports:
    - "8080:80"
    - "3000-3002:3000-3002"
```

## Notes

- SSH host port mapping is added automatically when `stage_1.ssh.host_port` is set.
- Because the values stay string-shaped, passthrough markers work cleanly in port mappings.

See [06 Port Mapping](../../examples/basic/06-port-mapping.md).
