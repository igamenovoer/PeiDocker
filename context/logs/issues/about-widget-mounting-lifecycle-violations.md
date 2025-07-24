# Widget Mounting Lifecycle Violations in Textual

## Issue Category: Widget Lifecycle Management

This document describes a common class of bugs in Textual GUI applications where widgets are mounted in violation of the proper widget lifecycle, causing `MountError` exceptions.

## Problem Signature

### Error Messages
```
MountError: Can't mount widget(s) before {ContainerWidget}() is mounted
```

### Code Pattern That Causes This Issue

**❌ PROBLEMATIC PATTERN:**
```python
# Creating a container widget
container = Horizontal(classes="some-class")

# Attempting to mount widgets to the container BEFORE the container is mounted
container.mount(Widget1())
container.mount(Widget2())
container.mount(Widget3())

# THEN mounting the container to parent
parent_container.mount(container)
```

### Root Cause
In Textual's widget system, you cannot mount child widgets to a container until that container is itself mounted to the widget tree. The widget lifecycle requires:
1. Container must be part of the widget tree first
2. Only then can child widgets be mounted to it

## Correct Implementation Patterns

### ✅ SOLUTION PATTERN 1: Constructor Composition
```python
# Create child widgets first
widget1 = Widget1()
widget2 = Widget2() 
widget3 = Widget3()

# Create container with widgets as constructor arguments
container = Horizontal(widget1, widget2, widget3, classes="some-class")

# Mount the complete container
parent_container.mount(container)
```

### ✅ SOLUTION PATTERN 2: Mount-Then-Add
```python
# Create and mount empty container first
container = Horizontal(classes="some-class")
parent_container.mount(container)

# NOW it's safe to mount children
container.mount(Widget1())
container.mount(Widget2())
container.mount(Widget3())
```

## How to Identify This Issue in Code

### Search Patterns
Use these patterns to find potentially problematic code:

**Grep/Search Patterns:**
```bash
# Look for container creation followed by immediate mounting
grep -A 5 -B 2 "= Horizontal\|= Vertical\|= Container" *.py | grep -A 3 "\.mount("

# Look for mount calls on variables that were just created
grep -A 10 "= Horizontal\|= Vertical" *.py | grep "\.mount("

# Look for multiple mount calls in sequence 
grep -A 5 -B 5 "\.mount(" *.py | grep -C 2 "\.mount("
```

**Code Review Checklist:**
1. ✅ Is the container variable created and immediately used for mounting children?
2. ✅ Are there multiple consecutive `.mount()` calls on the same container?
3. ✅ Is the container mounted to its parent AFTER children are added?

### Common Locations
- Navigation update methods (`_update_step`, `_update_navigation`)
- Dynamic UI generation methods
- Screen refresh/rebuild methods
- Widget state change handlers

## Specific Case Study: Simple Wizard Navigation

**File:** `src/pei_docker/gui/screens/simple/wizard.py`  
**Method:** `_update_step()`

**Problematic Code:**
```python
nav_buttons = Horizontal(classes="nav-buttons")
nav_buttons.mount(Button("Prev", id="prev", variant="default"))
nav_buttons.mount(Button("Next", id="next", variant="primary"))
nav_buttons.mount(Button("Cancel", id="cancel", variant="default"))
nav_container.mount(nav_buttons)  # TOO LATE!
```

**Fixed Code:**
```python
prev_button = Button("Prev", id="prev", variant="default")
next_button = Button("Next", id="next", variant="primary") 
cancel_button = Button("Cancel", id="cancel", variant="default")
nav_buttons = Horizontal(prev_button, next_button, cancel_button, classes="nav-buttons")
nav_container.mount(nav_buttons)  # CORRECT!
```

## Prevention Guidelines

### Code Writing Best Practices
1. **Favor constructor composition** over post-creation mounting
2. **Create all child widgets first** before creating containers
3. **Mount containers as complete units** when possible
4. **If dynamic mounting is needed**, ensure container is mounted to parent first

### Code Review Guidelines
1. **Flag any code** that creates containers and immediately calls `.mount()` on them
2. **Look for patterns** where widget creation and mounting are interleaved
3. **Verify mount order** follows the proper widget lifecycle
4. **Test navigation scenarios** that trigger UI rebuilding

## Testing Approaches

### Automated Detection
```python
# Headless test to catch mounting issues
async def test_widget_mounting():
    app = TestApp()
    async with app.run_test() as pilot:
        # Trigger methods that rebuild UI
        screen.some_update_method()
        # Will throw MountError if lifecycle violated
```

### Manual Testing Scenarios
- Navigate between screens multiple times
- Trigger UI state changes that rebuild navigation
- Test back-and-forth navigation patterns
- Test rapid UI updates

## Related Issues to Watch For

1. **Widget ID conflicts** - mounting widgets with duplicate IDs
2. **CSS class inconsistencies** - containers missing expected classes after remounting  
3. **Event handler loss** - handlers not properly attached after widget recreation
4. **Memory leaks** - old widgets not properly cleaned up during remounting

## Summary

Widget mounting lifecycle violations are a common source of crashes in Textual applications. They occur when developers try to mount widgets to containers before those containers are part of the widget tree. The solution is always to respect the proper lifecycle: create children first, compose containers, then mount complete structures. This pattern prevents `MountError` exceptions and leads to more robust GUI applications.