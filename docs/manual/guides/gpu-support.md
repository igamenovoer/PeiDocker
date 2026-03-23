# GPU Support

GPU access is enabled through `device.type: gpu` and a GPU-capable base image.

## Minimal GPU Config

```yaml
stage_1:
  image:
    base: nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
    output: pei-gpu:stage-1
  device:
    type: gpu

stage_2:
  image:
    output: pei-gpu:stage-2
  device:
    type: gpu
```

## Host Prerequisites

- NVIDIA GPU on the host
- Working NVIDIA drivers
- Docker configured to expose GPUs to containers
- A CUDA-compatible base image when you want GPU libraries in the image itself

## Verification

After building and starting the container:

```bash
docker compose exec stage-2 nvidia-smi
```

If you install CUDA-aware tooling in the image, you can also verify framework visibility from inside the container.

## Common Pitfalls

- Setting `device.type: gpu` with a CPU-only base image usually gives you device exposure without the user-space libraries you expected.
- GUI/OpenGL GPU workflows on Windows WSL often need additional runtime mounts beyond PeiDocker’s generated config. See [Vision OpenGL](../../examples/advanced/vision-opengl.md).
