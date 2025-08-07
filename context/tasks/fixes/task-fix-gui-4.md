# Do this task

Fix the following issues of the GUI. We use the terminology as said in `context/tasks/prefix/prefix-terminology.md`.

Useful info for testing:
- `context/tasks/prefix/prefix-test-info.md`: useful information about how to test the GUI.
- `context/hints/nicegui-kb/howto-test-nicegui-with-playwright.md`: about how to test the GUI using Playwright.
- `context/hints/nicegui-kb/howto-nicegui-save-page-html.md`: about how to save the page HTML using Playwright.


## Use Data Binding for All GUI Input Elements

Many gui elements modified by the user are not bound to the gui data model (see `src\pei_docker\webgui\models\ui_state.py`). This means that changes made in the GUI will get lost when the user navigates away from the tab or closes the application. We need to fix this by ensuring that all editable GUI elements are properly bound to the data model.

Terminology:
- `ui-data-model`: The data model that represents the state of the GUI, source code is in `src\pei_docker\webgui\models\ui_state.py`.
- `business-data-model`: The data model that represents `user_config.yml`, which is what `pei-docker-cli configure` command reads and configures the docker building `docker-compose.yml` , this is the "business logic" data model, because in the end, the GUI is just an easy way to generate the `user_config.yml` file (see `context/tasks/prefix/prefix-terminology.md`). The `business-data-model` is implemented using `pydantic` and is located in `src/pei_docker/webgui/models/config.py`.
- `ui-to-business-bridge`: The bridge that connects the `ui-data-model` and the `business-data-model`, implemented in `src/pei_docker/webgui/utils/ui_state_bridge.py`. We should implement bidirectional transformation between the two models, so that changes in the GUI can be validated and saved to the `business-data-model`, and when loading existing projects, the `user_config.yml` will be first loaded into the `business-data-model`, then transformed to the `ui-data-model` for the GUI to display.

## Requirements

After the fix, the GUI should behave as follows:
- All editable GUI elements should be bound to the `ui-data-model`, persisting changes made in the GUI even when navigating away from the tab. The legacy implementation of the GUI enforces the user to save changes before navigating away from the current tab, but this is not user-friendly, the new design should allow users to navigate freely without losing changes.
- in the final summary tab, `ui-data-model` should be transformed to `business-data-model`, which is then used to generate the `user_config.yml` IN MEMORY, for preview, and ONLY when the user clicks the `save` button, the `user_config.yml` file is written to disk as well as other temporary stuff like the "inline" script files created in the `script` tab (stored in its ui states data model).
- clicking `configure` button will forces the `save` behavior, so that the latest changes in the GUI will be applied, and then `pei-docker-cli configure` command is executed over the generated `user_config.yml` file.