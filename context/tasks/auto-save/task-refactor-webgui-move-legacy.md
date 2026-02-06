# Task: Refactor WebGUI by Moving Legacy Implementation to legacy_gui Module

## Overview
This task involved refactoring the @src/pei_docker/webgui/ module by moving all legacy implementations to a new @src/pei_docker/legacy_gui module, keeping only the latest refactored implementation in the webgui module.

## Context
- The webgui was being refactored according to @context/tasks/fixes/task-fix-gui-3.md
- The legacy GUI did not design the data model well
- The refactoring uses NiceGUI bidirectional binding (see @context/hints/howto-bidirectional-data-binding-nicegui.md)
- The refactoring was partly done, with both legacy and refactored versions coexisting

## Implementation Steps

1. **Create legacy_gui module structure**
   - Created @src/pei_docker/legacy_gui/ directory
   - Created subdirectories: tabs/, utils/, models/
   - Added appropriate __init__.py files

2. **Move legacy files to legacy_gui**
   - Moved app.py → legacy_gui/app.py
   - Moved legacy_models.py → legacy_gui/legacy_models.py
   - Moved legacy_utils.py → legacy_gui/legacy_utils.py
   - Moved utils/bridge.py → legacy_gui/utils/bridge.py

3. **Move legacy tab implementations**
   - Moved tabs/environment.py → legacy_gui/tabs/environment.py
   - Moved tabs/network.py → legacy_gui/tabs/network.py
   - Moved tabs/ssh.py → legacy_gui/tabs/ssh.py
   - Kept scripts.py (already refactored)
   - Kept project.py, storage.py, summary.py (not yet refactored)

4. **Rename refactored files**
   - app_refactored.py → app.py
   - tabs/environment_refactored.py → tabs/environment.py
   - tabs/network_refactored.py → tabs/network.py
   - tabs/ssh_refactored.py → tabs/ssh.py

5. **Update imports**
   - Fixed imports in app.py to use utils/utils.py instead of legacy_utils
   - Updated cli_launcher.py to import TabName and AppState from app
   - Fixed TYPE_CHECKING imports in refactored tabs
   - Updated utils/__init__.py and models/__init__.py
   - Fixed base.py to use app.ui_state instead of app.data

6. **Create new utilities**
   - Created utils/utils.py with ProjectManager class only
   - UIStateBridge handles file operations in the refactored architecture

## Remaining Work
The following tabs still need to be refactored to use the new data binding approach:
- project.py - Still uses app.data and legacy models
- storage.py - Still uses app.data and legacy models  
- summary.py - Still uses app.data and legacy models

These unrefactored tabs will need to be updated to:
- Use app.ui_state instead of app.data
- Implement proper NiceGUI data binding
- Follow the pattern established in the refactored tabs

## Type Safety
Running mypy --strict revealed type errors mainly in the unrefactored tabs. The refactored code follows strongly-typed principles as specified in @context/instructions/strongly-typed.md.

## Development Environment
- MacOS environment (@context/instructions/mac-env.md)
- Using pixi for Python environment management
- Development commands use `pixi run -e dev`
- No unicode emojis in code (@context/instructions/write-code.md)