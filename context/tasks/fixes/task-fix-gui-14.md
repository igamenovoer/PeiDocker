# Do this task

## Prerequisites

Read these first:
- Terminololy: `context/design/terminology.md`, to understand the concepts used in this task.
- Coding guide: `context/instructions/debug-code.md`, to understand how to debug the code, and also note that python code should be strongly typed, see `context/instructions/strongly-typed.md` for details.

## The problem

There are many constant strings spread across the codebase, and you mistakes them quite often, using incorrect strings in dicttionaries, leading to bugs that are hard to track down.

We need to refactor the code to collect these strings in a class, setting them as class members, so that you no longer need to remember the strings, and avoid typos.

### Custom Scripts

in `scripts.py`:

```python
class ScriptsTab(BaseTab):
    """Scripts configuration tab with proper data binding."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        
        # References to UI containers for lifecycle scripts
        self.stage1_lifecycle_containers: Dict[str, ui.column] = {}
        self.stage2_lifecycle_containers: Dict[str, ui.column] = {}
        
        # [IMPROVE: Use a class to hold lifecycle types]
        # Lifecycle types
        self.lifecycle_types: List[Tuple[str, str]] = [
            ('on_build', 'Runs during image building'),
            ('on_first_run', 'Runs on first container start (respective stage)'),
            ('on_every_run', 'Runs on every container start (respective stage)'),
            ('on_user_login', 'Runs when user logs in via SSH (respective stage)')
        ]
```

you should collect the strings `on_build`, `on_first_run`, `on_every_run`, and `on_user_login` in a class like this:

```python

class CustomScriptLifecycleTypes:
    """Class to hold custom script lifecycle types."""
    
    ON_BUILD = 'on_build'
    ON_FIRST_RUN = 'on_first_run'
    ON_EVERY_RUN = 'on_every_run'
    ON_USER_LOGIN = 'on_user_login'

# use these constants in the lifecycle_types list

```

and you have bugs related to these strings, in `src\pei_docker\webgui\utils\ui_state_bridge.py`:

```python
# from LINE: 515
        # Note: attrs model uses on_build, not pre_build/post_build
        if 'pre_build' in lifecycle_scripts:
            for script_data in lifecycle_scripts['pre_build']:
                if isinstance(script_data, dict):
                    if script_data.get('type') == 'file' and 'path' in script_data:
                        on_build.append(script_data['path'])
                    elif script_data.get('type') == 'inline' and 'name' in script_data:
                        # For inline scripts, use the proper path
                        on_build.append(f"/pei-docker/scripts/{script_data['name']}")
                elif isinstance(script_data, str):
                    on_build.append(script_data)
        
        if 'first_run' in lifecycle_scripts:
            for script_data in lifecycle_scripts['first_run']:
                if isinstance(script_data, dict):
                    if script_data.get('type') == 'file' and 'path' in script_data:
                        on_first_run.append(script_data['path'])
                    elif script_data.get('type') == 'inline' and 'name' in script_data:
                        on_first_run.append(f"/pei-docker/scripts/{script_data['name']}")
                elif isinstance(script_data, str):
                    on_first_run.append(script_data)
```

see these lines, they use `pre_build` and `first_run`, but the correct strings are `on_build` and `on_first_run`, so you need to fix these lines to use the constants from the class you created.