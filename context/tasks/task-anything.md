# Do this task

The GUI does not contain all the functionality of the `user_config.yml` and this PeiDocker project, this is expected, as the GUI aims to provide a user-friendly interface for common tasks, while the `user_config.yml` file contains detailed configurations that can be edited for advanced use cases.

So, some of the settings in `user_config.yml` will be simplified and then reflected in the GUI, for example, the environment variables in `user_config.yml` can be configured for `stage-1` and `stage-2` separately, but in the GUI, they are combined into a single section, so we assume that the GUI will set environment variables for both stages at the same time. When loading the project, you simply combine the environment variables from both stages, if `stage-1` and `stage-2` have the same variable, the value from `stage-2` will be used, the behavior is just like `export` command applied to the environment variables in stage-1 and then stage-2.

This princple applies to all the settings in `user_config.yml` where stage-1 and stage-2 can be configured separately but the GUI has only a single section for them. 

IMPORTANT: Note that, if the GUI already supports separete-stage settings, you should not change the behavior of the GUI, you should only change the behavior of the GUI it supports only a single section for the settings that are splitted into stage-1 and stage-2 in `user_config.yml`.