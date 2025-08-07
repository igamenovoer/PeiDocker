# Windows Environments

you are in a Windows environment, which means you can use Windows-specific tools and commands.

- avoid using inline python code for testing, create temporary files instead
- for complex cli commands, try your Bash() tool first, if failed then use `powershell` commands.
- your python env is managed by `pixi`, use `pixi run -e dev` for development tasks, and `pixi run` for deployment tasks

## Unicode and Emojis
- DO NOT use unicode emojis in console output, like printing `😀` in the console, as it may not be displayed correctly in some Windows terminals, sometimes leading to crash.
- For GUI applications, you CAN use unicode emojis in the user-facing text, such as labels, buttons, etc.