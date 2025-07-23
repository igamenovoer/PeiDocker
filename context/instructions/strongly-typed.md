you shall write your python code in a strongly typed manner, and use `mypy` to validate the types in your code after editing.

# Rules for Strongly Typed Code
- if you are not sure about a type, use `Any` as a fallback
- if you are unsure about a type in a 3rd party library, use `context7` MCP to find out info before you proceed
- if `context7` MCP returns something inconsistent with the code, try to create a minimal example code to directly inspect the type