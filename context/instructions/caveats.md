Some caveats to consider when editing the code.

# Known Issues

## Textual RadioSet.Changed Event: Context7 Documentation Error

**Issue**: Context7 MCP incorrectly documents the `RadioSet.Changed` event attributes for the Textual framework.

**Problem**: When looking up Textual's `RadioSet.Changed` event, Context7 documented:
```
textual.widgets.RadioSet.Changed
    Attributes:
      value (RadioButton): The selected radio button.
      previous (RadioButton | None): The previously selected radio button.
```

However, the actual API uses `pressed` instead of `value`:
```python
# Correct usage discovered through inspection:
def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
    selected_button = event.pressed  # NOT event.value
```
