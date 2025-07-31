# Implementing the GUI via NiceGUI

implement the GUI using `nicegui` library

## Design

you can find designs here:

- design doc: `context/plans/web-gui/webgui-general-design.md`
- demo: `context/plans/web-gui/demo/active-project.html`
- you can find current file true structure in `context/summaries/lsfiles-src-20250731-045506.md`.

## Requirements

- create a GUI that with `nicegui` default style, but with the same structure as the demo.
- source code should be put in `src/pei_docker/webgui`
- for anything not sure, find online info via `context7` or web search.

## Testing

- you are using `pixi` python management tool, run everything use the `dev` feature like `pixi run -e dev xxxx`
- if you want to test the GUI, use `pytest-playwright`
- temporary scripts and files should be placed in `<workspace>/tmp`, create subdirs for different purposes.