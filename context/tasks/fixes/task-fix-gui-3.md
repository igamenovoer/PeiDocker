# Do this task

Fix the following issues of the GUI. We use the terminology as said in `context/tasks/prefix/prefix-terminology.md`.

## Not all GUI elements are bound to the data model

The `script` tab has inline script editor, user can edit the script and save it to file. Currently these edits are not bound to the data model (see `src\pei_docker\webgui\models\ui_state.py`), so if user goes to another tab and comes back, the script editor will not preserve the previous states.

Modify the `script` tab data binding, so that:
- data model updates with GUI when `save` button is clicked, otherwise, edits are lost.
- once `save` is done, the script editor should reflect the current state of the data model. If user goes to another tab and comes back, the script editor should show the latest saved state.

Check if other tabs have similar issues, we MUST make sure all GUI editable elements are bound to the data model, so that user can always see the latest saved state when they navigate back to the tab.