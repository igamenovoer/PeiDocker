# Web Dev Node.js

Use this when you want a local web-app container with a host-mounted workspace, preserved user state, and predictable dev ports.

Source: `examples/advanced/web-dev-nodejs/user_config.yml`

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: pei-example-web-dev:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2236
    users:
      webdev:
        password: "web123"
        uid: 1100
  apt:
    repo_source: tuna

stage_2:
  image:
    output: pei-example-web-dev:stage-2
  ports:
    - "3000:3000"
    - "5173:5173"
  storage:
    app:
      type: image
    data:
      type: auto-volume
    workspace:
      type: host
      host_path: "${WEB_WORKSPACE:-/tmp/peidocker-web-workspace}"
  mount:
    home_webdev:
      type: auto-volume
      dst_path: /home/webdev
    npm_cache:
      type: auto-volume
      dst_path: /home/webdev/.npm
  custom:
    on_build:
      - "stage-1/system/nodejs/install-nvm-nodejs.sh --user webdev --nodejs-version 22"
```

Why it works:

- source code stays on the host for normal editor workflows
- Node.js is installed into the image during build
- the user home and npm cache live outside the image for faster iteration

Useful cross-refs:

- [Port Mapping](../../manual/guides/port-mapping.md)
- [Storage And Mounts](../../manual/guides/storage-and-mounts.md)
- [Simple Installers](../../manual/scripts/simple-installers.md)
