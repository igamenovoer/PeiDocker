# Refactor the data model to reduce duplicate code

- terminology: `context\tasks\prefix\prefix-terminology.md`, we will discuss using these terms in the refactor.

we now have three data models in the project:
- `peidocker-data-model`: This is the data model that represents the `user_config.yml` file during the configuration process, mainly used by the `pei-docker-cli` command line interface and `config_processor.py` module.
- `ui-data-model`: The data model that represents the state of the GUI, source code is in `src\pei_docker\webgui\models\ui_state.py`.
- `business-data-model`: The data model that represents `user_config.yml`, which is what `pei-docker-cli configure` command reads and configures the docker building `docker-compose.yml`, this is the "business logic" data model, because in the end, the GUI is just an easy way to generate the `user_config.yml` file (see `context/tasks/prefix/prefix-terminology.md`). The `business-data-model` is implemented using `pydantic` and is located in `src/pei_docker/webgui/models/config.py`.

and you can see, `business-data-model` and `peidocker-data-model` are very similar, they both represent the same data, but in different contexts, one for cli and one for gui, they all represent the same `user_config.yml` file, the `business-data-model` just have some extra validation and transformation logic.

We need to refactor the `business-data-model` to reuse the `peidocker-data-model` as much as possible, so that we can reduce the duplicate code and make the code more maintainable.