# Test of pixi support

now create a test case to test the pixi support

## Requirements

create a test user config file, name `simple-pixi-test.yml`, in `tests/configs`, which then build a docker images.

Details about the config:
- use `ubuntu:24.04` as base
- add my system ssh public key to authorized keys
- add my sustem ssh private key as its private key
- install pixi in stage-2, using `on_build` section in the user config
- create ml environment using `create-env-ml.bash` after pixi install
- bind `/workspace/docker-shared/app` as the `stage-2.storage.app`
- bind `/workspace/docker-shared/workspace` as the `stage-2.storage.workspace`
- bind `ig-data` (docker volume) as the `stage-2.storage.data`

then, create a test script to run the pei docker commands (`create` and `configure`), with `--progress=plain` in docker compose. The test script should be created in `tests/scripts`, name it as `run-simple-pixi-test.bash`

## References

These are reference info for you to accomplish the task.

- user config template: `pei_docker/templates/config-template-full.yml`
- example user config: `docs/examples/basic.md`