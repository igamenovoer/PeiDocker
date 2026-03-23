# ROS2

The ROS2 script family installs repositories, packages, and rosdep support for robotics-oriented images.

## Main Scripts

| Script | Purpose |
| --- | --- |
| `setup-ros2-repo.sh` | Configure the ROS2 APT repository |
| `install-ros2.sh` | Install the chosen ROS2 distribution and optional extras |
| `init-rosdep.sh` | Initialize and update rosdep |
| `setup-locale.sh` | Prepare locale requirements for ROS2 tooling |

## Important Flags

`install-ros2.sh` supports:

- `--distro <name>` such as `humble`
- `--with-gui`
- `--with-nav2-full`

`setup-ros2-repo.sh` supports:

- `--repo ros2|tuna`

## Typical Flow

```yaml
stage_1:
  custom:
    on_build:
      - "stage-1/system/ros2/setup-ros2-repo.sh --repo tuna"
      - "stage-1/system/ros2/install-ros2.sh --distro humble --with-gui"
```

## Notes

- These scripts assume root privileges during build.
- GUI robotics workflows often pair ROS2 with GPU and OpenGL support.

See [ROS2 Robotics](../../examples/advanced/ros2-robotics.md).
