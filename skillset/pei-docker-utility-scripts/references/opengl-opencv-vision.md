# OpenGL, OpenCV, And Vision Reference

## Source Files

- `docs/manual/scripts/opengl.md`
- `docs/manual/scripts/opencv.md`
- `docs/manual/scripts/simple-installers.md`
- `docs/examples/advanced/vision-opengl.md`
- `docs/examples/advanced/ros2-robotics.md`
- `src/pei_docker/examples/advanced/vision-opengl/user_config.yml`

## OpenGL

Canonical assets:

- `stage-1/system/opengl/setup-opengl-win32.sh`
- `stage-1/system/opengl/10_nvidia.json`
- `stage-1/system/opengl/docker-compose-win32.yml`

Use for NVIDIA and WSLg-style GUI/OpenGL workflows:

```yaml
stage_1:
  custom:
    on_build:
      - "stage-1/system/opengl/setup-opengl-win32.sh"
```

PeiDocker does not automatically inject every WSLg runtime mount. Host-specific GUI runtime setup may still need manual compose additions.

## OpenCV

Scripts:

- `stage-1/system/opencv/install-opencv-cpu.sh`
- `stage-1/system/opencv/install-opencv-cuda.sh`

Both accept:

- `--cache-dir <dir>`

Use CUDA build only when CUDA tooling is present in the image.

## Vision Dev

For broad CV tooling without a custom OpenCV source build:

```yaml
stage_1:
  custom:
    on_build:
      - "stage-1/system/vision-dev/install-vision-dev.bash"
```

Vision/OpenGL scenarios usually also require `device.type: gpu` and appropriate NVIDIA runtime env values.
