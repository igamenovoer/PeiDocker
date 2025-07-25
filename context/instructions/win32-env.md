# Windows Environments

you are in a Windows environment, which means you can use Windows-specific tools and commands.

- use `powershell` for CLI tasks, particularly using inline python code for testing
- your python env is managed by `pixi`, use `pixi run -e dev` for development tasks, and `pixi run` for deployment tasks
- DO NOT use unicode emojis in your code, or print, or logging