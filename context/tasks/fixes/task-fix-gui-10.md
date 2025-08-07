
# Do this task

## Prerequisites

Read these first:
- Terminololy: `context/design/terminology.md`, to understand the concepts used in this task.
- Coding guide: `context/instructions/debug-code.md`, to understand how to debug the code, and also note that python code should be strongly typed, see `context/instructions/strongly-typed.md` for details.

## The problem

Fix the following issues of the GUI. Currently you create dir by yourself, this is wrong, you should use the `pei-docker-cli create -p <dirpath>` command to create a project, the cli is in `src\pei_docker\pei.py`, you can also directly use python to call its functions. The created project will contain a `user_config.yml` file, which is the default configuration file for the project, and you should load the default values from this file into the gui's `ui-data-model`, and show them in GUI.

```python
# BUG: The current implementation creates a project directory manually, which is incorrect, should use pei-docker-cli to create a project.

    # Project management methods
    async def create_project(self, project_dir: str) -> None:
        """Create a new project."""
        try:
            # Create project directory
            Path(project_dir).mkdir(parents=True, exist_ok=True)
            
            # Set up new UI state with defaults
            self.ui_state = AppUIState()
            self.ui_state.project.project_directory = project_dir
            self.ui_state.project.project_name = Path(project_dir).name
            
            # Load default values from template
            self._load_default_configuration()
            
            # Switch to active state
            self.app_state = AppState.ACTIVE
            self.update_ui_state()
            
            ui.notify(f'✅ Project created: {project_dir}', type='positive')
            
            # Render first tab
            self.render_active_tab()
            
        except Exception as e:
            ui.notify(f'❌ Failed to create project: {str(e)}', type='negative')
```