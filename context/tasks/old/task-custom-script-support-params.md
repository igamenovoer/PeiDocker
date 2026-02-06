implement this feature: allow custom scripts to accept parameters within the `.yml` user config file (like `pei_docker\templates\config-template-full.yml`), for example:

```yaml
custom:
# scripts run during build
on_build: 
    - 'stage-1/custom/my-build-1.sh --param1=value1 --param2=value2'
...
```

you shall read `context\summaries\how-custom-scripts-work.md` to make sure you understand how custom scripts are executed during the build process.