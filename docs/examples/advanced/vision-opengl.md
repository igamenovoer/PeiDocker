# Vision OpenGL

Use this when you want a GPU-oriented computer-vision workstation that also needs GUI or OpenGL support.

Source: `examples/advanced/vision-opengl/user_config.yml`

```yaml
stage_1:
  image:
    base: nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
    output: pei-example-vision:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2240
    users:
      vision:
        password: "vision123"
        uid: 1100
  apt:
    repo_source: tuna
  device:
    type: gpu
  custom:
    on_build:
      - "stage-1/system/vision-dev/install-vision-dev.bash"
      - "stage-1/system/opengl/setup-opengl-win32.sh"

stage_2:
  image:
    output: pei-example-vision:stage-2
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
    home_vision:
      type: auto-volume
      dst_path: /home/vision
  environment:
    - "NVIDIA_VISIBLE_DEVICES=all"
    - "NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute"
```

Why it works:

- `vision-dev` installs a broad OpenCV-friendly package set
- OpenGL setup is included for GUI and rendering workflows
- user state persists separately from the image

If you need a custom OpenCV source build, swap in the dedicated OpenCV scripts from [OpenCV](../../manual/scripts/opencv.md).
