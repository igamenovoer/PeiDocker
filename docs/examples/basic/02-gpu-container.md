# 02 GPU Container

Use this when the first question is “how do I turn GPU support on?” rather than “how do I manage storage?”

Source: `examples/basic/gpu-container/user_config.yml`

```yaml
stage_1:
  image:
    base: nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
    output: pei-example-gpu:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2223
    users:
      dev:
        password: "123456"
  device:
    type: gpu

stage_2:
  image:
    output: pei-example-gpu:stage-2
  device:
    type: gpu
  environment:
    - "NVIDIA_VISIBLE_DEVICES=all"
    - "NVIDIA_DRIVER_CAPABILITIES=compute,utility"
```

Why it is shaped this way:

- the base image already contains CUDA user-space tooling
- `device.type: gpu` is set in both stages for clarity
- the stage-2 environment hints the runtime about visible devices and capabilities

Next reads:

- [GPU Support](../../manual/guides/gpu-support.md)
- [ML Dev GPU](../advanced/ml-dev-gpu.md)
