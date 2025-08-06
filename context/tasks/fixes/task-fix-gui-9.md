# Do this task

Fix the following issues of the GUI. We use the terminology as said in `context/tasks/prefix/prefix-terminology.md`.

## `Save` error

clicking `save` will results in the error below, you need to fix it:

```
(pei-docker) PS D:\code\PeiDocker> pei-docker-gui start
Starting PeiDocker Web GUI on port 8080...
Open http://localhost:8080 in your browser
NiceGUI ready to go on http://localhost:8080, http://10.10.14.48:8080, http://169.254.197.23:8080, http://169.254.246.34:8080, http://169.254.37.236:8080, http://169.254.50.228:8080, http://169.254.62.192:8080, http://172.22.64.1:8080, http://192.168.144.1:8080, http://192.168.245.1:8080, http://192.168.48.194:8080, http://192.168.56.1:8080, and http://198.18.0.1:8080
Task exception was never retrieved
future: <Task finished name='Task-348' coro=<PeiDockerWebGUI.save_configuration() done, defined at D:\code\PeiDocker\src\pei_docker\webgui\app.py:402> exception=RuntimeError('The current slot cannot be determined because the slot stack for this task is empty.\nThis may happen if you try to create UI from a background task.\nTo fix this, enter the target slot explicitly using `with container_element:`.')>
Traceback (most recent call last):
  File "D:\code\PeiDocker\src\pei_docker\webgui\app.py", line 421, in save_configuration
    await self._save_inline_scripts(project_path)
  File "D:\code\PeiDocker\src\pei_docker\webgui\app.py", line 448, in _save_inline_scripts
    entry_mode = getattr(scripts_ui, f'stage{stage_num}_entry_mode')
AttributeError: 'ScriptsUI' object has no attribute 'stage1_entry_mode'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\code\PeiDocker\src\pei_docker\webgui\app.py", line 436, in save_configuration
    ui.notify(f'Error saving configuration: {str(e)}', type='negative', timeout=10000)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\functions\notify.py", line 52, in notify
    client = context.client
             ^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 31, in client
    return self.slot.parent.client
           ^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 23, in slot
    raise RuntimeError('The current slot cannot be determined because the slot stack for this task is empty.\n'
                       'This may happen if you try to create UI from a background task.\n'
                       'To fix this, enter the target slot explicitly using `with container_element:`.')
RuntimeError: The current slot cannot be determined because the slot stack for this task is empty.
This may happen if you try to create UI from a background task.
To fix this, enter the target slot explicitly using `with container_element:`.
```