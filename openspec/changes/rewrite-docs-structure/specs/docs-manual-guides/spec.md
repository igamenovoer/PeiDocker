## ADDED Requirements

### Requirement: SSH setup guide covers all authentication methods
The SSH guide (`manual/guides/ssh-setup.md`) SHALL document password auth, pubkey file, pubkey text (inline), privkey file, privkey text, and auto-discovery (`~`). It SHALL cover multi-user configuration with different auth methods per user, UID/GID assignment, and host port mapping.

#### Scenario: User configures multi-user SSH
- **WHEN** a user reads the SSH guide
- **THEN** they can configure multiple SSH users with different authentication methods and connect to each

### Requirement: GPU support guide
The GPU guide (`manual/guides/gpu-support.md`) SHALL document how to enable GPU support via `device.type: gpu`, NVIDIA Docker runtime prerequisites, and verification steps inside the container.

#### Scenario: User enables GPU in their container
- **WHEN** a user reads the GPU guide
- **THEN** they can configure GPU access and verify it works with `nvidia-smi` inside the container

### Requirement: Proxy configuration guide
The proxy guide (`manual/guides/proxy-configuration.md`) SHALL document proxy address/port setup, `host.docker.internal` usage, `enable_globally` vs selective proxy, `remove_after_build`, HTTPS proxy, APT proxy integration, and stage-2 inheritance from stage-1.

#### Scenario: User behind a corporate proxy
- **WHEN** a user behind a corporate proxy reads the guide
- **THEN** they can configure proxy for both build-time and runtime, and optionally strip proxy settings from the final image

### Requirement: Custom scripts guide
The custom scripts guide (`manual/guides/custom-scripts.md`) SHALL document how to write custom lifecycle scripts, where to place them (`installation/stage-*/custom/`), how to reference them in config, parameter passing syntax, and logging behavior.

#### Scenario: User adds a build-time script
- **WHEN** a user reads the custom scripts guide
- **THEN** they can write a shell script, place it in the correct directory, and hook it into `on_build`

### Requirement: Storage and mounts guide
The storage guide (`manual/guides/storage-and-mounts.md`) SHALL document configuring each storage type, switching between types without changing application paths, using custom mounts with arbitrary names, and the relationship between storage keys and container paths.

#### Scenario: User switches from host mount to docker volume
- **WHEN** a user reads the storage guide
- **THEN** they can change storage type from `host` to `auto-volume` without modifying their application code or paths

### Requirement: Port mapping guide
The port mapping guide (`manual/guides/port-mapping.md`) SHALL document single port mapping, port ranges, and the Docker format syntax used in configuration.

#### Scenario: User exposes multiple ports
- **WHEN** a user reads the port mapping guide
- **THEN** they can configure both individual ports and port ranges

### Requirement: Networking guide
The networking guide (`manual/guides/networking.md`) SHALL document APT repository mirrors (predefined: tuna, aliyun, 163, ustc, cn), custom repository source files, and the `keep_repo_after_build` / `keep_proxy_after_build` options.

#### Scenario: User configures China APT mirror
- **WHEN** a user in China reads the networking guide
- **THEN** they can configure a predefined mirror and choose whether to keep it in the final image

### Requirement: Web GUI guide
The web GUI guide (`manual/guides/webgui.md`) SHALL document launching the GUI, navigating the interface, and how GUI configuration maps to `user_config.yml` fields.

#### Scenario: User configures via GUI
- **WHEN** a user reads the web GUI guide
- **THEN** they can launch the GUI and create a working configuration without editing YAML manually
