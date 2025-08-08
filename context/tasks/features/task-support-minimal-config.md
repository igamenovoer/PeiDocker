# Do this task

## Prerequisites

Read these first:
- Terminololy: `context/design/terminology.md`, to understand the concepts used in this task.
- Coding guide: `context/instructions/debug-code.md`, to understand how to debug the code, and also note that python code should be strongly typed, see `context/instructions/strongly-typed.md` for details.

## The problem

`pei-docker-cli create` command will by default copy the full template `src/pei_docker/templates/config-template-full.yml` to the project directory as `user_config.yml`, this may be too much for some users, so we need to provide a minimal template that only contains the essential configurations.

modify the `pei-docker-cli create`:
- it will copy the full template `src/pei_docker/templates/config-template-full.yml` to `project_dir/reference_config.yml`, this serves as a reference for users to understand the configuration. Note that, it will still copy the full template to `user_config.yml` as before (along with `reference_config.yml`), unless the user specifies the `--quick` option.
- `--quick <quick_template>` option will copy the quick template `src/pei_docker/templates/quick/config-<quick_template>.yml` to `project_dir/user_config.yml`, this is a quick start template that users can use to quickly get started with a specific configuration, it should contain only the essential configurations for that specific use case. Note that, in your help text, you should scan the `src/pei_docker/templates/quick/` directory and list all the available quick templates, so that users can choose one of them.