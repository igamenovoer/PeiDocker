# Stage And Image Reference

## Source Files

- `docs/manual/getting-started/build-modes.md`
- `docs/manual/concepts/two-stage-architecture.md`
- `src/pei_docker/templates/config-template-full.yml`
- `src/pei_docker/templates/quick/*.yml`
- `src/pei_docker/examples/basic/minimal-ssh/user_config.yml`
- `openspec/specs/docs-build-mode-onboarding/spec.md`

## Stage Rules

Use `stage_1` for the system layer:

- base image selection
- SSH setup
- APT mirrors and proxy-aware package setup
- low-level or shared installers
- stable dependencies reused by later images

Use `stage_2` for the final working layer:

- storage
- extra application ports
- app-specific environment values
- runtime-oriented hooks
- final image customization

If the user wants a single-stage project, omit `stage_2`. If the user wants one plain Docker build command while keeping both logical stages, keep `stage_2` and use `pei-docker-cli configure --with-merged`.

## Minimal Shapes

Stage-1-only:

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-stage1-only:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      dev:
        password: "123456"
```

Default two-stage:

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example:stage-1

stage_2:
  image:
    output: pei-example:stage-2
```

When `stage_2.image.base` is omitted, PeiDocker uses the stage-1 output image.

## Device Selection

For GPU work, use a GPU-capable base image and set `device.type: gpu` in relevant stages:

```yaml
stage_1:
  image:
    base: nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
  device:
    type: gpu

stage_2:
  device:
    type: gpu
```

Use `$pei-docker-run-project` for runtime GPU verification.
