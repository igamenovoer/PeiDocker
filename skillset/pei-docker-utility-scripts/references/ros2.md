# ROS2 Reference

## Source Files

- `docs/manual/scripts/ros2.md`
- `docs/examples/advanced/ros2-robotics.md`
- `src/pei_docker/examples/advanced/ros2-robotics/user_config.yml`

## Scripts

Canonical path: `stage-1/system/ros2/`.

Main scripts:

- `setup-ros2-repo.sh`
- `install-ros2.sh`
- `init-rosdep.sh`
- `setup-locale.sh`

Important flags:

- `setup-ros2-repo.sh --repo ros2|tuna`
- `install-ros2.sh --distro <name>`
- `install-ros2.sh --with-gui`
- `install-ros2.sh --with-nav2-full`

## Typical Pattern

ROS2 usually belongs in stage-1 `on_build` because it installs OS packages and stable robotics tooling:

```yaml
stage_1:
  custom:
    on_build:
      - "stage-1/system/ros2/setup-ros2-repo.sh --repo tuna"
      - "stage-1/system/ros2/install-ros2.sh --distro humble --with-gui"
```

Pair GUI robotics workflows with GPU and OpenGL guidance when needed.
