# Do this task

in demo page, the `script` tab (see `context/plans/web-gui/demo/active-project.html`), modify as follows:

- some `Lifecycle Scripts` subsection as defaults, like `on_every_run` section, remove them, we do not need defaults.
- recall how these custom scripts work, particularly about their execution order, and update `Script Execution Order Preview`. For this, you can check the `src/pei_docker/project_files/stage-{1,2}.Dockerfile`, and the `docs/`.