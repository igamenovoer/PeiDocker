# Basic Example Runtime Tests

This suite validates the packaged basic examples under `src/pei_docker/examples/basic/`
as real Docker projects.

It is intentionally opt-in because it builds images, starts containers, performs SSH
checks, and may exercise proxy- or GPU-sensitive behavior.

## Run

From repository root:

```bash
pytest -m basic_example_runtime tests/functional/basic_example_runtime -v
```

Run a targeted subset:

```bash
pytest -m basic_example_runtime tests/functional/basic_example_runtime -k pixi-environment -v
```

Pixi task:

```bash
pixi run test-basic-example-runtime
```

## Requirements

- Docker and Docker Compose plugin
- OpenSSH client
- `sshpass`
- Network access for examples that install tooling from external repositories

## Conditional Behavior

- `proxy-setup` is skipped when no usable `HTTP_PROXY` / `HTTPS_PROXY` environment is
  available from the invoking shell.
- `gpu-container` is skipped when the host does not expose a usable GPU runtime.

## Artifacts

Artifacts are retained under:

- `tmp/basic-example-runtime-e2e/`

Each scenario keeps:

- copied/generated project files
- command transcripts
- compose logs

## Cleanup

Each scenario attempts to:

- stop and remove compose services
- remove compose-created volumes
- remove the stage-1 and stage-2 images resolved for that scenario

## Verification Notes

Validated on 2026-03-23 with:

```bash
pixi run pytest tests/test_basic_examples_docs.py
pixi run pytest -m basic_example_runtime tests/functional/basic_example_runtime/test_basic_examples_runtime.py -k minimal-ssh -v
pixi run pytest -m basic_example_runtime tests/functional/basic_example_runtime/test_basic_examples_runtime.py -k 'host-mount or docker-volume or custom-script or env-variables or env-passthrough or apt-mirrors' -v
pixi run pytest -m basic_example_runtime tests/functional/basic_example_runtime/test_basic_examples_runtime.py -k 'port-mapping or multi-user-ssh' -v
pixi run pytest -m basic_example_runtime tests/functional/basic_example_runtime/test_basic_examples_runtime.py -k 'proxy-setup or gpu-container' -v
pixi run pytest -m basic_example_runtime tests/functional/basic_example_runtime/test_basic_examples_runtime.py -k 'pixi-environment or conda-environment' -v
```

Observed results in this environment:

- docs/example contract checks passed
- all 13 runtime scenarios passed across the targeted batches
- proxy and GPU scenarios executed successfully on this host
