you are tasked to validate the types in python code, make them strongly typed, and ensure consistency across the codebase.

do this follow these guidelines:
- use `mypy` for type checking, check all given source files
- fix the typing errors reported by `mypy` at your best effort
- if a type is not clear, use `Any` as a fallback
- ensure that all variables and functions have type annotations, unless it is not possible
- for unsure types in 3rd party libraries, use `context7` mcp to find out info before you proceed, `context7` can help you find the right types and usage examples.
- if `context7` MCP returns something inconsistent with the code, try to create a minimal example code to directly inspect the type