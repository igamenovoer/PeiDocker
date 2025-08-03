# Do this task

## Expanding widgets to full width

We are now not fully utilizing the available space in the widget area, many text widgets are difficult to read because they are too narrow. 

The "environment" tab (`src/pei_docker/webgui/tabs/environment.py`) has been fixed to use the full width of the widget area, except the top-level widget which is designed to be using a portion of the center area on the screen (otherwise it would be too wide on large screens). For the other tabs, always prefer to use the full width of its parent widget, unless there is a specific reason not to do so.

Check the GUI source code and fix them.