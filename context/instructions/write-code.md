you are tasked to write or modify source code, follow these guidelines

# Guidelines for Writing or Modifying Source Code
- ALWAYS use `context7` to find documentations if you encouter problems calling 3rd python library, or if you think needed or in doubt
- use online search to find best practices or solutions if needed or in doubt
- DO NOT use unicode emojis in your console output like print statements, as it may cause issues in some environments
- you CAN use unicode emojis in GUI code, like web-based applications, as they are generally well supported in modern browsers
- NEVER modify pyproject.toml directly due to missing packages, use pixi installation commands instead

## Python Code Guidelines

- Avoid using relative imports in Python code, prefer to use absolute imports to ensure clarity and avoid import errors.


# How to run code

If you want to run something, you should follow these instructions.

## Python Environment
- we are using `pixi` as python package manager, so use `pixi run` to run python code for deployment, **and `pixi run -e dev` for development tasks**
  
## Command Line Interface (CLI)
- for any interactive process that may block the terminal, timeout within 10 seconds
- for anything you need to wait for timeout, timeout in LESS THAN 15 seconds