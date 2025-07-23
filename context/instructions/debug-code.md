follow these guidelines to debug code:
- ALWAYS use `context7` to find documentations if you encouter problems calling 3rd python library, or if you think needed or in doubt
- use online search to find best practices or solutions if needed or in doubt
- DO NOT use unicode emojis in your code or print statements
- we are using `pixi` as python package manager, so use `pixi run` to run python code for deployment, **and `pixi run -e dev` for development tasks**
- for any interactive process that may block the terminal, timeout within 10 seconds
- NEVER modify pyproject.toml directly due to missing packages, use pixi installation commands instead
