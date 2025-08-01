# Implementing the GUI via NiceGUI

implement the GUI using `nicegui` library

## Design

you can find designs here:

- design doc: `context/plans/web-gui/webgui-general-design.md`
- demo: `context/plans/web-gui/demo`
- you can find current file true structure in `context/summaries/lsfiles-src-20250731-045506.md`.
- for nicegui documentation, you should find it using `context7` or web search.

## Requirements

- create a GUI that with `nicegui` default style, but with the same structure as the demo, that is, the same layout and components, and number of pages.
- source code should be put in `src/pei_docker/webgui`
- for anything not sure, find online info via `context7` or web search.

## Testing

- you are using `pixi` python management tool, run everything use the `dev` feature like `pixi run -e dev xxxx`
- if you want to test the GUI, use `pytest-playwright`
- temporary scripts and files should be placed in `<workspace>/tmp`, create subdirs for different purposes.

I'll provide more detailed analysis with references to online examples and best practices from the NiceGUI documentation.