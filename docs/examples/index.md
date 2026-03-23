# Examples

Every example in this section has two parts:

- A runnable config under the repository-root `examples/` directory.
- A narrative page in `docs/examples/` that explains why the config is shaped that way.

Use the basic set when you want one feature at a time. Use the advanced set when you want a realistic scenario to adapt.

Most of the numbered examples below assume the default two-stage Compose workflow. If you want a `stage-1-only` container or the `merged build` workflow instead, start with [Build Modes](../manual/getting-started/build-modes.md) before choosing an example.

## Workflow Variants

- [Build Modes](../manual/getting-started/build-modes.md) compares `stage-1-only`, the default `two-stage Compose` workflow, and `merged build`.
- The minimal SSH docs plus the build-modes page give the clearest beginner path if you are deciding between “omit `stage_2`” and “keep both stages but use `--with-merged`”.

## Basic

| Doc page | Source config | Focus |
| --- | --- | --- |
| [01 Minimal SSH](basic/01-minimal-ssh.md) | `examples/basic/minimal-ssh/user_config.yml` | Smallest useful PeiDocker project |
| [02 GPU Container](basic/02-gpu-container.md) | `examples/basic/gpu-container/user_config.yml` | GPU runtime selection |
| [03 Host Mount](basic/03-host-mount.md) | `examples/basic/host-mount/user_config.yml` | Host-backed storage |
| [04 Docker Volume](basic/04-docker-volume.md) | `examples/basic/docker-volume/user_config.yml` | Auto-managed Docker volumes |
| [05 Custom Script](basic/05-custom-script.md) | `examples/basic/custom-script/user_config.yml` | `on_build` hook plus extra file |
| [06 Port Mapping](basic/06-port-mapping.md) | `examples/basic/port-mapping/user_config.yml` | Port strings and ranges |
| [07 Proxy Setup](basic/07-proxy-setup.md) | `examples/basic/proxy-setup/user_config.yml` | Proxy plus APT proxy integration |
| [08 Env Variables](basic/08-env-variables.md) | `examples/basic/env-variables/user_config.yml` | Configure-time `${VAR}` |
| [09 Env Passthrough](basic/09-env-passthrough.md) | `examples/basic/env-passthrough/user_config.yml` | Compose-time `{{VAR}}` |
| [10 Pixi Environment](basic/10-pixi-environment.md) | `examples/basic/pixi-environment/user_config.yml` | Pixi installer flow |
| [11 Conda Environment](basic/11-conda-environment.md) | `examples/basic/conda-environment/user_config.yml` | Miniconda plus login activation |
| [12 Multi-User SSH](basic/12-multi-user-ssh.md) | `examples/basic/multi-user-ssh/user_config.yml` | Multiple users and auth styles |
| [13 APT Mirrors](basic/13-apt-mirrors.md) | `examples/basic/apt-mirrors/user_config.yml` | China mirror selection |

## Advanced

| Doc page | Source config | Scenario |
| --- | --- | --- |
| [ML Dev GPU](advanced/ml-dev-gpu.md) | `examples/advanced/ml-dev-gpu/user_config.yml` | GPU ML workstation with Pixi |
| [Web Dev Node.js](advanced/web-dev-nodejs.md) | `examples/advanced/web-dev-nodejs/user_config.yml` | Node app with host workspace and ports |
| [Team Dev Environment](advanced/team-dev-environment.md) | `examples/advanced/team-dev-environment/user_config.yml` | Multi-user shared environment |
| [China Corporate Proxy](advanced/china-corporate-proxy.md) | `examples/advanced/china-corporate-proxy/user_config.yml` | Mirrors plus proxy-sensitive installs |
| [ROS2 Robotics](advanced/ros2-robotics.md) | `examples/advanced/ros2-robotics/user_config.yml` | ROS2 with GPU and OpenGL support |
| [Vision OpenGL](advanced/vision-opengl.md) | `examples/advanced/vision-opengl/user_config.yml` | GPU, OpenGL, OpenCV, and vision tools |
| [Migrate From Dockerfile](advanced/migrate-from-dockerfile.md) | none | Conceptual mapping from hand-written Dockerfiles |
