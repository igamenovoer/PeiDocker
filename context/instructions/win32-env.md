# Windows Environments

you are in a Windows environment, which means you can use Windows-specific tools and commands.

- avoid using inline python code for testing, create temporary files instead
- for complex cli commands, try your Bash() tool first, if failed then use `powershell` commands.
- your python env is managed by `pixi`, use `pixi run -e dev` for development tasks, and `pixi run` for deployment tasks
- DO NOT use unicode emojis in your code, or print, or logging