you are tasked to add graphics to the given documents, with the following guidelines.


# Guidelines for Graphics Insertion

- use `dot` or `plantuml` to generate graphics
- if in doubt or encounter errors, consult `context7` about how the markup language works
- the generated graphics should be in SVG format if possible, or PNG if SVG is not supported
- the generated files should be stored in the same directory as the source files, in a subdir named after the given documentation (excluding extension), UNLESS specified otherwise
- after generated, the graphics should appear in the source document, replacing the existing graphics
- DO NOT use inline SVG, the svg should be external file
- by default, we KEEP the source code of the graphics in the source document, for easy to parse by AI tools, UNLESS explictly requested to remove the source code