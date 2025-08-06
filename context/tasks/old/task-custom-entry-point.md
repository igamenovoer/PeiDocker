# current issue

- current entry points are predefined, see `pei_docker\project_files\installation\stage-{1,2}\internals\entrypoint.sh`, let's call these system-provided entrypoints as `system_entrypoint`

- user cannot add arguments to `system_entrypoint`, so cannot run the container as a background task with custom arguments

- system entry point will start shell interactively, so pure background tasks are not possible

# implement custom entry point

- in `pei_docker\templates\config-template-full.yml`, add a new keyword in `custom` section, name it `on_entry`, like this:

```yaml
custom:
    on_entry:
        # in python script, verify that it has at most one entry point per stage, otherwise raise error
        - "stage-1/custom/my-entry.sh"

    # due to the uniqueness of entry points, this is also OK and supported, but a bit inconsistent with other custom sections
    on_entry: "stage-1/custom/my-entry.sh"
```

- `my-entry.sh` will be executed near the end of `system_entrypoint`, replacing shell startup. That is, if custom entry point is given, it will be the end of `system_entrypoint`, no more actions will be executed after it.

- if user wants interactive shell, they have to add it to `my-entry.sh` explicitly by themselves.

- the custom entry point DOES NOT replace `system_entrypoint`, it is just an additional script that will be executed at the end of `system_entrypoint`.

- when arguments are passed to the `system_entrypoint`, they will be passed to `my-entry.sh`, all of them.

- for each stage in user config `config-template-full.yml`, at most one custom entry point can be specified. If both stages have custom entry points, the second one will override the first one. If the first stage has a custom entry point, but the second stage does not, the first stage's custom entry point will be used.

# references
- see `context\summaries\how-custom-scripts-work.md` for more details on how custom scripts work in docker image building process.