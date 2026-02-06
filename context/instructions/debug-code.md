you are tasked to debug the source code, follow these guidelines to debug:

# Debugging Guidelines
- ALWAYS use `context7` to find documentations if you encouter problems calling 3rd python library, or if you think needed or in doubt
- use online search to find best practices or solutions if needed or in doubt
- DO NOT use unicode emojis in your console output like print statements, as it may cause issues in some environments
- you CAN use unicode emojis in GUI code, like web-based applications, as they are generally well supported in modern browsers
- we are using `pixi` as python package manager, so use `pixi run` to run python code for deployment, **and `pixi run -e dev` for development tasks**
- for any interactive process that may block the terminal, timeout within 10 seconds
- NEVER modify pyproject.toml directly due to missing packages, use pixi installation commands instead
- If you want to open browser, use `playwright` to open a new browser instance, do not reuse the current browser instance, as the user may be using it. And remember to close the browser instance after use.

# File Handling Guidelines
- temporary tests scripts should be placed in `<workspace_root>/tmp/tests` directory
- temporary outputs should be placed in `<workspace_root>/tmp/outputs` directory, create subdirectories for different test cases