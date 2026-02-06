# How to Track Unsaved Changes in NiceGUI Applications

This guide covers best practices and techniques for tracking unsaved changes in NiceGUI Python applications, including tools, patterns, and implementation strategies based on modern web development practices.

## Overview

Tracking unsaved changes (also known as "dirty state" tracking) is crucial for preventing data loss in form-based applications. This involves monitoring user input modifications and warning users before they navigate away from unsaved work.

## Core Concepts

### What is Dirty State?
Dirty state refers to the condition where form data has been modified by the user but not yet saved to persistent storage. This state needs to be tracked to:

- Warn users before leaving the page with unsaved changes
- Enable/disable save buttons based on modification status
- Provide visual feedback about unsaved changes
- Implement auto-save functionality

### Key Components
1. **State Tracking**: Monitor changes to form fields
2. **User Warning**: Prevent accidental data loss when navigating away
3. **Visual Feedback**: Show users when data has been modified
4. **Save Management**: Handle form submission and state reset

## NiceGUI-Specific Approaches

### 1. Using NiceGUI Reactive Variables

NiceGUI provides `ui.state` for creating reactive variables that automatically update the UI:

```python
from nicegui import ui

@ui.page('/')
def main_page():
    # Create reactive state variables
    form_data, set_form_data = ui.state({
        'name': '',
        'email': '',
        'description': ''
    })
    
    # Track if form is dirty
    is_dirty, set_is_dirty = ui.state(False)
    original_data, set_original_data = ui.state({})
    
    def mark_dirty():
        set_is_dirty(True)
    
    def save_form():
        # Save logic here
        set_original_data(form_data.copy())
        set_is_dirty(False)
        ui.notify('Changes saved!')
    
    def check_dirty():
        dirty = form_data != original_data
        set_is_dirty(dirty)
    
    # Form inputs with change tracking
    ui.input('Name').bind_value(form_data, 'name').on('change', check_dirty)
    ui.input('Email').bind_value(form_data, 'email').on('change', check_dirty)
    ui.textarea('Description').bind_value(form_data, 'description').on('change', check_dirty)
    
    # Save button that's only enabled when dirty
    ui.button('Save', on_click=save_form).bind_enabled_from(is_dirty, 'value')
    
    # Status indicator
    ui.label().bind_text_from(is_dirty, 'value', 
                             lambda dirty: '● Unsaved changes' if dirty else '✓ All changes saved')
```

### 2. Using Data Binding and Validation

Leverage NiceGUI's binding system for automatic state tracking:

```python
from nicegui import ui

class FormState:
    def __init__(self):
        self.name = ''
        self.email = ''
        self.description = ''
        self.is_dirty = False
        self.original_state = {}
    
    def mark_dirty(self):
        self.is_dirty = True
    
    def save(self):
        # Save logic
        self.original_state = self.get_current_state()
        self.is_dirty = False
    
    def get_current_state(self):
        return {
            'name': self.name,
            'email': self.email,
            'description': self.description
        }
    
    def check_changes(self):
        current = self.get_current_state()
        self.is_dirty = current != self.original_state

@ui.page('/')
def form_page():
    state = FormState()
    
    # Bind form fields to state object
    ui.input('Name').bind_value(state, 'name').on('change', state.check_changes)
    ui.input('Email').bind_value(state, 'email').on('change', state.check_changes)
    ui.textarea('Description').bind_value(state, 'description').on('change', state.check_changes)
    
    # UI elements that reflect dirty state
    with ui.row():
        ui.button('Save', on_click=state.save).bind_enabled_from(state, 'is_dirty')
        ui.button('Reset').bind_enabled_from(state, 'is_dirty')
    
    ui.label().bind_text_from(state, 'is_dirty', 
                             lambda dirty: 'Unsaved changes' if dirty else 'Saved')
```

### 3. Using Refreshable UI for Dynamic Updates

Combine `@ui.refreshable` with state tracking:

```python
from nicegui import ui

form_data = {'name': '', 'email': '', 'notes': ''}
original_data = {}
is_dirty = False

def check_dirty():
    global is_dirty
    is_dirty = form_data != original_data
    status_display.refresh()

@ui.refreshable
def status_display():
    if is_dirty:
        ui.label('● Unsaved changes').classes('text-orange-600')
    else:
        ui.label('✓ All saved').classes('text-green-600')

@ui.refreshable
def save_button():
    ui.button('Save', on_click=save_changes).props('disable' if not is_dirty else '')

def save_changes():
    global original_data, is_dirty
    # Save logic here
    original_data = form_data.copy()
    is_dirty = False
    save_button.refresh()
    status_display.refresh()
    ui.notify('Changes saved!')

@ui.page('/')
def form_page():
    global original_data
    
    ui.input('Name').bind_value(form_data, 'name').on('change', check_dirty)
    ui.input('Email').bind_value(form_data, 'email').on('change', check_dirty)
    ui.textarea('Notes').bind_value(form_data, 'notes').on('change', check_dirty)
    
    save_button()
    status_display()
```

