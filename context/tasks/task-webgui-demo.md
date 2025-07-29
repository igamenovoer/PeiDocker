# Web GUI Demo

This task involves creating a simple web GUI that demonstrates basic functionality. The goal is to provide an interactive interface that allows users to perform actions and view results in real-time.

## Requirements

the following docs defines how the GUI should behave:

- original requirement: `context/tasks/task-webgui-req.md`
- design doc: `context/plans/web-gui/webgui-general-design.md`

The demo itself DOES NOT have a welcome page saying that "this is a demo", it should look like a real application. 

## Implementation

### Split into Multiple Files

if we make a demo into a giant `index.html` file, it will be too large and hard to maintain, so we will split the demo into multiple files, each file is a separate page, and the main page will have tabs to switch between different pages. 

### Entry Point

the entry point of the demo is `index.html`, which has tabs as said in the design doc, and each tab will load a separate HTML file, which contains the content of the tab.