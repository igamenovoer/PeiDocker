# Do this task

Fix the following issues of the GUI. We use the terminology as said in `context/design/terminology.md`.

## Default `user_config.yml` is not loaded

- when a new project is created, the default `user_config.yml` is not loaded or not synced with the GUI states, should sync that.

## Project Information Tab

- remove the "Description" field, we do not need that
- "Generated Docker Images" should be horizontally aligned with "Project Information", so that user can see all of them in wide screen.

## Environment Variables Tab

- bug: `ui-data-model` is not correctly mapped to `peidocker-data-model`, see the mapping guide `context\design\gui-to-core-data-mapping.md`. Currently the set env variable only applies to `stage-1`, should be set in both `stage-1` and `stage-2`.

see the preview yaml when a new env is added:
```yaml
stage_1:
  image:
    base: ubuntu:22.04
    output: mydocker
  environment:
  - NEW_VAR=xxxx
  apt:
    repo_source: https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ [Note: this is not correct, it should be `tuna`, see the "docs/" or the `user_config.yml` template]
    use_proxy: false
  ports:
  - 8080:80
  - ':'
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '12345'
        uid: 2333
stage_2:

[Note: MISSING Environment Variables]

  storage:
    app:
      type: auto-volume
    data:
      type: auto-volume
    workspace:
      type: auto-volume
```

## Network Tab

- bug: clicking "remove" in port mapping does not work, no response, it should remove the port mapping from the list. And by default, there should be no port mappings, so the list should be empty.

- bug: "port mapping 1" created by default, there is a "8080:80" green text in the bottom of the card, should not be there, manually created "port mapping 2" has no such text, so it is a bug in the default port mapping.

## Summary Tab

### Bug: generated yaml preview is incorrect
- when the project is named "mydocker", the current generated yaml preview is:
  
```yaml
stage_1:
  image:
    base: ubuntu:22.04
    output: mydocker    [Note: this is incorrect, it should be `mydocker:stage-1`]
  ports:
  - 8080:80
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '12345'
        uid: 2333
stage_2:

    [Note: output is missing, it should be `mydocker:stage-2`]
    [Note: output keyword is MANDATORY in both stages, enforce this in your data model validation (in adapter layer)]

  storage:
    app:
      type: auto-volume
    data:
      type: auto-volume
    workspace:
      type: auto-volume
```