# OpenGL

OpenGL support in this repository is aimed at NVIDIA and WSLg-style workflows.

## Canonical Assets

- `stage-1/system/opengl/setup-opengl-win32.sh`
- `stage-1/system/opengl/10_nvidia.json`
- `stage-1/system/opengl/docker-compose-win32.yml`

## What The Script Is For

The setup script prepares OpenGL-related packages and configuration for Windows/WSLg-oriented GPU containers. It is most relevant when you want GUI acceleration from a WSL-backed Docker host.

## Important Caveat

PeiDocker does not automatically inject all WSLg-specific runtime mounts for you. Example workflows may still require manual compose additions for X11 or WSLg integration depending on host setup.

## Recommended Use

Pair it with a GPU base image and explicit scenario docs such as [Vision OpenGL](../../examples/advanced/vision-opengl.md) or [ROS2 Robotics](../../examples/advanced/ros2-robotics.md).