## Browser-Level Protection

### 1. Using JavaScript beforeunload Event

Add browser-level protection against accidental page closure:

```python
from nicegui import ui

@ui.page('/')
def protected_form():
    # Form state tracking
    is_dirty, set_is_dirty = ui.state(False)
    
    # JavaScript to warn on page unload
    ui.add_head_html("""
    <script>
    let formDirty = false;
    
    function setFormDirty(dirty) {
        formDirty = dirty;
    }
    
    window.addEventListener('beforeunload', function(e) {
        if (formDirty) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });
    
    // Clear warning on form submission
    document.addEventListener('submit', function() {
        formDirty = false;
    });
    </script>
    """)
    
    def mark_dirty():
        set_is_dirty(True)
        ui.run_javascript('setFormDirty(true)')
    
    def save_form():
        # Save logic
        set_is_dirty(False)
        ui.run_javascript('setFormDirty(false)')
        ui.notify('Saved!')
    
    # Form inputs
    ui.input('Field 1').on('change', mark_dirty)
    ui.input('Field 2').on('change', mark_dirty)
    ui.button('Save', on_click=save_form)
```

### 2. Advanced Browser Protection

More sophisticated browser-level tracking:

```python
from nicegui import ui

@ui.page('/')
def advanced_form():
    ui.add_head_html("""
    <script>
    class FormTracker {
        constructor() {
            this.originalData = {};
            this.isDirty = false;
            this.isSubmitting = false;
            this.init();
        }
        
        init() {
            // Store initial form state
            this.captureOriginalState();
            
            // Listen for input changes
            document.addEventListener('input', (e) => {
                this.checkDirty();
            });
            
            // Listen for form submission
            document.addEventListener('submit', (e) => {
                this.isSubmitting = true;
            });
            
            // Warn before leaving
            window.addEventListener('beforeunload', (e) => {
                if (this.isDirty && !this.isSubmitting) {
                    e.preventDefault();
                    e.returnValue = 'Changes you made may not be saved.';
                    return e.returnValue;
                }
            });
        }
        
        captureOriginalState() {
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                this.originalData[input.name || input.id] = input.value;
            });
        }
        
        checkDirty() {
            const inputs = document.querySelectorAll('input, textarea, select');
            this.isDirty = false;
            
            inputs.forEach(input => {
                const key = input.name || input.id;
                if (this.originalData[key] !== input.value) {
                    this.isDirty = true;
                }
            });
            
            // Notify Python side
            window.postMessage({
                type: 'form-dirty-state',
                isDirty: this.isDirty
            }, '*');
        }
        
        markClean() {
            this.captureOriginalState();
            this.isDirty = false;
            this.isSubmitting = false;
        }
    }
    
    // Initialize tracker
    const formTracker = new FormTracker();
    window.formTracker = formTracker;
    </script>
    """)
```

## Visual Feedback Patterns

### 1. Status Indicators

```python
from nicegui import ui

@ui.page('/')
def form_with_indicators():
    is_dirty, set_is_dirty = ui.state(False)
    
    def update_status():
        set_is_dirty(True)
    
    def save_changes():
        set_is_dirty(False)
        ui.notify('Changes saved!', type='positive')
    
    # Header with status
    with ui.header():
        ui.label('My Form')
        ui.space()
        with ui.row():
            ui.icon('circle', size='sm').bind_color_from(
                is_dirty, 'value', 
                lambda dirty: 'orange' if dirty else 'green'
            )
            ui.label().bind_text_from(
                is_dirty, 'value',
                lambda dirty: 'Unsaved changes' if dirty else 'All saved'
            )
    
    # Form content
    ui.input('Name').on('change', update_status)
    ui.textarea('Description').on('change', update_status)
    
    # Save button with visual state
    ui.button('Save Changes', on_click=save_changes).bind_enabled_from(is_dirty, 'value')
```

### 2. Tab-Based Forms with Individual Status

