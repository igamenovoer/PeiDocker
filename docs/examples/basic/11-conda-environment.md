# 11 Conda Environment

Use this when you want a predictable Miniconda location and a login-time activation flow.

Source: `examples/basic/conda-environment/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-conda:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2232
    users:
      scientist:
        password: "science123"
        uid: 1100
  apt:
    repo_source: tuna

stage_2:
  image:
    output: pei-example-conda:stage-2
  storage:
    app:
      type: image
    data:
      type: image
    workspace:
      type: auto-volume
  custom:
    on_build:
      - "stage-1/system/conda/install-miniconda.sh --install-dir=/hard/image/app/miniconda3 --pip-repo tuna"
    on_user_login:
      - "stage-1/system/conda/activate-conda-on-login.sh --conda-dir=/soft/app/miniconda3"
```

Why the paths differ:

- the build hook installs into `/hard/image/app/...`
- the login hook activates from `/soft/app/...`

Because `app` storage is image-backed here, both paths reach the same content at runtime.
