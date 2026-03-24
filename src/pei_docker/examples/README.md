# PeiDocker Examples

These example directories are the source-of-truth configs referenced by the docs site. Copy the `user_config.yml` you want into a project created with `pei-docker-cli create`, then copy any extra files from the same example directory if the example includes them.

## Basic

| Example | Description | Docs |
| --- | --- | --- |
| `basic/minimal-ssh/` | Smallest useful SSH-enabled project | [01 Minimal SSH](../../../docs/examples/basic/01-minimal-ssh.md) |
| `basic/gpu-container/` | Minimal GPU-capable container | [02 GPU Container](../../../docs/examples/basic/02-gpu-container.md) |
| `basic/host-mount/` | Workspace backed by a host path | [03 Host Mount](../../../docs/examples/basic/03-host-mount.md) |
| `basic/docker-volume/` | Stage-2 data stored in Docker volumes | [04 Docker Volume](../../../docs/examples/basic/04-docker-volume.md) |
| `basic/custom-script/` | Build hook plus a supporting shell script | [05 Custom Script](../../../docs/examples/basic/05-custom-script.md) |
| `basic/port-mapping/` | Single ports and ranges | [06 Port Mapping](../../../docs/examples/basic/06-port-mapping.md) |
| `basic/proxy-setup/` | Proxy and APT proxy configuration | [07 Proxy Setup](../../../docs/examples/basic/07-proxy-setup.md) |
| `basic/env-variables/` | Configure-time `${VAR}` substitution | [08 Env Variables](../../../docs/examples/basic/08-env-variables.md) |
| `basic/env-passthrough/` | Compose-time `{{VAR}}` passthrough | [09 Env Passthrough](../../../docs/examples/basic/09-env-passthrough.md) |
| `basic/pixi-environment/` | Pixi install plus common packages | [10 Pixi Environment](../../../docs/examples/basic/10-pixi-environment.md) |
| `basic/conda-environment/` | Miniconda install plus login activation | [11 Conda Environment](../../../docs/examples/basic/11-conda-environment.md) |
| `basic/multi-user-ssh/` | Multiple users with mixed auth styles | [12 Multi-User SSH](../../../docs/examples/basic/12-multi-user-ssh.md) |
| `basic/apt-mirrors/` | China mirror selection with APT | [13 APT Mirrors](../../../docs/examples/basic/13-apt-mirrors.md) |

## Advanced

| Example | Description | Docs |
| --- | --- | --- |
| `advanced/ml-dev-gpu/` | GPU ML workstation with Pixi and persistent caches | [ML Dev GPU](../../../docs/examples/advanced/ml-dev-gpu.md) |
| `advanced/web-dev-nodejs/` | Node.js dev setup with host workspace and app ports | [Web Dev Node.js](../../../docs/examples/advanced/web-dev-nodejs.md) |
| `advanced/team-dev-environment/` | Shared multi-user environment with common volumes | [Team Dev Environment](../../../docs/examples/advanced/team-dev-environment.md) |
| `advanced/china-corporate-proxy/` | Corporate proxy plus China mirrors | [China Corporate Proxy](../../../docs/examples/advanced/china-corporate-proxy.md) |
| `advanced/ros2-robotics/` | ROS2 with GPU and OpenGL-oriented setup | [ROS2 Robotics](../../../docs/examples/advanced/ros2-robotics.md) |
| `advanced/vision-opengl/` | GPU vision workstation with OpenGL and OpenCV tooling | [Vision OpenGL](../../../docs/examples/advanced/vision-opengl.md) |

## Usage Pattern

```bash
pei-docker-cli create -p demo --quick minimal
cp examples/basic/minimal-ssh/user_config.yml demo/user_config.yml
cd demo
pei-docker-cli configure
docker compose build stage-2
docker compose up -d
```

If an example contains `installation/` content, copy that subtree into the created project as well.
