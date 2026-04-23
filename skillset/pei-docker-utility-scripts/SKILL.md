---
name: pei-docker-utility-scripts
description: Guidance for using PeiDocker built-in utility scripts. Use when Codex needs to choose installer or helper scripts, understand their parameters, place them in user_config.yml custom hooks, or reason about build-time versus runtime paths.
---

# PeiDocker Utility Scripts

## Start Here

Use this skill when the user wants to reuse PeiDocker's built-in scripts instead of writing custom shell from scratch.

Primary sources:

- `docs/manual/scripts/index.md`
- `docs/manual/scripts/*.md`
- `docs/manual/concepts/script-lifecycle.md`
- `docs/manual/guides/custom-scripts.md`
- `src/pei_docker/project_files/installation/stage-1/system/`
- `src/pei_docker/project_files/installation/stage-2/system/`
- `openspec/specs/install-script-parameter-interface/spec.md`
- `openspec/specs/installer-flag-conventions/spec.md`
- `openspec/specs/stage1-system-canonical-installers/spec.md`
- `openspec/specs/stage2-system-wrapper-policy/spec.md`

Prefer canonical `stage-1/system/*` paths in config examples unless a source doc explicitly says otherwise. Most `stage-2/system/*` scripts are thin compatibility wrappers.

## Reference Routing

Read only the relevant reference file:

| Task | Reference |
| --- | --- |
| Pixi install, Pixi envs, package mirrors | `references/pixi.md` |
| Miniconda install, pip/conda mirrors, login activation | `references/conda.md` |
| ROS2 repository setup, ROS2 install, rosdep | `references/ros2.md` |
| OpenGL, OpenCV, vision tooling, GPU GUI workflows | `references/opengl-opencv-vision.md` |
| Node.js, UV, Bun, and other simple installers | `references/node-uv-bun-simple-installers.md` |
| Shell-level proxy helpers | `references/proxy-helpers.md` |

## Hook Placement

Use lifecycle timing before choosing a hook:

| Need | Hook |
| --- | --- |
| Install into image during build | `custom.on_build` |
| Initialize runtime storage once | `custom.on_first_run` |
| Reapply runtime setup every start | `custom.on_every_run` |
| Modify SSH login shell environment | `custom.on_user_login` |
| Replace default startup handoff | `custom.on_entry` |

Build-time script entries that need durable in-image paths should use `/hard/image/...`. Runtime hooks may use `/soft/...` after stage-2 storage links are prepared.

## Config Pattern

Add scripts under the relevant stage:

```yaml
stage_2:
  custom:
    on_build:
      - "stage-1/system/pixi/install-pixi.bash --user dev"
```

Script entries may include arguments. Preserve shell-like quoting when editing existing entries.

## Validation

After adding or changing hook entries, run:

```bash
pei-docker-cli configure -p <project-dir>
```

If the user needs runtime verification, build and run using `$pei-docker-run-project`.
