# ML Dev GPU

Use this when you want a reusable GPU ML workstation with persistent models, caches, and a Python package workflow.

Source: `examples/advanced/ml-dev-gpu/user_config.yml`

```yaml
stage_1:
  image:
    base: nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
    output: pei-example-ml-dev:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2235
    users:
      mldev:
        password: "ml123"
        uid: 1100
      root:
        password: "root123"
  apt:
    repo_source: tuna
  device:
    type: gpu

stage_2:
  image:
    output: pei-example-ml-dev:stage-2
  device:
    type: gpu
  storage:
    app:
      type: auto-volume
    data:
      type: auto-volume
    workspace:
      type: auto-volume
  mount:
    models:
      type: auto-volume
      dst_path: /models
    package_cache:
      type: auto-volume
      dst_path: /package-cache
    home_mldev:
      type: auto-volume
      dst_path: /home/mldev
  environment:
    - "NVIDIA_VISIBLE_DEVICES=all"
    - "NVIDIA_DRIVER_CAPABILITIES=all"
    - "CUDA_VISIBLE_DEVICES=all"
  custom:
    on_first_run:
      - "stage-1/system/pixi/install-pixi.bash --cache-dir=/package-cache/pixi --conda-repo tuna --pypi-repo tuna --user mldev"
      - "stage-1/system/pixi/create-env-common.bash"
      - "stage-1/system/pixi/create-env-ml.bash"
```

Why it works:

- stage-1 establishes the GPU-capable base image and SSH access
- stage-2 keeps the working state in volumes so models and caches survive rebuilds
- Pixi runs on first boot so the cache path can live in persistent runtime storage

Useful cross-refs:

- [GPU Support](../../manual/guides/gpu-support.md)
- [Storage Model](../../manual/concepts/storage-model.md)
- [10 Pixi Environment](../basic/10-pixi-environment.md)
