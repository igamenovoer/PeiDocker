# Do this task

## Prerequisites

Read these first:
- Terminololy: `context/design/terminology.md`, to understand the concepts used in this task.
- Coding guide: `context/instructions/debug-code.md`, to understand how to debug the code, and also note that python code should be strongly typed, see `context/instructions/strongly-typed.md` for details.

## The problem

the current yaml preview in summary tab shows this, this is buggy in port mapping:

```yaml
stage_1:
  image:
    base: ubuntu:24.04
    output: peidocker-20250807-220124:stage-1
  environment:
  - 'EXAMPLE_VAR_STAGE_1=example env var'
  proxy: {}
  apt:
    repo_source: https://mirrors.tuna.tsinghua.edu.cn/ubuntu/
    use_proxy: true

#[BUG: if no port mapping is specified, it should be empty instead of showing ":"]
  ports: 
  - ':'
  - ':'
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      me:
        password: '123456'
        uid: 1000
      you:
        password: '654321'
        uid: 1001
      root:
        password: root
        uid: 0
stage_2:
  image:
    output: peidocker-20250807-220124:stage-2
  environment:
  - 'EXAMPLE_VAR_STAGE_2=example env var'
  proxy: {}
  storage:
    app:
      type: auto-volume
    data:
      type: auto-volume
    workspace:
      type: auto-volume
```