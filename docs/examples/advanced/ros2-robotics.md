# ROS2 Robotics

Use this when you want a GPU-capable robotics image with ROS2 packages and OpenGL-oriented tooling.

Source: `examples/advanced/ros2-robotics/user_config.yml`

```yaml
stage_1:
  image:
    base: nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
    output: pei-example-ros2:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2239
    users:
      robot:
        password: "robot123"
        uid: 1100
  apt:
    repo_source: tuna
  device:
    type: gpu
  custom:
    on_build:
      - "stage-1/system/ros2/setup-ros2-repo.sh --repo tuna"
      - "stage-1/system/ros2/install-ros2.sh --distro humble --with-gui --with-nav2-full"
      - "stage-1/system/opengl/setup-opengl-win32.sh"

stage_2:
  image:
    output: pei-example-ros2:stage-2
  device:
    type: gpu
  storage:
    app:
      type: image
    data:
      type: auto-volume
    workspace:
      type: auto-volume
  mount:
    home_robot:
      type: auto-volume
      dst_path: /home/robot
  environment:
    - "NVIDIA_VISIBLE_DEVICES=all"
    - "NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute"
```

Why it works:

- ROS2 installation stays in the image layer
- stage-2 remains focused on runtime state and user persistence
- OpenGL setup is included because GUI robotics tools often need it

Host caveat: the provided OpenGL helper targets WSLg-style setups. On Linux hosts you may not need the same runtime mounts.

Useful cross-refs:

- [ROS2](../../manual/scripts/ros2.md)
- [OpenGL](../../manual/scripts/opengl.md)
