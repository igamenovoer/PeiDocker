# Do this task

Fix the following issues of the GUI. We use the terminology as said in `context/tasks/prefix/prefix-terminology.md`.

## State changes are lost when switching between tabs without explicitly saving

Previously, this is regarded as a bug, but now it is considered as a feature. We expect the user to save before switching tabs, otherwise, settings will be lost, so the GUI should not lose the current state when switching between tabs unless save, you can safely read the generated `user_config.yml` file on each tab switch, but the GUI should not automatically save the changes when switching tabs. If user switches tabs without saving, the GUI should show a warning that the changes will be lost if they do not save.

This will simplify the GUI logic and make it easier to understand for users.

## Summary Tab

- The "Generated user_config.yml Preview" says "Error generating preview: maximum recursion depth exceeded".
- remove the "Validation Status" section, validation should be done per-tab, when user is entering or when save, not in the summary tab.