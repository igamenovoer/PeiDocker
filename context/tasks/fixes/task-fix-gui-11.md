# Do this task

## Prerequisites

Read these first:
- Terminololy: `context/design/terminology.md`, to understand the concepts used in this task.
- Coding guide: `context/instructions/debug-code.md`, to understand how to debug the code, and also note that python code should be strongly typed, see `context/instructions/strongly-typed.md` for details.

## The problem

when creating new project, the `pei-docker-cli create` command will generate a project in the given dir, within it there is a `user_config.yml`, and currently the content inside it is not loaded into the GUI, I can see that the `summary tab` shows the content of the `user_config.yml` file, the GUI states like `script tab` or others does not refect the loaded `user_config.yml`, you may have forgotten to update the `ui-data-model`. 

for how to parse the `user_config.yml` into `peidocker-data-model`, check `src\pei_docker\pei.py` and `src\pei_docker\config_processor.py`. As for bridging the `peidocker-data-model` to the `ui-data-model`, you already have implemented that.