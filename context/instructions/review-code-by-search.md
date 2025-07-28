# Grabbing online info for code review

you are tasked to review the source code, with online resources as reference, follow these guidelines to review.

first and foremost, DO NOT TRY to modify the code under review, instead, you should provide a report with suggestions on how to improve the code.

## Guidelines

- scan through the code to understand the overall structure and logic, and most importantly, the intent of the code
- find online examples and best practices to do similar tasks, denote these materials as `online-examples`
- collect all 3rd party apis used in the code, for those that you do not understand fully, use `context7` to find documentations, if not found then look for online resources, denote these materials as `api-doc`
- combine `online-examples` and `api-doc` to form a comprehensive understanding of correct way to do the tasks in the code, and based on that, review the code
- create a report in `context/logs/code-reivew`, name it as `<timestamp>-<what-to-review>.md`, where `<timestamp>` is the current timestamp in `YYYYMMDD-HHMMSS` format, and `<what-to-review>` is a short description of the code being reviewed
- in your report, include the references, including online links and context7 ids.

### 3rd Party Libraries
- if there is `pyproject.toml` or `pixi.toml` or `requirements.txt` in the codebase, you should check what libraries are already being used, and use them if possible
- in your suggestions, introducing new libraries should be minimized, unless that library is widely accepted and has clear advantages over the current implementation.