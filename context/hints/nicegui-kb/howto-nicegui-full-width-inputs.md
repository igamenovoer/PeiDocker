# How to Make NiceGUI Inputs Take Full Width

This guide explains how to make NiceGUI input elements take up the full width of their parent container. This is a common layout issue that can be resolved by ensuring that all parent containers are also set to expand to the full width.

## The Problem

When creating complex layouts with nested containers, it's common for input elements to not expand to the full width of their parent card or container. This is often because one of the parent containers is not configured to expand, which constrains the width of its children.

## The Solution

The solution is to ensure that all parent containers are set to expand to the full width. This can be achieved by applying the `w-full` class to all parent `ui.column` and `ui.row` elements, and the `flex-1` class to the input elements themselves.

### Example

Here is an example of how to correctly structure your layout to ensure that input fields expand to the full width of their parent card:

```python
with ui.column().classes('w-full'):
    with self.create_card('My Card'):
        with self.create_form_group('My Form Group'):
            with ui.row().classes('w-full items-center gap-3 no-wrap'):
                name_input = ui.input(placeholder='Name').classes('flex-1')
                value_input = ui.input(placeholder='Value').classes('flex-1')
```

In this example, the `w-full` class is applied to the parent `ui.column` and `ui.row` elements, and the `flex-1` class is applied to the `ui.input` elements. This ensures that the input fields will expand to fill the available width of the card.

### Key Takeaways

- Ensure all parent containers are set to expand to the full width by applying the `w-full` class.
- Use the `flex-1` class on input elements to make them expand to fill the available space in a flex container.
- Use the `no-wrap` class on `ui.row` elements to prevent them from wrapping their children to the next line.