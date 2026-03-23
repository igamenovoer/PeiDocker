# OpenCV

PeiDocker ships source-build scripts for both CPU and CUDA-enabled OpenCV.

## Scripts

| Script | Purpose |
| --- | --- |
| `install-opencv-cpu.sh` | Build OpenCV with Qt support and contrib modules |
| `install-opencv-cuda.sh` | Build OpenCV with CUDA and DNN CUDA support |

## Important Flag

Both scripts accept:

- `--cache-dir <dir>`

Use it when you want Git clones and build artifacts outside the default stage temp directory.

## Preconditions

- CPU build: standard development toolchain plus internet access
- CUDA build: CUDA toolkit available in the image and GPU tooling such as `nvidia-smi`

## When To Use Them

These scripts are best for curated heavy images, not for the very first container you try. They are a good fit for dedicated CV or graphics-oriented scenarios such as [Vision OpenGL](../../examples/advanced/vision-opengl.md).