```python
from nicegui import ui

@ui.page('/')
def tabbed_form():
    # Track dirty state for each tab
    tab_states = {
        'basic': ui.state(False),
        'advanced': ui.state(False),
        'scripts': ui.state(False)
    }
    
    def mark_tab_dirty(tab_name):
        tab_states[tab_name][1](True)
    
    def get_tab_label(tab_name, base_label):
        is_dirty = tab_states[tab_name][0]
        return f"{base_label} {'●' if is_dirty else ''}"
    
    with ui.tabs() as tabs:
        basic_tab = ui.tab('basic')
        advanced_tab = ui.tab('advanced') 
        scripts_tab = ui.tab('scripts')
    
    with ui.tab_panels(tabs, value='basic'):
        with ui.tab_panel('basic'):
            ui.input('Project Name').on('change', lambda: mark_tab_dirty('basic'))
            ui.input('Description').on('change', lambda: mark_tab_dirty('basic'))
        
        with ui.tab_panel('advanced'):
            ui.input('Config Path').on('change', lambda: mark_tab_dirty('advanced'))
            ui.number('Port').on('change', lambda: mark_tab_dirty('advanced'))
        
        with ui.tab_panel('scripts'):
            ui.textarea('Custom Script').on('change', lambda: mark_tab_dirty('scripts'))
    
    # Update tab labels to show dirty state
    @ui.refreshable
    def update_tab_labels():
        basic_tab.set_text(get_tab_label('basic', 'Basic Info'))
        advanced_tab.set_text(get_tab_label('advanced', 'Advanced'))
        scripts_tab.set_text(get_tab_label('scripts', 'Scripts'))
```

## Best Practices

### 1. Performance Considerations

- **Debounce input events**: Avoid excessive state checks on every keystroke
- **Use reactive variables**: Leverage NiceGUI's built-in reactivity
- **Minimize DOM updates**: Group related updates together

```python
import asyncio
from nicegui import ui

@ui.page('/')
def optimized_form():
    # Debounced change detection
    debounce_timer = None
    
    async def debounced_check():
        nonlocal debounce_timer
        if debounce_timer:
            debounce_timer.cancel()
        
        debounce_timer = asyncio.create_task(asyncio.sleep(0.5))
        try:
            await debounce_timer
            # Perform expensive state check here
            check_form_state()
        except asyncio.CancelledError:
            pass
    
    def check_form_state():
        # Your state checking logic
        pass
    
    ui.input('Search').on('change', lambda: asyncio.create_task(debounced_check()))
```

### 2. Error Handling

```python
from nicegui import ui

@ui.page('/')
def robust_form():
    try:
        # Form logic with error handling
        def save_with_validation():
            try:
                # Validation logic
                if not validate_form():
                    ui.notify('Please fix validation errors', type='negative')
                    return
                
                # Save logic
                save_data()
                ui.notify('Saved successfully!', type='positive')
                
            except Exception as e:
                ui.notify(f'Save failed: {str(e)}', type='negative')
        
        def validate_form():
            # Implement validation logic
            return True
        
        def save_data():
            # Implement save logic
            pass
            
    except Exception as e:
        ui.notify(f'Form initialization failed: {str(e)}', type='negative')
```

### 3. Memory Management

```python
from nicegui import ui, app

@ui.page('/')
def memory_conscious_form():
    # Use app.storage for persistent state
    if 'form_data' not in app.storage.user:
        app.storage.user['form_data'] = {}
    
    # Clean up on page exit
    def cleanup():
        # Clean up any resources
        pass
    
    # Register cleanup
    ui.context.client.on_disconnect(cleanup)
```

## Tools and Libraries

### 1. Built-in NiceGUI Features
- `ui.state`: Reactive variables for state management
- `ui.refreshable`: Dynamic UI updates
- Binding system: Automatic data synchronization
- Storage system: Persistent state management

### 2. JavaScript Libraries (for advanced cases)
- **FormData API**: Native browser form handling
- **MutationObserver**: DOM change detection
- **Proxy objects**: Deep object change tracking

### 3. Third-party Python Libraries
- **Pydantic**: Data validation and serialization
- **marshmallow**: Object serialization/deserialization
- **attrs/dataclasses**: Structured data management

## Implementation Checklist

- [ ] Choose appropriate state tracking method (reactive variables vs manual)
- [ ] Implement change detection for all form fields
- [ ] Add browser-level protection against data loss
- [ ] Provide visual feedback for unsaved changes
- [ ] Handle form submission and state reset
- [ ] Add validation and error handling
- [ ] Test edge cases (page refresh, navigation, etc.)
- [ ] Optimize performance for large forms
- [ ] Document the implementation for maintenance

## Common Pitfalls

1. **Not handling form submission**: Remember to clear dirty state on successful save
2. **Excessive event handlers**: Use debouncing for performance
3. **Memory leaks**: Clean up event listeners and timers
4. **Browser compatibility**: Test beforeunload behavior across browsers
5. **Race conditions**: Handle async operations properly

## References

- [NiceGUI Documentation - Refreshable UI](https://nicegui.io/documentation/refreshable)
- [NiceGUI Documentation - Storage](https://nicegui.io/documentation/storage)
- [NiceGUI Documentation - Binding Properties](https://nicegui.io/documentation/section_binding_properties)
- [MDN - beforeunload event](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event)
- [Web Forms Best Practices](https://www.smashingmagazine.com/2018/08/best-practices-for-mobile-form-design/)
