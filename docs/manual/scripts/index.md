# Script Catalog

Most built-in installer scripts are canonical under `installation/stage-1/system/`. Many `stage-2/system/*` paths are compatibility wrappers that forward to those stage-1 implementations.

## Overview

| Script family | Purpose | Preferred path | Complexity |
| --- | --- | --- | --- |
| Pixi | Install Pixi and curated environments | `stage-1/system/pixi/` | High |
| Conda | Install Miniconda and activate it on login | `stage-1/system/conda/` | High |
| SSH | Example keys and SSH-related assets | `stage-1/system/ssh/` | Medium |
| ROS2 | Repo setup, package install, rosdep init | `stage-1/system/ros2/` | High |
| Proxy | Enable or disable shell proxy vars | `stage-1/system/proxy/` | Medium |
| OpenGL | WSLg/OpenGL setup assets and helpers | `stage-1/system/opengl/` | High |
| OpenCV | Build OpenCV from source | `stage-1/system/opencv/` | High |
| Node.js | NVM and Node installers | `stage-1/system/nodejs/` | Medium |
| Bun | Bun runtime installer | `stage-1/system/bun/` | Low |
| UV | UV installer | `stage-1/system/uv/` | Low |
| Clang | LLVM/Clang installer helper | `stage-1/system/clang/` | Low |
| Firefox | Mozilla repo setup | `stage-1/system/firefox/` | Low |
| NGC | NVIDIA helper fixes | `stage-1/system/ngc/` | Low |
| LiteLLM | Install LiteLLM proxy via `uv tool` | `stage-1/system/litellm/` | Low |
| Claude Code | Install CLI via Bun | `stage-1/system/claude-code/` | Low |
| Codex CLI | Install CLI via Bun | `stage-1/system/codex-cli/` | Low |
| Magnum | Build Corrade and Magnum | `stage-1/system/magnum/` | Medium |
| Vision Dev | Install common CV tooling | `stage-1/system/vision-dev/` | Low |
| Set Locale | Locale helper for packages that require UTF-8 | `stage-1/system/set-locale.sh` | Low |

## Choosing A Script

- Start with the dedicated pages for Pixi, Conda, SSH, ROS2, Proxy, OpenGL, and OpenCV.
- Use [Simple Installers](simple-installers.md) for everything that behaves more like “install one tool” than “configure a workflow”.
- Prefer explicit path flags over implicit `/soft/*` assumptions when the script supports them.
