# Build Modes

PeiDocker supports three distinct workflows. The default docs path uses the two-stage Compose workflow, but you do not have to use both stages.

## Quick Decision

| Mode | Config shape | `configure` writes | Build / run path | Good fit |
| --- | --- | --- | --- | --- |
| `stage-1-only` | Only `stage_1` in `user_config.yml` | `docker-compose.yml` with only the `stage-1` service | `docker compose build stage-1` and `docker compose up -d stage-1` | Small SSH-ready or system-base containers |
| `two-stage Compose` | `stage_1` plus `stage_2` | `docker-compose.yml` with both services | `docker compose build ...` and `docker compose up ...` | Default development workflow with storage and final runtime behavior |
| `merged build` | `stage_1` plus `stage_2` | `docker-compose.yml` plus `merged.Dockerfile`, `merged.env`, `build-merged.sh`, and `run-merged.sh` | `./build-merged.sh` and `./run-merged.sh` | Plain `docker build` / `docker run` workflow while keeping the two-stage model |

`merged build` is not the same as `stage-1-only`.

- `stage-1-only` changes the config shape by omitting `stage_2`.
- `merged build` keeps both stages in the config and changes only how you build and run them.

## 1. `stage-1-only`

Use this when you want the simplest practical container and do not need stage-2 storage or stage-2 runtime customization yet.

Minimal config:

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

Workflow:

```bash
pei-docker-cli create -p demo --quick minimal
# Replace demo/user_config.yml with the stage-1-only config above
cd demo
pei-docker-cli configure
docker compose build stage-1
docker compose up -d stage-1
ssh dev@localhost -p 2222
```

What changes:

- The generated `docker-compose.yml` contains only the `stage-1` service.
- The project scaffold still includes stage-2 template files, so you can add `stage_2` later without recreating the project.

## 2. `two-stage Compose` (Default)

Use this when you want the full PeiDocker model: a reusable system base in stage-1 and a final runtime image in stage-2.

This is the best default when you need:

- `stage_2.storage`
- extra runtime ports
- runtime-oriented hooks
- a final image that keeps app-layer customization separate from the system base

Workflow:

```bash
pei-docker-cli create -p demo --quick minimal
cd demo
pei-docker-cli configure
docker compose build stage-1
docker compose build stage-2
docker compose up -d
ssh me@localhost -p 2222
```

Start here if you are unsure. Then read [Quickstart](quickstart.md) and [Two-Stage Architecture](../concepts/two-stage-architecture.md).

## 3. `merged build`

Use this when you want to keep the logical two-stage model but build and run the final image through generated helper scripts instead of the default Compose build path.

Workflow:

```bash
pei-docker-cli create -p demo --quick minimal
cd demo
pei-docker-cli configure --with-merged
./build-merged.sh
./run-merged.sh -d
ssh me@localhost -p 2222
```

Generated artifacts:

- `merged.Dockerfile`
- `merged.env`
- `build-merged.sh`
- `run-merged.sh`

Important constraints:

- `merged build` still uses `stage_1` and `stage_2` from your config. It is not a `stage-1-only` shortcut.
- Compose passthrough markers such as `{{VAR}}` are incompatible with `--with-merged`.

## Which One Should A First-Time User Pick?

- Pick `stage-1-only` if your immediate goal is “give me one SSH-ready container and I do not need stage-2 features yet”.
- Pick `two-stage Compose` if you want the default PeiDocker workflow and expect to use storage, runtime hooks, or a final stage-2 image.
- Pick `merged build` if your real requirement is “keep the two-stage model, but build with one generated `docker build` workflow”.

## Next Step

- Follow [Quickstart](quickstart.md) for the default two-stage path.
- Use [01 Minimal SSH](../../examples/basic/01-minimal-ssh.md) if you want the smallest default example explained line by line.
- Read [CLI Reference](../cli-reference.md) for command details and [Two-Stage Architecture](../concepts/two-stage-architecture.md) for the deeper model behind the default workflow.
