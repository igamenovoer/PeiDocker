# Code review mainly based on your knowledge

you are tasked to review the source code, mainly based on your knowledge, with online resources as reference if needed, follow these guidelines to review.

first and foremost, DO NOT TRY to modify the code under review, instead, you should provide a report with suggestions on how to improve the code.

## Guidelines

- scan through the code to understand the overall structure and logic, and most importantly, the intent of the code
- create a report in `context/logs/code-reivew`, name it as `<timestamp>-<what-to-review>.md`, where `<timestamp>` is the current timestamp in `YYYYMMDD-HHMMSS` format, and `<what-to-review>` is a short description of the code being reviewed
- if you are not sure, then find online info, or you can just find online info for verification.
- if you find online resources and used them, in your report, include the references, including online links and context7 ids.

### 3rd Party Libraries
- if there is `pyproject.toml` or `pixi.toml` or `requirements.txt` in the codebase, you should check what libraries are already being used, and use them if possible
- in your suggestions, introducing new libraries should be minimized, unless that library is widely accepted and has clear advantages over the current implementation.